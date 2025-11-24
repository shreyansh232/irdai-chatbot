import streamlit as st
import os
import json
import faiss
import numpy as np
import openai
from prompt_template import build_prompt
from typing import List, Dict
from dotenv import load_dotenv
import re

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root (parent of app/)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# Construct paths relative to project root
INDEX_DIR = os.path.join(PROJECT_ROOT, "irdai_pdfs", "index")
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
META_PATH = os.path.join(INDEX_DIR, "meta.jsonl")
CHUNKS_DIR = os.path.join(PROJECT_ROOT, "irdai_pdfs", "chunks")


@st.cache_resource
def load_index():
    idx = faiss.read_index(INDEX_PATH)
    meta = []
    with open(META_PATH, encoding="utf-8") as f:
        for line in f:
            meta.append(json.loads(line))
    # also load chunk text content
    chunk_map = {}
    for fname in os.listdir(CHUNKS_DIR):
        with open(os.path.join(CHUNKS_DIR, fname), encoding="utf-8") as fh:
            for line in fh:
                j = json.loads(line)
                chunk_map[j["chunk_id"]] = j["text"]
    return idx, meta, chunk_map


def embed_query(q):
    resp = client.embeddings.create(input=q, model="text-embedding-3-small")
    return np.array(resp.data[0].embedding).astype("float32")


def retrieve_top_k(index, meta, chunk_map, q_embedding, k=4):
    D, I = index.search(np.array([q_embedding]), k)
    ids = I[0].tolist()
    results = []
    for idx in ids:
        if idx < 0:
            continue
        m = meta[idx]
        chunk_text = chunk_map.get(m["chunk_id"], "")
        results.append(
            {"doc_id": m["doc_id"], "chunk_id": m["chunk_id"], "text": chunk_text}
        )
    return results


def call_chatgpt(messages: List[Dict[str, str]]):
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=400,
    )
    return resp.choices[0].message.content


def get_citations(answer: str, retrieved_chunks: List[dict]) -> List[str]:
    citations = set()
    # Split answer into sentences
    answer_sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", answer)

    for chunk in retrieved_chunks:
        chunk_sentences = re.split(
            r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", chunk["text"]
        )
        for cs in chunk_sentences:
            for ans_sent in answer_sentences:
                # Simple substring check
                if cs.strip() in ans_sent.strip() and len(cs.strip()) > 20:
                    citations.add(
                        f"- {cs.strip()} (Source: {chunk['doc_id']}/{chunk['chunk_id']})"
                    )
    return list(citations)


def main():
    st.title("IRDAI Chatbot")
    st.markdown(
        "Ask questions about IRDAI circulars. Answers will include citations to the source chunk."
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if query := st.chat_input("What is your question?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            with st.spinner("Searching IRDAI corpus..."):
                idx, meta, chunk_map = load_index()
                q_emb = embed_query(query)
                retrieved = retrieve_top_k(idx, meta, chunk_map, q_emb, k=4)

            with st.spinner("Generating answer..."):
                # Get last 3 Q/A pairs for history
                history = st.session_state.messages[
                    -7:-1
                ]  # 3 pairs of user/assistant messages

                prompt_messages = build_prompt(query, retrieved, history)
                ans = call_chatgpt(prompt_messages)

                citations = get_citations(ans, retrieved)

                full_response += ans
                if citations:
                    full_response += "\n\n**Cited Sources:**\n" + "\n".join(citations)

                message_placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()

