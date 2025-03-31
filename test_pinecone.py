from pinecone import Pinecone

PINECONE_API_KEY = "your_actual_api_key"
PINECONE_ENV = "your_actual_env"

pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

print(pc.list_indexes().names) 