from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *
from modules.cards_functions import *

from __main__ import app
from __main__ import turbo

@app.route('/user/<username>/acheter', methods = ['POST', 'GET'])
@is_logged
def buy_list_page(username):
    create_list_form = CreateList()
    if username == current_user.username :
        buy_lists = db.session.query(User, DeckBuilder, DeckBuilder_Card, Card).join(DeckBuilder, User.id == DeckBuilder.id_user).join(
            DeckBuilder_Card, DeckBuilder.id == DeckBuilder_Card.id_deckbuilder).join(
                Card, Card.id == DeckBuilder_Card.id_card).filter(DeckBuilder.id_user == current_user.id).filter(
                    DeckBuilder.id_type == 1).order_by(DeckBuilder.id).all()

        cards = [card[3].name for card in buy_lists]

        buy_lists_id = db.session.query(User, DeckBuilder).join(DeckBuilder, User.id == DeckBuilder.id_user).filter(
            User.id == current_user.id).filter(DeckBuilder.id_type == 1).order_by(DeckBuilder.name).all()

        if buy_lists == [] : 
            buy_lists = buy_lists_id

        limit = 2
        page = request.args.get('page', 1, type=int) if request.args.get('page', 1, type=int) <  limit + 1 else limit
        if page == 0 :
            page = 1

        search_list = db.session.query(User, Card, DeckBuilder_Card, Info).join(
            DeckBuilder, User.id == DeckBuilder.id_user).join(
                DeckBuilder_Card, DeckBuilder.id == DeckBuilder_Card.id_deckbuilder).join(
                    Card, Card.id == DeckBuilder_Card.id_card).join(
                        Info, Info.id == DeckBuilder_Card.id_info).filter(Card.name.in_(cards)
                        ).filter(User.id != current_user.id).filter(DeckBuilder.id_type == 2).order_by(User.username).all()

        seller_list = list(dict.fromkeys([search[0] for search in search_list]))

        if turbo.can_stream():   
            print('turbo')
            return turbo.stream([
                turbo.update(
                    render_template("_research_buy_list.html", buy_lists = buy_lists, buy_lists_id = buy_lists_id), target="research-buy-list"),
                turbo.replace(
                    render_template('_research_table.html', search_list = search_list, seller_list = seller_list), target='search-table-list'),
                turbo.replace(
                    render_template('_research_select_list.html', buy_lists_id = buy_lists_id), target='select-list'),])

        return render_template('user/deckbuilder/buy.html', create_list_form=create_list_form, username=username, buy_lists=buy_lists, buy_lists_id=buy_lists_id, search_list=search_list, seller_list=seller_list)
    return redirect(url_for('home'))

@app.route('/user/create_page_list/<int:id_type>', methods=['POST', 'GET'])
@is_logged
def create_deckbuilder_list(id_type):
    create_list_form = CreateList()
    if create_list_form.validate_on_submit():
        name = cleanhtml(create_list_form.new_list.data)
        date = datetime.datetime.now()
        id_user = current_user.id      
        create = create_list([name, date, id_type, id_user])
        if create:
            flash(f"Votre liste a bien été ajoutée.", "succès")
        else:
            flash(f"Création de cette liste impossible.", "erreur")
    
    if not create_list_form.validate_on_submit():
        message = "Maximum 15 caractères" if len(create_list_form.new_list.data) > 30 else "Nom de liste requis."
        flash(message, "erreur")
    
    if id_type == 1 :
        return redirect(url_for('buy_list_page', username=current_user.username))
    if id_type == 2 :
        return redirect(url_for('sell_list_page', username=current_user.username))
    if id_type == 3 :
        return redirect(url_for('deckbuilder_list_page', username=current_user.username))

@app.route('/user/add_to_buy_list', methods = ['POST', 'GET'])
@is_logged
def add_to_buy():
    if request.method == 'POST':
        id_deckbuilder = cleanhtml(request.form['id_input_deckbuilder'])
        card_name = cleanhtml(request.form['bar-research'])
        if id_deckbuilder.isdigit() and card_name:            
            nb = cleanhtml(request.form['quantity'])       
            adds = add_card_to_list([id_deckbuilder, card_name, nb])
            if adds:
                flash(f"{card_name.capitalize()} a bien été rajoutée.", "succès")
            else:
                flash(f"Problème lors de l'enregistrement de {card_name.capitalize()}.", "erreur")
        else :
            flash(f"Problème lors de l'enregistrement.", "erreur")
    return redirect(url_for('buy_list_page', username=current_user.username))

@app.route('/user/delete_page_list', methods=['POST'])
@is_logged
def delete_list():   
    if request.method == 'POST':
        id = cleanhtml(request.form['delete-id'])
        list_cards_to_delete = DeckBuilder_Card.query.filter_by(id_deckbuilder=id).all()
        if list_cards_to_delete != []:
            for card_to_delete in list_cards_to_delete:
                db.session.delete(card_to_delete)
            db.session.commit()
        list_to_delete = DeckBuilder.query.filter_by(id=id).first()
        if list_to_delete:
            id_type = list_to_delete.id_type
            list_name = list_to_delete.name
            db.session.delete(list_to_delete)
            db.session.commit()
            flash(f"{list_name} a bien été supprimée.", "succès")
        else:
            flash(f"Suppression de la liste impossible.", "erreur")
        if id_type == 1 :
            return redirect(url_for('buy_list_page', username=current_user.username))
        if id_type == 2 :
            return redirect(url_for('sell_list_page', username=current_user.username))
        if id_type == 3 :
            return redirect(url_for('deckbuilder_list_page', username=current_user.username))
    return redirect(url_for('home'))


@app.route('/user/delete_buy_card_list/<int:card_id>/<int:deckbuilder_id>', methods=['POST'])
@is_logged
def delete_buy_card_list(card_id, deckbuilder_id):
    if request.method == 'POST':
        card_to_delete = DeckBuilder_Card.query.filter(DeckBuilder_Card.id_card == card_id).filter(DeckBuilder_Card.id_deckbuilder == deckbuilder_id).first()
        if card_to_delete:
            db.session.delete(card_to_delete)
            db.session.commit()
            return redirect(url_for('buy_list_page', username=current_user.username))
    return redirect(url_for('home', username=current_user.username))


############################# SELL LIST ################################################

@app.route('/user/<username>/vendre', methods = ['POST', 'GET'])
@is_logged
def sell_list_page(username):
    if username == current_user.username:
        create_list_form = CreateList()
        sell_list_form = SellList()
        sell_lists = db.session.query(User, DeckBuilder, DeckBuilder_Card, Card, Info).join(DeckBuilder, User.id == DeckBuilder.id_user).join(
            DeckBuilder_Card, DeckBuilder.id == DeckBuilder_Card.id_deckbuilder).join(
                Card, Card.id == DeckBuilder_Card.id_card).join(Info, Info.id == DeckBuilder_Card.id_info).filter(DeckBuilder.id_user == current_user.id).filter(
                    DeckBuilder.id_type == 2).order_by(DeckBuilder.id).all()

        sell_lists_id = db.session.query(User, DeckBuilder).join(DeckBuilder, User.id == DeckBuilder.id_user).filter(
            User.id == current_user.id).filter(DeckBuilder.id_type == 2).all()

        if sell_lists == [] : 
            sell_lists = sell_lists_id

        if turbo.can_stream():   
            return turbo.stream([
                turbo.update(
                    render_template('_research_sell_list.html', sell_lists = sell_lists, sell_lists_id = sell_lists_id), target='research-sell-list'), 
                turbo.update(
                    render_template('_research_select_list.html', sell_lists_id = sell_lists_id), target='select-list')])

        return render_template('user/deckbuilder/sell.html', sell_list_form=sell_list_form, create_list_form=create_list_form, username=username, sell_lists=sell_lists, sell_lists_id = sell_lists_id)
    return redirect(url_for('home'))

@app.route('/user/add_to_sell_list', methods = ['POST', 'GET'])
@is_logged
def add_to_sell():
    sell_form = SellList()
    if request.method == 'POST' and sell_form.validate_on_submit():

        id_deckbuilder = cleanhtml(request.form['id_input_deckbuilder'])
        card_name = cleanhtml(request.form['bar-research'])
        nb = cleanhtml(request.form['quantity'])    
        edition = cleanhtml(sell_form.edition.data)
        creation = cleanhtml(sell_form.creation_date.data)
        language = cleanhtml(sell_form.language.data)
        rarity = cleanhtml(sell_form.rarity.data)
        quality = cleanhtml(sell_form.quality.data)
        price = cleanhtml(sell_form.price.data)

        sells = add_card_to_sell_list([id_deckbuilder, card_name, nb, edition, creation, language, rarity, quality, price])
        if sells:
            flash(f"{card_name.capitalize()} a bien été rajoutée.", "succès")
        else :
            flash(f"Problème lors de l'enregistrement de {card_name.capitalize()}.", "erreur")
    if request.method == 'POST' and not sell_form.validate_on_submit():
        flash("Enregistrement impossible. Merci de bien compléter tout les champs.", "erreur")
    return redirect(url_for('sell_list_page', username=current_user.username))
  
@app.route('/user/delete_sell_card_list/<card>', methods=['GET','POST'])
@is_logged
def delete_sell_card_list(card):
    if request.method == 'POST':
        card_id = cleanhtml(request.form['card-id'])
        deckbuilder_id = cleanhtml(request.form['deck-id'])
        
        card_to_delete = DeckBuilder_Card.query.filter(DeckBuilder_Card.id_card == card_id).filter(DeckBuilder_Card.id_deckbuilder == deckbuilder_id).first()
        if card_to_delete:
            db.session.delete(card_to_delete)
            db.session.commit()
            flash(f"La carte {card} a bien été supprimée.","succès")
        else:
            flash(f"La carte {card} n'a pas été supprimée.", "erreur")
    return redirect(url_for('sell_list_page', username=current_user.username))


############################# DECKBUILDER #########################################

@app.route('/user/<username>/deckbuilder')
@is_logged
def deckbuilder_list_page(username):
    if username == current_user.username:
        return render_template('user/deckbuilder/deckbuilder.html', username=current_user.username)
    return redirect(url_for('home'))