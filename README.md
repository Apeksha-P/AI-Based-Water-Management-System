# AI-Based Water Management System
## Introduction
The AI-Based Water Management System is a Flask-based web application designed to facilitate efficient water management in Faculty of Computing and Technology, University of Kelaniya. The system utilizes artificial intelligence techniques to optimize water usage, detect anlysis, predictions and provide insights for better decision-making.

## Features
<ul>
  <li>User Registration and Authentication:</li>
Users can sign up as either students or staff members, providing necessary details such as name, email, password, and contact number. Authentication ensures secure access to the system.<br><br>

<li>Email Verification:</li>
During registration, users receive an email with a one-time password (OTP) for verification. This enhances the security of the sign-up process.<br><br>

<li>Dashboard:</li>
The system offers personalized dashboards for students and staff, providing relevant information and tools for water management activities.<br><br>

<li>Data Analysis and Prediction:</li>
Staff members have access to advanced features for analyzing water consumption patterns and predicting future usage trends. This enables proactive measures to optimize water usage and prevent wastage.<br><br>

<li>Profile Management:</li>
Users can view and update their profiles, including personal information and contact details, ensuring up-to-date records within the system.<br><br>
</ul>

## Installation
1. Clone the repository to your local machine:<br>
   git clone https://github.com/Apeksha-P/AI-Based-Water-Management-System.git<br><br>
2. Install dependencies:<br>
   pip install ---------<br><br>
3. Set up the database:<br>
  Configure your database settings in app.py under the Database configurations section.<br>
  Run the following commands to create the database tables:<br>
    flask db init<br>
    flask db migrate<br>
    flask db upgrade<br><br>
4. Configure email settings:<br>
  Update the MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, and MAIL_PASSWORD variables in app.py with your email server details.<br><br>
5. Run the application:<br>
  flask run<br><br>
6. Access the application in your web browser at http://3.106.228.248:5000 or scan below QR code <br>
   
![Untitled](https://github.com/user-attachments/assets/7251806d-15a2-4e29-89ed-eb45ffa26a4f)


## Usage
<ol>
  <li>Sign up as a student or staff member using the provided registration form.</li>
  <li>Verify your email address by entering the OTP sent to your email.</li>
  <li>Log in to access your dashboard, profile, and other features.</li>
  <li>Explore the dashboard for insights into water consumption and take necessary actions to optimize usage.</li>
  <li>Update your profile as needed to ensure accurate records within the system.</li>
</ol>

## Contributing
Contributions to the AI-Based Water Management System project are welcome! If you'd like to contribute, please fork the repository, make your changes, and submit a pull request. Be sure to follow the contribution guidelines and adhere to the code of conduct.

