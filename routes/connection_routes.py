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
        form_user = [cleanhtml(form.username.data), cleanhtml(form.email.data), cleanhtml(form.password.data)]     
        new_user = create_user(form_user)
        if new_user : 
            login_user(new_user),
            return redirect(url_for('home', logged_in=current_user.is_authenticated))
        flash(f" Cet account ne peut être créer. Un planeswalker du nom de : <{form_user[0]}> ou <{form_user[1]}> existe déjà.", "erreur")

    return render_template("register.html", form=form, username=username)

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

@app.route('/forgotten_password')
def forgotten_password_page():
    return render_template('forgotten_password.html')

