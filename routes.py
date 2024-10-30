from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Expense, Category, SavingsGoal
from forms import LoginForm, RegisterForm, ExpenseForm, SavingsGoalForm
from datetime import datetime

# Initialize categories
def init_categories():
    categories = ['Housing', 'Transportation', 'Food', 'Utilities', 'Healthcare', 'Entertainment']
    existing_categories = Category.query.all()
    if not existing_categories:
        for category_name in categories:
            category = Category(name=category_name)
            db.session.add(category)
        db.session.commit()

# Initialize categories when the app starts
with app.app_context():
    init_categories()

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', expenses=expenses, goals=goals)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            description=form.description.data,
            category_id=form.category.data,
            date=form.date.data,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!')
        return redirect(url_for('expenses'))
        
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    return render_template('expenses.html', form=form, expenses=expenses)

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    form = SavingsGoalForm()
    if form.validate_on_submit():
        goal = SavingsGoal(
            name=form.name.data,
            target_amount=form.target_amount.data,
            deadline=form.deadline.data,
            user_id=current_user.id
        )
        db.session.add(goal)
        db.session.commit()
        flash('Savings goal added successfully!')
        return redirect(url_for('goals'))
        
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', form=form, goals=goals)

@app.route('/api/expense_stats')
@login_required
def expense_stats():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    categories = {}
    for expense in expenses:
        cat_name = expense.category.name
        if cat_name in categories:
            categories[cat_name] += expense.amount
        else:
            categories[cat_name] = expense.amount
    return jsonify(categories)
