from sqlalchemy.sql.expression import update
from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *
from modules.cards_functions import *
from modules.classes import *
from modules.comments import *
from modules.upload import upload_in_db

from __main__ import app
from __main__ import turbo

@app.route('/user/<username>')
@is_logged
def user_page(username):  
    if current_user.username != username:
        return redirect(url_for('home')) 
    form_avatar = Avatar()
    form_profil = DataProfil()

    comments = db.session.query(
        Comment, Card, User, Media).join(
            User, Comment.id_user == User.id).join(
                Card, Card.id == Comment.id_card).join(
                    Media, User.id == Media.id_user).filter(User.username==username).filter(Comment.title != None).order_by(desc(Comment.id)).limit(3).all()
    
    user = db.session.query(User, Media).join(Media, Media.id_user == User.id).filter(User.username==username).first()

    return render_template('user/user.html', comments=comments, user=user, form_avatar=form_avatar, username=username, form_profil=form_profil)

@app.route('/user/<username>/update/avatar', methods=['POST'])
def user_update_avatar_page(username):
    form_avatar = Avatar()
    if request.method == 'POST' and form_avatar.validate_on_submit():
        new_avatar = form_avatar.file.data.filename  
        media_update = Media.query.filter(Media.id_user == current_user.id).first()
        if new_avatar and media_update:   
            avatar_upload = upload_in_db(form_avatar.file.data, app.config['UPLOAD_AVATAR_PATH'], str(current_user.username) + "_") 
            if avatar_upload:
                media_update.path = f"/static/img/avatar/{username}_" + new_avatar
                media_update.alt = new_avatar
                media_update.title = new_avatar
                db.session.commit()
                flash('Votre avatar a bien été mise à jour.', "succès")
    return redirect(url_for('user_page', username=username))

@app.route('/user/<username>/update/profile', methods=['POST', 'GET'])
@is_logged
def user_update_profil_page(username):
    form_profil = DataProfil()
    update_user = User.query.filter(User.id == current_user.id).first()
    if update_user: 
        form_profil.name.render_kw['placeholder'] = update_user.name
        form_profil.lastname.render_kw['placeholder'] = update_user.lastname
        form_profil.email.render_kw['placeholder'] = update_user.email
        form_profil.phone.render_kw['placeholder'] = update_user.phone
        form_profil.zipcode.render_kw['placeholder'] = update_user.zipcode

        if request.method == 'POST' and form_profil.validate_on_submit() and current_user.username == username:      
            update_user.name = cleanhtml(form_profil.name.data)
            update_user.lastname = cleanhtml(form_profil.lastname.data)
            update_user.email = cleanhtml(form_profil.email.data)
            update_user.phone = cleanhtml(form_profil.phone.data)    
            update_user.zipcode = cleanhtml(form_profil.zipcode.data)   
            db.session.commit()
            flash('Votre profil a bien été mise à jour.',"succès")
            return redirect(url_for('user_page', username=username))      
    return render_template('user/profil_form.html', username=username, form_profil=form_profil)

