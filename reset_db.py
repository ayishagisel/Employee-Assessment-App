from app import create_app, db
from app.models import User, Assessment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json

def reset_db():
    """Reset the database and add test data."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create tables
        db.create_all()
        
        # Create test user
        test_user = User(username="testuser", email="test@example.com")
        test_user.set_password("password")
        db.session.add(test_user)
        db.session.commit()
        
        # Create mock assessments
        mock_assessments = [
            {
                "employee_name": "Mike Johnson",
                "employee_id": "EMP001",
                "position": "UX Designer",
                "department": "Design",
                "review_text": "Mike has shown great progress in his UX design skills...",
                "performance_metrics": {
                    "overall_rating": 3.5,
                    "attendance": 0.9,
                    "productivity": 0.85,
                    "quality": 0.8,
                    "teamwork": 0.9,
                    "initiative": 0.75,
                    "communication": 0.8
                },
                "sentiment_analysis": {
                    "sentiment_score": 0.75,
                    "sentiment_label": "Positive",
                    "confidence": 0.85,
                    "strengths": ["Design skills", "Team collaboration"],
                    "weaknesses": ["Time management"],
                    "key_themes": ["Design", "Collaboration"]
                },
                "promotion_recommendation": {
                    "promotion_recommended": False,
                    "confidence_score": 0.8,
                    "recommended_role": None,
                    "timeline": "6-12 months",
                    "rationale": "Needs more experience in current role",
                    "development_areas": ["Leadership skills", "Project management"]
                },
                "status": "completed"
            },
            {
                "employee_name": "Jane Smith",
                "employee_id": "EMP002",
                "position": "Product Manager",
                "department": "Product",
                "review_text": "Jane has demonstrated exceptional leadership...",
                "performance_metrics": {
                    "overall_rating": 4.8,
                    "attendance": 0.95,
                    "productivity": 0.9,
                    "quality": 0.95,
                    "teamwork": 0.9,
                    "initiative": 0.95,
                    "communication": 0.9
                },
                "sentiment_analysis": {
                    "sentiment_score": 0.9,
                    "sentiment_label": "Positive",
                    "confidence": 0.95,
                    "strengths": ["Leadership", "Strategic thinking"],
                    "weaknesses": [],
                    "key_themes": ["Leadership", "Strategy"]
                },
                "promotion_recommendation": {
                    "promotion_recommended": True,
                    "confidence_score": 0.9,
                    "recommended_role": "Senior Product Manager",
                    "timeline": "3-6 months",
                    "rationale": "Consistently exceeds expectations",
                    "development_areas": ["Executive communication"]
                },
                "status": "completed"
            },
            {
                "employee_name": "John Doe",
                "employee_id": "EMP003",
                "position": "Software Engineer",
                "department": "Engineering",
                "review_text": "John is a skilled developer with strong technical abilities...",
                "performance_metrics": {
                    "overall_rating": 4.2,
                    "attendance": 0.85,
                    "productivity": 0.9,
                    "quality": 0.9,
                    "teamwork": 0.8,
                    "initiative": 0.85,
                    "communication": 0.75
                },
                "sentiment_analysis": {
                    "sentiment_score": 0.8,
                    "sentiment_label": "Positive",
                    "confidence": 0.85,
                    "strengths": ["Technical skills", "Problem solving"],
                    "weaknesses": ["Communication"],
                    "key_themes": ["Technical excellence", "Development"]
                },
                "promotion_recommendation": {
                    "promotion_recommended": True,
                    "confidence_score": 0.85,
                    "recommended_role": "Senior Software Engineer",
                    "timeline": "6-9 months",
                    "rationale": "Strong technical skills and growing leadership",
                    "development_areas": ["Team communication", "Mentoring"]
                },
                "status": "pending"
            }
        ]
        
        # Add mock assessments
        for data in mock_assessments:
            assessment = Assessment(
                employee_name=data["employee_name"],
                employee_id=data["employee_id"],
                position=data["position"],
                department=data["department"],
                review_text=data["review_text"],
                performance_metrics=json.dumps(data["performance_metrics"]),
                sentiment_analysis=json.dumps(data["sentiment_analysis"]),
                promotion_recommendation=json.dumps(data["promotion_recommendation"]),
                review_date=datetime.utcnow() - timedelta(days=len(mock_assessments)),
                status=data["status"],
                user_id=test_user.id
            )
            db.session.add(assessment)
        
        db.session.commit()
        print("Database reset complete. Test user and mock assessments created.")

if __name__ == "__main__":
    reset_db() 