from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, DateField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class IncomeForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    source = StringField('Source', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    recurring = BooleanField('Recurring Income')
    frequency = SelectField('Frequency', choices=[
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly')
    ], default='monthly')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    recurring = BooleanField('Recurring Expense')
    frequency = SelectField('Frequency', choices=[
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly')
    ], default='monthly')

class SavingsGoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired()])
    target_amount = FloatField('Target Amount', validators=[DataRequired()])
    deadline = DateField('Target Date', validators=[DataRequired()])
