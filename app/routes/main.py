from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Assessment
from app.forms import AssessmentForm
from app.workflows.assessment_pipeline import AssessmentPipeline
from app.workflows.db_utils import add_review_to_vector_store, get_review_statistics
from datetime import datetime
import os
import asyncio
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

main = Blueprint('main', __name__)

def get_pipeline():
    return AssessmentPipeline(
        db_connection_string=os.getenv('DATABASE_URL'),
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get review statistics
    stats = get_review_statistics(os.getenv('DATABASE_URL'))
    return render_template('dashboard.html', stats=stats)

@main.route('/assessment/new', methods=['GET', 'POST'])
@login_required
def new_assessment():
    form = AssessmentForm()
    if form.validate_on_submit():
        # Create the assessment
        assessment = Assessment(
            employee_name=form.employee_name.data,
            position=form.position.data,
            department=form.department.data,
            review_period=form.review_period.data,
            performance_rating=form.performance_rating.data,
            strengths=form.strengths.data,
            areas_for_improvement=form.areas_for_improvement.data,
            goals=form.goals.data,
            comments=form.comments.data,
            user_id=current_user.id
        )
        db.session.add(assessment)
        db.session.commit()

        # Get performance metrics
        pipeline = get_pipeline()
        metrics = pipeline.get_performance_metrics(form.employee_name.data)

        # Process the assessment through the pipeline
        review_text = f"""
        Employee: {form.employee_name.data}
        Position: {form.position.data}
        Department: {form.department.data}
        Review Period: {form.review_period.data}
        
        Strengths:
        {form.strengths.data}
        
        Areas for Improvement:
        {form.areas_for_improvement.data}
        
        Goals:
        {form.goals.data}
        
        Additional Comments:
        {form.comments.data}
        """

        # Run the pipeline asynchronously
        async def process_assessment():
            result = await pipeline.process_single_review(
                review_text=review_text,
                employee_id=str(assessment.id),
                performance_metrics=metrics
            )
            
            # Store the review in vector database
            await add_review_to_vector_store(
                pipeline.vector_store,
                review_text,
                {
                    "employee_id": str(assessment.id),
                    "department": form.department.data,
                    "position": form.position.data
                }
            )
            
            return result

        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_assessment())
        loop.close()

        if result["status"] == "success":
            flash('Assessment created and analyzed successfully!', 'success')
        else:
            flash('Assessment created but analysis failed. Please try analyzing again later.', 'warning')

        return redirect(url_for('main.view_assessment', id=assessment.id))
    return render_template('assessment_form.html', form=form)

@main.route('/assessment/<int:id>')
@login_required
def view_assessment(id):
    try:
        assessment = Assessment.query.get_or_404(id)
        if assessment.user_id != current_user.id:
            flash('You do not have permission to view this assessment.', 'danger')
            return redirect(url_for('main.dashboard'))

        # Get the analysis results
        pipeline = get_pipeline()
        try:
            metrics = pipeline.get_performance_metrics(assessment.employee_name)
            logger.info(f"Retrieved metrics for {assessment.employee_name}: {metrics}")
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            flash('Error retrieving performance metrics.', 'warning')
            metrics = {}
        
        # Run the pipeline asynchronously to get fresh analysis
        async def get_analysis():
            try:
                review_text = f"""
                Employee: {assessment.employee_name}
                Position: {assessment.position}
                Department: {assessment.department}
                Review Period: {assessment.review_period}
                
                Strengths:
                {assessment.strengths}
                
                Areas for Improvement:
                {assessment.areas_for_improvement}
                
                Goals:
                {assessment.goals}
                
                Comments:
                {assessment.comments}
                """
                
                result = await pipeline.process_single_review(
                    review_text=review_text,
                    employee_id=str(assessment.id),
                    performance_metrics=metrics
                )
                
                if not result or "status" not in result:
                    logger.error("Invalid analysis result format")
                    return None
                
                return result
            except Exception as e:
                logger.error(f"Error in analysis: {str(e)}")
                return None

        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(get_analysis())
        loop.close()

        if analysis is None:
            flash('Unable to analyze the assessment. Please try again later.', 'warning')
            return render_template('view_assessment.html', assessment=assessment, analysis=None)

        return render_template('view_assessment.html', assessment=assessment, analysis=analysis)
    except Exception as e:
        logger.error(f"Error viewing assessment: {str(e)}")
        flash('An error occurred while viewing the assessment. Please try again later.', 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/assessment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != current_user.id:
        flash('You do not have permission to edit this assessment.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = AssessmentForm()
    if form.validate_on_submit():
        assessment.employee_name = form.employee_name.data
        assessment.position = form.position.data
        assessment.department = form.department.data
        assessment.review_period = form.review_period.data
        assessment.performance_rating = form.performance_rating.data
        assessment.strengths = form.strengths.data
        assessment.areas_for_improvement = form.areas_for_improvement.data
        assessment.goals = form.goals.data
        assessment.comments = form.comments.data
        assessment.updated_at = datetime.utcnow()
        db.session.commit()

        # Update the vector store with the new version
        pipeline = get_pipeline()
        review_text = f"""
        Employee: {form.employee_name.data}
        Position: {form.position.data}
        Department: {form.department.data}
        Review Period: {form.review_period.data}
        
        Strengths:
        {form.strengths.data}
        
        Areas for Improvement:
        {form.areas_for_improvement.data}
        
        Goals:
        {form.goals.data}
        
        Additional Comments:
        {form.comments.data}
        """

        async def update_vector_store():
            await add_review_to_vector_store(
                pipeline.vector_store,
                review_text,
                {
                    "employee_id": str(assessment.id),
                    "department": form.department.data,
                    "position": form.position.data,
                    "is_update": True
                }
            )

        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(update_vector_store())
        loop.close()

        flash('Assessment updated successfully!', 'success')
        return redirect(url_for('main.view_assessment', id=assessment.id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.employee_name.data = assessment.employee_name
        form.position.data = assessment.position
        form.department.data = assessment.department
        form.review_period.data = assessment.review_period
        form.performance_rating.data = assessment.performance_rating
        form.strengths.data = assessment.strengths
        form.areas_for_improvement.data = assessment.areas_for_improvement
        form.goals.data = assessment.goals
        form.comments.data = assessment.comments
    
    return render_template('assessment_form.html', form=form, assessment=assessment)

@main.route('/assessment/<int:id>/analyze')
@login_required
def analyze_assessment(id):
    """Endpoint to manually trigger analysis of an assessment."""
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != current_user.id:
        return jsonify({"error": "Permission denied"}), 403

    pipeline = get_pipeline()
    metrics = pipeline.get_performance_metrics(assessment.employee_name)
    
    async def run_analysis():
        review_text = f"""
        Employee: {assessment.employee_name}
        Position: {assessment.position}
        Department: {assessment.department}
        Review Period: {assessment.review_period}
        
        Strengths:
        {assessment.strengths}
        
        Areas for Improvement:
        {assessment.areas_for_improvement}
        
        Goals:
        {assessment.goals}
        
        Additional Comments:
        {assessment.comments}
        """
        
        return await pipeline.process_single_review(
            review_text=review_text,
            employee_id=str(assessment.id),
            performance_metrics=metrics
        )

    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run_analysis())
    loop.close()

    if result["status"] == "success":
        return jsonify(result)
    else:
        return jsonify({"error": result["error"]}), 500 