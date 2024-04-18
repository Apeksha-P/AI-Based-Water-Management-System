from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import random
from flask_mail import *
from flask import flash
from flask_bcrypt import Bcrypt, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static/')
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

app.config["MAIL_SERVER"]='smtp.office365.com'
app.config["MAIL_PORT"]=587
app.config["MAIL_USERNAME"]="apeksha-cs20070@stu.kln.ac.lk"
app.config["MAIL_PASSWORD"]='CpDa@6080Ap'
app.config["MAIL_USE_TLS"]=True
app.config["MAIL_USE_SSL"]=False
app.config['MAIL_DEBUG'] = True
mail = Mail(app)

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/reg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Student(db.Model):
    __student__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50),primary_key=True, unique=True)
    password = db.Column(db.String(50))
    cnumber = db.Column(db.String(50))
    picture = db.Column(db.String(255))

class Staff(db.Model):
    __staff__ = 'staffs'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    cnumber = db.Column(db.String(50))
    picture = db.Column(db.String(255))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    cnumber = db.Column(db.String(50))

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

def send_otp_email(email, otp):
    msg = Message('Email verification', sender=app.config["MAIL_USERNAME"], recipients=[email])
    msg.body = f"Hi,\nYour email OTP is: {otp}"
    try:
        mail.send(msg)
    except Exception as e:
        print("An error occurred while sending the email:", e)
        # Handle error


@app.route('/signupStudent', methods=["POST"])
def signupStudent():
    if request.method == "POST":
        email = request.form.get('email')
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash('Email already exists. Please use a different email.')
            return redirect(url_for('alreadySignupStudent_form'))
        else:
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            password = request.form.get('password')
            cnumber = request.form.get('cnumber')

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Send OTP via email
            send_otp_email(email, otp)

            # Store signup data in session
            session['signup_data'] = {
                'fname': fname,
                'lname': lname,
                'email': email,
                'password': hashed_password,
                'cnumber': cnumber,
                'otp': otp
            }

            # Redirect to verifyStudent page
            return redirect(url_for('verifyStudent'))

    return render_template('signupStudent.html')

@app.route('/alreadySignupStudent')
def alreadySignupStudent_form():
    return render_template('alreadySignupStudent.html')

@app.route('/signupStaff', methods=["POST"])
def signupStaff():
    if request.method == "POST":
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        cnumber = request.form.get('cnumber')

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Send OTP via email
        send_otp_email(email, otp)

        # Store signup data in session
        session['signup_data'] = {
            'fname': fname,
            'lname': lname,
            'email': email,
            'password': password,
            'cnumber': cnumber,
            'otp': otp
        }

        # Redirect to verifyStudent page
        return redirect(url_for('verifyStaff'))

    return render_template('signupStaff.html')


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
            # Create Staff object and add to database
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

    # If GET request, render the verifyStaff.html template
    return render_template('verifyStaff.html')

@app.route('/signinStudent', methods=["GET", "POST"])
def signinStudent_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Query the database for the student with the given email
        student = Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            # Passwords match, user is authenticated
            # Store student's information in session
            session['student_id'] = student.id
            session['student_email'] = student.email
            session['student_fname'] = student.fname
            # Redirect to the home page after successful login
            return redirect(url_for('homeStudent'))
        else:
            # Invalid email or password, render the signinStudent.html template with an error message
            return render_template('signinStudent.html', error_message="Invalid email or password.")
    # Render the signinStudent.html template for GET requests
    return render_template('signinStudent.html')


@app.route('/signinStaff', methods=["GET", "POST"])
def signinStaff_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Query the database for the staff with the given email and password
        staff = Staff.query.filter_by(email=email, password=password).first()
        if staff:
            # Store staff information in session
            session['staff_id'] = staff.id
            session['staff_email'] = staff.email
            session['staff_fname'] = staff.fname
            # Redirect to the home page after successful login
            return redirect(url_for('homeStaff'))
        else:
            # Users not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signinStaff.html', error_message="Invalid email or password.")

    return render_template('signinStaff.html')


@app.route('/signinAdmin', methods=["GET", "POST"])
def signinAdmin_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Query the database for the Admin with the given email and password
        admin = Admin.query.filter_by(email=email, password=password).first()
        if admin:
            # Store Admin information in session
            session['admin_id'] = admin.id
            session['admin_email'] = admin.email
            session['admin_fname'] = admin.fname
            # Redirect to the home page after successful login
            return redirect(url_for('homeAdmin'))
        else:
            # Users not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signinAdmin.html', error_message="Invalid email or password.")
    return render_template('signinAdmin.html')



@app.route('/homeStudent')
def homeStudent():
    # Check if student is logged in
    if 'student_id' in session:
        return render_template('homeStudent.html', student_email=session['student_email'], student_fname=session['student_fname'])
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStudent_form'))

@app.route('/homeStaff')
def homeStaff():
    # Check if staff is logged in
    if 'staff_id' in session:
        return render_template('homeStaff.html', staff_email=session['staff_email'], staff_fname=session['staff_fname'])
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStaff_form'))


@app.route('/homeAdmin')
def homeAdmin():
    # Check if Admin is logged in
    if 'admin_id' in session:
        return render_template('homeAdmin.html', admin_email=session['admin_email'], admin_fname=session['admin_fname'])
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinAdmin_form'))

@app.route('/dashboardStudent')
def dashboardStudent_form():
    return render_template('dashboardStudent.html')

@app.route('/dashboardStaff')
def dashboardStaff_form():
    return render_template('dashboardStaff.html')

@app.route('/dashboardAdmin')
def dashboardAdmin_form():
    return render_template('dashboardAdmin.html')

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
                    # Update the student's profile picture filename in the database
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


@app.route('/uploads/<filename>')
def serve_uploaded_picture(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/profileStaff')
def profileStaff_form():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff = Staff.query.get(staff_id)
        if staff:
            return render_template('profileStaff.html', staff=staff)
        else:
            # Handle the case where the staff does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStaff_form'))


@app.route('/profileAdmin')
def profileAdmin_form():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin = Admin.query.get(admin_id)
        if admin:
            return render_template('profileAdmin.html', admin=admin)
        else:
            # Handle the case where the Admin does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinAdmin_form'))

@app.route('/predictionsStaff')
def predictionStaff_form():
    return render_template('predictionsStaff.html')

@app.route('/predictionsAdmin')
def predictionAdmin_form():
    return render_template('predictionsAdmin.html')

@app.route('/analysingStaff')
def analysingStaff_form():
    return render_template('analysingStaff.html')

@app.route('/analysingAdmin')
def analysingAdmin_form():
    return render_template('analysingAdmin.html')


@app.route('/accessAdmin')
def accessAdmin_form():
    return render_template('accessAdmin.html')


@app.route('/meterAdmin')
def meterAdmin_form():
    return render_template('meterAdmin.html')


@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

if __name__ == '__main__':
    app.run(debug=True)