from flask import Flask
from flask import request, redirect, url_for, session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

import flask_login

import rate_calculator as rc

app = Flask(__name__)
app.secret_key = 'qwdghky12346h'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):

    __tablename__ = 'user'

    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     if email not in users:
#         return
#
#     user = User()
#     user.id = email
#
#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     user.is_authenticated = request.form['pw'] == users[email]['pw']
#
#     return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('info.html', message='Unauthorized')


@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('authenticated'):
        return redirect(url_for('rate_card'))

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    pw = request.form['pw']
    user = User.query.get(username)

    if user:
        if bcrypt.check_password_hash(user.password, pw):
            session['authenticated'] = True
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            flask_login.login_user(user)
            return redirect(url_for('rate_card'))

    return render_template('info.html', message='bad log in')


@app.route('/logout')
@flask_login.login_required
def logout():
    user = flask_login.current_user
    session['authenticated'] = False
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    flask_login.logout_user()
    return render_template('info.html', message='successfully log out')


@app.route('/rate-card', methods=['GET', 'POST'])
@flask_login.login_required
def rate_card():
    if request.method == 'GET':
        origins = ['Tennesse & Pennysylvania',
                   'Hong Kong City',
                   'London City',
                   'New York City',
                   'United Kingdom Area 1',
                   'United Kingdom Area 2',
                   'United Kingdom Area 3',
                   'United Kingdom Area 4',
                   'United Kingdom Area 5',
                   ]
        dests = ['Dubai']
        modes = ['airfreight', 'seafreight']
        return render_template('main.html', origins=origins, dests=dests, modes=modes)

    if request.method == 'POST':
        origin = request.form.get('origin')
        weight = request.form.get('weight', type=int)
        percentage = request.form.get('percentage', type=int)

        data = request.form.to_dict()

        if origin == 'Tennesse & Pennysylvania':
            pre_charge = rc.tennesse_pennysylvania(weight, percentage)
            on_charge = rc.dubai(weight)

        elif origin == 'Hong Kong City':
            pre_charge = rc.hong_kong(weight, percentage)
            on_charge = rc.dubai(weight)

        elif origin == 'London City':
            pre_charge = rc.london(weight, percentage)
            on_charge = rc.dubai(weight)

        elif origin == 'New York City':
            pre_charge = rc.new_york(weight, percentage)
            on_charge = rc.dubai(weight)

        elif 'United Kingdom' in origin:
            area = origin[-1]
            pre_charge = rc.uk(weight, area, percentage)
            on_charge = rc.dubai(weight)

        rate = {
                'pre': pre_charge,
                'on': on_charge,
                'total': pre_charge + on_charge * 0.27  # converting AED to USD
        }

        return render_template('output.html', data=data, rate=rate)


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080, debug=True)
