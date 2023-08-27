from app import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    pin = Column(String(60), nullable=False)
    photo = Column(String(500), nullable=False)
    token = Column(String(500), nullable=True)

    def __init__(self, name, email, phone, pin, photo):
        self.name = name
        self.email = email
        self.phone = phone
        self.pin = generate_password_hash(pin)
        self.photo = photo
        self.token = None


db.create_all()