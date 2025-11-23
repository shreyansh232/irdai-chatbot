from typing import List, Dict

SYSTEM_PROMPT = """You are an assistant that answers user questions using only the provided IRDAI circular excerpts.
Be concise. If the excerpt does not contain the answer, say "I cannot find that in the provided IRDAI circulars" instead of hallucinating.
Always include a short citation showing the doc_id and chunk position used.
Use the conversation history to understand follow-up questions.
"""


def build_prompt(question: str, retrieved_chunks: List[dict], history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    retrieved_chunks: list of dicts with keys: text, doc_id, chunk_id
    history: list of dicts with keys: role, content
    """
    # System prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add history
    messages.extend(history)
        
    # Add retrieved chunks to the user message
    preface = "Here are the IRDAI excerpts to use as facts:\n"
    parts = []
    for i, c in enumerate(retrieved_chunks, 1):
        parts.append(
            f"Excerpt {i} (source: {c['doc_id']} chunk:{c['chunk_id']}):\n{c['text']}\n---"
        )
    parts_text = "\n".join(parts)
    
    # Add the latest question with context
    user_message = f"{preface}\n{parts_text}\n\nQuestion: {question}\nAnswer concisely and provide the citation(s)."
    messages.append({"role": "user", "content": user_message})
    
    return messages
