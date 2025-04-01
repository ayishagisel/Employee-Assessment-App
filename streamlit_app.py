import streamlit as st
import os
from dotenv import load_dotenv
from app import create_app
from app.models import db, User, Assessment
from app.workflows.assessment_pipeline import AssessmentPipeline
from app.workflows.db_utils import setup_vector_store, add_review_to_vector_store, batch_add_reviews_to_vector_store
import asyncio
import json
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List
import logging
import sys
from flask import Flask

# Configure Streamlit at the very beginning
st.set_page_config(
    page_title="Employee Assessment System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    # Initialize Flask app
    logger.info("Initializing Flask app...")
    app = create_app()
    
    # Initialize assessment pipeline
    logger.info("Initializing assessment pipeline...")
    pipeline = AssessmentPipeline(
        db_connection_string=os.getenv("DATABASE_URL"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise

# Add custom CSS
st.markdown("""
<style>
.metric-card {
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    padding: 20px;
    background-color: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    margin-bottom: 20px;
}
.rating-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: bold;
    color: white;
    display: inline-block;
}
.rating-3 { background-color: #ffc107; }
.rating-4 { background-color: #28a745; }
.rating-5 { background-color: #17a2b8; }
.action-button {
    display: inline-block;
    padding: 4px 12px;
    margin: 0 4px;
    border-radius: 4px;
    border: 1px solid #007bff;
    color: #007bff;
    background: transparent;
    text-decoration: none;
    cursor: pointer;
}
.action-button:hover {
    background: #007bff;
    color: white;
}
.stButton > button {
    width: 100%;
}
div[data-testid="stMetricValue"] {
    font-size: 24px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def landing_page():
    """Display the landing page."""
    st.title("Welcome to Employee Assessment System")
    st.write("A comprehensive platform for managing employee performance reviews and assessments.")
    
    # Feature cards using columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Performance Reviews
        Create and manage comprehensive employee performance reviews with customizable criteria.
        """)
    
    with col2:
        st.markdown("""
        ### Goal Tracking
        Set and monitor employee goals, track progress, and provide regular feedback.
        """)
    
    with col3:
        st.markdown("""
        ### Analytics
        Generate insights and reports to make data-driven decisions about employee development.
        """)
    
    # Call to action
    st.markdown("---")
    if not st.session_state.get('authenticated', False):
        st.write("Please log in to get started.")
    else:
        if st.button("Go to Dashboard", type="primary"):
            st.session_state['page'] = 'dashboard'
            st.experimental_rerun()

def login():
    """Handle user login."""
    with app.app_context():
        st.title("Employee Assessment System")
        st.write("Please log in to continue")
        
        # Add login instructions for development
        st.info("For testing, use username: 'testuser' and password: 'password'")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                logger.info(f"Login attempt for username: {username}")
                user = User.query.filter_by(username=username).first()
                
                if user:
                    logger.info("User found in database")
                    if user.check_password(password):
                        logger.info("Password check successful")
                        st.session_state['user'] = user
                        st.session_state['authenticated'] = True
                        st.session_state['page'] = 'dashboard'
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        logger.warning("Invalid password for user")
                        st.error("Invalid username or password")
                else:
                    logger.warning(f"No user found with username: {username}")
                    st.error("Invalid username or password")

def dashboard():
    """Display the dashboard."""
    with app.app_context():
        st.title("Dashboard")
        
        # Create header with new assessment button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Create New Assessment", type="primary"):
                st.session_state['page'] = 'new_assessment'
                st.experimental_rerun()
        
        # Get assessment counts
        total_assessments = Assessment.query.filter_by(user_id=st.session_state['user'].id).count()
        pending_reviews = Assessment.query.filter_by(
            user_id=st.session_state['user'].id,
            status='pending'
        ).count()
        completed_reviews = Assessment.query.filter_by(
            user_id=st.session_state['user'].id,
            status='completed'
        ).count()
        
        # Metric Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Recent Assessments</h3>
                <h2>{total_assessments}</h2>
                <p>Total assessments created</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Pending Reviews</h3>
                <h2>{pending_reviews}</h2>
                <p>Assessments awaiting review</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Completed Reviews</h3>
                <h2>{completed_reviews}</h2>
                <p>Finalized assessments</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent Assessments Table
        st.markdown("### Recent Assessments")
        
        # Get assessments
        assessments = Assessment.query.filter_by(user_id=st.session_state['user'].id).order_by(Assessment.review_date.desc()).limit(5).all()
        
        if not assessments:
            st.info("No assessments found. Create your first assessment to get started!")
            return
        
        # Create table data
        table_data = []
        for assessment in assessments:
            metrics = json.loads(assessment.performance_metrics)
            rating = metrics["overall_rating"]
            rating_class = f"rating-{int(rating)}"
            
            # Format the rating badge with color
            rating_badge = f'<span class="rating-badge {rating_class}">{rating}/5</span>'
            
            # Format action buttons
            actions = f'''
            <div style="white-space: nowrap;">
                <a href="#" class="action-button">View</a>
                <a href="#" class="action-button">Edit</a>
            </div>
            '''
            
            table_data.append({
                "Employee Name": assessment.employee_name,
                "Position": assessment.position,
                "Department": assessment.department,
                "Review Period": assessment.review_date.strftime("Q%q %Y"),
                "Rating": rating_badge,
                "Actions": actions
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(table_data)
        
        # Display table with HTML and additional styling
        st.markdown("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .dataframe th {
            background-color: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
        }
        .dataframe td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
            vertical-align: middle;
        }
        .dataframe tr:hover {
            background-color: #f5f5f5;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(
            df.to_html(
                escape=False,
                index=False,
                classes=['table', 'table-striped', 'table-hover'],
                table_id='assessments-table'
            ),
            unsafe_allow_html=True
        )

def assessment_form():
    """Display and handle the assessment form."""
    with app.app_context():
        st.title("New Employee Assessment")
        
        with st.form("assessment_form"):
            # Employee Information
            st.subheader("Employee Information")
            col1, col2 = st.columns(2)
            with col1:
                employee_name = st.text_input("Employee Name")
                employee_id = st.text_input("Employee ID")
            with col2:
                department = st.selectbox("Department", ["Engineering", "Sales", "Marketing", "HR", "Finance"])
                position = st.text_input("Current Position")
            
            # Performance Review
            st.subheader("Performance Review")
            review_text = st.text_area("Review Text", height=200)
            
            # Performance Metrics
            st.subheader("Performance Metrics")
            col1, col2 = st.columns(2)
            
            with col1:
                overall_rating = st.slider("Overall Rating", 1.0, 5.0, 3.0, 0.1)
                attendance = st.slider("Attendance", 0.0, 1.0, 0.9, 0.1)
                productivity = st.slider("Productivity", 0.0, 1.0, 0.8, 0.1)
                quality = st.slider("Quality of Work", 0.0, 1.0, 0.85, 0.1)
                teamwork = st.slider("Teamwork", 0.0, 1.0, 0.9, 0.1)
                initiative = st.slider("Initiative", 0.0, 1.0, 0.85, 0.1)
                communication = st.slider("Communication", 0.0, 1.0, 0.9, 0.1)
                leadership = st.slider("Leadership", 0.0, 1.0, 0.8, 0.1)
            
            with col2:
                technical_skills = st.slider("Technical Skills", 0.0, 1.0, 0.85, 0.1)
                problem_solving = st.slider("Problem Solving", 0.0, 1.0, 0.9, 0.1)
                adaptability = st.slider("Adaptability", 0.0, 1.0, 0.85, 0.1)
                reliability = st.slider("Reliability", 0.0, 1.0, 0.95, 0.1)
                creativity = st.slider("Creativity", 0.0, 1.0, 0.8, 0.1)
                time_management = st.slider("Time Management", 0.0, 1.0, 0.85, 0.1)
                customer_focus = st.slider("Customer Focus", 0.0, 1.0, 0.9, 0.1)
            
            # Additional Comments
            st.subheader("Additional Comments")
            additional_comments = st.text_area("Additional Comments", height=100)
            
            # Submit Button
            submitted = st.form_submit_button("Submit Assessment")
            
            if submitted:
                if not all([employee_name, employee_id, review_text]):
                    st.error("Please fill in all required fields")
                    return
                
                # Prepare assessment data
                assessment_data = {
                    "employee_name": employee_name,
                    "employee_id": employee_id,
                    "department": department,
                    "position": position,
                    "review_text": review_text,
                    "performance_metrics": {
                        "overall_rating": overall_rating,
                        "attendance": attendance,
                        "productivity": productivity,
                        "quality": quality,
                        "teamwork": teamwork,
                        "initiative": initiative,
                        "communication": communication,
                        "leadership": leadership,
                        "technical_skills": technical_skills,
                        "problem_solving": problem_solving,
                        "adaptability": adaptability,
                        "reliability": reliability,
                        "creativity": creativity,
                        "time_management": time_management,
                        "customer_focus": customer_focus
                    },
                    "additional_comments": additional_comments,
                    "review_date": datetime.utcnow().isoformat()
                }
                
                try:
                    # Process assessment
                    with st.spinner("Processing assessment..."):
                        result = asyncio.run(pipeline.process_single_review(
                            review_text=review_text,
                            employee_id=employee_id,
                            performance_metrics=assessment_data["performance_metrics"]
                        ))
                    
                    if result["status"] == "success":
                        # Save to database
                        assessment = Assessment(
                            employee_id=employee_id,
                            employee_name=employee_name,
                            department=department,
                            position=position,
                            review_text=review_text,
                            performance_metrics=json.dumps(assessment_data["performance_metrics"]),
                            sentiment_analysis=json.dumps(result["sentiment_analysis"]),
                            promotion_recommendation=json.dumps(result["promotion_recommendation"]),
                            additional_comments=additional_comments,
                            review_date=datetime.utcnow(),
                            user_id=st.session_state['user'].id
                        )
                        
                        db.session.add(assessment)
                        db.session.commit()
                        
                        # Add to vector store
                        asyncio.run(add_review_to_vector_store(
                            pipeline.vector_store,
                            review_text,
                            {
                                "employee_id": employee_id,
                                "department": department,
                                "position": position
                            }
                        ))
                        
                        st.success("Assessment submitted successfully!")
                        st.balloons()
                        
                        # Display results
                        st.subheader("Assessment Results")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Sentiment Analysis
                            st.write("### Sentiment Analysis")
                            sentiment = result["sentiment_analysis"]
                            st.write(f"Overall Sentiment: {sentiment['sentiment_label']}")
                            st.write(f"Confidence: {sentiment['confidence']:.2f}")
                            st.write("Strengths:")
                            for strength in sentiment["strengths"]:
                                st.write(f"- {strength}")
                        
                        with col2:
                            # Promotion Recommendation
                            st.write("### Promotion Recommendation")
                            promotion = result["promotion_recommendation"]
                            st.write(f"Recommendation: {'Recommended' if promotion['promotion_recommended'] else 'Not Recommended'}")
                            if promotion["promotion_recommended"]:
                                st.write(f"Recommended Role: {promotion['recommended_role']}")
                                st.write(f"Timeline: {promotion['timeline']}")
                            st.write(f"Confidence: {promotion['confidence_score']:.2f}")
                            st.write("Rationale:", promotion["rationale"])
                            
                            if promotion["development_areas"]:
                                st.write("Development Areas:")
                                for area in promotion["development_areas"]:
                                    st.write(f"- {area}")
                    else:
                        st.error(f"Error processing assessment: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    logger.error(f"Error in assessment submission: {str(e)}")
                    st.error(f"An error occurred while processing the assessment: {str(e)}")

def view_assessments():
    """View and analyze submitted assessments."""
    with app.app_context():
        # Get all assessments
        assessments = Assessment.query.filter_by(user_id=st.session_state['user'].id).all()
        
        if not assessments:
            st.info("No assessments found. Create your first assessment to get started!")
            return
        
        # Convert to DataFrame
        data = []
        for assessment in assessments:
            try:
                metrics = json.loads(assessment.performance_metrics)
                sentiment = json.loads(assessment.sentiment_analysis)
                promotion = json.loads(assessment.promotion_recommendation)
                
                # Format rating with color
                rating = float(metrics.get("overall_rating", 0))
                rating_class = f"rating-{int(rating)}"
                rating_badge = f'<span class="rating-badge {rating_class}">{rating:.1f}/5</span>'
                
                # Format actions
                actions = f'''
                <div style="white-space: nowrap;">
                    <a href="#" class="action-button">View</a>
                    <a href="#" class="action-button">Edit</a>
                </div>
                '''
                
                data.append({
                    "Employee Name": assessment.employee_name,
                    "Position": assessment.position,
                    "Department": assessment.department,
                    "Review Date": assessment.review_date.strftime("%Y-%m-%d"),
                    "Rating": rating,  # Store raw number for calculations
                    "Rating_Display": rating_badge,  # Store HTML for display
                    "Sentiment": sentiment.get("sentiment_label", "N/A"),
                    "Promotion": "Yes" if promotion.get("promotion_recommended", False) else "No",
                    "Actions": actions
                })
            except Exception as e:
                logger.error(f"Error processing assessment {assessment.id}: {str(e)}")
                continue
        
        if not data:
            st.error("Error loading assessment data. Please try again later.")
            return
            
        df = pd.DataFrame(data)
        
        # Display filters
        col1, col2 = st.columns(2)
        
        with col1:
            department_filter = st.multiselect(
                "Filter by Department",
                options=df["Department"].unique(),
                default=df["Department"].unique()
            )
        
        with col2:
            position_filter = st.multiselect(
                "Filter by Position",
                options=df["Position"].unique(),
                default=df["Position"].unique()
            )
        
        # Apply filters
        filtered_df = df[
            (df["Department"].isin(department_filter)) &
            (df["Position"].isin(position_filter))
        ]
        
        # Calculate metrics safely
        try:
            avg_rating = filtered_df["Rating"].mean()
            promotion_rate = (filtered_df["Promotion"] == "Yes").mean() * 100
            sentiment_map = {"Positive": 100, "Neutral": 50, "Negative": 0, "N/A": 0}
            avg_sentiment = filtered_df["Sentiment"].map(sentiment_map).mean()
            
            # Display metrics with styling
            metrics_html = f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div class="metric-card" style="flex: 1; margin: 0 10px;">
                    <h4>Average Rating</h4>
                    <h2>{avg_rating:.1f}/5.0</h2>
                </div>
                <div class="metric-card" style="flex: 1; margin: 0 10px;">
                    <h4>Promotion Rate</h4>
                    <h2>{promotion_rate:.1f}%</h2>
                </div>
                <div class="metric-card" style="flex: 1; margin: 0 10px;">
                    <h4>Average Sentiment</h4>
                    <h2>{avg_sentiment:.1f}%</h2>
                </div>
            </div>
            """
            st.markdown(metrics_html, unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            st.warning("Unable to calculate metrics. Some data may be missing or invalid.")
        
        # Prepare display DataFrame
        display_df = filtered_df.copy()
        display_df["Rating"] = display_df["Rating_Display"]
        display_df = display_df.drop(columns=["Rating_Display"])
        
        # Display table with HTML
        st.markdown("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .dataframe th {
            background-color: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
        }
        .dataframe td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
            vertical-align: middle;
        }
        .dataframe tr:hover {
            background-color: #f5f5f5;
        }
        </style>
        """, unsafe_allow_html=True)
        
        try:
            st.markdown(
                display_df.to_html(
                    escape=False,
                    index=False,
                    classes=['table', 'table-striped', 'table-hover'],
                    table_id='assessments-table'
                ),
                unsafe_allow_html=True
            )
        except Exception as e:
            logger.error(f"Error displaying table: {str(e)}")
            st.error("Error displaying assessment table. Please try again later.")

def main():
    """Main application entry point."""
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'landing'
    
    # Navigation
    if not st.session_state['authenticated']:
        if st.session_state['page'] == 'landing':
            landing_page()
            if st.button("Login"):
                st.session_state['page'] = 'login'
                st.experimental_rerun()
        else:
            login()
    else:
        # Sidebar navigation
        st.sidebar.title("Navigation")
        pages = {
            "Dashboard": "dashboard",
            "New Assessment": "new_assessment",
            "View Assessments": "view_assessments"
        }
        
        selected_page = st.sidebar.radio("Go to", list(pages.keys()))
        st.session_state['page'] = pages[selected_page]
        
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.session_state['page'] = 'landing'
            st.experimental_rerun()
        
        # Display selected page
        if st.session_state['page'] == 'dashboard':
            dashboard()
        elif st.session_state['page'] == 'new_assessment':
            assessment_form()
        elif st.session_state['page'] == 'view_assessments':
            st.title("Assessment History")
            view_assessments()

if __name__ == "__main__":
    try:
        logger.info("Starting Streamlit app...")
        main()
    except Exception as e:
        logger.error(f"Error running Streamlit app: {str(e)}")
        st.error(f"An error occurred while starting the application: {str(e)}")
        raise 