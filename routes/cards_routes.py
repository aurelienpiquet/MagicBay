from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *
import requests

from __main__ import app

############################# LOGGED OUT ROUTES #############################################################

@app.route('/card/cards', methods=['POST', 'GET'])
def cards():
    username = get_current_user()

    # Top By Rating

    cards_rating = db.session.query(Card, func.avg(Rating.rating), Info, Media, func.count(Rating.rating)).join(Card, Card.id == Rating.id_card).join(Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).group_by(Rating.id_card).order_by(desc(func.avg(Rating.rating))).limit(3).all()
#
    cards_rating_legacy = db.session.query(Card, func.avg(Rating.rating), Info, Media, func.count(Rating.rating)).join(Card, Card.id == Rating.id_card).join(
        Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).filter(Info.legality !='vintage').group_by(Rating.id_card).order_by(desc(func.avg(Rating.rating))).limit(3).all()

    cards_rating_modern = db.session.query(Card, func.avg(Rating.rating), Info, Media, func.count(Rating.rating)).join(Card, Card.id == Rating.id_card).join(
        Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).filter(Info.legality !='legacy').filter(Info.legality !='vintage').group_by(Rating.id_card).order_by(desc(func.avg(Rating.rating))).limit(3).all()
#
    cards_rating_standard = db.session.query(Card, func.avg(Rating.rating), Info, Media, func.count(Rating.rating)).join(Card, Card.id == Rating.id_card).join(
        Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).filter(Info.legality != 'modern').filter(Info.legality !='legacy').filter(Info.legality !='vintage').group_by(Rating.id_card).order_by(desc(func.avg(Rating.rating))).limit(3).all()
    
    # Top By Search 

    cards_search = db.session.query(Card, Card.search, Info, Media).join(Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).order_by(desc(Card.search)).limit(3).all()
    cards_search_legacy = db.session.query(Card, Card.search, Info, Media).join(Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).filter(Info.legality !='vintage').order_by(desc(Card.search)).limit(3).all()
    cards_search_modern = db.session.query(Card, Card.search, Info, Media).join(Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).filter(Info.legality !='legacy').filter(Info.legality !='vintage').order_by(desc(Card.search)).limit(3).all()
    cards_search_standard = db.session.query(Card, Card.search, Info, Media).join(Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).filter(Info.legality != 'modern').filter(Info.legality !='legacy').filter(Info.legality !='vintage').order_by(desc(Card.search)).limit(3).all()

    return render_template('cards/cards.html', search = cards_search, search_legacy=cards_search_legacy, search_modern=cards_search_modern, 
    search_standard=cards_search_standard, rating=cards_rating, rating_modern=cards_rating_modern, rating_standard=cards_rating_standard, 
    rating_legacy=cards_rating_legacy, username=username)

@app.route('/card/<name>')
def card_page(name):
    card = Card.query.filter_by(name=name).first()
    rulling_form = RullingCard()
    post_form = PostCard()
    post_modify_form = PostModifyCard()
    response_form = ResponseCard()    
    response_modify_form = ResponseModifyCard()
    if card: 

        # load des datas de la carte 

        card_media = db.session.query(Card, Media).join(Media, Card.id == Media.id_card).filter(Card.name==card.name).first()

        card_info = db.session.query(Info, Card, Rulling).join(
            Card, Info.id_card == Card.id).join(Rulling, Card.id == Rulling.id_card).filter(Card.name == card.name).order_by(Rulling.id).all()

        card_rating = db.session.query(func.avg(Rating.rating)).filter(Rating.id_card == card.id).first()

        # test si des users vendent cette carte

        sellers_price = db.session.query(func.avg(Info.price)).join(DeckBuilder_Card, DeckBuilder_Card.id_info == Info.id).filter(DeckBuilder_Card.id_card==card.id).filter(DeckBuilder_Card.id_info!=0).all()

        sellers_price = round(sellers_price[0][0], 2) if sellers_price[0][0] != None else card.price

        # test si rating sur la carte
        if card_rating[0] :
            rating = round(card_rating[0],1)
            count = db.session.query(Rating).filter(Rating.id_card  == card.id).count()

        else :
            rating = 0
            count = 0

        # test si user a fait rating sur la carte
        try:
            username = current_user.username
            card_rating_user = db.session.query(Rating.rating).filter(Rating.id_card == card.id).filter(Rating.id_user == current_user.id).first()
            if card_rating_user != None :
                user_rating = int(card_rating_user[0])
            else :
                user_rating = None
        except AttributeError:
            user_rating = "no_user"
            username = "no_user"

        # check s'il y a des commentaires sur la carte
        try :
            comments = db.session.query(Comment, User, Media).join(
                User, Comment.id_user == User.id).join(
                        Media, User.id == Media.id_user).filter(Comment.id_card == card.id).order_by((Comment.date)).all()
        except IndexError:
            comments = []

        return render_template('cards/card.html', card=card, sellers_price=sellers_price, comments=comments, username=username, 
                media=card_media, info = card_info, rating=rating, user_rating=user_rating, count=count,
                rulling_form=rulling_form, post_form=post_form, response_form=response_form, post_modify_form=post_modify_form, 
                response_modify_form=response_modify_form)
    
    return redirect(url_for('home'))

@app.route('/card/recherche', methods=['POST'])
def card_page_research():
    username = get_current_user()
    if request.method == 'POST':
        new_card_name = cleanhtml(request.form['bar-research'])
        searched_card = Card.query.filter_by(name=new_card_name).first()
        if searched_card :
            searched_card.search += 1
            db.session.commit()
        return redirect(url_for('card_page', name=new_card_name))


####################################### LOGGED IN ROUTES ###################################################################

@app.route('/card/rating', methods = ['POST'])
@is_logged
def card_rating_page():
    rating = cleanhtml(request.form['rating'])
    card_id = cleanhtml(request.form['id'])
    card = Card.query.get(card_id)
    if card :
        if not Rating.query.filter(Rating.id_user == current_user.id).filter(Rating.id_card == card_id).first():
            new_rating = Rating(rating=rating, date=datetime.datetime.now(), id_user=current_user.id, id_card=card_id)
            db.session.add(new_rating)
            db.session.commit()
            flash(f"Votre rating a bien été pris en compte pour la carte {card.name}")
        else :
            flash(f"Un problème est survenu pendant l'ajout de votre rating.", "erreur")
        return redirect(url_for('card_page', name=card.name))

@app.route('/card/dict')
def card_dict():
    ### accès à protéger par la suite via token
    cards = Card.query.all()
    liste_cards = [card.as_dict() for card in cards]
    return jsonify(liste_cards)

@app.route('/card/editions')
@is_logged
def card_edition_page():
    r = requests.get(f"https://api.magicthegathering.io/v1/sets").json()['sets']
    return jsonify(r)