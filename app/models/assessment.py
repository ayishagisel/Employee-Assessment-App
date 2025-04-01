from app import db
from datetime import datetime

class Assessment(db.Model):
    __tablename__ = 'assessment'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    performance_metrics = db.Column(db.JSON, nullable=False)
    sentiment_analysis = db.Column(db.JSON, nullable=False)
    promotion_recommendation = db.Column(db.JSON, nullable=False)
    additional_comments = db.Column(db.Text)
    review_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending' or 'completed'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Assessment {self.employee_name} - {self.review_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'department': self.department,
            'position': self.position,
            'review_text': self.review_text,
            'performance_metrics': self.performance_metrics,
            'sentiment_analysis': self.sentiment_analysis,
            'promotion_recommendation': self.promotion_recommendation,
            'additional_comments': self.additional_comments,
            'review_date': self.review_date.isoformat(),
            'status': self.status,
            'user_id': self.user_id
        } 