import os
import json
import glob
from tqdm.auto import tqdm
import numpy as np
import faiss
import openai
import time
import math
from dotenv import load_dotenv


load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise EnvironmentError("No API Key")

openai.api_key = openai_api_key

client = openai.OpenAI(api_key=openai_api_key)


EMBED_MODEL = "text-embedding-3-small"
INDEX_DIR = "irdai_pdfs/index"

os.makedirs(INDEX_DIR, exist_ok=True)


def read_chunks():
    files = glob.glob("irdai_pdfs/chunks/*.jsonl")
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                yield json.loads(line)


def embed_texts(texts, batch_size=16):
    # batch embeddings to reduce rate-limit risk
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # Use OpenAI embeddings API
        resp = client.embeddings.create(input=batch, model=EMBED_MODEL)
        for emb in resp.data:
            embeddings.append(emb.embedding)
        time.sleep(0.1)  # be gentle
    return embeddings


def main():
    entries = list(read_chunks())
    texts = [e["text"] for e in entries]
    meta = [
        {"doc_id": e["doc_id"], "chunk_id": e["chunk_id"], "position": e["position"]}
        for e in entries
    ]
    print("Total chunks:", len(texts))

    # embed all texts (memory: embedding vectors float list)
    B = 16
    vectors = embed_texts(texts, batch_size=B)
    vectors = np.array(vectors).astype("float32")
    # create FAISS index (Flat L2 for simplicity)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    # save index
    faiss.write_index(index, os.path.join(INDEX_DIR, "faiss.index"))
    # save metadata mapping (index -> meta)
    with open(os.path.join(INDEX_DIR, "meta.jsonl"), "w", encoding="utf-8") as f:
        for m in meta:
            f.write(json.dumps(m) + "\n")
    print("Built index and saved to", INDEX_DIR)


if __name__ == "__main__":
    main()
