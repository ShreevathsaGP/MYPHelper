from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
import mysql.connector
from passlib.hash import pbkdf2_sha256

# mysql_database --> info
global host, user, passwd, database_name, port
host="myp-1080.cyjehjgg2bmr.us-east-1.rds.amazonaws.com"
database_name = "myp"
user = "admin"
passwd = "dinky2004.aws"
port = 3306

""" VERIFICATION OF USERNAME AND PASSWORD """
def invalid_credentials(form, field):
    # Check password and username
    username_entered = form.username.data
    password_entered = field.data

    # Verify username
    mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database_name, port=port)
    cursor = mydb.cursor()

    cursor.execute("SELECT username, password FROM users")

    username_index = None

    existing_usernames_login = []
    existing_passwords_login = []

    for x in cursor:
        existing_usernames_login.append(str(x[0]))
        existing_passwords_login.append(str(x[1]))
    mydb.close()

    if username_entered in existing_usernames_login:
        username_index = existing_usernames_login.index(username_entered)
    else:
        raise ValidationError(message='Username or password is incorrect!')

    if pbkdf2_sha256.verify(password_entered, existing_passwords_login[username_index]):
        pass
    else:
        raise ValidationError(message='Username or password is incorrect!')
""" VERIFICATION OF USERNAME AND PASSWORD """

""" REGISTRATION FORM """
class RegistrationForm(FlaskForm):
    # Registration Form
    # Works with labels inside the html file
    
    username = StringField('username_label', validators=[InputRequired(message="Username Required"), Length(min=4, max=15, message='Username must be between 4 - 15 characters')])
    password = PasswordField('password_label', validators=[InputRequired(message='Password Required'), Length(min=4, max=25, message='Password must be 4 - 25 characters')])
    confirm_password = PasswordField('confirm_password_label', validators=[InputRequired(message='Password Required'), EqualTo('password', message='Passwords must match!')])

    school = StringField('school_label', validators=[InputRequired(message='School Name Required'), Length(min=4, message='School Name must be more than 4 characters')])
    role = SelectField('ChooseRole', choices = [('Student', 'Student'), ('Mentor', 'Mentor')], default="Student")

    submit_button = SubmitField('Register')

    def validate_username(self, username):
        mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database_name, port=port)
        cursor = mydb.cursor()

        existing_usernames = []

        cursor.execute("SELECT username FROM users")
        for x in cursor:
            existing_usernames.append(str(x[0]))
        
        for existing_username in existing_usernames:
            if existing_username == str(username.data):
                raise ValidationError("Username already exists!")
            else:
                pass
""" REGISTRATION FORM """

""" LOGIN FORM """
class LoginForm(FlaskForm):
    # Login form
    # Works with labels indside the html file

    username = StringField('username_label', validators=[InputRequired(message="Username Required")])
    password = PasswordField('password_label', validators=[InputRequired(message="Please enter password!"), invalid_credentials])
    submit_button = SubmitField('Login')
""" LOGIN FORM """

""" CHAT FORM """
class ChatForm(FlaskForm):
    # Chat form
    # Works with labels inside the html file

    message = StringField('chat_label', validators=[InputRequired(message="Message Cannot Be Empty!")])

""" CHAT FORM """