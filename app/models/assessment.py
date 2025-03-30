from app import db
from datetime import datetime

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    review_period = db.Column(db.String(50), nullable=False)
    performance_rating = db.Column(db.Integer, nullable=False)
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    goals = db.Column(db.Text)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to link assessment to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Assessment {self.employee_name} - {self.review_period}>'

    def to_dict(self):
        return {
            'id': self.id,
            'employee_name': self.employee_name,
            'position': self.position,
            'department': self.department,
            'review_period': self.review_period,
            'performance_rating': self.performance_rating,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement,
            'goals': self.goals,
            'comments': self.comments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        } 