from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *

from modules.admin_cards import add_card_to_db, update_card_in_db, delete_card_in_db

from __main__ import app

@app.route('/admin')
@is_admin
def admin_page():
    nb = db.session.query(Card).count()
    limit = 10

    page = request.args.get('page', 1, type=int) if request.args.get('page', 1, type=int) <  round(nb/limit) + 1 else round(nb/limit)
    if page == 0 :
        page = 1
    
    cards = db.session.query(Card, Info).join(Info, Info.id_card == Card.id).order_by(Card.name).paginate(page=page, per_page=limit)
    all_users = db.session.query(User, Status).join(Status, User.id_status == Status.id).all()
    return render_template('admin.html', page = page, cards = cards, users = all_users[1:], username=current_user.username)


@app.route('/admin/card/<name>/add_rulling', methods=['POST'])
@is_admin
def add_rulling(name):
    rulling_form = RullingCard()
    card = Card.query.filter_by(name=name).first()
    if card:
        if request.method == 'POST' and rulling_form.validate_on_submit():
            rulling_form = cleanhtml(rulling_form.rulling.data)
            date = datetime.datetime.now()
            new_rulling = Rulling(rule=rulling_form, date=date, id_card=card.id)
            db.session.add(new_rulling)
            db.session.commit()
    return redirect(url_for('card_page', name=name))


@app.route('/admin/card/<name>/delete_rulling/<id>', methods=['POST'])
@is_admin
def delete_rulling(name,id):
    if request.method == 'POST':
        try :
           rulling_to_delete = Rulling.query.filter_by(id=id).first()
           db.session.delete(rulling_to_delete)
           db.session.commit()
           return redirect(url_for('card_page', name=name))
        except sqlalchemy.exc.SQLAlchemyError:
            return redirect(url_for('home'))

@app.route('/admin/card/add', methods=['GET','POST'])
@is_admin
def add_page():
    form = AddCard()   
    if request.method == 'POST' and form.validate_on_submit(): 
        add_card = [cleanhtml(form.data[key]) for key in form.data.keys()]
        card_add = [add_card[0], add_card[1] , add_card[2], add_card[3], add_card[4], add_card[5], add_card[6].filename, add_card[7], add_card[8]]
        new_card = add_card_to_db(card_add)
        
        if new_card:
            flash(f"{card_add[0]} a bien été ajoutée.", "succès") 
        else:
            flash(f"Un problème est survenu pendant l'ajoût de <{card_add[0]}>.", "erreur")
        return redirect(url_for('admin_page')) 
         
    return render_template('add.html', username=current_user.username, form=form) 

@app.route('/admin/card/update/<id>', methods=['GET','POST'])
@is_admin
def update_page(id):    
       
    card_to_update = db.session.query(Card, Info, Media).join(Info, Card.id == Info.id_card).join(
        Media, Card.id == Media.id_card).filter(Card.id == id).first()
   
    if card_to_update != None:
        form = UpdateCard()
        form.name.render_kw['placeholder'] = card_to_update[0].name
        form.edition.render_kw['placeholder'] = card_to_update[1].edition
        form.creation_date.render_kw['placeholder'] = card_to_update[1].creation_date
        form.price.render_kw['placeholder'] = card_to_update[0].price
        form.search.render_kw['placeholder'] = card_to_update[0].search
        form.ccm.render_kw['placeholder'] = card_to_update[0].ccm if card_to_update[0].ccm != None else "Pas de ccm pour cette carte"

        if request.method == 'POST' and form.validate_on_submit():
            update_card = [cleanhtml(form.data[key]) for key in form.data.keys()]
            card_update = update_card_in_db([id, update_card[0],update_card[5] , update_card[6], update_card[7].filename, 
                    update_card[1], update_card[2], update_card[3], update_card[4], update_card[8], update_card[9]])    
            if card_update:
                flash(f"Mise à jour de la carte {update_card[0]} effectué.", "succès")
            else :
                flash(f"Mise à jour de la carte {update_card[0]} impossible.", "erreur")
            return redirect(url_for('admin_page'))
        return render_template('update.html', card=card_to_update, username=current_user.username, form=form)

    flash("Erreur, Id de carte incorrecte.", "erreur")
    return redirect(url_for('admin_page'))

@app.route('/admin/card/delete/<int:id>', methods=['GET'])
@is_admin
def delete_page(id):    
    if request.method == 'GET':
        card_to_delete = Card.query.get(id)
        if card_to_delete:
            card_name = card_to_delete.name
            delete_card = delete_card_in_db(id)
            if delete_card:
                flash(f"{card_name} a bien été supprimée de la database.", "succès")
            else:
                flash(f"{card_name} n'a pas été supprimée de la database.", "erreur")
    return redirect(url_for('admin_page'))


@app.route('/admin/user/update/<int:id>', methods=['POST', 'GET'])
@is_admin
def update_user_page(id):       
    username = get_current_user()
    if request.method == 'POST':
        user = User.query.get(id)
        if user :
            try:
                status = [cleanhtml(request.form[key]) for key in request.form.keys()][0]
                if user and user.id_status != status:
                    user.id_status = status
                    db.session.commit()
                    flash(f"Status de l'utilisateur {user.username} mise à jour.", "succès")
            except IndexError:
                flash(f"Erreur, mise à jour du status de {user.username} impossible.", "erreur")
        else:
            flash('Utilisateur inconnu.', 'erreur')
    return redirect(url_for('admin_page'))