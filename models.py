from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"

    username = db.Column(db.String(20), nullable=False, unique=True, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"{self.username} {self.password} {self.email} {self.first_name} {self.last_name}"

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register user w/hashed password & return user."""
        bcryptt = Bcrypt()
        hashed = bcryptt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        """Register user w/hashed password & return user."""
        u = User.query.filter_by(username=username).first()
        bcrypttt = Bcrypt()
        if u and bcrypttt.check_password_hash(u.password, password):
            return u
        else:
            return False


class Feedback(db.Model):
    """Feedback"""
    __tablename__ = "feedback"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'))
    user = db.relationship('User', backref='feedback')
