from flask import Flask, render_template, redirect, url_for, flash, g, request, abort, Response, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, ForeignKey, text, column, desc, or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_manager, login_user, LoginManager, login_required, current_user, logout_user
#from flask_ckeditor import CKEditor, CKEditorField
from wtforms import *
from wtforms.validators import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
import werkzeug.exceptions
from turbo_flask import Turbo


from PIL import Image
import sys, os, logging, datetime, sqlalchemy.exc, io, base64, pprint, time


CUR_dir = os.path.dirname(os.path.abspath(__file__))
IMG_dir = os.path.join(CUR_dir, 'static\img')
MODULE_dir = os.path.join(CUR_dir, 'modules')

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
turbo = Turbo(app)
app.config['SECRET_KEY']  = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#ckeditor = CKEditor(app)
Bootstrap(app) #wtflask form et import dans html


############### IMPORT MODULES ############################
sys.path.append(MODULE_dir)

from modules.conversion_functions import check_datas, cleanhtml
from modules.errorHandler import forbidden, page_not_found
from modules.login import is_admin, is_user, is_logged

#### FORM
from modules.form import *

#### BDD
from modules.database import *

#### FORM GET KEYS - DATAS
#form = [cleanhtml(request.form[key]) for key in request.form.keys()]
#####################################################################

##### Login Manager Flask #########
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#################### QUERY SUR DATABASE #######################

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

##################### FONCTIONS SUR CARDS ######################

#### refactor add card
def add_card_to_db(form):
    #card_add = [name, edition, creation, legality, rarity, price, path]
    try:        
        new_card = Card(
                    name = form[0],                    
                    price = form[5], 
                    search = 0, 
                    type=form[7],
                    ccm=form[8]                    
                    )
        db.session.add(new_card)
        db.session.commit()     
        id_card = db.session.query(Card.id).order_by(desc(Card.id)).first()
        new_info = Info(   
                    edition = form[1],
                    creation_date = form[2],
                    legality = form[3],
                    rarity = form[4],
                    id_card = id_card[0],
                    )
        new_media = Media(
                    path='/static/img/cards/' + str(form[6]), 
                    title='image de ' + str(form[0]),
                    alt='image de ' + str(form[0]),
                    id_card = id_card[0]
                    )
        new_rulling = Rulling(
                        rule = "Pas de rulling sur cette carte",
                        id_card = id_card[0],
                        date = datetime.datetime.now()
        )
        db.session.add(new_info)
        db.session.add(new_media)
        db.session.add(new_rulling)
        db.session.commit()
        return True
    except sqlalchemy.exc.StatementError:
        return False
#
def update_card_in_db(form):
    #print(form)
    try:
        card_to_update = Card.query.filter_by(id=form[0]).first()  
        card_to_update.name = form[1]
        card_to_update.price = form[2]
        card_to_update.type = form[9]
        card_to_update.ccm = form[10]
        try:
            card_to_update.search = round(int(form[3]))
        except ValueError:
            return "Le nombre de recherche doit être un nombre (exemple: 75846521)"
        media_to_update = Media.query.filter_by(id_card=form[0]).first()
        media_to_update.path = '/static/img/cards/' + form[4]
        media_to_update.title = "image de " + str(form[1])
        media_to_update.alt = "image de " + str(form[1])
        info_to_update = Info.query.filter_by(id_card=form[0]).first()
        info_to_update.edition = form[5]
        info_to_update.creation_date = form[6]
        info_to_update.legality = form[7]
        info_to_update.rarity = form[8]

        db.session.commit() 
        return f"La mise à jour de {form[1]} a bien été effectuée"
    except sqlalchemy.exc.StatementError:
        return "Un problème est survenu pendant l'enregistrement de la mise à jour. Vérifiez vos données."
#
#def get_cards_by_ratings():
#    all_datas_ordered = Cards.query.order_by(Cards.rating).all()
#    return all_datas_ordered[-3:]
#
#def get_cards_by_searchs():
    #all_datas_ordered = Card.query.order_by(Card.search).all()
    #return all_datas_ordered[-3:] 
    
#
#def copy_image_to_folder():
#    #need shuthil and full path shutil.copy(src, dst, *, follow_symlinks=True)
#    pass
#
####################### FUNCTION DECKBUILDER ########################
def create_list(datas):
    #[name, date, id_type, id_user]
    try:
        new_deckbuilder = DeckBuilder(name=datas[0], date=datas[1], id_type=datas[2], id_user=datas[3])
        db.session.add(new_deckbuilder)
        db.session.commit()
        return True
    except sqlalchemy.exc.StatementError:
        return False

def add_card_to_list(datas):
    #datas = [id_deckbuilder, card_name, nb]
    try :
        card = Card.query.filter_by(name=datas[1]).first()
        card_id = card.id
        card_in_list = DeckBuilder_Card.query.filter(DeckBuilder_Card.id_card == card_id).filter(DeckBuilder_Card.id_deckbuilder == datas[0]).first()
        if card_in_list != None:
            card_in_list.nb = card_in_list.nb + abs(int(datas[2]))
            if card_in_list.nb > 4:
                card_in_list.nb = 4
            #print(card_in_list.nb, type(card_in_list.nb))
        else :
            new_deckbuilder_card = DeckBuilder_Card(nb=datas[2], id_card=card_id, id_deckbuilder=datas[0], id_info=0)
            db.session.add(new_deckbuilder_card)        
            db.session.commit()
            if new_deckbuilder_card.nb > 4 :
                new_deckbuilder_card.nb = 4
        db.session.commit()
        return True
    except sqlalchemy.exc.StatementError:
        return False
    except AttributeError:
        return False

def add_card_to_sell_list(datas):
    try:
        card = Card.query.filter_by(name=datas[1]).first()
        card_id = card.id
        new_info = Info(edition=datas[3], language=datas[5], quality=datas[7], creation_date=datas[4], rarity=datas[6], price=datas[8])
        db.session.add(new_info)
        db.session.commit()
        new_deckbuilder_card = DeckBuilder_Card(nb=datas[2], id_card=card_id, id_deckbuilder=datas[0], id_info=new_info.id)
        db.session.add(new_deckbuilder_card)
        db.session.commit()
        return True
    except sqlalchemy.exc.StatementError:
        return "Problème d'enregistrement"

####################### FUNCTION DB User #######################
#
def create_user(form):
    password_hash = generate_password_hash(password=form[2], method='pbkdf2:sha256', salt_length=8)
    try:
        new_user = User(
                        username=form[0],
                        email=form[1], 
                        password=password_hash,
                        name="",
                        lastname="",
                        phone="",  
                        zipcode="", 
                        id_status = 1,            
                        )
        db.session.add(new_user)
        db.session.commit()   
        return new_user    
    except sqlalchemy.exc.SQLAlchemyError:
        return False

def get_current_user():
    try:
        username = current_user.username        
    except AttributeError:
        username = None
    return username

# A DELETE APRES REMISE A JOUR
#def get_avatar():
#    if current_user:
#        try:
#            return base64.b64encode(current_user.avatar).decode('ascii')
#        except TypeError:
#            return None
#    return None   

def delete_in_db(id):
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

###################### COMMENTAIRE ############################
def add_comment_db(form):
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

def add_response_db(form):
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

def update_comment_db(form):
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

######################## CLASS ###########################

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

    #def __repr__(self):
    #    return f"User Id : {self.id} - User Username : {self.username}"

######################## HOME PAGE ROUTE ########################

@app.route('/')
def home():
    username = get_current_user()
    if username :
        avatar = get_user_avatar()
        return render_template('index.html', username=username, avatar=avatar)
    return render_template('index.html')

###################### REGISTER - LOGIN ROUTES #######################################
@app.route('/login', methods=['POST', 'GET'])
def login_page():
    username = get_current_user()
    if request.method == 'POST':
        username_form = cleanhtml(request.form['username-email'])
        email_form = cleanhtml(request.form['username-email'])
        password_form = cleanhtml(request.form['password'])
        user = User.query.filter((User.username == username_form) | (User.email == email_form)).first()
       
        if not user:
            flash("Cet Username ou Email n'existe pas.")
        elif not check_password_hash(user.password, password_form):
            flash('Mauvais mot de passe.')        
        else:
            login_user(user, remember=True)
            logging.info(f'USER {user.username} CONNECTE')                             
            return redirect(url_for('home'))#, username = user.username))     

    return render_template("login.html", username=username)

@app.route("/logout")
def log_out_page():
    if current_user:
        logging.warning(f'{current_user} se déconnecte')
    logout_user()
    return redirect(url_for('home'))

@app.route('/forgotten_password', methods=['POST', 'GET'])
def forgotten_password_page():
    if request.method == 'POST':
        print('test')
        return render_template('forgotten_password.html')
    return render_template('forgotten_password.html')

@app.route('/register', methods=['POST', 'GET'])
def register_page():    
    username = get_current_user()
    message = ""
    form = Register()
    if form.validate_on_submit():
        form_user = [cleanhtml(form.username.data), cleanhtml(form.email.data), cleanhtml(form.password.data)]
                
        new_user = create_user(form_user)
        if new_user : 
            login_user(new_user),
            return redirect(url_for('home', logged_in=current_user.is_authenticated))
        message = f" Ce nouvel account ne peut être créer. <{form_user[0]}> ou <{form_user[1]} existe déjà."
        flash(message)

    return render_template("register.html", form=form, message=message, username=username)

#
########################### CARDS BASED ROUTE ####################
#
@app.route('/card/dict')
def card_dict():
    ### accès à protéger par la suite via token
    cards = Card.query.all()
    liste_cards = [card.as_dict() for card in cards]
    return jsonify(liste_cards)

@app.route('/cards', methods=['POST', 'GET'])
def cards():
    username = get_current_user()

    # Top By Rating

    cards_rating = db.session.query(Card, func.avg(Rating.rating), Info, Media, func.count(Rating.rating)).join(Card, Card.id == Rating.id_card).join(
        Info, Info.id_card == Card.id).join(Media, Media.id_card==Card.id).group_by(Rating.id_card).order_by(desc(func.avg(Rating.rating))).limit(3).all()
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

    return render_template('cards.html', search = cards_search, search_legacy=cards_search_legacy, search_modern=cards_search_modern, 
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

        return render_template('card.html', card=card, sellers_price=sellers_price, comments=comments, username=username, 
                media=card_media, info = card_info, rating=rating, user_rating=user_rating, count=count,
                rulling_form=rulling_form, post_form=post_form, response_form=response_form, post_modify_form=post_modify_form, 
                response_modify_form=response_modify_form)
    
    return redirect(url_for('home'))

@app.route('/card/<name>/add_rulling', methods=['POST'])
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


@app.route('/card/<name>/delete_rulling/<id>', methods=['POST'])
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

@app.route('/card/rating', methods = ['POST'])
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
#

@app.route('/admin/card/delete/<int:id>', methods=['GET'])
@is_admin
def delete_page(id):    
    if request.method == 'GET':
        #card_id = int(cleanhtml(request.args.get('id', 0, str))) 
        card_id = id
        try:  
            card_to_delete = Card.query.get(card_id)

            rullings = db.session.query(Rulling).filter(Rulling.id_card == card_id).all()
            for rulling in rullings:
                db.session.delete(rulling)

            db.session.delete(db.session.query(Media).filter(Media.id_card == card_id).first())
            db.session.delete(db.session.query(Info).filter(Info.id_card == card_id).first())

            ratings = db.session.query(Rating).filter(Rating.id_card == card_id).all()
            for rating in ratings:
                db.session.delete(rating)

            db.session.delete(card_to_delete)
            
            card_name = card_to_delete.name.capitalize()
            db.session.commit()
            flash(f"{card_name} a bien été supprimée de la database.", "succès")
        except sqlalchemy.exc.StatementError:
            flash(f"{card_name} n'a pas été supprimée de la database.", "erreur")
    return redirect(url_for('admin_page'))

@app.route('/admin/user/update/<int:id>', methods=['POST', 'GET'])
@is_admin
def update_user_page(id):       
    username = get_current_user()
    if request.method == 'POST':
        try:
            status = [cleanhtml(request.form[key]) for key in request.form.keys()][0]
            user = User.query.get(id)
            if user and user.id_status != status:
                user.id_status = status
                db.session.commit()
                flash(f"Status de l'utilisateur {user.username} mise à jour.", "succès")
        except IndexError:
            flash(f"Erreur, mise à jour du status de {user.username} impossible.", "erreur")
    return redirect(url_for('admin_page'))


##################### USER APP ROUTES ########################

#
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
#
@app.route('/user/<username>', methods=['POST', 'GET'])
@is_user
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

#################################### SEARCH-BUY PAGE #######################################################

@app.route('/user/<username>/acheter', methods = ['POST', 'GET'])
@is_user
def buy_list_page(username):
    create_list_form = CreateList()
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

    return render_template('buy.html', create_list_form=create_list_form, username=username, buy_lists=buy_lists, buy_lists_id=buy_lists_id, search_list=search_list, seller_list=seller_list)

@app.route('/user/create_page_list/<int:id_type>', methods=['POST'])
@is_user
def create_deckbuilder_list(id_type):
    list_form = CreateList()
    name = cleanhtml(list_form.new_list.data)
    date = datetime.datetime.now()
    id_user = current_user.id      
    create = create_list([name, date, id_type, id_user])
    if create:
        flash(f"Votre liste a bien été ajoutée.", "succès")
    else:
        flash(f"Création de cette liste impossible.", "erreur")
    if id_type == 1 :
        return redirect(url_for('buy_list_page', username=current_user.username))
    if id_type == 2 :
        return redirect(url_for('sell_list_page', username=current_user.username))
    if id_type == 3 :
        return redirect(url_for('deckbuilder_list_page', username=current_user.username))


@app.route('/user/add_to_buy_list', methods = ['POST', 'GET'])
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
@is_user
def delete_list():   
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


@app.route('/user/delete_buy_card_list/<int:card_id>/<int:deckbuilder_id>', methods=['POST'])
@is_user
def delete_buy_card_list(card_id, deckbuilder_id):
    card_to_delete = DeckBuilder_Card.query.filter(DeckBuilder_Card.id_card == card_id).filter(DeckBuilder_Card.id_deckbuilder == deckbuilder_id).first()
    if card_to_delete:
        db.session.delete(card_to_delete)
        db.session.commit()
        return redirect(url_for('buy_list_page', username=current_user.username))
    return redirect(url_for('home', username=current_user.username))

############################# SELL LIST ################################################

@app.route('/user/<username>/vendre', methods = ['POST', 'GET'])
@is_user
def sell_list_page(username):
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
        
    return render_template('sell.html', sell_list_form=sell_list_form, create_list_form=create_list_form, username=username, sell_lists=sell_lists, sell_lists_id = sell_lists_id)

@app.route('/user/add_to_sell_list', methods = ['POST', 'GET'])
@is_user
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
        else:
            flash(f"Problème lors de l'enregistrement de {card_name.capitalize()}.", "erreur")
        return redirect(url_for('sell_list_page', username=current_user.username))
  
@app.route('/user/delete_sell_card_list', methods=['POST'])
@is_user
def delete_sell_card_list():
    card_id = cleanhtml(request.form['card-id'])
    deckbuilder_id = cleanhtml(request.form['deck-id'])
    card_to_delete = DeckBuilder_Card.query.filter(DeckBuilder_Card.id_card == card_id).filter(DeckBuilder_Card.id_deckbuilder == deckbuilder_id).first()
    card_name = card_to_delete.name
    if card_to_delete:
        db.session.delete(card_to_delete)
        db.session.commit()
        flash(f"{card_to_delete.capitalize()} a bien été supprimée.","succès")
    flash(f"{card_to_delete.capitalize()} n'a pas été supprimée.", "erreur")
    return redirect(url_for('sell_list_page', username=current_user.username))


############################# DECKBUILDER #########################################

@app.route('/user/deckbuilder')
@is_user
def deckbuilder_list_page():
    return render_template('deckbuilder.html')

############################# MESSAGE ROUTE #############################################

@app.route('/user/<username>/message')
@is_user
def message_page(username):

    messages = Contact.query.filter((Contact.id_user == current_user.id) | (Contact.receiver_id == current_user.id)).order_by(desc(Contact.date)).order_by(desc(Contact.id)).all()
    return render_template('messenger.html', username=current_user.username, messages=messages)
     

@app.route('/user/<username>/message/<receiver>/<card>/<info>', methods=['POST'])
@is_user
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
@is_user
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
@is_user
def chat_delete_page(post_id):
    message = Message(id = int(post_id))
    if message.deleteMessage() == True:
        return redirect(url_for('home'))
    else :
        return 'ok'

########################### COMMENT ROUTES #######################################

@app.route('/card/add_comment/<int:card_id>/<author>', methods=['POST', 'GET'])
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

@app.route('/card/update_comment/<int:card_id>/<int:comment_id>/<int:author_id>', methods=['POST'])
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

@app.route('/card/delete_comment/<comment_id>/<author>/<card_id>')
@is_logged
def delete_comment(comment_id, author, card_id):
    card_name = Card.query.get(cleanhtml(card_id))
    if author == current_user.username:
        comment_to_delete = delete_in_db(comment_id)
    return redirect(url_for('card_page', name=card_name.name))

@app.route('/card/add_response/<int:comment_id>/<int:author_id>/<int:card_id>', methods=['POST'])
@is_logged
def add_response(comment_id, author_id, card_id):
    card_name = Card.query.get(cleanhtml(card_id))
    response_form = ResponseCard()

    if card_name :
        if request.method == 'POST' and response_form.validate_on_submit():
            content = cleanhtml(response_form.content.data)
            new = add_response_db([comment_id, author_id, card_id, content])
    return redirect(url_for('card_page', name=card_name.name))


@app.route('/card/update_response/<int:card_id>/<int:comment_id>/<int:author_id>', methods=['POST'])
@is_logged
def update_response(card_id, comment_id, author_id):
    card = Card.query.get(card_id)
    response_modify_form = ResponseModifyCard()
    if card:
        if request.method == 'POST' and response_modify_form.validate_on_submit():
            content = cleanhtml(response_modify_form.content.data)
            update = update_comment_db([card_id, comment_id, author_id, None, content])
    return redirect(url_for('card_page', name=card.name))
    

#
#
#
#
if __name__ == "__main__":
    app.run(debug=True)
    
    
        