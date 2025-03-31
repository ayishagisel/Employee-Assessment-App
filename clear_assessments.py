from app import create_app, db
from app.models import Assessment
from config import Config

def clear_assessments():
    app = create_app(Config)
    with app.app_context():
        Assessment.query.delete()
        db.session.commit()
        print("All assessments cleared successfully!")

if __name__ == '__main__':
    clear_assessments() 