from flask import Blueprint, render_template, request, url_for
from flask_login import login_required, current_user
from app.services.chromadb_service import ChromaDBService
from app.models.assessment import Assessment
from app import db

main = Blueprint('main', __name__)

# Initialize ChromaDB service
chromadb_service = ChromaDBService()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get the user's assessments with the Assessment model
    assessments = current_user.assessments.order_by(Assessment.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', assessments=assessments)

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('search_query')
        results = chromadb_service.search_assessments(query)
        return render_template('search_results.html', results=results)
    return render_template('search.html')

@main.route('/assessment/<int:assessment_id>')
@login_required
def assessment_detail(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    return render_template('assessment_detail.html', assessment=assessment)