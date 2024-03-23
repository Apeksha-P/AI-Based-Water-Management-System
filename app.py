from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/static/')
app.secret_key = 'your_secret_key'

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/reg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Users model with the correct column definitions
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Define the primary key column
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    cnumber = db.Column(db.String(50))
    position = db.Column(db.String(50))

@app.route('/')
def index_form():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard_form():
    return render_template('dashboard.html')

@app.route('/analysing')
def analysing_form():
    return render_template('analysing.html')

@app.route('/prediction')
def prediction_form():
    return render_template('predictions.html')

@app.route('/profile')
def profile_form():
    if 'users_id' in session:
        user_id = session['users_id']
        user = Users.query.get(user_id)
        if user:
            return render_template('profile.html', user=user)
        else:
            # Handle the case where the user does not exist
            return "User not found"
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signin_form'))

@app.route('/signup')
def signup_form():
    return render_template('signup.html')

@app.route('/signup', methods=["POST"])
def signup():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    cnumber = request.form.get('cnumber')
    position = request.form.get('position')

    # Create a new Users instance and add it to the database
    users = Users(fname=fname, lname=lname, email=email, password=password, cnumber=cnumber, position=position)
    db.session.add(users)
    db.session.commit()

    # Redirect to the sign-in page after successful signup
    return redirect(url_for('signin_form'))

@app.route('/signin', methods=["GET", "POST"])
def signin_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for the users with the given email and password
        users = Users.query.filter_by(email=email, password=password).first()

        if users:
            # Store users information in session
            session['users_id'] = users.id
            session['users_email'] = users.email
            session['users_fname'] = users.fname
            # Redirect to the home page after successful login
            return redirect(url_for('home'))  # Redirect to the home page
        else:
            # Users not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signin.html', error_message="Invalid email or password.")

    return render_template('signin.html')

@app.route('/home')
def home():
    # Check if users is logged in
    if 'users_id' in session:
        return render_template('home.html', users_email=session['users_email'], users_fname=session['users_fname'])
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signin_form'))

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

if __name__ == '__main__':
    # Initialize database before running the app
    with app.app_context():
        db.create_all()
    # Run the app
    app.run(debug=True)
