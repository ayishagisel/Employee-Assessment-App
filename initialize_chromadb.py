from app import create_app
from app.services.chromadb_service import ChromaDBService

def initialize_chromadb():
    # Create Flask app context
    app = create_app()
    with app.app_context():
        print("Initializing ChromaDB service...")
        
        # Initialize ChromaDB service
        chromadb_service = ChromaDBService()
        
        # Sync existing assessments
        print("Syncing existing assessments to ChromaDB...")
        chromadb_service.sync_assessments()
        
        print("ChromaDB initialization completed successfully!")
        print("You can now use semantic search on your assessments.")

if __name__ == '__main__':
    initialize_chromadb()