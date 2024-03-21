from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/static/')

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/reg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    cnumber = db.Column(db.String(50))
    position = db.Column(db.String(50))

@app.route('/')
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

    user = User(fname=fname, lname=lname, email=email, password=password, cnumber=cnumber, position=position)
    db.session.add(user)

    db.session.commit()

    # Redirect to the sign-in page after successful signup
    return redirect(url_for('signin_form'))
@app.route('/signin', methods=["GET", "POST"])
def signin_form():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for the user with the given email and password
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            # Store user information in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_fname'] = user.fname
            # Redirect to the home page or some other page after successful login
            return redirect(url_for('home'))
        else:
            # User not found or incorrect credentials, redirect back to sign-in page with a message
            return render_template('signin.html', error_message="Invalid email or password.")

    return render_template('signin.html')

@app.route('/home')
def home():
    # Check if user is logged in
    if 'user_id' in session:
        return render_template('index.html', user_email=session['user_email'], user_fname=session['user_fname'])
    else:
        # Redirect to sign-in page if not logged in
        return redirect(url_for('signin_form'))

if __name__ == '__main__':
    # Initialize database before running the app
    with app.app_context():
        db.create_all()
    # Run the app
    app.run(debug=True)
