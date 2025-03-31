from app import create_app, db
from app.models import User
from config import Config

def create_admin_user():
    app = create_app(Config)
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully')
        else:
            print('Admin user already exists')

if __name__ == '__main__':
    create_admin_user() 