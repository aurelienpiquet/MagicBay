from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *

from __main__ import app

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

@app.route('/register', methods=['POST', 'GET'])
def register_page():    
    username = get_current_user()
    form = Register()
    if form.validate_on_submit():
        form_user = [cleanhtml(form.user.data), cleanhtml(form.email.data), cleanhtml(form.password.data)]  
        user_in_db = User.query.filter((User.username == form_user[0]) | (User.email == form_user[1])).first()
        if user_in_db :
            flash(f" Cet account ne peut être créer. Un planeswalker du nom de : <{form_user[0]}> ou <{form_user[1]}> existe déjà.", "erreur")
            return redirect(url_for('register_page'))
        new_user = create_user(form_user)
        if new_user : 
            login_user(new_user)
            user = User.query.filter(User.username==form_user[0]).first()
            new_avatar = Media(path="/static/img/avatar.png", alt="avatar", title="avatar", id_user=user.id)
            db.session.add(new_avatar)
            db.session.commit()
            flash(f"Bienvenu {form_user[0]}","succes")
            return redirect(url_for('home', logged_in=current_user.is_authenticated))      
    return render_template("connection/register.html", form=form, username=username)

@app.route('/login', methods=['POST', 'GET'])
def login_page():
    username = get_current_user()
    form = Login()
    if request.method == 'POST' and form.validate_on_submit():
        username_form = cleanhtml(form.user.data)
        password_form = cleanhtml(form.password.data)

        user = User.query.filter((User.username == username_form) | (User.email == username_form)).first()
       
        if not user:
            flash("Cet Utilisateur ou Email n'existe pas.", "erreur")
        elif not check_password_hash(user.password, password_form):
            flash("Ce mot de passe ne correspond pas à cet Utilisteur ou Email.", "erreur")        
        else:
            login_user(user, remember=True)
            logging.info(f'USER {user.username} CONNECTE')                             
            return redirect(url_for('home'))    

    return render_template("connection/login.html", form=form, username=username)

@app.route("/logout")
def log_out_page():
    if current_user:
        logging.warning(f'{current_user} se déconnecte')
    logout_user()
    return redirect(url_for('home'))

@app.route('/forgotten_password')
def forgotten_password_page():
    return render_template('connection/forgotten_password.html')

