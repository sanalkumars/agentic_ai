import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def main() -> None:
    embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    # Persistent storage means data is saved in the local folder ./chroma_db.
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(
        name="articles",
        embedding_function=embedding_function,
    )

    docs = [
        "Tata is a leading automobile company in India.",
        "The Mahindra Thar is popular among middle-class families in India.",
        "Apple is a leading smartphone company in the Indian market.",
    ]
    ids = ["id1", "id2", "id3"]

    existing = collection.get(ids=ids, include=[])
    if existing.get("ids"):
        print("Data already exists in Chroma.")
    else:
        collection.add(ids=ids, documents=docs)
        print("Data added to Chroma.")

    results = collection.query(query_texts=["Which vehicle is popular in India?"], n_results=2)
    print("\nSearch results:")
    print(results["documents"])


if __name__ == "__main__":
    main()
