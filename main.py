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


class Result(db.Model):

    __tablename__ = 'results'

    user_id = db.Column(db.String, primary_key=True)
    origin = db.Column(db.String, primary_key=True)
    dest = db.Column(db.String, primary_key=True)
    mode = db.Column(db.String, primary_key=True)
    weight = db.Column(db.String, primary_key=True)
    pre = db.Column(db.Float)
    on = db.Column(db.Float)
    total = db.Column(db.Float)
    percentage = db.Column(db.Integer, primary_key=True)
    original_rate = db.Column(db.Integer)
    rate_per_kg = db.Column(db.Integer)

    def __init__(self, user_id, origin, dest, weight, pre, on, total, percentage, mode, original_rate, rate_per_kg):
        self.user_id = user_id
        self.origin = origin
        self.dest = dest
        self.weight = weight
        self.pre = pre
        self.on = on
        self.total = total
        self.percentage = percentage
        self.mode = mode
        self.original_rate = original_rate
        self.rate_per_kg = rate_per_kg
        self.id = self.__dict__

    def __repr__(self):
        return '<id {}>'.format(self.id)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('info.html', message='Unauthorized', display='Go to Login')


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

    return render_template('info.html', message='bad log in', display='Go to Login')


@app.route('/logout')
@flask_login.login_required
def logout():
    user = flask_login.current_user
    session['authenticated'] = False
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    flask_login.logout_user()
    return render_template('info.html', message='successfully log out', display='Go to Log in')


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
        modes = ['Sea Freight', 'Air Freight']
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
                'pre': round(pre_charge[0], 2),
                'on': round(on_charge, 2),
                'total': round(pre_charge[0] + on_charge * 0.27, 2)  # converting AED to USD
        }

        user_id = flask_login.current_user.get_id()
        rate.update(data)
        rate.update({'user_id': user_id})
        rate.update({'original_rate': round(pre_charge[1], 2), 'rate_per_kg': round(pre_charge[2], 2)})
        result = Result(**rate)

        db.session.merge(result)
        db.session.commit()

        return render_template('output.html', data=data, rate=rate)


@app.route('/history', methods=['GET', 'POST'])
@flask_login.login_required
def history():
    if request.method == 'GET':
        current_user = flask_login.current_user.get_id()
        entries = db.session.query(Result).filter(Result.user_id == current_user)
        return render_template('table.html', entries=entries)

    if request.method == 'POST':
        current_user = flask_login.current_user.get_id()
        Result.query.filter(Result.user_id == current_user).delete()
        db.session.commit()
        return render_template('info.html', message='cleared all the history', display='Home')


@app.route('/precalc')
@flask_login.login_required
def pre_calc():
    if request.method == 'GET':
        entries = db.session.query(Result).filter(Result.user_id == 'precalc')
        return render_template('table.html', entries=entries)


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080, debug=True)
