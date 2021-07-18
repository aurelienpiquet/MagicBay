from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *


from __main__ import app

def get_comment_user_media():
    try: 
        datas = db.session.query(Comment, User, Media).join(User, Comment.id_user == User.id).join(
                    Media, User.id == Media.id_user).order_by(desc(Comment.date))
        return datas
    except sqlalchemy.exc.StatementError:
        return False

def get_user_avatar():
    try: 
        avatar = db.session.query(User, Media).join(Media, User.id == Media.id_user).filter(Media.id_user == current_user.id).first()
        return avatar[1].path

    except sqlalchemy.exc.StatementError:
        return '../static/img/avatar.png'