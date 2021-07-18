from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *
from modules.cards_functions import *
from modules.classes import *
from modules.comments import *

from __main__ import app
from __main__ import turbo

##################### USER APP ROUTES ########################

#
@app.route('/user/<username>', methods=['POST', 'GET'])
@is_logged
def user_page(username):  
    if current_user.username != username:
        return redirect(url_for('home')) 
    form_avatar = Avatar()
    user = db.session.query(
        Comment, Card, User, Media).join(
            User, Comment.id_user == User.id).join(
                Card, Card.id == Comment.id_card).join(
                    Media, User.id == Media.id_user).filter(User.username==username).filter(Comment.title != None).order_by(desc(Comment.id)).limit(3).all()

    if request.method == 'POST':
        try:     
            update_user = User.query.filter(User.id == current_user.id).first()           
            update_user.name = cleanhtml(request.form['name'])
            update_user.lastname = cleanhtml(request.form['lastname'])
            update_user.email = cleanhtml(request.form['email'])
            update_user.phone = cleanhtml(request.form['phone'])    
            update_user.zipcode = cleanhtml(request.form['zipcode'])      
            db.session.commit()
            return redirect(url_for('user_page', username=username))
        except werkzeug.exceptions.BadRequestKeyError:
            new_avatar = form_avatar.file.data.filename  
            media_update = Media.query.filter(Media.id_user == current_user.id).first()
            if new_avatar and media_update:    
                if new_avatar.endswith('.jpg') or new_avatar.endswith('.png'):
                    media_update.path = '/static/img/' + new_avatar
                    media_update.alt = new_avatar
                    media_update.title = new_avatar
                    db.session.commit()
                    message=""
                else:
                    message="L'avatar doit être un .jpg ou .png"
            else:
                message="Sélectionner une image en .jpg ou .png"
            flash(message)

    return render_template('user.html', user=user, form=form_avatar, username=username)

########################### COMMENT ROUTES #######################################

@app.route('/user/card/add_comment/<int:card_id>/<author>', methods=['POST', 'GET'])
@is_logged
def add_comment(card_id, author):
    post_form = PostCard()
    card_name = Card.query.get(card_id)
    if card_name and author == current_user.username:
        if request.method == 'POST' and post_form.validate_on_submit():   
            title = cleanhtml(post_form.title.data)
            content = cleanhtml(post_form.content.data)
            comment_form = [card_id, title, content]
            new = add_comment_db(comment_form)
    return redirect(url_for('card_page', name=card_name.name))

@app.route('/user/card/update_comment/<int:card_id>/<int:comment_id>/<int:author_id>', methods=['POST'])
@is_logged
def update_comment(card_id, comment_id, author_id):
    card = Card.query.get(card_id)
    post_modify_form = PostModifyCard()
    if card:
        if request.method == 'POST' and post_modify_form.validate_on_submit():
            title = cleanhtml(post_modify_form.title.data)
            print(title)
            content = cleanhtml(post_modify_form.content.data)
            update = update_comment_db([card_id, comment_id, author_id, title, content])
    return redirect(url_for('card_page', name=card.name))

@app.route('/user/card/delete_comment/<comment_id>/<author>/<card_id>')
@is_logged
def delete_comment(comment_id, author, card_id):
    card_name = Card.query.get(cleanhtml(card_id))
    if author == current_user.username:
        comment_to_delete = delete_comment_in_db(comment_id)
    return redirect(url_for('card_page', name=card_name.name))

@app.route('/user/card/add_response/<int:comment_id>/<int:author_id>/<int:card_id>', methods=['POST'])
@is_logged
def add_response(comment_id, author_id, card_id):
    card_name = Card.query.get(cleanhtml(card_id))
    response_form = ResponseCard()

    if card_name :
        if request.method == 'POST' and response_form.validate_on_submit():
            content = cleanhtml(response_form.content.data)
            new = add_response_db([comment_id, author_id, card_id, content])
    return redirect(url_for('card_page', name=card_name.name))


@app.route('/user/card/update_response/<int:card_id>/<int:comment_id>/<int:author_id>', methods=['POST'])
@is_logged
def update_response(card_id, comment_id, author_id):
    card = Card.query.get(card_id)
    response_modify_form = ResponseModifyCard()
    if card:
        if request.method == 'POST' and response_modify_form.validate_on_submit():
            content = cleanhtml(response_modify_form.content.data)
            update = update_comment_db([card_id, comment_id, author_id, None, content])
    return redirect(url_for('card_page', name=card.name))