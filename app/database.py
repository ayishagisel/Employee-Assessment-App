from app import create_app, db
from app.models.user import User
from app.models.assessment import Assessment
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        
        print("Creating test user...")
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123', method='pbkdf2:sha256'),
            is_active=True,
            is_admin=True
        )
        db.session.add(test_user)
        
        print("Creating test assessments...")
        # Start of generated assessment data
        assessments = [
            Assessment(
                employee_name='John Doe',
                position='Senior Software Engineer',
                department='Engineering',
                review_period='Q1 2024',
                performance_rating=4.5,
                strengths='Strong technical skills, excellent problem-solving abilities, great team player',
                areas_for_improvement='Could improve documentation practices',
                goals='Lead a major project in Q2, mentor junior developers',
                comments='John has consistently delivered high-quality work and shown great leadership potential',
                author=test_user
            ),
            Assessment(
                employee_name='Jane Smith',
                position='Product Manager',
                department='Product',
                review_period='Q1 2024',
                performance_rating=4.8,
                strengths='Exceptional stakeholder management, strong product vision, excellent communication',
                areas_for_improvement='Could focus more on technical details',
                goals='Launch new product feature in Q2, improve cross-team collaboration',
                comments='Jane has been instrumental in driving product success and building strong relationships with stakeholders',
                author=test_user
            ),
            Assessment(
                employee_name='Mike Johnson',
                position='UI/UX Designer',
                department='Design',
                review_period='Q1 2024',
                performance_rating=4.2,
                strengths='Creative design solutions, attention to detail, user-centered approach',
                areas_for_improvement='Could improve time management',
                goals='Lead design system improvements, mentor junior designers',
                comments='Mike consistently delivers visually stunning and user-friendly designs that exceed expectations',
                author=test_user
            ),
            Assessment(
                employee_name='Sarah Williams',
                position='Data Scientist',
                department='Analytics',
                review_period='Q1 2024',
                performance_rating=4.9,
                strengths='Advanced analytical skills, innovative problem-solving, excellent research capabilities',
                areas_for_improvement='Could improve presentation skills',
                goals='Publish research paper, optimize data processing pipeline',
                comments='Sarah\'s work has significantly improved our data-driven decision-making processes',
                author=test_user
            ),
            Assessment(
                employee_name='Robert Brown',
                position='DevOps Engineer',
                department='Engineering',
                review_period='Q1 2024',
                performance_rating=4.7,
                strengths='Infrastructure automation expertise, strong security knowledge, excellent troubleshooting',
                areas_for_improvement='Could improve documentation',
                goals='Implement CI/CD improvements, enhance security protocols',
                comments='Robert has been crucial in maintaining our infrastructure reliability and security',
                author=test_user
            ),
            Assessment(
                employee_name='Dakota Smith',
                position='UI/UX Designer',
                department='Design',
                review_period='Q2 2024',
                performance_rating=4.3,
                strengths='Creative thinking, excellent presentation skills, campaign management',
                areas_for_improvement='Needs to increase speed of delivery',
                goals='Master financial forecasting model',
                comments='Highly effective performer. Dakota\'s work on master financial forecasting model has been impactful. Continue fostering campaign management.',
                author=test_user
            ),
            Assessment(
                employee_name='Micah Clark',
                position='Sales Operations Analyst',
                department='Sales',
                review_period='Q4 2024',
                performance_rating=4.3,
                strengths='Detail-oriented, infrastructure automation, campaign management',
                areas_for_improvement='Needs more experience with tool y',
                goals='Master financial forecasting model, increase lead generation by w%',
                comments='Performance meets expectations. Micah should focus on needs more experience with tool y while continuing to leverage detail-oriented.',
                author=test_user
            ),
            Assessment(
                employee_name='Finley Moore',
                position='Senior Software Engineer',
                department='Engineering',
                review_period='Q2 2024',
                performance_rating=4.0,
                strengths='Talent sourcing',
                areas_for_improvement='Needs to build confidence in area z, could engage more in team discussions',
                goals='Master financial forecasting model',
                comments='Finley is a valuable member of the team, demonstrating strong talent sourcing.',
                author=test_user
            ),
            Assessment(
                employee_name='Sophia Johnson',
                position='Supply Chain Analyst',
                department='Operations',
                review_period='Q4 2024',
                performance_rating=4.8,
                strengths='Collaborates effectively across teams, great team player',
                areas_for_improvement='Needs deeper technical understanding in x area, needs to develop cross-functional collaboration',
                goals='Lead a major project',
                comments='Sophia has shown significant growth. Areas like great team player are strong, while needs to develop cross-functional collaboration is an area for development.',
                author=test_user
            ),
            Assessment(
                employee_name='Emerson Baker',
                position='Associate Product Manager',
                department='Product',
                review_period='Q4 2024',
                performance_rating=4.9,
                strengths='Strong analytical abilities',
                areas_for_improvement='None noted this period.',
                goals='Achieve x% sales target, lead a major project',
                comments='Reliable and consistent performer. Emerson\'s strong analytical abilities makes them a dependable team member. Agreed focus on lead a major project for next period.',
                author=test_user
            ),
            Assessment(
                employee_name='Remi Perez',
                position='Sales Development Representative',
                department='Sales',
                review_period='Q3 2023',
                performance_rating=3.9,
                strengths='Excellent presentation skills, financial modeling',
                areas_for_improvement='Needs to build confidence in area z',
                goals='Improve team velocity',
                comments='Remi has shown significant growth. Areas like excellent presentation skills are strong, while needs to build confidence in area z is an area for development.',
                author=test_user
            ),
            Assessment(
                employee_name='Amelia Walker',
                position='Operations Manager',
                department='Operations',
                review_period='Q4 2023',
                performance_rating=4.4,
                strengths='Proactive problem-solver, deep domain knowledge',
                areas_for_improvement='Could enhance reporting clarity',
                goals='Improve customer satisfaction scores',
                comments='Amelia is a valuable member of the team, demonstrating strong deep domain knowledge.',
                author=test_user
            ),
            Assessment(
                employee_name='Lucas Evans',
                position='Talent Acquisition Specialist',
                department='HR',
                review_period='Q1 2024',
                performance_rating=3.1,
                strengths='Collaborates effectively across teams, strong leadership potential, strong analytical abilities',
                areas_for_improvement='Needs more experience with tool y',
                goals='Improve design system adoption',
                comments='Excellent progress shown by Lucas, particularly in achieving improve design system adoption.',
                author=test_user
            ),
            Assessment(
                employee_name='Noah Williams',
                position='Digital Marketing Manager',
                department='Marketing',
                review_period='Q4 2024',
                performance_rating=4.3,
                strengths='Code quality focus, proactive problem-solver',
                areas_for_improvement='Needs to build confidence in area z',
                goals='Increase lead generation by w%, develop new marketing campaign strategy',
                comments='Noah is a valuable member of the team, demonstrating strong proactive problem-solver.',
                author=test_user
            ),
            Assessment(
                employee_name='Peyton Taylor',
                position='SEO Manager',
                department='Marketing',
                review_period='Q3 2024',
                performance_rating=3.8,
                strengths='Efficient time management',
                areas_for_improvement='Needs to refine requirements gathering, needs more experience with tool y',
                goals='Lead a major project',
                comments='A solid performance from Peyton this period. Key contributions include lead a major project.',
                author=test_user
            ),
            Assessment(
                employee_name='Benjamin Clark',
                position='DevOps Engineer',
                department='Engineering',
                review_period='Q1 2023',
                performance_rating=4.2,
                strengths='Collaborates effectively across teams, efficient time management',
                areas_for_improvement='Needs to improve prioritization skills, needs to delegate more effectively',
                goals='Lead a major project, mentor junior developers/colleagues',
                comments='Benjamin demonstrates potential. Key strengths include collaborates effectively across teams. Next steps involve focusing on lead a major project and addressing needs to improve prioritization skills.',
                author=test_user
            ),
            Assessment(
                employee_name='Isabella King',
                position='Product Manager',
                department='Product',
                review_period='Q2 2023',
                performance_rating=4.3,
                strengths='Strong analytical abilities',
                areas_for_improvement='Needs to improve prioritization skills, could enhance reporting clarity',
                goals='Mentor junior developers/colleagues',
                comments='A solid performance from Isabella this period. Key contributions include mentor junior developers/colleagues.',
                author=test_user
            ),
            Assessment(
                employee_name='Micah Brown',
                position='Business Intelligence Analyst',
                department='Analytics',
                review_period='Q3 2023',
                performance_rating=3.8,
                strengths='Code quality focus, detail-oriented',
                areas_for_improvement='Needs to manage stakeholder expectations better, needs to enhance presentation skills',
                goals='Lead a major project',
                comments='Micah has shown significant growth. Areas like code quality focus are strong, while needs to manage stakeholder expectations better is an area for development.',
                author=test_user
            ),
            Assessment(
                employee_name='Sawyer Turner',
                position='Systems Architect',
                department='Engineering',
                review_period='Q3 2023',
                performance_rating=4.5,
                strengths='Excellent presentation skills',
                areas_for_improvement='Could improve documentation practices',
                goals='Refine onboarding process',
                comments='Sawyer has shown significant growth. Areas like excellent presentation skills are strong, while could improve documentation practices is an area for development.',
                author=test_user
            ),
            Assessment(
                employee_name='Jordan King',
                position='Sales Development Representative',
                department='Sales',
                review_period='Q2 2023',
                performance_rating=3.9,
                strengths='Stakeholder management',
                areas_for_improvement='Could engage more in team discussions, could be more proactive in communication',
                goals='Complete certification z',
                comments='Reliable and consistent performer. Jordan\'s stakeholder management makes them a dependable team member. Agreed focus on complete certification z for next period.',
                author=test_user
            ),
            Assessment(
                employee_name='Dakota Turner',
                position='HR Generalist',
                department='HR',
                review_period='Q2 2024',
                performance_rating=4.1,
                strengths='Excellent presentation skills',
                areas_for_improvement='Needs to develop cross-functional collaboration, needs to delegate more effectively',
                goals='Improve design system adoption, streamline reporting process',
                comments='A solid performance from Dakota this period. Key contributions include improve design system adoption.',
                author=test_user
            ),
            Assessment(
                employee_name='Chris White',
                position='Account Executive',
                department='Sales',
                review_period='Q3 2024',
                performance_rating=4.0,
                strengths='Manages complexity well, delivers high-quality results consistently',
                areas_for_improvement='Needs to delegate more effectively, needs to build confidence in area z',
                goals='Master financial forecasting model',
                comments='Highly effective performer. Chris\'s work on master financial forecasting model has been impactful. Continue fostering manages complexity well.',
                author=test_user
            ),
            Assessment(
                employee_name='Isabella Robinson',
                position='Content Strategist',
                department='Marketing',
                review_period='Q4 2024',
                performance_rating=4.5,
                strengths='Mentors junior team members, proactive problem-solver',
                areas_for_improvement='Could improve attention to detail on routine tasks, could work on meeting deadlines more consistently',
                goals='Achieve x% sales target',
                comments='Isabella has shown significant growth. Areas like proactive problem-solver are strong, while could improve attention to detail on routine tasks is an area for development.',
                author=test_user
            ),
            Assessment(
                employee_name='Cameron Phillips',
                position='Operations Manager',
                department='Operations',
                review_period='Q2 2024',
                performance_rating=4.6,
                strengths='Strategic thinking, infrastructure automation',
                areas_for_improvement='Focus remains on leveraging strengths.',
                goals='Lead a major project',
                comments='Highly effective performer. Cameron\'s work on lead a major project has been impactful. Continue fostering infrastructure automation.',
                author=test_user
            ),
            Assessment(
                employee_name='Chris Young',
                position='Design Lead',
                department='Design',
                review_period='Q4 2024',
                performance_rating=4.8,
                strengths='Positive attitude, excellent communication skills',
                areas_for_improvement='None noted this period.',
                goals='Refine onboarding process',
                comments='Chris is a valuable member of the team, demonstrating strong positive attitude.',
                author=test_user
            ),
            Assessment(
                employee_name='Sam Roberts',
                position='Sales Operations Analyst',
                department='Sales',
                review_period='Q1 2024',
                performance_rating=3.9,
                strengths='Code quality focus, excellent presentation skills, quick learner',
                areas_for_improvement='Needs to build confidence in area z',
                goals='Increase lead generation by w%, master financial forecasting model',
                comments='Excellent progress shown by Sam, particularly in achieving increase lead generation by w%.',
                author=test_user
            ),
            Assessment(
                employee_name='Alexander Thomas',
                position='Compensation Analyst',
                department='HR',
                review_period='Q3 2024',
                performance_rating=4.6,
                strengths='Customer-focused',
                areas_for_improvement='Needs deeper technical understanding in x area, could improve time management',
                goals='Lead a major project, take on more leadership responsibilities',
                comments='Highly effective performer. Alexander\'s work on take on more leadership responsibilities has been impactful. Continue fostering customer-focused.',
                author=test_user
            ),
            Assessment(
                employee_name='Harper Johnson',
                position='QA Engineer',
                department='Engineering',
                review_period='Q2 2023',
                performance_rating=4.0,
                strengths='Manages complexity well',
                areas_for_improvement='Needs to develop cross-functional collaboration',
                goals='Gain expertise in technology x',
                comments='Highly effective performer. Harper\'s work on gain expertise in technology x has been impactful. Continue fostering manages complexity well.',
                author=test_user
            ),
            Assessment(
                employee_name='Avery Rodriguez',
                position='Accountant',
                department='Finance',
                review_period='Q1 2023',
                performance_rating=3.4,
                strengths='Code quality focus',
                areas_for_improvement='Needs to build confidence in area z',
                goals='Enhance security protocols, implement ci/cd improvements',
                comments='Highly effective performer. Avery\'s work on enhance security protocols has been impactful. Continue fostering code quality focus.',
                author=test_user
            ),
            Assessment(
                employee_name='Lucas Scott',
                position='Social Media Coordinator',
                department='Marketing',
                review_period='Q3 2023',
                performance_rating=5.0,
                strengths='Creative thinking',
                areas_for_improvement='Could be more proactive in communication',
                goals='Improve team velocity',
                comments='Highly effective performer. Lucas\'s work on improve team velocity has been impactful. Continue fostering creative thinking.',
                author=test_user
            ),
            Assessment(
                employee_name='Dakota Lee',
                position='Finance Manager',
                department='Finance',
                review_period='Q4 2023',
                performance_rating=3.3,
                strengths='Talent sourcing',
                areas_for_improvement='Could enhance reporting clarity',
                goals='Launch new product feature',
                comments='A solid performance from Dakota this period. Key contributions include launch new product feature.',
                author=test_user
            ),
            Assessment(
                employee_name='Chris Campbell',
                position='Machine Learning Engineer',
                department='Analytics',
                review_period='Q3 2024',
                performance_rating=4.2,
                strengths='Strong leadership potential',
                areas_for_improvement='Needs to enhance presentation skills, could be more proactive in communication',
                goals='Master financial forecasting model',
                comments='Performance meets expectations. Chris should focus on needs to enhance presentation skills while continuing to leverage strong leadership potential.',
                author=test_user
            ),
            Assessment(
                employee_name='Henry Smith',
                position='Customer Success Manager',
                department='Sales',
                review_period='Q2 2024',
                performance_rating=4.4,
                strengths='Positive attitude, takes initiative, talent sourcing',
                areas_for_improvement='Needs to delegate more effectively',
                goals='Increase lead generation by w%, launch new product feature',
                comments='Henry consistently exceeds expectations. Strengths in takes initiative and talent sourcing are particularly notable.',
                author=test_user
            ),
            Assessment(
                employee_name='Taylor Adams',
                position='UI/UX Designer',
                department='Design',
                review_period='Q3 2024',
                performance_rating=4.6,
                strengths='Positive attitude, deep domain knowledge',
                areas_for_improvement='Focus remains on leveraging strengths.',
                goals='Take on more leadership responsibilities',
                comments='Reliable and consistent performer. Taylor\'s deep domain knowledge makes them a dependable team member. Agreed focus on take on more leadership responsibilities for next period.',
                author=test_user
            ),
        ]
        
        for assessment in assessments:
            db.session.add(assessment)
        
        print("Committing changes...")
        db.session.commit()
        print("Database initialization completed successfully!")

if __name__ == '__main__':
    init_db()