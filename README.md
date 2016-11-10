to add new user

from main import db

db.create_all()

from main import User, bcrypt

pw1 = bcrypt.generate_password_has('1234')
user1 = User('username', pw1)

db.session.add(user1)
db.session.commit()

to use google cloud SQL in google app engine enable Google Cloud SQL API and create key for app engine
