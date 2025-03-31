from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class AssessmentForm(FlaskForm):
    employee_name = StringField('Employee Name', validators=[DataRequired(), Length(min=2, max=100)])
    position = StringField('Position', validators=[DataRequired(), Length(min=2, max=100)])
    department = SelectField('Department', choices=[
        ('Engineering', 'Engineering'),
        ('Product', 'Product'),
        ('Design', 'Design'),
        ('Data', 'Data'),
        ('Marketing', 'Marketing'),
        ('Sales', 'Sales'),
        ('HR', 'HR'),
        ('Finance', 'Finance')
    ], validators=[DataRequired()])
    review_period = StringField('Review Period', validators=[DataRequired(), Length(max=50)])
    performance_rating = IntegerField('Performance Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    strengths = TextAreaField('Strengths', validators=[DataRequired()])
    areas_for_improvement = TextAreaField('Areas for Improvement', validators=[DataRequired()])
    goals = TextAreaField('Goals', validators=[DataRequired()])
    comments = TextAreaField('Additional Comments')
    submit = SubmitField('Submit Assessment') 