from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *

from modules.admin_cards import add_card_to_db, update_card_in_db, delete_card_in_db

from __main__ import app

class Message():
    def __init__(self, id = None, content = None, receiver = None):
        self.id = id
        self.content = content
        self.author = current_user
        self.receiver = receiver
        self.notification = 0

    def setNotification(self):
        self.notification = not self.notification
        message_to_update = Contact.query.get(self.id)
        message_to_update.notification = self.notification
        db.session.commit()
        return self

    def readMessage(self):
        if self.id != 0 and self.id.isdigit():
            self = Contact.query.get(self.id)
            self.notification = 1
            db.session.commit()
        return self

    def sendMessage(self, post_id = None, id_info = None):
        new_message = Contact(content = self.content, 
                              date=datetime.datetime.now(), 
                              notification = self.notification,
                              post_id = post_id, 
                              author = self.author.username,
                              receiver_id = self.receiver.id,
                              receiver = self.receiver.username, 
                              id_user = self.author.id,
                              id_info = id_info)
        try:
            db.session.add(new_message)
            db.session.commit()
            if new_message.post_id == None :
                new_message.post_id = new_message.id
                db.session.commit()
            self.id = new_message.id
            return True
        except sqlalchemy.exc.StatementError:
            return False

    def deleteMessage(self):
        message_to_delete = Contact.query.get(self.id)
        if message_to_delete.id == message_to_delete.post_id:
            messages = Contact.query.filter(Contact.post_id == message_to_delete.id).all()
            
            for message in messages:
                print(message.id, message.post_id)
                db.session.delete(message)
            db.session.commit()
            return True
        else :
            db.session.delete(message_to_delete)
            db.session.commit()
            return False

    def __repr__(self):
        return f"Message author : {self.author.username} - Message receiver : {self.receiver.username} - Message content : {self.content}"
        
class UserClass():
    def __init__(self):
        self.id = ""
        self.username = ""


    def getId(self, username):
        user = User.query.filter_by(username=username).first()
        self.id = user.id
        self.username = user.username
        return self.id

    def getUsername(self, id):
        user = User.query.get(id).first()
        self.username = user.username
        self.id = user.id
        return self.username
