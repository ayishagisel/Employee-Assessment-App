from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from sqlalchemy import create_engine, text
import logging
from typing import List, Dict, Any
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

async def setup_vector_store(connection_string: str, openai_api_key: str) -> PGVector:
    """Initialize and setup the vector store in PostgreSQL."""
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vector_store = PGVector.from_documents(
            [],  # Empty initial documents
            embeddings,
            collection_name="employee_reviews",
            connection_string=connection_string,
        )
        logger.info("Vector store initialized successfully")
        return vector_store
    except Exception as e:
        logger.error(f"Error setting up vector store: {str(e)}")
        raise

async def add_review_to_vector_store(
    vector_store: PGVector,
    review_text: str,
    metadata: Dict[str, Any]
) -> bool:
    """Add a new review to the vector store with metadata."""
    try:
        await vector_store.aadd_texts(
            texts=[review_text],
            metadatas=[{
                **metadata,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
        logger.info(f"Added review to vector store for employee {metadata.get('employee_id')}")
        return True
    except Exception as e:
        logger.error(f"Error adding review to vector store: {str(e)}")
        return False

def setup_metrics_table(connection_string: str):
    """Create the employee metrics table if it doesn't exist."""
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS employee_metrics (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    monthly_sales FLOAT,
                    projects_completed INT,
                    customer_satisfaction FLOAT,
                    attendance_rate FLOAT,
                    peer_review_score FLOAT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_employee_date UNIQUE (employee_id, date)
                );
                
                CREATE INDEX IF NOT EXISTS idx_employee_metrics_employee_id_date 
                ON employee_metrics(employee_id, date);
            """))
            connection.commit()
        logger.info("Employee metrics table setup completed")
    except Exception as e:
        logger.error(f"Error setting up metrics table: {str(e)}")
        raise

async def batch_add_reviews_to_vector_store(
    vector_store: PGVector,
    reviews: List[Dict[str, Any]],
    batch_size: int = 50
) -> Dict[str, Any]:
    """Add multiple reviews to the vector store in batches."""
    total = len(reviews)
    successful = 0
    failed = 0
    
    for i in range(0, total, batch_size):
        batch = reviews[i:i + batch_size]
        try:
            texts = [r["review_text"] for r in batch]
            metadatas = [{
                "employee_id": r["employee_id"],
                "timestamp": datetime.utcnow().isoformat(),
                "department": r.get("department", ""),
                "position": r.get("position", "")
            } for r in batch]
            
            await vector_store.aadd_texts(texts=texts, metadatas=metadatas)
            successful += len(batch)
            logger.info(f"Successfully processed batch {i//batch_size + 1}")
        except Exception as e:
            failed += len(batch)
            logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
    
    return {
        "total": total,
        "successful": successful,
        "failed": failed
    }

def get_review_statistics(connection_string: str) -> Dict[str, Any]:
    """Get statistics about stored reviews and embeddings."""
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            # Get vector store statistics
            vector_stats = connection.execute(text("""
                SELECT 
                    COUNT(*) as total_reviews,
                    COUNT(DISTINCT metadata->>'employee_id') as unique_employees,
                    MIN(metadata->>'timestamp')::timestamp as oldest_review,
                    MAX(metadata->>'timestamp')::timestamp as newest_review
                FROM langchain_pg_embedding;
            """)).fetchone()
            
            # Get department distribution
            dept_dist = connection.execute(text("""
                SELECT 
                    metadata->>'department' as department,
                    COUNT(*) as count
                FROM langchain_pg_embedding
                GROUP BY metadata->>'department'
                ORDER BY count DESC;
            """)).fetchall()
            
            return {
                "total_reviews": vector_stats[0],
                "unique_employees": vector_stats[1],
                "oldest_review": vector_stats[2].isoformat() if vector_stats[2] else None,
                "newest_review": vector_stats[3].isoformat() if vector_stats[3] else None,
                "department_distribution": {
                    d[0]: d[1] for d in dept_dist if d[0]
                }
            }
    except Exception as e:
        logger.error(f"Error getting review statistics: {str(e)}")
        return {} 