from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
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
from ..validation.fairness_validator import FairnessValidator
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from ..models import db, Assessment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalysis(BaseModel):
    """Model for sentiment analysis results."""
    sentiment_score: float = Field(description="Overall sentiment score between -1 and 1")
    sentiment_label: str = Field(description="Human-readable sentiment label (e.g., 'Positive', 'Negative', 'Neutral')")
    confidence: float = Field(description="Confidence score between 0 and 1")
    strengths: List[str] = Field(description="List of identified strengths in the review")
    weaknesses: Optional[List[str]] = Field(description="List of identified areas for improvement", default_factory=list)
    key_themes: Optional[List[str]] = Field(description="Key themes identified in the review", default_factory=list)

class PromotionRecommendation(BaseModel):
    """Model for promotion recommendation results."""
    promotion_recommended: bool = Field(description="Whether a promotion is recommended")
    recommended_role: Optional[str] = Field(description="Recommended new role if promotion is recommended")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    timeline: Optional[str] = Field(description="Recommended timeline for promotion")
    rationale: str = Field(description="Explanation for the recommendation")
    development_areas: Optional[List[str]] = Field(description="Areas that need development before promotion", default_factory=list)

class AssessmentPipeline:
    def __init__(self, db_connection_string: str, openai_api_key: str):
        """Initialize the assessment pipeline with database connection and OpenAI API key."""
        self.db_connection_string = db_connection_string
        self.openai_api_key = openai_api_key
        
        # Initialize embeddings with minimal required parameters
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model="text-embedding-ada-002"
        )
        
        # Initialize language model
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Initialize vector store as None - will be created lazily when needed
        self.vector_store = None
        
        # Initialize fairness validator
        self.validator = FairnessValidator()
        
        # Initialize result cache
        self._result_cache = {}
        self._employee_data_cache = {}
        
        # Initialize prompts
        self.sentiment_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at analyzing employee performance reviews and identifying key themes and sentiments."),
            ("user", "Analyze the following performance review and provide a detailed analysis:\n\n{review_text}")
        ])
        
        self.promotion_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at evaluating employee performance and making promotion recommendations."),
            ("user", "Based on the following performance review and metrics, provide a promotion recommendation:\n\nReview: {review_text}\n\nMetrics: {metrics}")
        ])
        
        # Initialize output parsers
        self.sentiment_parser = PydanticOutputParser(pydantic_object=SentimentAnalysis)
        self.promotion_parser = PydanticOutputParser(pydantic_object=PromotionRecommendation)
        
        # Initialize chains
        self.sentiment_chain = LLMChain(
            llm=self.llm,
            prompt=self.sentiment_prompt,
            output_parser=self.sentiment_parser
        )
        
        self.promotion_chain = LLMChain(
            llm=self.llm,
            prompt=self.promotion_prompt,
            output_parser=self.promotion_parser
        )

    def _initialize_vector_store(self):
        """Lazily initialize the vector store when needed."""
        if self.vector_store is None:
            try:
                self.vector_store = FAISS.from_texts(
                    ["Initial placeholder text"],
                    self.embeddings
                )
            except Exception as e:
                logger.error(f"Error initializing vector store: {str(e)}")
                if "insufficient_quota" in str(e):
                    logger.warning("OpenAI API quota exceeded. Vector store functionality will be limited.")
                    # Create a mock vector store that returns empty results
                    self.vector_store = None
                else:
                    raise

    def _cache_result(self, result: Dict[str, Any], employee_data: Dict[str, Any]):
        """Cache assessment results for validation."""
        self._result_cache[employee_data["id"]] = result
        self._employee_data_cache[employee_data["id"]] = employee_data

    def _run_validation(self) -> Dict[str, Any]:
        """Run fairness validation on cached results."""
        if len(self._result_cache) < 5:
            return {
                "status": "skipped",
                "message": "Not enough data for meaningful validation (minimum 5 assessments required)"
            }

        # Run validations
        sentiment_results = self.validator.validate_sentiment_analysis(
            list(self._result_cache.values()),
            list(self._employee_data_cache.values())
        )
        
        promotion_results = self.validator.validate_promotion_recommendations(
            list(self._result_cache.values()),
            list(self._employee_data_cache.values())
        )
        
        # Store results
        self.validator.results = sentiment_results + promotion_results
        
        # Generate report
        report = self.validator.generate_report()
        
        # Log validation results
        self.validator.log_results()
        
        return {
            "status": "completed",
            "report": report,
            "has_failures": report["failed_validations"] > 0
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def get_similar_reviews(self, review_text: str, limit: int = 3) -> List[Document]:
        """Retrieve similar historical reviews from vector store."""
        try:
            self._initialize_vector_store()
            if self.vector_store is None:
                logger.warning("Vector store not available due to API quota limits. Returning empty results.")
                return []
            results = await self.vector_store.asimilarity_search(review_text, k=limit)
            logger.info(f"Retrieved {len(results)} similar reviews")
            return results
        except Exception as e:
            logger.error(f"Error retrieving similar reviews: {str(e)}")
            if "insufficient_quota" in str(e):
                logger.warning("OpenAI API quota exceeded. Returning empty results.")
                return []
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

            result = {
                "status": "success",
                "sentiment_analysis": sentiment_analysis,
                "promotion_recommendation": promotion_recommendation,
                "employee_id": employee_id
            }

            # Cache result for validation
            employee_data = {
                "id": employee_id,
                "department": review_text.split("Department:")[1].split("\n")[0].strip(),
                "role_level": review_text.split("Position:")[1].split("\n")[0].strip(),
                "gender": "unknown"  # You might want to add this to your assessment form
            }
            self._cache_result(result, employee_data)

            # Run validation if we have enough data
            validation_result = self._run_validation()
            if validation_result["status"] == "completed" and validation_result["has_failures"]:
                self.logger.warning("Fairness validation detected potential biases in assessments")
                result["validation_warning"] = True
                result["validation_report"] = validation_result["report"]

            return result

        except Exception as e:
            self.logger.error(f"Error in mock analysis: {str(e)}")
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