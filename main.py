from flask import Flask
from flask import request, redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

import flask_login


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
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    pw = request.form['pw']
    user = User.query.get(username)

    if user:
        if bcrypt.check_password_hash(user.password, pw):
            flask_login.login_user(user)
            return redirect(url_for('rate_card'))

    return render_template('info.html', message='bad log in')


@app.route('/logout')
@flask_login.login_required
def logout():
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
        origin = request.form['origin']
        weight = int(request.form['weight'])

        data = request.form.to_dict()

        if origin == 'Tennesse & Pennysylvania':
            pre_charge = tennesse_pennysylvania(weight)
            on_charge = dubai(weight)

        elif origin == 'Hong Kong City':
            pre_charge = hong_kong(weight)
            on_charge = dubai(weight)

        elif origin == 'London City':
            pre_charge = london(weight)
            on_charge = dubai(weight)

        elif origin == 'New York City':
            pre_charge = new_york(weight)
            on_charge = dubai(weight)

        elif 'United Kingdom' in origin:
            area = origin[-1]
            pre_charge = uk(weight, area)
            on_charge = dubai(weight)

        rate = {
                'pre': pre_charge,
                'on': on_charge,
                'total': pre_charge + on_charge * 0.27  # converting AEd to USD
        }

        return render_template('output.html', data=data, rate=rate)


def tennesse_pennysylvania(weight):
    rates = {100: 1.65, 300: 1.60}  # USD
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    fsc = weight * 0.85
    sec = weight * 0.17

    pick_up = max(35, weight * 0.35)
    transfer = max(20, weight * 0.12)
    export_formalities = 75

    total = weight * rate + fsc + sec + pick_up + transfer + export_formalities

    return total


def hong_kong(weight):
    rates = {300: 1.79}  # USD
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    airline_handling = 35
    terminal_handling = weight * 0.23
    cartage = weight * 0.10
    pick_up = max(45, weight * 0.10)

    total = weight * rate + airline_handling + terminal_handling + cartage + pick_up

    return total


def london(weight):
    rates = {300: 1.30}  # USD
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    pick_up = (25 + weight * 0.15) * 1.23  # converting GBP to USD

    total = weight * rate + pick_up

    return total


def uk(weight, area):
    rates = {45: 1.65, 100: 1.40, 300: 1.30, 500: 1.15, 1000: 1.10}  # GBP
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    if area == '1':
        pick_up = 25 + weight * 0.10
    if area == '2':
        pick_up = 25 + weight * 0.15
    if area == '3':
        pick_up = 25 + weight * 0.20
    if area == '4':
        pick_up = 30 + weight * 0.30
    if area == '5':
        pick_up = 30 + weight * 0.35

    final_rate = max(60, weight * rate)
    total = (final_rate + pick_up) * 1.23  # converting GBP to USD

    return total


def new_york(weight):
    rates = {300: 2.75}  # AED
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    total = weight * rate

    return total


# all values in AED
def dubai(weight):
    custom_clearance = 200
    delivery_order = 300
    transportation = max(150, weight * 0.30 if weight <= 3000 else weight * 0.20)
    airline_handling = max(90, weight * 0.30)
    custom_bill = 110
    cargo_transfer = 120
    total = custom_clearance + delivery_order + transportation + airline_handling + custom_bill + cargo_transfer

    return total  # AED


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080, debug=True)
