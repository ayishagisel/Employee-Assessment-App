from app import create_app, db
from app.models import User, Assessment
from config import Config
from datetime import datetime, timedelta
import random

def create_mock_assessments():
    app = create_app(Config)
    with app.app_context():
        # Get the admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Error: Admin user not found")
            return

        # Sample data
        employees = [
            {
                'name': 'John Smith',
                'position': 'Senior Software Engineer',
                'department': 'Engineering',
                'strengths': 'Strong problem-solving skills, excellent team player, quick learner, architecture design',
                'improvements': 'Could improve documentation practices, needs to speak up more in meetings',
                'goals': 'Complete AWS certification, lead a major project, mentor junior developers'
            },
            {
                'name': 'Sarah Johnson',
                'position': 'Product Manager',
                'department': 'Product',
                'strengths': 'Outstanding leadership, clear communication, strategic thinking',
                'improvements': 'Could delegate more tasks, work on time management',
                'goals': 'Launch new product line, improve team velocity by 20%'
            },
            {
                'name': 'Michael Chen',
                'position': 'Senior UX Designer',
                'department': 'Design',
                'strengths': 'Creative problem solving, user empathy, attention to detail',
                'improvements': 'Could improve presentation skills, needs more technical knowledge',
                'goals': 'Create design system, improve user testing processes'
            },
            {
                'name': 'Emily Rodriguez',
                'position': 'Software Engineer',
                'department': 'Engineering',
                'strengths': 'Excellent coding skills, great debugging abilities, strong CS fundamentals',
                'improvements': 'Could improve code review thoroughness, needs to work on project estimation',
                'goals': 'Master React and TypeScript, contribute to open source projects'
            },
            {
                'name': 'David Kim',
                'position': 'Data Scientist',
                'department': 'Data',
                'strengths': 'Strong analytical skills, machine learning expertise, good communication',
                'improvements': 'Could improve data visualization, needs to document analysis better',
                'goals': 'Implement ML pipeline, publish research paper, improve A/B testing framework'
            },
            {
                'name': 'Lisa Wang',
                'position': 'UI Designer',
                'department': 'Design',
                'strengths': 'Excellent visual design skills, strong prototyping abilities',
                'improvements': 'Could improve collaboration with developers, needs more user research experience',
                'goals': 'Create component library, improve design system documentation'
            },
            {
                'name': 'James Wilson',
                'position': 'DevOps Engineer',
                'department': 'Engineering',
                'strengths': 'Infrastructure expertise, automation skills, security focus',
                'improvements': 'Could improve documentation of processes, needs to transfer knowledge better',
                'goals': 'Implement zero-trust architecture, improve CI/CD pipeline'
            },
            {
                'name': 'Maria Garcia',
                'position': 'Product Analyst',
                'department': 'Product',
                'strengths': 'Data analysis skills, user insights, strategic thinking',
                'improvements': 'Could improve SQL optimization, needs to create more dashboards',
                'goals': 'Build automated reporting system, improve data accessibility'
            },
            {
                'name': 'Alex Thompson',
                'position': 'Frontend Engineer',
                'department': 'Engineering',
                'strengths': 'UI/UX implementation, performance optimization, accessibility focus',
                'improvements': 'Could improve unit testing coverage, needs to work on state management',
                'goals': 'Implement micro-frontend architecture, improve page load times'
            },
            {
                'name': 'Rachel Brown',
                'position': 'Technical Project Manager',
                'department': 'Engineering',
                'strengths': 'Technical background, great coordination, risk management',
                'improvements': 'Could improve agile practices, needs more stakeholder management',
                'goals': 'Implement scaled agile framework, improve sprint velocity'
            }
        ]

        performance_comments = [
            "Consistently exceeds expectations and delivers high-quality work.",
            "Shows great initiative and leadership potential.",
            "Valuable team member with strong technical skills.",
            "Has made significant progress in key areas.",
            "Demonstrates excellent problem-solving abilities.",
            "Great team player who helps others succeed.",
            "Innovative thinker with practical implementation skills.",
            "Reliable performer who consistently meets deadlines.",
            "Shows strong potential for growth and leadership.",
            "Excellent communicator and collaborator."
        ]

        # Create assessments for each employee
        for employee in employees:
            # Create four assessments per employee with different dates
            for i in range(4):
                months_ago = i * 3  # 0, 3, 6, and 9 months ago
                review_date = datetime.utcnow() - timedelta(days=30 * months_ago)
                period = f"{review_date.strftime('%B %Y')} Review"

                # Vary performance ratings more realistically
                base_rating = 3
                if i == 0:  # Most recent review
                    rating_change = random.choice([0, 1, 1])  # Bias toward improvement
                else:
                    rating_change = random.choice([-1, 0, 1])
                performance_rating = min(max(base_rating + rating_change, 1), 5)

                # Select two random comments and combine them
                selected_comments = random.sample(performance_comments, 2)
                combined_comment = f"{selected_comments[0]} {selected_comments[1]} {employee['name']} continues to grow in their role."

                assessment = Assessment(
                    employee_name=employee['name'],
                    position=employee['position'],
                    department=employee['department'],
                    review_period=period,
                    performance_rating=performance_rating,
                    strengths=employee['strengths'],
                    areas_for_improvement=employee['improvements'],
                    goals=employee['goals'],
                    comments=combined_comment,
                    user_id=admin.id,
                    created_at=review_date,
                    updated_at=review_date
                )
                db.session.add(assessment)

        db.session.commit()
        print("Mock assessments created successfully!")

if __name__ == '__main__':
    create_mock_assessments() 