import os
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
chromadb_client = chromadb.PersistentClient(path="./chroma_store")
collection = chromadb_client.get_or_create_collection("course_materials")

def load_all_docs(folder="./docs"):

    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            text = f.read()


        chunks = []
        i = 0
        while i < len(text):
            chunk = text[i : i+400]
            chunks.append(chunk)
            i += 400
        embeddings = model.encode(chunks).tolist()
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"{filename}_{j}" for j in range(len(chunks))]
        )



def retrieve(query: str, n=3) -> str:
    query_emb = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_emb, n_results=n)
    if not results["documents"][0]:
        return ""
    return "\n\n".join(results["documents"][0])