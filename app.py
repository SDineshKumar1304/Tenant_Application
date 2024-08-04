from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import joblib
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'DK1329'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/Tenant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

VALID_USERNAME = 'Dinesh Kumar'
VALID_PASSWORD = 'Dinesh@123'
ADMIN_PROFILE = {
    'username': 'S Dinesh Kumar',
    'email': 'svani4830@gmail.com',
    'full_name': 'User',
    'phone': '123-456-7890',
    'address': '123  St, City, AC 12345',
    'profile_photo': 'profile.jpg'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model = joblib.load('decision_tree_model.joblib')
scaler = joblib.load('scaler.joblib')
label_encoders = joblib.load('label_encoders.joblib')

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get total tenants count
    total_tenants = TenantApplication.query.count()
    
    # Get counts of approved and rejected tenants
    approved_count = TenantApplication.query.filter_by(result='Approved').count()
    rejected_count = TenantApplication.query.filter_by(result='Rejected').count()

    # Generate plot for approved vs rejected tenants
    status_counts = {'Approved': approved_count, 'Rejected': rejected_count}
    status_fig = px.bar(x=list(status_counts.keys()), y=list(status_counts.values()), title='Approved vs Rejected Tenants', labels={'x': 'Status', 'y': 'Count'})
    status_plot = pio.to_html(status_fig, full_html=False)

    # Get tenant data
    tenants = TenantApplication.query.all()
    tenant_data = [{
        'id': tenant.id,
        'employment_history': tenant.employment_history,
        'income': tenant.income,
        'rental_history': tenant.rental_history,
        'credit_score': tenant.credit_score,
        'payment_history': tenant.payment_history,
        'outstanding_debts': tenant.outstanding_debts,
        'criminal_records': tenant.criminal_records,
        'legal_issues': tenant.legal_issues,
        'employment_verification': tenant.employment_verification,
        'income_verification': tenant.income_verification,
        'personal_references': tenant.personal_references,
        'professional_references': tenant.professional_references,
        'result': tenant.result
    } for tenant in tenants]

    return render_template('dashboard.html', total_tenants=total_tenants, status_plot=status_plot, tenant_data=tenant_data)



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            ADMIN_PROFILE['profile_photo'] = filename
            return redirect(url_for('profile'))
        else:
            flash('Invalid file type')
            return redirect(request.url)

    return render_template('profile.html', profile=ADMIN_PROFILE)

class TenantApplication(db.Model):
    __tablename__ = 'tenant_applications'  # Correct table name
    id = db.Column(db.Integer, primary_key=True)
    employment_history = db.Column(db.String(255))
    income = db.Column(db.Numeric(10, 2))
    rental_history = db.Column(db.String(255))
    credit_score = db.Column(db.Integer)
    payment_history = db.Column(db.String(255))
    outstanding_debts = db.Column(db.Numeric(10, 2))
    criminal_records = db.Column(db.String(255))
    legal_issues = db.Column(db.String(255))
    employment_verification = db.Column(db.String(255))
    income_verification = db.Column(db.String(255))
    personal_references = db.Column(db.String(255))
    professional_references = db.Column(db.String(255))
    result = db.Column(db.String(50))

@app.route('/model_analysis', methods=['GET', 'POST'])
def model_analysis():
    if 'username' not in session:
        return redirect(url_for('login'))

    result = None

    if request.method == 'POST':
        data = {
            'Employment History': [request.form['employment_history']],
            'Income': [request.form['income']],
            'Rental History': [request.form['rental_history']],
            'Credit Score': [request.form['credit_score']],
            'Payment History': [request.form['payment_history']],
            'Outstanding Debts': [request.form['outstanding_debts']],
            'Criminal Records': [request.form['criminal_records']],
            'Legal Issues': [request.form['legal_issues']],
            'Employment Verification': [request.form['employment_verification']],
            'Income Verification': [request.form['income_verification']],
            'Personal References': [request.form['personal_references']],
            'Professional References': [request.form['professional_references']]
        }

        input_df = pd.DataFrame(data)

        # Handle encoding if necessary
        for column in label_encoders:
            if column in input_df.columns:
                le = label_encoders[column]
                input_df[column] = le.transform(input_df[column])

        input_scaled = scaler.transform(input_df)

        prediction = model.predict(input_scaled)
        result = "Approved" if prediction[0] == 1 else "Rejected"

        try:
            new_application = TenantApplication(
                employment_history=request.form['employment_history'],
                income=request.form['income'],
                rental_history=request.form['rental_history'],
                credit_score=request.form['credit_score'],
                payment_history=request.form['payment_history'],
                outstanding_debts=request.form['outstanding_debts'],
                criminal_records=request.form['criminal_records'],
                legal_issues=request.form['legal_issues'],
                employment_verification=request.form['employment_verification'],
                income_verification=request.form['income_verification'],
                personal_references=request.form['personal_references'],
                professional_references=request.form['professional_references'],
                result=result
            )

            db.session.add(new_application)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Error inserting data:", e)

    return render_template('model_analysis.html', result=result)
@app.route('/analysis')
def analysis():
    # Use Flask's database engine
    query = "SELECT * FROM tenant_applications"
    df = pd.read_sql(query, db.engine)  # Use db.engine instead of create_engine

    # Generate plots
    credit_score_fig = px.histogram(df, x='credit_score', title='Credit Score Distribution')
    income_fig = px.histogram(df, x='income', title='Income Distribution')

    # Count of tenants plot
    total_tenants = df.shape[0]
    count_data = pd.DataFrame({'Category': ['Total Tenants'], 'Count': [total_tenants]})
    count_fig = px.bar(count_data, x='Category', y='Count', title='Total Count of Tenants')

    # Convert figures to HTML
    credit_score_plot = pio.to_html(credit_score_fig, full_html=False)
    income_plot = pio.to_html(income_fig, full_html=False)
    count_plot = pio.to_html(count_fig, full_html=False)

    return render_template('analysis.html', credit_score_plot=credit_score_plot, income_plot=income_plot, count_plot=count_plot)

def create_credit_score_plot(data):
    fig = px.histogram(data, x='credit_score', title='Credit Score Distribution')
    fig.update_layout(xaxis_title='Credit Score', yaxis_title='Frequency')
    plot_html = pio.to_html(fig, full_html=False)
    return plot_html

def create_income_plot(data):
    fig = px.histogram(data, x='income', title='Income Distribution')
    fig.update_layout(xaxis_title='Income', yaxis_title='Frequency')
    plot_html = pio.to_html(fig, full_html=False)
    return plot_html


if __name__ == '__main__':
    app.run(debug=True)
