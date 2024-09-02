from flask_sqlalchemy import SQLAlchemy


auth_db = SQLAlchemy()
class User(auth_db.Model):
    __tablename__ = 'user'
    id = auth_db.Column(auth_db.Integer, primary_key=True)
    forename = auth_db.Column(auth_db.String(256), unique=False, nullable=False)
    surname = auth_db.Column(auth_db.String(256), unique=False, nullable=False)
    email = auth_db.Column(auth_db.String(256), unique=True, nullable=False)
    password = auth_db.Column(auth_db.String(256), nullable=False)
    role = auth_db.Column(auth_db.ForeignKey('role.id'), nullable=False)

    user_role = auth_db.relationship('Role', back_populates='users')

class Role(auth_db.Model):
    __tablename__ = 'role'
    id = auth_db.Column(auth_db.Integer, primary_key=True)
    name = auth_db.Column(auth_db.String(16), unique=True, nullable=False)

    users = auth_db.relationship('User', back_populates='user_role')