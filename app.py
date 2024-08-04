from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import joblib
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import plotly.io as pio
import traceback

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

    total_tenants = TenantApplication.query.count()
    
    approved_count = TenantApplication.query.filter_by(result='Approved').count()
    rejected_count = TenantApplication.query.filter_by(result='Rejected').count()

    status_counts = {'Approved': approved_count, 'Rejected': rejected_count}
    status_fig = px.bar(x=list(status_counts.keys()), y=list(status_counts.values()), title='Approved vs Rejected Tenants', labels={'x': 'Status', 'y': 'Count'})
    status_plot = pio.to_html(status_fig, full_html=False)

    tenants = TenantApplication.query.all()
    tenant_data = []

    for tenant in tenants:
        decoded_tenant = {
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
        }

        for column, le in label_encoders.items():
            if column in decoded_tenant:
                try:
                    decoded_tenant[column] = le.inverse_transform([decoded_tenant[column]])[0]
                except Exception as e:
                    print(f"Error decoding {column}: {e}")

        tenant_data.append(decoded_tenant)

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
    preview_html = None  # Initialize preview_html to avoid UnboundLocalError

    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['csv_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            file_path = os.path.join('static/uploads', secure_filename(file.filename))
            file.save(file_path)
            
            # Read the CSV file into a DataFrame
            preview_df = pd.read_csv(file_path)
            # Display the first few rows for preview
            preview_html = preview_df.head().to_html(classes='table table-striped')

            # Handle encoding if necessary
            for column in label_encoders:
                if column in preview_df.columns:
                    le = label_encoders[column]
                    preview_df[column] = le.transform(preview_df[column])

            input_scaled = scaler.transform(preview_df)
            predictions_encoded = model.predict(input_scaled)
            # Decode the results
            result = ["Approved" if pred == 1 else "Rejected" for pred in predictions_encoded]

            try:
                # Save results to the database
                for index, row in preview_df.iterrows():
                    new_application = TenantApplication(
                        employment_history=row.get('Employment History'),
                        income=row.get('Income'),
                        rental_history=row.get('Rental History'),
                        credit_score=row.get('Credit Score'),
                        payment_history=row.get('Payment History'),
                        outstanding_debts=row.get('Outstanding Debts'),
                        criminal_records=row.get('Criminal Records'),
                        legal_issues=row.get('Legal Issues'),
                        employment_verification=row.get('Employment Verification'),
                        income_verification=row.get('Income Verification'),
                        personal_references=row.get('Personal References'),
                        professional_references=row.get('Professional References'),
                        result=result[index]  # Save the decoded result
                    )
                    db.session.add(new_application)
                db.session.commit()
                flash('File successfully processed and results saved.')
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving results: {e}')
                print("Error inserting data:", e)

    return render_template('model_analysis.html', result=result, preview_html=preview_html)

@app.route('/analysis')
def analysis():
    query = "SELECT * FROM tenant_applications"
    df = pd.read_sql(query, db.engine)  
    credit_score_fig = px.histogram(df, x='credit_score', title='Credit Score Distribution')
    income_fig = px.histogram(df, x='income', title='Income Distribution')

    total_tenants = df.shape[0]
    count_data = pd.DataFrame({'Category': ['Total Tenants'], 'Count': [total_tenants]})
    count_fig = px.bar(count_data, x='Category', y='Count', title='Total Count of Tenants')

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
@app.route('/tenant', methods=['GET', 'POST'])
def tenant():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'aadhar' not in request.files or 'income' not in request.files or 'birth_certificate' not in request.files:
            flash('All documents are required')
            return redirect(request.url)
        
        files = {
            'aadhar': request.files['aadhar'],
            'income': request.files['income'],
            'birth_certificate': request.files['birth_certificate']
        }
        
        # Save uploaded files
        for file_key, file in files.items():
            if file and allowed_file(file.filename) and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
            else:
                flash(f'Invalid file type for {file_key}')
                return redirect(request.url)

        flash('Documents successfully uploaded.')
        return redirect(url_for('tenant'))

    tenants = TenantApplication.query.all()
    return render_template('tenant.html', tenants=tenants)

@app.route('/tenant/<int:tenant_id>')
def tenant_details(tenant_id):
    tenant = TenantApplication.query.get_or_404(tenant_id)
    
    # Construct file paths (assuming you store the files with the tenant ID or some identifier)
    aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{tenant_id}_aadhar.pdf')
    income_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{tenant_id}_income.pdf')
    birth_certificate_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{tenant_id}_birth_certificate.pdf')
    
    # Add paths to context
    return render_template('tenant_details.html', tenant=tenant, aadhar_path=aadhar_path, income_path=income_path, birth_certificate_path=birth_certificate_path)

if __name__ == '__main__':
    app.run(debug=True)
