from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = "users"

    #use this code below to be able to view things better in ipython
    # def __repr__(self):
    #     p = self
    #     return f"name={p.name} email={p.email}>"

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), primary_key=True, nullable=False, unique=True)

    password = db.Column(db.String(100), nullable=False)

    @classmethod
    def register(cls, name, email, password):
        """" Register user with hashed password"""
        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode("utf8")

        return cls(name=name, email=email, password=hashed_utf8)

    @classmethod
    def authenticate(cls, email, password):
        u = User.query.filter_by(email=email).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

class Watchlist(db.Model):
    __tablename__= "watchlist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.Column(db.String(50), nullable=False)
    email_id = db.Column(db.Text, db.ForeignKey('users.email'))

    user = db.relationship('User', backref='watchlist')

