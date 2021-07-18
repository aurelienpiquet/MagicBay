from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *
from modules.cards_functions import *
from modules.classes import *

from __main__ import app
from __main__ import turbo


@app.route('/user/<username>/message')
@is_logged
def message_page(username):

    messages = Contact.query.filter((Contact.id_user == current_user.id) | (Contact.receiver_id == current_user.id)).order_by(desc(Contact.date)).order_by(desc(Contact.id)).all()
    return render_template('messenger.html', username=current_user.username, messages=messages)
     

@app.route('/user/<username>/message/<receiver>/<card>/<info>', methods=['POST'])
@is_logged
def send_message(username, receiver, card, info):
    if request.method == 'POST': 
        user_receiver = UserClass()
        user_receiver.getId(receiver)
        card_info = Info.query.filter_by(id=int(info)).first()
        if card_info :
            content = f"L'utilisateur {username} est intéressé par votre carte {card} : Edition : {card_info.edition} -- Qualité : {card_info.quality} -- Langue : {card_info.language} -- Prix : {card_info.price}"
            message = Message(receiver = user_receiver, content = content)
            new_message = message.sendMessage(id_info=card_info.id)
            if new_message :
                flash(f"Votre message a bien été envoyé à l'utilisateur {user_receiver}.", "succès")
            else:
                flash("Un problème est survenu pendant l'envoi de votre message.", "erreur")
    return redirect(url_for('buy_list_page', username=current_user.username))


@app.route('/user/<username>/message/<receiver>/<int:message_id>', methods=['POST', 'GET'])
@is_logged
def chat_page(username, receiver, message_id):
    chat_form = ChatMessage()
    if request.method == 'POST' and chat_form.validate_on_submit():
        #message = request.form['message']
        message = cleanhtml(chat_form.message.data)
        new_receiver = UserClass()
        new_receiver.getId(receiver)
        new_message = Message(content = message, receiver = new_receiver)
        new_message.sendMessage(post_id = message_id)
        
        if turbo.can_stream():
            message = Contact.query.filter(Contact.post_id == message_id).order_by(desc(Contact.date)).first()
            return turbo.stream([
                   turbo.append(
                       render_template('_message.html', message=message, now=datetime.datetime.now()), target='message-chat'),
                   ])

    messages = Contact.query.filter(Contact.post_id == message_id).order_by((Contact.date)).all()
    #max_id_messages = db.session.query(func.max(Contact.id)).filter(Contact.post_id == message_id).all()
    #print(max_id_messages)
    for message in messages :
        #print(message.id)
        if message.receiver == current_user.username:
            new_message = Message(message.id) 
            new_message.setNotification()

    return render_template('chat.html', chat_form=chat_form, username=username, receiver=receiver, messages=messages, now=datetime.datetime.now())

@app.route('/user/chat_delete/<int:post_id>')
@is_logged
def chat_delete_page(post_id):
    message = Message(id = int(post_id))
    if message.deleteMessage() == True:
        return redirect(url_for('home'))
    else :
        return 'ok'