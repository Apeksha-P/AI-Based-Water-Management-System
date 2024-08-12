import json
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash,g
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt,check_password_hash
import mysql.connector
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os
import re
import random
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA


import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__, static_url_path='/static/')
app.secret_key = 'your_secret_key'

# Configure Flask-Mail
app.config["MAIL_SERVER"] = 'smtp.office365.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "abhayas-cs20048@stu.kln.ac.lk"
app.config["MAIL_PASSWORD"] = 'Sk19990919..'
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config['MAIL_DEFAULT_SENDER'] = 'apeksha-cs20070@stu.kln.ac.lk'
app.config['MAIL_DEBUG'] = True
mail = Mail(app)

# Configure Flask-SQLAlchemy to connect to RDS MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+mysqlconnector://admin:AIBWMS123db@aibwms-db.cbk24q4qotkj.ap-southeast-2.rds.amazonaws.com:3306/AIBWMS_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Database configuration (no longer needed if you use SQLAlchemy directly)
db_config = {
    'user': 'admin',
    'password': 'AIBWMS123db',
    'host': 'aibwms-db.cbk24q4qotkj.ap-southeast-2.rds.amazonaws.com',
    'database': 'AIBWMS_db'
}

# Create SQLAlchemy engine
engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

# Load existing CSV data
csv_file = 'data/dataset.csv'
if os.path.exists(csv_file):
    try:
        df_existing = pd.read_csv(csv_file, parse_dates=['Date'])
    except Exception as e:
        print(f"Error reading existing CSV file: {e}")
        df_existing = pd.DataFrame(columns=['Date', 'Usage', 'Temp', 'ph', 'TDS', 'MeterReading'])
else:
    df_existing = pd.DataFrame(columns=['Date', 'Usage', 'Temp', 'ph', 'TDS', 'MeterReading'])

# Fetch new data from MySQL
query = "SELECT * FROM water_measurement"
try:
    with engine.connect() as connection:
        df_new = pd.read_sql(query, connection, parse_dates=['Date'])
except Exception as e:
    print(f"Error fetching data from MySQL: {e}")
    df_new = pd.DataFrame(columns=['Date', 'Usage', 'Temp', 'ph', 'TDS', 'MeterReading'])

# Check if dataframes are empty before concatenating
if df_existing.empty and df_new.empty:
    df_combined = pd.DataFrame(columns=['Date', 'Usage', 'Temp', 'ph', 'TDS', 'MeterReading'])
elif df_existing.empty:
    df_combined = df_new
elif df_new.empty:
    df_combined = df_existing
else:
    # Combine existing and new data, keeping only the most recent entry for each date
    df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset='Date', keep='last')

# Ensure 'Date' is of datetime type
df_combined['Date'] = pd.to_datetime(df_combined['Date'], errors='coerce')

# Remove rows with invalid dates
df_combined = df_combined.dropna(subset=['Date'])

# Sort by date for proper MeterReading calculation
df_combined.sort_values(by='Date', inplace=True)

# Calculate MeterReading based on cumulative usage
df_combined['MeterReading'] = df_combined['Usage'].cumsum()

# Save updated DataFrame to CSV
try:
    df_combined.to_csv(csv_file, index=False)
except PermissionError as e:
    print(f"Permission error: {e}")
except Exception as e:
    print(f"Error saving CSV file: {e}")


# Optional: Function to create the database if it doesn't exist
def create_database_if_not_exists():
    try:
        cnx = mysql.connector.connect(user=db_config['user'], password=db_config['password'], host=db_config['host'])
        cursor = cnx.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        cursor.close()
        cnx.close()
        print(f"Database '{db_config['database']}' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


UPLOAD_FOLDER = 'static/pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    cnumber = db.Column(db.String(20))
    picture = db.Column(db.String(255), nullable=True, default=None)

    def __init__(self, fname, lname, email, password, cnumber, picture=None):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.cnumber = cnumber
        self.picture = picture

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    cnumber = db.Column(db.String(50))
    picture = db.Column(db.String(255), nullable=True, default=None)

    def __init__(self, fname, lname, email, password, cnumber, picture=None):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.cnumber = cnumber
        self.picture = picture

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    cnumber = db.Column(db.String(50))
    picture = db.Column(db.String(255), nullable=True, default=None)

    def __init__(self, fname, lname, email, password, cnumber, picture=None):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.cnumber = cnumber
        self.picture = picture
@app.before_request
def create_tables():
    if not hasattr(g, '_db_tables_created'):
        db.create_all()
        g._db_tables_created = True

@app.route('/')
def index_form():
    return render_template('index.html')

@app.route('/approval_form')
def approval_form():
    return render_template('approval.html')

@app.route('/signupStudent')
def signupStudent_form():
    return render_template('signupStudent.html')

@app.route('/signupStaff')
def signupStaff_form():
    return render_template('signupStaff.html')


def send_otp_email(email, otp, fname):
    try:
        msg = Message('Email verification', sender=app.config["MAIL_DEFAULT_SENDER"], recipients=[email])
        msg.html = render_template('emailtemplate.html', otp=otp, email=email, fname=fname)
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("An error occurred while sending the email:", e)
        flash("An error occurred while sending the email. Please try again later.", "danger")

def send_otp_email_p(email, otp):
    try:
        msg = Message('Email verification', sender=app.config["MAIL_USERNAME"], recipients=[email])
        msg.html = render_template('emailtemplate.html', otp=otp, email=email)
        mail.send(msg)
    except Exception as e:
        print("An error occurred while sending the email:", e)
        flash("An error occurred while sending the email. Please try again later.", "danger")


@app.route('/signupStudent', methods=["POST"])
def signupStudent():
    if request.method == "POST":
        email = request.form.get('email')
        email_pattern = r'^[a-zA-Z0-9._%+-]+@stu\.kln\.ac\.lk$'
        if not re.match(email_pattern, email):
            flash('Invalid email address. Please use a student email in the format name-CSXXXXX@stu.kln.ac.lk.')
            return redirect(url_for('signupStudent'))

        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash('Email already exists. Please use a different email.')
            return redirect(url_for('alreadySignupStudent_form'))

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        password = request.form.get('password')
        cnumber = request.form.get('cnumber')

        # Password validation
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[@$!%*?&.#^(),]', password):
            flash('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, and a special character.')
            return redirect(url_for('signupStudent'))

        otp = str(random.randint(100000, 999999))

        send_otp_email_p(email, otp)

        session['signup_data'] = {
            'fname': fname,
            'lname': lname,
            'email': email,
            'password': password,
            'cnumber': cnumber,
            'otp': otp
        }

        return redirect(url_for('verifyStudent'))

    return render_template('signupStudent.html')

@app.route('/alreadySignupStudent')
def alreadySignupStudent_form():
    return render_template('alreadySignupStudent.html')

@app.route('/signupStaff', methods=["POST"])
def signupStaff():
    if request.method == "POST":
        email = request.form.get('email')
        # Check if email matches the pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@stu\.kln\.ac\.lk$'
        if not re.match(email_pattern, email):
            flash('Invalid email address. Please use an email with the pattern name-CSXXXXX@stu.kln.ac.lk.', 'danger')
            return redirect(url_for('signupStaff'))

        existing_staff = Staff.query.filter_by(email=email).first()
        if existing_staff:
            flash('Email already exists. Please use a different email.')
            return redirect(url_for('alreadySignupStaff_form'))
        else:
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            password = request.form.get('password')
            cnumber = request.form.get('cnumber')

            # Password validation
            if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[@$!%*?&.#^(),]', password):
                flash('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, and a special character.')
                return redirect(url_for('signupStaff'))

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            # Send OTP via email
            send_otp_email_p(email, otp)
            # Store signup data in session
            session['signup_data'] = {
                'fname': fname,
                'lname': lname,
                'email': email,
                'password': password,
                'cnumber': cnumber,
                'otp': otp
            }
            return redirect(url_for('verifyStaff'))
    return render_template('signupStaff.html')

@app.route('/alreadySignupStaff')
def alreadySignupStaff_form():
    return render_template('alreadySignupStaff.html')

@app.route('/alreadySignupAdmin')
def alreadySignupAdmin_form():
    return render_template('alreadySignupAdmin.html')

@app.route('/verifyStudent', methods=["GET", "POST"])
def verifyStudent():
    if request.method == "POST":
        entered_otp = request.form.get('otp')
        signup_data = session.get('signup_data')
        if signup_data['otp'] == entered_otp:
            # Create Student object and add to database
            student = Student(
                fname=signup_data['fname'],
                lname=signup_data['lname'],
                email=signup_data['email'],
                password=signup_data['password'],
                cnumber=signup_data['cnumber'],
            )
            try:
                db.session.add(student)
                db.session.commit()
                flash('Email verified successfully! Please sign in.')
                return redirect(url_for('signinStudent_form'))
            except Exception as e:
                flash('An error occurred while saving data. Please try again later.')
                print("Error:", e)
                return redirect(url_for('verifyStudent'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('verifyStudent'))
    # If GET request, render the verifyStudent.html template
    return render_template('verifyStudent.html')

@app.route('/verifyStaff', methods=["GET", "POST"])
def verifyStaff():
    if request.method == "POST":
        entered_otp = request.form.get('otp')
        signup_data = session.get('signup_data')
        if signup_data['otp'] == entered_otp:
            # Create Student object and add to database
            staff = Staff(
                fname=signup_data['fname'],
                lname=signup_data['lname'],
                email=signup_data['email'],
                password=signup_data['password'],
                cnumber=signup_data['cnumber'],
            )
            try:
                db.session.add(staff)
                db.session.commit()
                flash('Email verified successfully! Please sign in.')
                return redirect(url_for('signinStaff_form'))
            except Exception as e:
                flash('An error occurred while saving data. Please try again later.')
                print("Error:", e)
                return redirect(url_for('verifyStaff'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('verifyStaff'))
    # If GET request, render the verifyStudent.html template
    return render_template('verifyStaff.html')


@app.route('/verifyAdmin', methods=["GET", "POST"])
def verifyAdmin():
    if request.method == "POST":
        entered_otp = request.form.get('otp')
        addAdmin_data = session.get('addAdmin_data')
        if addAdmin_data['otp'] == entered_otp:
            # Create Admin object and add to database
            admin = Admin(
                fname=addAdmin_data['fname'],
                lname=addAdmin_data['lname'],
                email=addAdmin_data['email'],
                password=addAdmin_data['password'],
                cnumber=addAdmin_data['cnumber'],
            )
            try:
                db.session.add(admin)
                db.session.commit()
                flash('Email verified successfully!')
                return redirect(url_for('accessAdmin_form'))
            except Exception as e:
                flash('An error occurred while saving data. Please try again later.')
                print("Error:", e)
                return redirect(url_for('verifyAdmin'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('verifyAdmin'))
    # If GET request, render the verifyAdmin.html template
    return render_template('verifyAdmin.html')


@app.route('/signinStudent', methods=["GET", "POST"])
def signinStudent_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        student = Student.query.filter_by(email=email).first()

        if student and bcrypt.check_password_hash(student.password, password):
            session['student_id'] = student.id
            session['student_email'] = student.email
            session['student_fname'] = student.fname
            return redirect(url_for('homeStudent'))
        else:
            flash("Invalid email or password.", "danger")
            return render_template('signinStudent.html', error_message="Invalid email or password.")

    return render_template('signinStudent.html')


@app.route('/signinStaff', methods=["GET", "POST"])
def signinStaff_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Query the database for the staff with the given email
        staff = Staff.query.filter_by(email=email).first()
        if staff and bcrypt.check_password_hash(staff.password, password):
            # Passwords match, user is authenticated
            # Store staff's information in session
            session['staff_id'] = staff.id
            session['staff_email'] = staff.email
            session['staff_fname'] = staff.fname
            # Redirect to the home page after successful login
            return redirect(url_for('homeStaff'))
        else:
            # Invalid email or password, render the signinStaff.html template with an error message
            flash("Invalid email or password.", "danger")
            return render_template('signinStaff.html', error_message="Invalid email or password.")
    # Render the signinStaff.html template for GET requests
    return render_template('signinStaff.html')

@app.route('/signinAdmin', methods=["GET", "POST"])
def signinAdmin_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        admin = Admin.query.filter_by(email=email).first()
        if admin and bcrypt.check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_email'] = admin.email
            session['admin_fname'] = admin.fname
            return redirect(url_for('homeAdmin'))
        else:
            flash("Invalid email or password.")
            return render_template('signinAdmin.html')
    return render_template('signinAdmin.html')


@app.route('/signinAccessAdmin', methods=["GET", "POST"])
def signinAccessAdmin_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Query the database for the Admin with the given email and password
        admin = Admin.query.filter_by(email=email).first()
        if admin and bcrypt.check_password_hash(admin.password, password):
            # Store Admin information in session
            session['admin_id'] = admin.id
            session['admin_email'] = admin.email
            session['admin_fname'] = admin.fname
            # Redirect to the home page after successful login
            return redirect(url_for('accessAdmin_form'))
        else:
            # Users not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signinAccessAdmin.html', error_message="Invalid email or password.")
    return render_template('signinAccessAdmin.html')

@app.route('/homeStudent')
def homeStudent():
    # Check if student is logged in
    if 'student_id' in session:
        student_id = session['student_id']
        student_email = session['student_email']
        student = Student.query.filter_by(id=student_id, email=student_email).first()
        if student:
            return render_template('homeStudent.html', student=student)
        else:
            # Handle the case where the student does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStudent_form'))

@app.route('/homeStaff')
def homeStaff():
    # Check if staff is logged in
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff_email = session['staff_email']
        staff = Staff.query.filter_by(id=staff_id,email=staff_email).first()
        if staff:
            return render_template('homeStaff.html', staff=staff)
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStaff_form'))


@app.route('/homeAdmin')
def homeAdmin():
    # Check if Admin is logged in
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id,email=admin_email).first()
        if admin:
            return render_template('homeAdmin.html', admin=admin)
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinAdmin_form'))

@app.route('/dashboardStudent')
def dashboardStudent_form():
    if 'student_id' in session:
        student_id = session['student_id']
        student_email = session['student_email']
        student = Student.query.filter_by(id=student_id, email=student_email).first()
        if student:
            return render_template('dashboardStudent.html', student=student)
        else:
            # Handle the case where the student does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStudent_form'))

@app.route('/dashboardStaff')
def dashboardStaff_form():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff_email = session['staff_email']
        staff = Staff.query.filter_by(id=staff_id,email=staff_email).first()
        if staff:
            return render_template('dashboardStaff.html', staff=staff)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinStaff_form'))

@app.route('/dashboardAdmin')
def dashboardAdmin_form():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id,email=admin_email).first()
        if admin:
            return render_template('dashboardAdmin.html', admin=admin)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinAdmin_form'))

@app.route('/profileStudent')
def profileStudent_form():
    if 'student_id' in session:
        student_id = session['student_id']
        student_email = session['student_email']
        student = Student.query.filter_by(id=student_id, email=student_email).first()
        if student:
            return render_template('profileStudent.html', student=student)
        else:
            # Handle the case where the student does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStudent_form'))


@app.route('/upload_pictureStudent', methods=['POST'])
def upload_pictureStudent():
    if 'student_id' in session:
        student_id = session['student_id']
        student_email = session['student_email']
        student = Student.query.filter_by(id=student_id, email=student_email).first()
        if student:
            if 'picture' in request.files:
                file = request.files['picture']
                if file.filename != '':
                    # Save the uploaded file
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Update the student's profile picture filename in the database
                    student.picture = filename
                    db.session.commit()  # Save changes to the database
                    flash('Profile picture uploaded successfully!')
                    return redirect(url_for('profileStudent_form'))
                else:
                    flash('No file selected!')
            else:
                flash('No file part!')
        else:
            flash('Student not found!')
    else:
        flash('You need to be logged in!')
    return redirect(url_for('profileStudent_form'))

@app.route('/upload_pictureStaff', methods=['POST'])
def upload_pictureStaff():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff_email = session['staff_email']
        staff = Staff.query.filter_by(id=staff_id, email=staff_email).first()
        if staff:
            if 'picture' in request.files:
                file = request.files['picture']
                if file.filename != '':
                    # Save the uploaded file
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Update the staff's profile picture filename in the database
                    staff.picture = filename
                    db.session.commit()  # Save changes to the database
                    flash('Profile picture uploaded successfully!')
                    return redirect(url_for('profileStaff_form'))
                else:
                    flash('No file selected!')
            else:
                flash('No file part!')
        else:
            flash('Student not found!')
    else:
        flash('You need to be logged in!')
    return redirect(url_for('profileStaff_form'))


@app.route('/upload_pictureAdmin', methods=['POST'])
def upload_pictureAdmin():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id, email=admin_email).first()
        if admin:
            if 'picture' in request.files:
                file = request.files['picture']
                if file.filename != '':
                    # Save the uploaded file
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Update the admin's profile picture filename in the database
                    admin.picture = filename
                    db.session.commit()  # Save changes to the database
                    flash('Profile picture uploaded successfully!')
                    return redirect(url_for('profileAdmin_form'))
                else:
                    flash('No file selected!')
            else:
                flash('No file part!')
        else:
            flash('Admin not found!')
    else:
        flash('You need to be logged in!')
    return redirect(url_for('profileAdmin_form'))

@app.route('/uploads/<filename>')
def serve_uploaded_picture(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/profileStaff')
def profileStaff_form():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff_email = session['staff_email']
        staff= Staff.query.filter_by(id=staff_id, email=staff_email).first()
        if staff:
            return render_template('profileStaff.html', staff=staff)
        else:
            # Handle the case where the staff does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStaff_form'))

@app.route('/update_profileStaff', methods=['POST'])
def update_profileStaff():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff_email = session['staff_email']
        staff = Staff.query.filter_by(id=staff_id, email=staff_email).first()
        if staff:
            # Update the profile details based on the form submission
            staff.fname = request.form['fname']
            staff.lname = request.form['lname']
            staff.cnumber = request.form['cnumber']

            db.session.commit()  # Save changes to the database
            flash('Profile details updated successfully!')
            return redirect(url_for('profileStaff_form'))
        else:
            flash('Staff not found!')
    else:
        flash('You need to be logged in!')
    return redirect(url_for('profileStaff_form'))



@app.route('/profileAdmin')
def profileAdmin_form():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id, email=admin_email).first()
        if admin:
            return render_template('profileAdmin.html', admin=admin)
        else:
            # Handle the case where the Admin does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinAdmin_form'))

@app.route('/update_profileAdmin', methods=['POST'])
def update_profileAdmin():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id, email=admin_email).first()
        if admin:
            # Update the profile details based on the form submission
            admin.fname = request.form['fname']
            admin.lname = request.form['lname']
            admin.cnumber = request.form['cnumber']

            db.session.commit()  # Save changes to the database
            flash('Profile details updated successfully!')
            return redirect(url_for('profileAdmin_form'))
        else:
            flash('Admin not found!')
    else:
        flash('You need to be logged in!')
    return redirect(url_for('profileAdmin_form'))

@app.route('/update_profileStudent', methods=['POST'])
def update_profileStudent():
    if 'student_id' in session:
        student_id = session['student_id']
        student_email = session['student_email']
        student = Student.query.filter_by(id=student_id, email=student_email).first()
        if student:
            # Update the profile details based on the form submission
            student.fname = request.form['fname']
            student.lname = request.form['lname']
            student.cnumber = request.form['cnumber']

            db.session.commit()  # Save changes to the database
            flash('Profile details updated successfully!')
            return redirect(url_for('profileStudent_form'))
        else:
            flash('Student not found!')
    else:
        flash('You need to be logged in!')
    return redirect(url_for('profileStudent_form'))



@app.route('/predictionsStaff')
def predictionStaff_form():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff_email = session['staff_email']
        staff = Staff.query.filter_by(id=staff_id,email=staff_email).first()
        if staff:
            return render_template('predictionsStaff.html', staff=staff)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinStaff_form'))

@app.route('/predictionsStudent')
def predictionStudent_form():
    if 'student_id' in session:
        student_id = session['student_id']
        student_email = session['student_email']
        student = Student.query.filter_by(id=student_id, email=student_email).first()
        if student:
            return render_template('predictionsStudent.html', student=student)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinStudent_form'))


@app.route('/predictionsAdmin')
def predictionAdmin_form():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id,email=admin_email).first()
        if admin:
            return render_template('predictionsAdmin.html', admin=admin)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinAdmin_form'))

@app.route('/analysingStaff')
def analysingStaff_form():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff_email = session['staff_email']
        staff = Staff.query.filter_by(id=staff_id,email=staff_email).first()
        if staff:
            return render_template('analysingStaff.html', staff=staff)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinStaff_form'))


@app.route('/analysingAdmin')
def analysingAdmin_form():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id,email=admin_email).first()
        if admin:
            return render_template('analysingAdmin.html', admin=admin)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinAdmin_form'))


@app.route('/accessAdmin', methods=["GET","POST"])
def accessAdmin_form():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id,email=admin_email).first()
        if admin:
            admins = Admin.query.all()
            students = Student.query.order_by(Student.id.asc()).all()
            staff = Staff.query.all()
            return render_template('accessAdmin.html', admin=admin, admins=admins, students=students, staff=staff)
        else:
            return "user not found"
    else:
        return redirect(url_for('signinAdmin_form'))


# def get_last_month_reading():
#     df = pd.read_csv('data/dataset.csv')
#     # Assuming 'Date' is in the format 'YYYY-MM-DD' and 'Reading' is the meter reading
#     df['Date'] = pd.to_datetime(df['Date'])
#     last_month = df['Date'].dt.month.max() - 1
#     last_month_data = df[df['Date'].dt.month == last_month]
#     last_month_total = last_month_data['MeterReading'].max()
#     return last_month_total

def get_last_month_reading():
    df = pd.read_csv('data/dataset.csv')

    # Convert the 'Date' column to datetime, allowing pandas to infer the format
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Drop rows with invalid dates if any
    df = df.dropna(subset=['Date'])

    # Calculate the last month based on the most recent date in the dataset
    last_date = df['Date'].max()
    first_day_last_month = (last_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    last_day_last_month = last_date.replace(day=1) - pd.DateOffset(days=1)

    # Filter data for the last month
    last_month_data = df[(df['Date'] >= first_day_last_month) & (df['Date'] <= last_day_last_month)]
    last_month_total = last_month_data['MeterReading'].max()

    return last_month_total




# def update_daily_usage(date, usage):
#     df = pd.read_csv('data/dataset.csv')
#     new_entry = {'Date': date, 'Usage': usage}
#     df = df.append(new_entry, ignore_index=True)
#     df.to_csv('dataset.csv', index=False)

# def update_daily_usage(date, usage):
#     # Load the dataset
#     df = pd.read_csv('data/dataset.csv')
#
#     # Create a new DataFrame for the new entry
#     new_entry = pd.DataFrame({'Date': [date], 'Usage': [usage]})
#
#     # Concatenate the old DataFrame with the new entry
#     df = pd.concat([df, new_entry], ignore_index=True)
#
#     # Save the updated DataFrame back to CSV
#     df.to_csv('data/dataset.csv', index=False)

def update_daily_usage(date, usage):
    # Load the dataset
    df = pd.read_csv('data/dataset.csv')

    # Convert the input date to the desired format
    formatted_date = pd.to_datetime(date).strftime("%m/%d/%Y %I:%M:%S %p")

    # Ensure the 'Date' column in the DataFrame is in datetime format for comparison
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Drop rows with invalid dates if any
    df = df.dropna(subset=['Date'])

    # Get the last meter reading
    last_meter_reading = df['MeterReading'].max()

    # Calculate the new meter reading
    new_meter_reading = last_meter_reading + float(usage)

    # Create a new entry with the formatted date
    new_entry = pd.DataFrame({'Date': [formatted_date], 'MeterReading': [new_meter_reading], 'Usage': [usage]})

    # Concatenate the old DataFrame with the new entry
    df = pd.concat([df, new_entry], ignore_index=True)

    # Save the updated DataFrame back to CSV
    df.to_csv('data/dataset.csv', index=False)




# def get_this_month_data():
#     df = pd.read_csv('data/dataset.csv')
#     df['Date'] = pd.to_datetime(df['Date'])
#     this_month = df['Date'].dt.month.max()
#     this_month_data = df[df['Date'].dt.month == this_month]
#     return this_month_data['MeterReading'].max(), this_month_data['Usage'].sum()

def get_this_month_data():
    df = pd.read_csv('data/dataset.csv')

    # Convert the 'Date' column to datetime, allowing pandas to infer the format
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Drop rows with invalid dates if any
    df = df.dropna(subset=['Date'])

    # Calculate the current month based on the most recent date in the dataset
    current_month_start = df['Date'].max().replace(day=1)
    next_month_start = (current_month_start + pd.DateOffset(months=1)).replace(day=1)

    # Filter data for the current month
    this_month_data = df[(df['Date'] >= current_month_start) & (df['Date'] < next_month_start)]
    this_month_reading = this_month_data['MeterReading'].max()
    this_month_usage = this_month_data['Usage'].sum()

    return this_month_reading, this_month_usage


#
# @app.route('/meterAdmin')
# def meterAdmin_form():
#     if 'admin_id' in session:
#         admin_id = session['admin_id']
#         admin_email = session['admin_email']
#         admin = Admin.query.filter_by(id=admin_id,email=admin_email).first()
#         if admin:
#             return render_template('meterAdmin.html', admin=admin)
#         else:
#             return "user not found"
#     else:
#         return redirect(url_for('signinAdmin_form'))

@app.route('/meterAdmin', methods=['GET', 'POST'])
def meterAdmin_form():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_email = session['admin_email']
        admin = Admin.query.filter_by(id=admin_id, email=admin_email).first()
        if admin:
            if request.method == 'POST':
                date = request.form['date']
                usage = request.form['usage']
                update_daily_usage(date, usage)
                return redirect(url_for('meterAdmin_form'))

            last_month_reading = get_last_month_reading()
            this_month_reading, this_month_usage = get_this_month_data()

            return render_template('meterAdmin.html', admin=admin,
                                   last_month=last_month_reading,
                                   this_month=this_month_reading,
                                   usage=this_month_usage)
        else:
            return "User not found"
    else:
        return redirect(url_for('signinAdmin_form'))

@app.route('/addAdmin', methods=["GET", "POST"])
def addAdmin_form():
    if request.method == "POST":
        # Check if the email already exists
        email = request.form.get('email')
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            flash("Email already exists. Please use a different email.")
            return redirect(url_for("alreadySignupAdmin_form"))

        else:
            # Get data from form
            fname = request.form.get("firstname")
            lname = request.form.get("lastname")
            email = request.form.get("email")
            password = request.form.get("password")
            cnumber = request.form.get("contact")

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            # Send OTP via email
            send_otp_email_p(email, otp)
            # Store addAdmin data in session
            session['addAdmin_data'] = {
                'fname': fname,
                'lname': lname,
                'email': email,
                'password': hashed_password,
                'cnumber': cnumber,
                'otp': otp
            }
            return redirect(url_for('verifyAdmin'))

            # Hash the password
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

            # Create a new Admin object and add it to the database
            admin = Admin(
                fname=fname,
                lname=lname,
                email=email,
                password=hashed_password,
                cnumber=cnumber
            )

            try:
                db.session.add(admin)
                db.session.commit()
                flash("Admin added successfully!")
                return redirect(url_for("verifyAdmin"))  # Redirect to the admin management page
            except Exception as e:
                flash("An error occurred while saving data. Please try again.")
                print("Error:", e)
                return redirect(url_for("addAdmin_form"))  # Redirect back to the add admin form
    else:
        # This would handle the GET request if needed, such as displaying the form
        return render_template("addAdmin.html")  # Replace with rendering a template or appropriate response



@app.route('/delete_student', methods=["POST"])
def delete_student():
    # Check if user has proper permissions to delete
    if 'admin_id' not in session:
        flash("You need to be logged in as an admin to perform this action.")
        return redirect(url_for("signinAdmin_form"))

    # Get the student ID from the form data
    student_id = request.form.get("student_id")
    logged_in_student_id = session.get('student_id')

    # Query the student to be deleted
    student = Student.query.filter_by(id=student_id).first()

    if student:
        try:
            db.session.delete(student)  # Remove the student from the database
            db.session.commit()  # Save changes
            flash("Student deleted successfully.")

            # Check if the deleted student is the currently logged-in student
            if student_id == str(logged_in_student_id):
                session.pop('student_id')  # Clear the session
                return redirect(url_for("signinStudent_form"))  # Redirect to sign-in page

        except Exception as e:
            flash("An error occurred while trying to delete the student. Please try again.")
            print("Error:", e)
    else:
        flash("Student not found.")

    # Redirect back to the table after deletion
    return redirect(url_for("accessAdmin_form"))



@app.route('/delete_staff', methods=["POST"])
def delete_staff():
    # Check if user has proper permissions to delete
    if 'admin_id' not in session:
        flash("You need to be logged in as an admin to perform this action.")
        return redirect(url_for("signinAdmin_form"))

    # Get the staff ID from the form data
    staff_id = request.form.get("staff_id")
    logged_in_staff_id = session.get('staff_id')

    # Query the staff to be deleted
    staff = Staff.query.filter_by(id=staff_id).first()

    if staff:
        try:
            db.session.delete(staff)  # Remove the staff from the database
            db.session.commit()  # Save changes
            flash("Staff deleted and successfully.")

            # Check if the deleted staff is the currently logged-in staff
            if staff_id == str(logged_in_staff_id):
                session.pop('staff_id')  # Clear the session
                return redirect(url_for("signinStaff_form"))  # Redirect to sign-in page

        except Exception as e:
            flash("An error occurred while trying to delete the staff. Please try again.")
            print("Error:", e)
    else:
        flash("Staff not found.")

    # Redirect back to the table after deletion
    return redirect(url_for("accessAdmin_form"))

@app.route('/delete_admin', methods=["POST"])
def delete_admin():
    # Check if user has proper permissions to delete
    if 'admin_id' not in session:
        flash("You need to be logged in as an admin to perform this action.")
        return redirect(url_for("signinAdmin_form"))

    # Get the admin ID from the form data
    admin_id = request.form.get("admin_id")
    logged_in_admin_id = session.get('admin_id')

    # Query the admin to be deleted
    admin = Admin.query.filter_by(id=admin_id).first()

    if admin:
        try:
            db.session.delete(admin)  # Remove the admin from the database
            db.session.commit()  # Save changes
            flash("Admin deleted successfully.")

            # Check if the deleted admin is the currently logged-in admin
            if admin_id == str(logged_in_admin_id):
                session.pop('admin_id')  # Clear the session
                return redirect(url_for("signinAdmin_form"))  # Redirect to sign-in page

        except Exception as e:
            flash("An error occurred while trying to delete the admin. Please try again.")
            print("Error:", e)
    else:
        flash("Admin not found.")

    # Redirect back to the table after deletion if the deleted admin is not the currently logged-in admin
    return redirect(url_for("accessAdmin_form"))

@app.route('/forgotPasswordStudent', methods=["GET","POST"])
def forgotPasswordStudent():
    if request.method == "POST":
        email = request.form.get('email')
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            otp = str(random.randint(100000, 999999))
            send_otp_email_p(email, otp)
            session['forgot_password_data'] = {
                'email': email,
                'otp': otp
            }
            return redirect(url_for('verifyOTPStudent'))
        else:
            return render_template('signupStudent.html')
    else:
        return render_template('forgotPasswordStudent.html')

@app.route('/verifyOTPStudent', methods=["GET", "POST"])
def verifyOTPStudent():
    if request.method == "POST":
        entered_otp = request.form.get('otp')
        forgot_password_data = session.get('forgot_password_data')
        if forgot_password_data['otp'] == entered_otp:
            return redirect(url_for('resetPasswordStudent'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('verifyOTPStudent'))
    return render_template('verifyOTPStudent.html')

@app.route('/resetPasswordStudent',methods=["GET","POST"])
def resetPasswordStudent():
    if request.method == "POST":
        new_password = request.form.get('newpassword')
        reentered_password = request.form.get('reenternewpassword')
        if new_password == reentered_password:
            student = Student.query.filter_by(email=session['forgot_password_data']['email']).first()
            student.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()

            flash('Password reset successful! Please sign in with your new password.')
            return redirect(url_for('signinStudent_form'))
        else:
            flash('Passwords do not match. Please re-enter.')
            return redirect(url_for('resetPasswordStudent'))
    return render_template('resetPasswordStudent.html')

@app.route('/forgotPasswordStaff', methods=["GET","POST"])
def forgotPasswordStaff():
    if request.method == "POST":
        email = request.form.get('email')
        existing_staff = Staff.query.filter_by(email=email).first()
        if existing_staff:
            otp = str(random.randint(100000, 999999))
            send_otp_email_p(email, otp)
            session['forgot_password_data'] = {
                'email': email,
                'otp': otp
            }
            return redirect(url_for('verifyOTPStaff'))
        else:
            return render_template('signupStaff.html')
    else:
        return render_template('forgotPasswordStaff.html')

@app.route('/verifyOTPStaff', methods=["GET", "POST"])
def verifyOTPStaff():
    if request.method == "POST":
        entered_otp = request.form.get('otp')
        forgot_password_data = session.get('forgot_password_data')
        if forgot_password_data['otp'] == entered_otp:
            return redirect(url_for('resetPasswordStaff'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('verifyOTPStaff'))
    return render_template('verifyOTPStaff.html')

@app.route('/resetPasswordStaff',methods=["GET","POST"])
def resetPasswordStaff():
    if request.method == "POST":
        new_password = request.form.get('newpassword')
        reentered_password = request.form.get('reenternewpassword')
        if new_password == reentered_password:
            staff = Staff.query.filter_by(email=session['forgot_password_data']['email']).first()
            staff.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()

            flash('Password reset successful! Please sign in with your new password.')
            return redirect(url_for('signinStaff_form'))
        else:
            flash('Passwords do not match. Please re-enter.')
            return redirect(url_for('resetPasswordStaff'))
    return render_template('resetPasswordStaff.html')


@app.route('/forgotPasswordAdmin', methods=["GET","POST"])
def forgotPasswordAdmin():
    if request.method == "POST":
        email = request.form.get('email')
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            otp = str(random.randint(100000, 999999))
            send_otp_email_p(email, otp)
            session['forgot_password_data'] = {
                'email': email,
                'otp': otp
            }
            return redirect(url_for('verifyOTPAdmin'))
        else:
            return render_template('approval.html')
    else:
        return render_template('forgotPasswordAdmin.html')


@app.route('/verifyOTPAdmin', methods=["GET", "POST"])
def verifyOTPAdmin():
    if request.method == "POST":
        entered_otp = request.form.get('otp')
        forgot_password_data = session.get('forgot_password_data')
        if forgot_password_data['otp'] == entered_otp:
            return redirect(url_for('resetPasswordAdmin'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('verifyOTPAdmin'))
    return render_template('verifyOTPAdmin.html')


@app.route('/resetPasswordAdmin',methods=["GET","POST"])
def resetPasswordAdmin():
    if request.method == "POST":
        new_password = request.form.get('newpassword')
        reentered_password = request.form.get('reenternewpassword')
        if new_password == reentered_password:
            admin = Admin.query.filter_by(email=session['forgot_password_data']['email']).first()
            admin.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()

            flash('Password reset successful! Please sign in with your new password.')
            return redirect(url_for('signinAdmin_form'))
        else:
            flash('Passwords do not match. Please re-enter.')
            return redirect(url_for('resetPasswordAdmin'))
    return render_template('resetPasswordAdmin.html')



@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

@app.route('/ viewMore')
def view_more():
    return render_template('viewMore.html')

@app.route('/ viewmoreStudent')
def viewmoreStudent_form():
    return render_template('viewmoreStudent.html')

@app.route('/remove_pictureStudent', methods=['POST'])
def remove_pictureStudent():
    student = get_current_student()
    if student:
        filename = student.picture
        if filename:
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(picture_path):
                os.remove(picture_path)
            student.picture = None
            db.session.commit()
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'error': 'No profile picture to remove'}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({'error': 'Student not found'}), 404, {'ContentType': 'application/json'}

@app.route('/remove_pictureStaff', methods=['POST'])
def remove_pictureStaff():
    staff = get_current_staff()
    if staff:
        filename = staff.picture
        if filename:
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(picture_path):
                os.remove(picture_path)
            staff.picture = None
            db.session.commit()
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'error': 'No profile picture to remove'}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({'error': 'staff not found'}), 404, {'ContentType': 'application/json'}

@app.route('/remove_pictureAdmin', methods=['POST'])
def remove_pictureAdmin():
    admin = get_current_admin()
    if admin:
        filename = admin.picture
        if filename:
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(picture_path):
                os.remove(picture_path)
            admin.picture = None
            db.session.commit()
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'error': 'No profile picture to remove'}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({'error': 'staff not found'}), 404, {'ContentType': 'application/json'}

def get_current_student():
    if 'student_id' in session:
        student_id = session['student_id']
        return Student.query.get(student_id)
    return None

def get_current_staff():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        return Staff.query.get(staff_id)

def get_current_admin():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        return Admin.query.get(admin_id)


# -----------------------------------------------Predictions---------------------------------------------------------
@app.route("/test")
def call_weekly_predictions():
    # partition_data()
    data = get_weekly_data()
    return (
        data,
        200,
        {"ContentType": "application/json"},
    )


PREDICTION_FEATURE = "Usage"
ARIMA_ORDER = (6, 0, 6)
#
# @app.route("/test")
# def call_weekly_predictions():
#     data = get_weekly_data()
#     return jsonify(data)
#
def get_weekly_data(prediction_count=4):
    df = pd.read_csv("data/weekly_data_train.csv", index_col="Date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index, freq="W")
    df_train = df.dropna()

    model = ARIMA(df_train[PREDICTION_FEATURE], order=ARIMA_ORDER)
    model_fit = model.fit()
    forecast_value = model_fit.forecast(steps=prediction_count)

    forecast_value.index = forecast_value.index.astype(str)
    df.index = df.index.astype(str)

    return {
        "labels": list(df.index[-prediction_count:]),  # Last 'prediction_count' dates
        "data": list(forecast_value.clip(lower=0))
    }

#change prediction count to look more into the future
# def get_weekly_data(prediction_count=4):
#     df = pd.read_csv("data/weekly_data_train.csv", index_col="Date", parse_dates=True)
#     df.index = pd.DatetimeIndex(df.index, freq="W")
#     df_train = df.dropna()
#     model = ARIMA(df_train[PREDICTION_FEATURE], order=ARIMA_ORDER)
#     model_fit = model.fit()
#     forecast_value = model_fit.forecast(steps=prediction_count)
#
#     forecast_value.index = forecast_value.index.astype(str)
#     df.index = df.index.astype(str)
#
#     forecast_json = forecast_value.clip(lower=0).to_dict()
#     current_data_json = df["Usage"].to_dict()
#     return {"forecast": forecast_json, "current_data": current_data_json}



PREDICTION_FEATURE = "Usage"
ARIMA_ORDER_MONTHLY = (2, 1, 2)  # Adjust the ARIMA order as needed

@app.route("/monthly_predictions")
def call_monthly_predictions():
    # partition_data()
    data = get_monthly_data()
    return (
        data,
        200,
        {"ContentType": "application/json"},
    )
# change prediction count to look more into the future
def get_monthly_data(prediction_count=4):
    df = pd.read_csv("data/monthly_data_train.csv", index_col="Date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index, freq="M")
    df_train = df.dropna()
    model = ARIMA(df_train[PREDICTION_FEATURE], order=ARIMA_ORDER)
    model_fit = model.fit()
    forecast_value = model_fit.forecast(steps=prediction_count)
#     forecast_value.index = forecast_value.index.astype(str)
#     df.index = df.index.astype(str)
#
#     forecast_json = forecast_value.clip(lower=0).to_dict()
#     current_data_json = df["Usage"].to_dict()
#     return {"forecast": [forecast_json], "current_data": [current_data_json]}
#
    forecast_value.index = forecast_value.index.astype(str)
    df.index = df.index.astype(str)

    return {
        "labels": list(df.index[-prediction_count:]),  # Last 'prediction_count' dates
        "data": list(forecast_value.clip(lower=0))
    }



# Run this to partition dataset.csv
def partition_data():
    df = pd.read_csv("data/dataset.csv", index_col="Date", parse_dates=True)
    df = df[["Usage"]]

    weekly_data_train = df.resample("W").sum()
    weekly_data_train.to_csv("data/weekly_data_train.csv")
    monthly_data_train = df.resample("M").sum()
    monthly_data_train.to_csv("data/monthly_data_train.csv")

if __name__ == "__main__":
    create_database_if_not_exists()  # Ensure the database exists before running the app
    app.run(host='0.0.0.0', port=5000, debug=True)
