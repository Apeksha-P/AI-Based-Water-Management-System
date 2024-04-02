from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import random
from flask_mail import *
from flask import flash



app = Flask(__name__, static_url_path='/static/')
app.secret_key = 'your_secret_key'

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


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    cnumber = db.Column(db.String(50))
    otp = db.Column(db.String(6))


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    cnumber = db.Column(db.String(50))


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


@app.route('/signupStudent', methods=["POST"])
def signupStudent():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    cnumber = request.form.get('cnumber')

    otp = str(random.randint(100000, 999999))

    msg = Message('Email verification', sender=app.config["MAIL_USERNAME"], recipients=[email])
    msg.body = f"Hi {fname},\nYour email OTP is: {otp}"

    try:
        mail.send(msg)
    except Exception as e:
        print("An error occurred while sending the email:", e)
        return "An error occurred while sending the email. Please try again later."


    student = Student(fname=fname, lname=lname, email=email, password=password, cnumber=cnumber, otp=otp)
    db.session.add(student)
    db.session.commit()

    return redirect(url_for('verifyStudent', email=email))

@app.route('/verifyStudent', methods=["GET", "POST"])
def verifyStudent():
    if request.method == "POST":
        email = request.form.get('email')
        entered_otp = request.form.get('otp')
        student = Student.query.filter_by(email=email).first()
        if student:
            if student.otp == entered_otp:
                flash('Email verified successfully! Please sign in.')
                return redirect(url_for('signinStudent_form'))
            else:
                flash('Invalid OTP. Please try again.')
                return redirect(url_for('verifyStudent', email=email))  # Redirect to verification page
        else:
            flash('Student not found.')
            return redirect(url_for('index_form'))  # Redirect to homepage or appropriate page
    else:
        email = request.args.get('email')  # Fetch email from query parameters
        student = Student.query.filter_by(email=email).first()
        if student:
            return render_template('verifyStudent.html', student=student)
        else:
            flash('Student not found.')
            return redirect(url_for('index_form'))


@app.route('/signupStaff', methods=["POST"])
def signupStaff():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    cnumber = request.form.get('cnumber')

    # Create a new Users instance and add it to the database
    staff = Staff(fname=fname, lname=lname, email=email, password=password, cnumber=cnumber)
    db.session.add(staff)
    db.session.commit()

    # Redirect to the sign-in page after successful signup
    return redirect(url_for('signinStaff_form'))


@app.route('/signinStudent', methods=["GET", "POST"])
def signinStudent_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for the users with the given email and password
        student = Student.query.filter_by(email=email, password=password).first()

        if student:
            # Store users information in session
            session['student_id'] = student.id
            session['student_email'] = student.email
            session['student_fname'] = student.fname
            # Redirect to the home page after successful login
            return redirect(url_for('homeStudent'))  # Redirect to the home page
        else:
            # Users not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signinStudent.html', error_message="Invalid email or password.")

    return render_template('signinStudent.html')

@app.route('/signinStaff', methods=["GET", "POST"])
def signinStaff_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for the users with the given email and password
        staff = Staff.query.filter_by(email=email, password=password).first()

        if staff:
            # Store users information in session
            session['staff_id'] = staff.id
            session['staff_email'] = staff.email
            session['staff_fname'] = staff.fname
            # Redirect to the home page after successful login
            return redirect(url_for('homeStaff'))  # Redirect to the home page
        else:
            # Users not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signinStaff.html', error_message="Invalid email or password.")

    return render_template('signinStaff.html')


@app.route('/signinAdmin', methods=["GET", "POST"])
def signinAdmin_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for the users with the given email and password
        admin = Admin.query.filter_by(email=email, password=password).first()

        if admin:
            # Store users information in session
            session['admin_id'] = admin.id
            session['admin_email'] = admin.email
            session['admin_fname'] = admin.fname
            # Redirect to the home page after successful login
            return redirect(url_for('homeAdmin'))  # Redirect to the home page
        else:
            # Users not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signinAdmin.html', error_message="Invalid email or password.")

    return render_template('signinAdmin.html')



@app.route('/homeStudent')
def homeStudent():
    # Check if user is logged in
    if 'student_id' in session:
        return render_template('homeStudent.html', student_email=session['student_email'], student_fname=session['student_fname'])
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStudent_form'))

@app.route('/homeStaff')
def homeStaff():
    # Check if user is logged in
    if 'staff_id' in session:
        return render_template('homeStaff.html', staff_email=session['staff_email'], staff_fname=session['staff_fname'])
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStaff_form'))

@app.route('/dashboardStudent')
def dashboardStudent_form():
    return render_template('dashboardStudent.html')

@app.route('/dashboardStaff')
def dashboardStaff_form():
    return render_template('dashboardStaff.html')

@app.route('/profileStudent')
def profileStudent_form():
    if 'student_id' in session:
        student_id = session['student_id']
        student = Student.query.get(student_id)
        if student:
            return render_template('profileStudent.html', student=student)
        else:
            # Handle the case where the user does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStudent_form'))


@app.route('/profileStaff')
def profileStaff_form():
    if 'staff_id' in session:
        staff_id = session['staff_id']
        staff = Staff.query.get(staff_id)
        if staff:
            return render_template('profileStaff.html', staff=staff)
        else:
            # Handle the case where the user does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signinStaff_form'))

@app.route('/predictionsStaff')
def predictionStaff_form():
    return render_template('predictionsStaff.html')

@app.route('/analysingStaff')
def analysingStaff_form():
    return render_template('analysingStaff.html')



@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

if __name__ == '__main__':
    app.run(debug=True)