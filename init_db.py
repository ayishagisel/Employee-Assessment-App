from app import create_app, db
from app.models.user import User
from app.models.assessment import Assessment
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create test user if it doesn't exist
        if not User.query.filter_by(username='testuser').first():
            test_user = User(
                username='testuser',
                email='test@example.com'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            
            # Create some test assessments
            assessments = [
                Assessment(
                    employee_name='John Doe',
                    position='Software Engineer',
                    department='Engineering',
                    review_period='Q1 2024',
                    performance_rating=4,
                    strengths='Strong problem-solving skills, excellent communication',
                    areas_for_improvement='Time management, documentation',
                    goals='Complete advanced certification, mentor junior developers',
                    comments='Overall excellent performance',
                    user_id=test_user.id
                ),
                Assessment(
                    employee_name='Jane Smith',
                    position='Product Manager',
                    department='Product',
                    review_period='Q1 2024',
                    performance_rating=5,
                    strengths='Strategic thinking, leadership',
                    areas_for_improvement='Technical knowledge',
                    goals='Launch new feature set, improve team collaboration',
                    comments='Outstanding leadership and vision',
                    user_id=test_user.id
                ),
                Assessment(
                    employee_name='Mike Johnson',
                    position='UX Designer',
                    department='Design',
                    review_period='Q1 2024',
                    performance_rating=3,
                    strengths='Creativity, user empathy',
                    areas_for_improvement='Meeting deadlines, attention to detail',
                    goals='Complete design system, improve prototyping skills',
                    comments='Needs improvement in time management',
                    user_id=test_user.id
                )
            ]
            
            for assessment in assessments:
                db.session.add(assessment)
            
            db.session.commit()
            print('Test data created successfully!')
        else:
            print('Test user already exists.')

if __name__ == '__main__':
    init_db() 