from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import joblib
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import plotly.io as pio
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR)



app = Flask(__name__)
app.secret_key = 'DK1329'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/Tenant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif','pdf'}
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


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled Exception: {e}")
    return "An unexpected error occurred. Please try again later.", 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model = joblib.load('decision_tree_model.joblib')
scaler = joblib.load('scaler.joblib')
label_encoders = joblib.load('label_encoders.joblib')

@app.route('/')
def index():
    print("Index page is being accessed")
    return render_template('index.html')

class Tenant(db.Model):
    __tablename__ = 'tenant_applications'
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

class TenantRegistration(db.Model):
    __tablename__ = 'tenant_registrations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_details = db.Column(db.String(20), nullable=False)
    employment_history = db.Column(db.String(255))
    income = db.Column(db.Numeric(10, 2))
    rental_history = db.Column(db.String(255))
    credit_score = db.Column(db.Integer)
    aadhar = db.Column(db.String(255))  # Path to uploaded Aadhaar document
    pan = db.Column(db.String(255))     # Path to uploaded PAN document
    income_certificate = db.Column(db.String(255))  # Path to uploaded income certificate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TenantCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum('tenant', 'admin'), default='tenant')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant_applications.id'))  # Corrected reference
    tenant = db.relationship('Tenant', backref=db.backref('credentials', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/tenant_register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            contact_details = request.form.get('contact_details')
            employment_history = request.form.get('employment_history')
            income = request.form.get('income')
            rental_history = request.form.get('rental_history')
            credit_score = request.form.get('credit_score')

            print(f"Name: {name}, Contact Details: {contact_details}, Employment History: {employment_history}")
            print(f"Income: {income}, Rental History: {rental_history}, Credit Score: {credit_score}")

            if not all([name, contact_details, employment_history, income, rental_history, credit_score]):
                flash('All fields are required!')
                return redirect(request.url)

            aadhar_file = request.files.get('aadhar')
            pan_file = request.files.get('pan')
            income_certificate_file = request.files.get('income_certificate')

            if not (aadhar_file and pan_file and income_certificate_file):
                flash('All documents are required')
                return redirect(request.url)

            if not (allowed_file(aadhar_file.filename) and allowed_file(pan_file.filename) and allowed_file(income_certificate_file.filename)):
                flash('Invalid file type')
                return redirect(request.url)

            aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(aadhar_file.filename))
            pan_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(pan_file.filename))
            income_certificate_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(income_certificate_file.filename))

            aadhar_file.save(aadhar_path)
            pan_file.save(pan_path)
            income_certificate_file.save(income_certificate_path)

            new_registration = TenantRegistration(
                name=name,
                contact_details=contact_details,
                employment_history=employment_history,
                income=income,
                rental_history=rental_history,
                credit_score=credit_score,
                aadhar=aadhar_path,
                pan=pan_path,
                income_certificate=income_certificate_path
            )

            print(f"New registration object: {new_registration}")

            db.session.add(new_registration)
            db.session.commit()

            flash('Registration successful!')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {e}')
            print(f"Error: {e}")

    return render_template('tenant_register.html')

def verify_user(username, password):
    user = TenantCredentials.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return True
    return False


@app.route('/create_credentials', methods=['GET', 'POST'])
def create_credentials():
    if 'tenant_id' not in session:
        flash('No tenant session found.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate username and password
        if TenantCredentials.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(request.url)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        new_credentials = TenantCredentials(
            username=username,
            password_hash=hashed_password,
            user_type='tenant',
            tenant_id=session['tenant_id']  # Store tenant_id from session
        )

        db.session.add(new_credentials)
        db.session.commit()

        flash('Credentials created successfully!')
        return redirect(url_for('login'))

    return render_template('create_credentials.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form.get('user_type', 'admin')

        if user_type == 'admin' and username == VALID_USERNAME and password == VALID_PASSWORD:
            session['username'] = username
            return redirect(url_for('dashboard'))
        elif user_type == 'tenant' and verify_user(username, password):
            session['username'] = username
            return redirect(url_for('tenant_dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/tenant_login', methods=['GET', 'POST'])
def tenant_login():
    if 'username' in session:
        return redirect(url_for('tenant_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('tenant_dashboard'))
        else:
            flash('Invalid tenant username or password')

    return render_template('tenant_login.html')


@app.route('/logout')
def logout():
    if 'username' in session:
        print("Logging out:", session['username'])
        session.pop('username', None)
    else:
        print("No user session found.")
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    total_tenants = Tenant.query.count()
    
    approved_count = Tenant.query.filter_by(result='Approved').count()
    rejected_count = Tenant.query.filter_by(result='Rejected').count()

    status_counts = {'Approved': approved_count, 'Rejected': rejected_count}
    status_fig = px.bar(x=list(status_counts.keys()), y=list(status_counts.values()), title='Approved vs Rejected Tenants', labels={'x': 'Status', 'y': 'Count'}, color_discrete_sequence=['#87CEFA'])
    status_fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)', paper_bgcolor='rgba(255, 255, 255, 0.8)', font=dict(color='black'))
    status_plot = pio.to_html(status_fig, full_html=False)

    tenants = Tenant.query.all()
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
            flash('Profile photo updated successfully.')
        else:
            flash('Invalid file type')
        return redirect(url_for('profile'))

    return render_template('profile.html', profile=ADMIN_PROFILE)



@app.route('/model_analysis', methods=['GET', 'POST'])
def model_analysis():
    if 'username' not in session:
        return redirect(url_for('login'))

    result = None
    preview_html = None  

    try:
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
                
                preview_df = pd.read_csv(file_path)
                preview_html = preview_df.head().to_html(classes='table table-striped')

                for column in label_encoders:
                    if column in preview_df.columns:
                        le = label_encoders[column]
                        preview_df[column] = le.transform(preview_df[column])

                input_scaled = scaler.transform(preview_df)
                predictions_encoded = model.predict(input_scaled)

                result = ["Approved" if pred == 1 else "Rejected" for pred in predictions_encoded]

                for index, row in preview_df.iterrows():
                    new_application = Tenant(
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
                        result=result[index]  
                    )
                    db.session.add(new_application)
                db.session.commit()
                flash('File successfully processed and results saved.')
            else:
                flash('Invalid file type. Only CSV files are allowed.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing file: {e}')
        print(f"Error: {e}")

    return render_template('model_analysis.html', result=result, preview_html=preview_html)


@app.route('/analysis')
def analysis():
    query = "SELECT * FROM tenant_applications"
    df = pd.read_sql(query, db.engine)  
    
    credit_score_plot = create_credit_score_plot(df)
    income_plot = create_income_plot(df)

    total_tenants = df.shape[0]
    count_data = pd.DataFrame({'Category': ['Total Tenants'], 'Count': [total_tenants]})
    count_fig = px.bar(count_data, x='Category', y='Count', title='Total Count of Tenants', color_discrete_sequence=['#67baf5'])
    count_fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)', paper_bgcolor='rgba(255, 255, 255, 0.8)', font=dict(color='black'))
    count_plot = pio.to_html(count_fig, full_html=False)

    return render_template('analysis.html', credit_score_plot=credit_score_plot, income_plot=income_plot, count_plot=count_plot)

def create_credit_score_plot(data):
    fig = px.histogram(data, x='credit_score', title='Credit Score Distribution', color_discrete_sequence=['#67baf5'])
    fig.update_layout(xaxis_title='Credit Score', yaxis_title='Frequency', plot_bgcolor='rgba(255, 255, 255, 0.8)', paper_bgcolor='rgba(255, 255, 255, 0.8)', font=dict(color='black'))
    plot_html = pio.to_html(fig, full_html=False)
    return plot_html

def create_income_plot(data):
    fig = px.histogram(data, x='income', title='Income Distribution', color_discrete_sequence=['#67baf5'])
    fig.update_layout(xaxis_title='Income', yaxis_title='Frequency', plot_bgcolor='rgba(255, 255, 255, 0.8)', paper_bgcolor='rgba(255, 255, 255, 0.8)', font=dict(color='black'))
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

    tenants = Tenant.query.all()
    return render_template('tenant.html', tenants=tenants)


@app.route('/tenant/<int:tenant_id>')
def tenant_details(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    
    aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{tenant_id}_aadhar.pdf')
    income_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{tenant_id}_income.pdf')
    birth_certificate_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{tenant_id}_birth_certificate.pdf')
    
    return render_template('tenant_details.html', tenant=tenant, aadhar_path=aadhar_path, income_path=income_path, birth_certificate_path=birth_certificate_path)

@app.route('/property')
def property_details():
    properties = [
        {
            'address': '123 Main St',
            'Property_type': '1BHK',
            'tenant_status': 'Occupied',
            'rent': '$1200',
            'contact': '9876543210',
            'lease_agreement': 'lease_agreement_123_main_st.pdf',
            'image_url': url_for('static', filename='images/1BHK.png')
        },
        {
            'address': '456 Elm St',
            'Property_type': '2BHK',
            'tenant_status': 'Vacant',
            'rent': '$1500',
            'contact': '1234567890',
            'lease_agreement': 'lease_agreement_456_elm_st.pdf',
            'image_url': url_for('static', filename='images/2BHK.png')
        },
        {
            'address': '789 Oak St',
            'Property_type': '3BHK',
            'tenant_status': 'Occupied',
            'rent': '$1100',
            'contact': '2345678901',
            'lease_agreement': 'lease_agreement_789_oak_st.pdf',
            'image_url': url_for('static', filename='images/3BHK.png')
        }
        
    ]
    return render_template('property_details.html', properties=properties)


if __name__ == '__main__':
    app.run(debug=True)
