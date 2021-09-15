from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *


def add_comment_db(form: list) -> bool:
    new_comment = Comment(title = form[1],
                         content = form[2],
                         date = datetime.datetime.now(),
                         id_user = current_user.id, 
                         id_card = form[0]
                         ) 
    db.session.add(new_comment)
    db.session.commit()
    try:
        new_comment_id = db.session.query(Comment).filter(Comment.post_id == None ).order_by(desc(Comment.id)).first()
        new_comment_id.post_id = new_comment_id.id
        db.session.commit()
        return True
    except sqlalchemy.exc.SQLAlchemyError:
        return False

def add_response_db(form: list) -> bool:
    try:
        new_comment = Comment(title = None,
                             content = form[3],
                             date = datetime.datetime.now(),
                             id_user = form[1],   
                             id_card = form[2],
                             post_id = form[0]) #a modifier pb dans djinja 
        db.session.add(new_comment)
        db.session.commit()
        return True
    except sqlalchemy.exc.SQLAlchemyError:
        return False

def update_comment_db(form : list) -> bool:
    #([card_id, comment_id, author, title, content])
    print(form)
    comment_to_update = Comment.query.filter_by(id=form[1]).first()         
    try:
        if len(form) == 5 and comment_to_update.id_user == int(form[2]) and comment_to_update.id_card == int(form[0]):
            comment_to_update.content = form[4]
            comment_to_update.title = form[3]
            comment_to_update.date = datetime.datetime.now()
        db.session.commit()
    #print(comment_to_update, comment_to_update.id_user, comment_to_update.id_card) 
        return True
    except sqlalchemy.exc.SQLAlchemyError:
        return False

def delete_comment_in_db(id: int) -> bool:
    try:
        card_to_delete = Comment.query.get(id)
        sousposts = Comment.query.filter_by(post_id=id)
        for souspost in sousposts :
            db.session.delete(souspost)
        db.session.delete(card_to_delete)
        db.session.commit()
        return True
    except sqlalchemy.exc.StatementError:
        return False