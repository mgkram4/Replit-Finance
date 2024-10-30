from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Expense, Category, SavingsGoal, Income
from forms import LoginForm, RegisterForm, ExpenseForm, SavingsGoalForm, IncomeForm
from datetime import datetime, timedelta
from sqlalchemy import func

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

def process_recurring_expenses():
    """Process all recurring expenses and create new entries if needed"""
    current_date = datetime.utcnow()
    recurring_expenses = Expense.query.filter_by(recurring=True).all()
    
    for expense in recurring_expenses:
        if not expense.last_recurring_date:
            expense.last_recurring_date = expense.date
            continue
            
        next_date = None
        if expense.frequency == 'monthly':
            next_date = expense.last_recurring_date + timedelta(days=30)
        elif expense.frequency == 'weekly':
            next_date = expense.last_recurring_date + timedelta(days=7)
        elif expense.frequency == 'yearly':
            next_date = expense.last_recurring_date + timedelta(days=365)
            
        if next_date and next_date <= current_date:
            new_expense = Expense(
                amount=expense.amount,
                description=expense.description,
                category_id=expense.category_id,
                user_id=expense.user_id,
                recurring=True,
                frequency=expense.frequency,
                date=next_date,
                last_recurring_date=next_date
            )
            expense.last_recurring_date = next_date
            db.session.add(new_expense)
    
    db.session.commit()

def calculate_savings_recommendations(user_id):
    # Get monthly income
    monthly_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == user_id,
        Income.recurring == True,
        Income.frequency == 'monthly'
    ).scalar() or 0

    # Get one-time income for the current month
    current_month = datetime.utcnow()
    one_time_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == user_id,
        Income.recurring == False,
        func.extract('month', Income.date) == current_month.month,
        func.extract('year', Income.date) == current_month.year
    ).scalar() or 0

    total_monthly_income = monthly_income + one_time_income

    # Calculate recommended savings (25% of income)
    recommended_savings = total_monthly_income * 0.25

    # Get monthly expenses by category
    expenses_by_category = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(Expense).filter(
        Expense.user_id == user_id,
        func.extract('month', Expense.date) == current_month.month,
        func.extract('year', Expense.date) == current_month.year
    ).group_by(Category.name).all()

    # Calculate total expenses
    total_expenses = sum(expense.total for expense in expenses_by_category)

    # Generate recommendations
    recommendations = []
    expense_percentages = {}
    
    for category, amount in expenses_by_category:
        percentage = (amount / total_monthly_income * 100) if total_monthly_income > 0 else 0
        expense_percentages[category] = percentage
        
        # Add category-specific recommendations
        if category == 'Entertainment' and percentage > 10:
            recommendations.append(f"Consider reducing entertainment expenses (currently {percentage:.1f}% of income)")
        elif category == 'Food' and percentage > 15:
            recommendations.append(f"Food expenses are high ({percentage:.1f}% of income). Try meal planning to reduce costs")
        elif category == 'Transportation' and percentage > 15:
            recommendations.append(f"Look for ways to reduce transportation costs (currently {percentage:.1f}% of income)")

    return {
        'monthly_income': total_monthly_income,
        'recommended_savings': recommended_savings,
        'current_expenses': total_expenses,
        'expense_percentages': expense_percentages,
        'recommendations': recommendations
    }

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    process_recurring_expenses()  # Process recurring expenses before showing dashboard
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    savings_recommendations = calculate_savings_recommendations(current_user.id)
    return render_template('dashboard.html', 
                         expenses=expenses, 
                         goals=goals, 
                         recommendations=savings_recommendations)

@app.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    form = IncomeForm()
    if form.validate_on_submit():
        income = Income(
            amount=form.amount.data,
            source=form.source.data,
            date=form.date.data,
            recurring=form.recurring.data,
            frequency=form.frequency.data,
            user_id=current_user.id
        )
        db.session.add(income)
        db.session.commit()
        flash('Income added successfully!')
        return redirect(url_for('income'))
        
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
    return render_template('income.html', form=form, incomes=incomes)

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
    process_recurring_expenses()  # Process recurring expenses before showing the page
    form = ExpenseForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            description=form.description.data,
            category_id=form.category.data,
            date=form.date.data,
            user_id=current_user.id,
            recurring=form.recurring.data,
            frequency=form.frequency.data if form.recurring.data else 'monthly',
            last_recurring_date=form.date.data if form.recurring.data else None
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!')
        return redirect(url_for('expenses'))
        
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
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

@app.route('/api/savings_recommendations')
@login_required
def savings_recommendations():
    return jsonify(calculate_savings_recommendations(current_user.id))
