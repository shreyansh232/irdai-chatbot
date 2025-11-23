import os
from glob import glob
import json

# create a chunks directory to store chunks
os.makedirs("irdai_pdfs/chunks", exist_ok=True)


def chunk_text(text, max_tokens=450, overlap=50):
    # convert the text into list of strings
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + max_tokens]
        chunks.append(" ".join(chunk_words))
        i += max_tokens - overlap
    return chunks


def main():
    for path in glob("irdai_pdfs/texts/*.txt"):
        docid = os.path.basename(path).replace(".txt", "")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            continue
        # chunk by words (approx tokens)
        chunks = chunk_text(text, max_tokens=450, overlap=50)
        out_file = os.path.join("irdai_pdfs/chunks", docid + ".jsonl")
        with open(out_file, "w", encoding="utf-8") as out:
            for i, c in enumerate(chunks):
                entry = {
                    "doc_id": docid,
                    "chunk_id": f"{docid}_{i}",
                    "text": c,
                    "position": i,
                }
                out.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print("Wrote chunks for", docid, "count:", len(chunks))


if __name__ == "__main__":
    main()
