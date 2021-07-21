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