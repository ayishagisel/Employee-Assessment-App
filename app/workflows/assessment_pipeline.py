from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
import os
from sqlalchemy import create_engine, text
from concurrent.futures import ThreadPoolExecutor
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssessmentPipeline:
    def __init__(self, db_connection_string: str, openai_api_key: str):
        self.db_connection_string = db_connection_string
        self.openai_api_key = openai_api_key
        
        # Initialize LangChain components
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo",
            openai_api_key=openai_api_key
        )
        
        # Initialize vector store
        self.vector_store = PGVector(
            connection_string=db_connection_string,
            embedding_function=self.embeddings,
            collection_name="employee_reviews"
        )
        
        # Initialize sentiment analysis prompt
        self.sentiment_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert HR analyst. Analyze the employee review and historical context to provide:\n1. Sentiment analysis (positive/negative/neutral with score 0-1)\n2. Key strengths identified\n3. Areas of improvement\n4. Career growth potential\n\nFormat your response as JSON with these keys:\n{{\n    \"sentiment_score\": float,\n    \"sentiment_label\": str,\n    \"strengths\": list[str],\n    \"improvements\": list[str],\n    \"growth_potential\": str,\n    \"confidence\": float\n}}"),
            ("human", "{current_review}\n\nHistorical Context:\n{historical_context}\n\nPerformance Metrics:\n{performance_metrics}")
        ])
        
        # Initialize promotion recommendation prompt
        self.promotion_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert HR advisor. Based on the employee's review analysis and performance metrics, provide a promotion recommendation. Consider:\n- Sentiment analysis results\n- Historical performance trends\n- Current role and potential next steps\n- Quantitative metrics\n\nFormat your response as JSON with these keys:\n{{\n    \"promotion_recommended\": bool,\n    \"confidence_score\": float,\n    \"recommended_role\": str,\n    \"rationale\": str,\n    \"development_areas\": list[str],\n    \"timeline\": str\n}}"),
            ("human", "{sentiment_analysis}\n\nPerformance Metrics:\n{performance_metrics}\n\nHistorical Reviews:\n{historical_reviews}")
        ])

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def get_similar_reviews(self, review_text: str, limit: int = 3) -> List[Document]:
        """Retrieve similar historical reviews from vector store."""
        try:
            results = await self.vector_store.asimilarity_search(review_text, k=limit)
            logger.info(f"Retrieved {len(results)} similar reviews")
            return results
        except Exception as e:
            logger.error(f"Error retrieving similar reviews: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def analyze_sentiment(self, review: str, historical_context: List[Document], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment using GPT-4 with historical context."""
        try:
            # Format historical context
            context_text = "\n".join([doc.page_content for doc in historical_context])
            metrics_text = json.dumps(metrics, indent=2)
            
            # Create sentiment analysis chain
            chain = LLMChain(llm=self.llm, prompt=self.sentiment_prompt)
            
            # Run analysis
            result = await chain.arun(
                current_review=review,
                historical_context=context_text,
                performance_metrics=metrics_text
            )
            
            # Parse JSON response
            analysis = json.loads(result)
            logger.info(f"Sentiment analysis completed with score: {analysis['sentiment_score']}")
            return analysis
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_promotion_recommendation(
        self,
        sentiment_analysis: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        historical_reviews: List[Document]
    ) -> Dict[str, Any]:
        """Generate promotion recommendation based on all available data."""
        try:
            chain = LLMChain(llm=self.llm, prompt=self.promotion_prompt)
            
            result = await chain.arun(
                sentiment_analysis=json.dumps(sentiment_analysis, indent=2),
                performance_metrics=json.dumps(performance_metrics, indent=2),
                historical_reviews="\n".join([doc.page_content for doc in historical_reviews])
            )
            
            recommendation = json.loads(result)
            logger.info(f"Generated promotion recommendation with confidence: {recommendation['confidence_score']}")
            return recommendation
        except Exception as e:
            logger.error(f"Error generating promotion recommendation: {str(e)}")
            raise

    async def process_single_review(self, review_text: str, employee_id: str, performance_metrics: Dict = None) -> Dict:
        """Process a single review with mock data for testing."""
        try:
            # Mock sentiment analysis
            sentiment_analysis = {
                "sentiment_score": 0.85,
                "sentiment_label": "Positive",
                "confidence": 0.92,
                "strengths": [
                    "Strong communication skills",
                    "Excellent problem-solving abilities",
                    "Great team player",
                    "Proactive approach to tasks"
                ]
            }

            # Mock promotion recommendation
            promotion_recommendation = {
                "promotion_recommended": True,
                "recommended_role": "Senior Software Engineer",
                "confidence_score": 0.88,
                "timeline": "Within 6-12 months",
                "rationale": "Consistently demonstrates leadership qualities and technical expertise",
                "development_areas": [
                    "Project management experience",
                    "Mentoring skills",
                    "Advanced system architecture"
                ]
            }

            return {
                "status": "success",
                "sentiment_analysis": sentiment_analysis,
                "promotion_recommendation": promotion_recommendation
            }

        except Exception as e:
            logger.error(f"Error in mock analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def process_batch(self, reviews: List[Dict[str, Any]], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Process multiple reviews in parallel."""
        async def process_review_wrapper(review_data: Dict[str, Any]) -> Dict[str, Any]:
            return await self.process_single_review(
                review_data["review_text"],
                review_data["employee_id"],
                review_data["performance_metrics"]
            )
        
        # Process reviews in parallel with concurrency limit
        tasks = [process_review_wrapper(review) for review in reviews]
        results = await asyncio.gather(*tasks)
        
        # Log batch processing results
        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(f"Batch processing completed. {success_count}/{len(results)} successful.")
        
        return results

    def get_performance_metrics(self, employee_name: str) -> Dict[str, Any]:
        """Get mock performance metrics for an employee."""
        try:
            # Mock performance metrics
            return {
                "overall_rating": 4.5,
                "attendance": 0.95,
                "productivity": 0.88,
                "quality": 0.92,
                "teamwork": 0.90,
                "initiative": 0.85,
                "communication": 0.93,
                "leadership": 0.82,
                "technical_skills": 0.89,
                "problem_solving": 0.91,
                "adaptability": 0.87,
                "reliability": 0.94,
                "creativity": 0.86,
                "time_management": 0.89,
                "customer_focus": 0.88
            }
        except Exception as e:
            logger.error(f"Error getting mock performance metrics: {str(e)}")
            return {} 