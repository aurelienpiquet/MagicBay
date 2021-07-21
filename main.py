from modules.imports import *

############ CREATION OF PATH ###################
CUR_dir = os.path.dirname(os.path.abspath(__file__))
IMG_dir = os.path.join(CUR_dir, 'static\img')
MODULE_dir = os.path.join(CUR_dir, 'modules')
ROUTE_dir = os.path.join(CUR_dir, 'routes')

############ CREATION APP ########################
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.config['SECRET_KEY']  = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#ckeditor = CKEditor(app)
turbo = Turbo(app)
Bootstrap(app) #wtflask form et import dans html

############### IMPORT MODULES ############################
sys.path.append(MODULE_dir)

from modules.form import *
from modules.database import *
from modules.conversion_functions import check_datas, cleanhtml
from modules.errorHandler import forbidden, page_not_found
from modules.login import get_current_user
from modules.admin_cards import *
from modules.user_functions import *

############### IMPORT ROUTES #############################
sys.path.append(ROUTE_dir)

from routes.cards_routes import *
from routes.connection_routes import *
from routes.admin_routes import *
from routes.user_deckbuilder_routes import *
from routes.user_chat_routes import *
from routes.user_routes import *
from routes.user_comment_routes import *


##### Login Manager Flask #########
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#### HOME PAGE #####
@app.route('/')
def home():
    username = get_current_user()
    if username :
        avatar = get_user_avatar()
        return render_template('index.html', username=username, avatar=avatar)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
    
    
        