import os
import json
import flask
from flask import Flask, request, render_template, url_for, redirect, session, make_response
from time import localtime, strftime
import datetime
from datetime import timedelta
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import random

""" -----------------------------------------------------------------"""
""" wt_forms (must be same as what is in file called wtform_fields.py)"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
import mysql.connector
from passlib.hash import pbkdf2_sha256

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
        print(existing_usernames)
        mydb.close()
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
""" wt_forms (must be same as what is in file called wtform_fields.py)"""
""" -----------------------------------------------------------------"""


""" MYSQL """
# mysql_database --> info
global host, user, passwd, database_name, port
host = os.environ.get("host")
database_name = os.environ.get("database_name")
user = os.environ.get("user")
passwd = os.environ.get("db_password")
port = 3306
""" MYSQL """

# Initializing app, secret key, session, and socket
app = Flask(__name__)
app.secret_key = 'z$#GKA4+qK9PRws^UvM*'
app.permanent_session_lifetime = timedelta(days=30)
socketio = SocketIO(app)
ROOMS = ["Maintenance (Admins)", "Physics", "Chemistry", "Biology", "Design", "History", "Geography", "Economics", "Business", "Math Extended", "Math Regular", "English", "Second Languages", "Personal Project"]

CLIENTS = {}
# This clients dictionary will contain all the clients in each room

""" VIEW COUNTER (Measure site activity and visits) + REQUEST HEADERS"""
@app.before_request
def view_counter():
    #""" # When in localhost
    # If the request it not for any files, socketio messages or for the web keep alive bot, then add as page view
    if str(request.url_rule) != '/cron' and str(request.url_rule).find('static') == -1 and str(request.url_rule).find('socket') == -1 and str(request.url_rule).find('?') == -1 and str(request.url_rule) != '/analytics' and str(request.url_rule).find('url_for') == -1: # This last one is to avoid adding page views for parameters

        # Getting request headers
        headers = flask.request.headers
        print("---------- REQUEST HEADERS ----------")
        for header in list(headers):
            print("    {} : {}".format(str(header[0]), str(header[1])))
        print("---------- REQUEST HEADERS ----------")

        try:
            mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database_name, port=port)
            cursor = mydb.cursor()
            date_today = datetime.datetime.now()
            
            # Getting the end of the latest week to compare current date
            cursor.execute("SELECT end, views FROM analytics WHERE id = (SELECT MAX(id) FROM analytics)")
            for x in cursor:
                week_limit = x[0]
                week_views = int(x[1])

            # Getting id from the latest week
            cursor.execute("SELECT id FROM analytics WHERE end = '{}'".format(week_limit))
            for x in cursor:
                week_limit_id = x[0]

            # Adding the views to the right place
            if date_today < week_limit:
                week_views += 1
                try:
                    cursor.execute("UPDATE analytics SET views = {} WHERE id = {}".format(week_views, week_limit_id))
                    mydb.commit()
                except:
                    print("\n\n    UPDATE Page View Problem at --> {}".format(datetime.datetime.now()))
            else:
                try:
                    cursor.execute("INSERT INTO analytics (views, start, end) VALUES (1, '{}', '{}')".format(date_today.date(), date_today.date() + timedelta(days=7)))
                    mydb.commit()
                except:
                    print("\n\n    INSERT Page View Problem at --> {}".format(datetime.datetime.now()))
        except:
            print("\n\n    PAGE VIEW FAILED AT --> {}".format(datetime.datetime.now()))
        
        mydb.close()
    #"""
""" VIEW COUNTER (Measure site activity and visits) + REQUEST HEADERS"""

""" ANALYTICS PAGE """
@app.route('/analytics')
def analytics():
    if 'user' in session:
        if session['role'] == 'Admin':
            mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database_name, port=port)
            cursor = mydb.cursor()

            username = "{} ({}) ".format(session['user'], session['role'])
            login_status = 'Log Out'
            href = "{{url_for('logout')}}"

            # Page views
            view_data = {}
            cursor.execute("SELECT start, end, views from analytics")
            for x in list(cursor):
                view_data["{} ----> {}".format(str(x[0].date()), str(x[1].date()))] = int(x[2])
            
            # User information
            users_data = {}
            cursor.execute("SELECT id, username from users")
            for x in list(cursor):
                if len(str(x[0])) > 1:
                    users_data[int(str(x[0])[:-1])+1] = str(x[1])
                else:
                    users_data[x[0]] = str(x[1])
            mydb.close()
            #print(users_data)

            return render_template('analytics.html', username=username, href=href, login_status=login_status, view_dict=view_data, users_dict=users_data, view_graph_dict=json.dumps(view_data))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

""" ANALYTICS PAGE """


@app.route('/')
def index():
    """ When on localhost, to prevent SSL mysql problem
    session['user'] = 'Placeholder'
    session['role'] = 'Placeholder'
    session['school'] = 'Placeholder'
    #"""
    name_display = random.choice(["Shreevathsa & Akhil", "Akhil & Shreevathsa"])

    if 'user' in session:
        username = "{} ({}) ".format(session['user'], session['role'])
        
        #username='' # When running on localhost
        login_status = 'Log Out'
        href = "{{url_for('logout')}}"
        return render_template('index.html', username=username, href=href, login_status=login_status, by_statement=name_display)
    else:
        username = " "
        login_status = 'Log In'
        href = "{{url_for('login')}}"
        return render_template('index.html', username=username, href=href, login_status=login_status, by_statement=name_display)


""" CORE PROJECTS & NON-ESSENTIAL SUBJECTS """
@app.route('/IDU')
def IDU():
    return render_template('IDU.html', Subject='Inter Disciplinary Unit')


@app.route('/E-Portfolio')
def EPortfolio():
    return render_template('eportfolio.html', Subject='E-Portfolio')


@app.route('/Personal_Project')
def PersonalProject():
    #questions = [("Current prime minister of india?", ["modi", "bsy", "akhil", "shree"], "modi"), ('When did partition happen? (year)', ['1947', '1847', '2020', 'yesterday'], '1947')]
    return render_template('personalproject.html', Subject='Personal Project')
""" CORE PROJECTS & NON-ESSENTIAL SUBJECTS """

""" CORE SUBJECTS """
@app.route('/Math')
def Math():
    return render_template('math.html', Subject='Math')

@app.route('/English')
def English():
    return render_template('english.html', Subject='English')

@app.route('/Sciences')
def Sciences():
    return render_template('science.html', Subject='Sciences')

@app.route('/Humanities')
def Humanities():
    return render_template('i&s.html', Subject='I&S')

# Branches into Economics and Business Management
@app.route('/Special')
def Special():
    return redirect(url_for('index'))
# Branches into Economics and Business Management

@app.route('/about_us')
def about_us():
    return render_template('aboutus.html')
""" CORE SUBJECTS """


""" PAGE NOT FOUND """
@app.route('/<random>')
def error(random):
    return redirect('/')
   #return redirect('page_not_found.html')
""" PAGE NOT FOUND """
   
""" CRON """
@app.route('/cron')
def cron():
    return render_template("cron.html")
""" CRON """

""" QUIZ """
# Whenever you want to render different questions for quizzes coming from different pages, you need to set the href as:
# href="{{url_for('quiz', quiz_data = ('question', ['choice-1', 'choice-2', 'choice-3', 'choice-4'], 'answer') )}}"
# Depending on number of questions, put the tuples into a list and then index in the quiz file
# Use JSON in this manner to load lists/tuples:
#     Python file: json.dumps(list_upload_variable)
#     HTML file: JSON.parse({{list_recieve_variable|tojson|safe}})

@app.route('/quiz/<string:quiz_data>')
def quiz(quiz_data):
    return render_template('quiz.html', data=quiz_data)
""" QUIZ """

""" REGISTER """
@app.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database_name, port=port)
        cursor = mydb.cursor()

        username = registration_form.username.data
        password = registration_form.password.data

        school = registration_form.school.data
        role = registration_form.role.data

        hashed_password = pbkdf2_sha256.hash(password)

        new_user = ("INSERT INTO users (username, password, school, role) VALUES (%s, %s, %s, %s)")
        
        # Registering new user
        cursor.execute(new_user, [username, hashed_password, school, role])
        mydb.commit()
        mydb.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=registration_form)
""" REGISTER """

""" LOGIN """
@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'user' not in session:
        login_form = LoginForm()

        if login_form.validate_on_submit():
            username = login_form.username.data
            
            mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database_name, port=port)
            cursor = mydb.cursor()
            cursor.execute("SELECT school FROM users WHERE username = '{}'".format(username))
            for x in cursor:
                school = x[0]

            cursor.execute("SELECT role FROM users WHERE username = '{}'".format(username))
            for x in cursor:
                role = x[0]

            mydb.close()
            # validating the permanent session (lasts for a couple weeks)
            session.permanent = True

            # Adding the user's username and school to the session
            session['user'] = username
            session['school'] = school
            session['role'] = role # This must be either MENTOR or STUDENT

            return redirect(url_for('index'))

        return render_template('login.html', form=login_form)
    else:
        return redirect(url_for('index'))
""" LOGIN """

"""  LOGOUT """
@app.route('/logout')
def logout():
    session.pop('user')
    session.pop('school')
    session.pop('role')

    return redirect(url_for('index'))
"""  LOGOUT """

""" CHAT """
@app.route('/chat')
def redirect_chat():
    return redirect(url_for('chat_index'))

@app.route('/chat_index')
def chat_index():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        pass
    return render_template('chat_index.html', available_rooms = ROOMS)

@app.route('/chat/<room>')
def chat(room):
    url = str(request.url)
    status = str(request.args.get('status'))
    
    if status != 'factored':
        final_url = url + "?status=factored"
        #print("Redirect to --> {}".format(final_url))
        return redirect(url.replace('https', 'http') + "?status=factored")
    else:
        pass

    if room not in ROOMS:
        print(room)
        return redirect(url_for('chat_index'))
    else:
        global room_index
        room_index = ROOMS.index(room)
        
        if 'user' not in session:
            return redirect(url_for('login'))
        else:
            if room == ROOMS[0]:
                if session['role'] != 'Admin':
                    return redirect(url_for('chat_index'))
                else:
                    pass
            else:
                pass
            return render_template('chat.html', username=str(session['user']), room_name=room)

@socketio.on('message')
def message(data):
    send(data, room=data['room'])

@socketio.on('join')
def join(data):
    room_reference = data['room']

    if room_reference == ROOMS[0]:
        if session['role'] != 'Admin':
            return redirect(url_for('chat_index'))
        else:
            pass
    else:
        pass

    join_room(data['room'])

    username_reference = data['username']

    # Clients being addded
    if room_reference in list(CLIENTS.keys()):
        # If username is already in the room, there is nothing to do, flask sucks
        if username_reference in CLIENTS[room_reference]:
            print("\n\n    Connection error with {} in {} (possible double connection)!\n\n".format(username_reference, room_reference))
            pass
        else:
            CLIENTS[room_reference].append(username_reference)
    else:
        CLIENTS[room_reference] = []

        # If username is already in the room, there is nothing to do, flask sucks
        if username_reference in CLIENTS[room_reference]:
            print("\n\n    Connection error with {} in {} (possible double connection)!\n\n".format(username_reference, room_reference))
            pass
        else:
            CLIENTS[room_reference].append(username_reference)

    emit('user-update', CLIENTS, room=data['room'])

    send({'username':'ChatModerator', 'msg':data['username'] + " has joined the " + data['room'] + " room!"}, room = data['room'])

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    
    room_reference = data['room']
    username_reference = data['username']

    # Clients being deleted
    if username_reference in list(CLIENTS[room_reference]):
        remove_index = list(CLIENTS[room_reference]).index(username_reference)
        CLIENTS[room_reference].pop(remove_index)
    else:
        print("\n\n    Error occured with removing {} from {}.\n".format(username_reference, room_reference))
    emit('user-update', CLIENTS, room=data['room'])
    send({'username':'ChatModerator', 'msg':data['username'] + " has left the " + data['room'] + " room!"}, room = data['room'])

""" CHAT """

""" SITEMAP """

@app.route('/sitemap')
def actual_sitemap():
    template = render_template('sitemap.xml')
    response = make_response(template)
    response.headers['Content-type'] = 'application/xml'

    return response

""" SITEMAP """


""" RUNNING APP """
if __name__ == '__main__':
    #socketio.run(app, debug=True)
    app.run(debug=True)
""" RUNNING APP """
