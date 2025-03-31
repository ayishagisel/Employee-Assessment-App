from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

PINECONE_API_KEY = "your_actual_api_key"
PINECONE_ENV = "your_actual_env"

pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

class VectorDB:
    def __init__(self, index_name, dimension):
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric='cosine'
            )
        self.index = pc.Index(index_name)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def add_vectors(self, data):
        vectors = self.model.encode(data['text']).tolist()
        self.index.upsert(vectors=zip(data['id'], vectors))

    def search_vectors(self, query, top_k=5):
        query_vector = self.model.encode([query]).tolist()
        result = self.index.query(queries=query_vector, top_k=top_k, include_metadata=True)
        return [{"id": match['id'], "score": match['score'], "metadata": match['metadata']} for match in result['matches'][0]] 