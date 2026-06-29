import os
import glob
from sentence_transformers import SentenceTransformer
import chromadb

def load_documents(kb_dir="kb"):
    documents = []
    for path in glob.glob(os.path.join(kb_dir, "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        documents.append({"source": os.path.basename(path), "text": text})
    return documents

def chunk_text(text, max_words=150):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def main():
    print("Loading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # open the on-disk vector database
    client = chromadb.PersistentClient(path="./chroma_db")

    # start fresh each run so we never get duplicates
    try:
        client.delete_collection("beastlife")
    except Exception:
        pass
    collection = client.create_collection(
        name="beastlife",
        metadata={"hnsw:space": "cosine"},
    )

    docs = load_documents()
    ids, embeddings, documents, metadatas = [], [], [], []

    for doc in docs:
        for j, chunk in enumerate(chunk_text(doc["text"])):
            vector = embedder.encode(chunk).tolist()      # STEP 3: embed
            ids.append(f"{doc['source']}-chunk{j}")
            embeddings.append(vector)
            documents.append(chunk)
            metadatas.append({"source": doc["source"]})   # the label

    # STEP 4: store everything in the vector DB
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Done. Stored {len(documents)} chunks in Chroma.")

if __name__ == "__main__":
    main()