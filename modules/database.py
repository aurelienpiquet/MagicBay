from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
import sqlalchemy.exc
from flask_login import UserMixin, login_manager, login_user, LoginManager, login_required, current_user, logout_user
from __main__ import app
import os

CUR_dir = os.path.dirname(os.path.abspath(__file__))

db=SQLAlchemy(app)

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False, unique=True)
    search = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, nullable=False)
    ccm = db.Column(db.String, nullable=True)

    def as_dict(self):
        return {'name' : self.name}

class Card_Rating(db.Model):
    __tablename__ = 'card_rating'
    id_card = db.Column(db.Integer, ForeignKey('card.id'), primary_key=True, nullable=True)
    id_Rating = db.Column(db.Integer, ForeignKey('rating.id'), primary_key=True, nullable=True)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(50), nullable=False)
    post_id = db.Column(db.Integer, nullable=True)
    id_user = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    id_card = db.Column(db.Integer, ForeignKey('card.id'), nullable=True)

class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    content = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    notification = db.Column(db.Integer, nullable=True)
    post_id = db.Column(db.Integer, nullable=True)
    receiver = db.Column(db.Text, nullable=True)
    author = db.Column(db.Text, nullable=True)
    receiver_id = db.Column(db.Integer, nullable=True)
    id_info = db.Column(db.Integer, ForeignKey('info.id'), nullable=True)
    id_user = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)

class DeckBuilder(db.Model):
    __tablename__ = 'deckbuilder'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    id_type = db.Column(db.Integer, ForeignKey('type.id'), nullable=True)
    id_user = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)

    #cards = relationship('Card', secondary='deckbuilder_card')

class DeckBuilder_Card(db.Model):
    __tablename__ = 'deckbuilder_card'
    nb = db.Column(db.Integer, nullable=False)
    id_card = db.Column(db.Integer, ForeignKey('card.id'), primary_key=True, nullable=True)
    id_deckbuilder = db.Column(db.Integer, ForeignKey('deckbuilder.id'), primary_key=True, nullable=True)
    id_info = db.Column(db.Integer, ForeignKey('info.id'), primary_key=True, nullable=True)

class Info(db.Model):
    __tablename__ = 'info'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    edition = db.Column(db.String(255), nullable=True)
    language = db.Column(db.String(255), nullable=True)
    quality = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(db.String(255), nullable=True)
    legality = db.Column(db.String(255), nullable=True)
    rarity = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=True)
    id_card = db.Column(db.Integer, ForeignKey('card.id'), nullable=True)


class Media(db.Model):
    __tablename__ = 'media'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    path = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    alt = db.Column(db.String(255), nullable=False)
    id_user = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    id_card = db.Column(db.Integer, ForeignKey('card.id'), nullable=True)
    id_deckbuilder = db.Column(db.Integer, ForeignKey('deckbuilder.id'), nullable=True)

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    date = db.Column(db.DateTime(255), nullable=True)
    id_user = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    id_card = db.Column(db.Integer, ForeignKey('card.id'), nullable=True)
    #cards = relationship('Card', secondary='card_rating')

class Rulling(db.Model):
    __tablename__ = 'rulling'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    rule = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=True)
    id_card = db.Column(db.Integer, ForeignKey('card.id'), nullable=True)

class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(255), nullable=False)

class Type(db.Model):
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    type = db.Column(db.String(255), nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    lastname = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)
    zipcode = db.Column(db.Integer, nullable=True)
    id_status = db.Column(db.Integer, ForeignKey('status.id'), nullable=True) 

if not os.path.exists(os.path.join(CUR_dir, "database.db")):
    db.create_all() 
