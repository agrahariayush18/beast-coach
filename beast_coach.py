import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
HEALTH_FLAGS = ["pregnant", "pregnancy", "kidney", "diabetes", "blood pressure",
                "heart", "medication", "disease", "thyroid", "under 18", "child"]

load_dotenv()  # load the API key from .env

# Load the pieces ONCE (not on every question)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("beastlife")
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def answer(question):
    # STEP 6 — RETRIEVE: embed the question, find the 3 nearest chunks
    q_vector = embedder.encode(question).tolist()
    results = collection.query(query_embeddings=[q_vector], n_results=3)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    distances = results["distances"][0]          

    # GUARDRAIL 1 — honest fallback: nothing relevant found
    if not chunks or min(distances) > 0.8:
        return ("I don't have that in my knowledge base yet. For anything I'm unsure "
                "about, please check beastlife.in or contact care@beastlife.in."), []

    # STEP 7 — AUGMENT: build the prompt with the retrieved chunks
    context = "\n\n---\n\n".join(chunks)
    system_prompt = (
        "You are Beast Coach, BeastLife's friendly supplement advisor. "
        "Answer using ONLY the context below. If the answer isn't in the context, "
        "say you don't have that info. Never make up products, prices, or specs. "
        "Keep it clear and motivating.\n\n"
        f"CONTEXT:\n{context}"
    )

    # STEP 8 — GENERATE: ask the LLM
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
    )
    reply = response.choices[0].message.content

    # GUARDRAIL 2 — medical safety
    if any(flag in question.lower() for flag in HEALTH_FLAGS):
        reply += ("\n\n⚠️ Note: I'm not a medical professional. If you have a health "
                  "condition, are pregnant, or are under 18, please consult a doctor "
                  "before starting any supplement.")

    return reply, sources


