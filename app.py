from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
app.secret_key = 'DK1329'

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
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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
    return render_template('dashboard.html')

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

@app.route('/model_analysis', methods=['GET', 'POST'])
def model_analysis():
    if 'username' not in session:
        return redirect(url_for('login'))

    result = None
    # if request.method == 'POST':
    #     data = {
    #         'Employment History': [int(request.form['employment_history'])],
    #         'Income': [int(request.form['income'])],
    #         'Rental History': [int(request.form['rental_history'])],
    #         'Credit Score': [int(request.form['credit_score'])],
    #         'Payment History': [int(request.form['payment_history'])],
    #         'Outstanding Debts': [int(request.form['outstanding_debts'])],
    #         'Criminal Records': [int(request.form['criminal_records'])],
    #         'Legal Issues': [int(request.form['legal_issues'])],
    #         'Employment Verification': [int(request.form['employment_verification'])],
    #         'Income Verification': [int(request.form['income_verification'])],
    #         'Personal References': [int(request.form['personal_references'])],
    #         'Professional References': [int(request.form['professional_references'])]
    #     }

    
    return render_template('model_analysis.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
