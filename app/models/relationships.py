from app import db
from app.models.user import User
from app.models.assessment import Assessment

def setup_relationships():
    # Set up relationships
    User.assessments = db.relationship('Assessment', backref='author', lazy='dynamic') 