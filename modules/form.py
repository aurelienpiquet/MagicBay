from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.fields.html5 import EmailField
from wtforms.fields import HiddenField
from wtforms.validators import ValidationError
import re

#def FileSizeLimit(max_size_in_mb):
#    max_bytes = max_size_in_mb*1024*1024
#    def file_length_check(form, field):
#        if len(field.data.read()) > max_bytes:
#            raise ValidationError(f"File size must be less than {max_size_in_mb}MB")
#    
#    return file_length_check

#class SignupForm(Form):
#    age = IntegerField(u'Age')
#
#    def validate_age(form, field):
#        if field.data < 13:
#            raise ValidationError("We're sorry, you must be 13 or older to register")

class Card():
    def __init__(self):
        self.card_name = None

    def getName(self):
        return self.card_name
    
    def setName(self, new_name):
        self.card_name = new_name
        return self

########### CARDS FORM ###############""

class AddCard(FlaskForm):
    name = StringField('Nom de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Nom"})
    edition = StringField('Edition de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Edition"})
    creation_date = StringField('Date de création', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Année: 2010"})
    legality = SelectField('Légalité', choices=[('Vintage', 'Vintage'), ('Legacy', 'Legacy'),('Modern', 'Modern'),('Standard', 'Standard')], validators=[DataRequired(message='DataRequired')])
    rarity = SelectField('Rareté', choices=[('mythique', 'Mythique'), ('rare', 'Rare'),('unco', 'Unco'),('commune', 'Commune'),('token', 'Token')], validators=[DataRequired(message='DataRequired')])
    price = FloatField('Prix', validators=[DataRequired(message='Formatage pour le prix: 1.00')], render_kw={"placeholder": "1.00"})
    file = FileField('Image')
    type = SelectField('Type', choices=[('artefact','Artefact'),('créature','Créature'),('enchantement','Enchantement'),('éphémère','Ephémère'),('terrain','Terrain'),('planeswalker','Planeswalker'),('rituel','Rituel'), ('token','Token')], validators=[DataRequired(message='DataRequired')])
    ccm = StringField('CCM', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "1RR"})
    submit = SubmitField('Ajouter Carte')

class UpdateCard(FlaskForm):
    name = StringField('Nom de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder":""})
    edition = StringField('Edition de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": ""})
    creation_date = StringField('Date de création', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Année: 2010"})
    legality = SelectField('Légalité', choices=[('Vintage', 'Vintage'), ('Legacy', 'Legacy'),('Modern', 'Modern'),('Standard', 'Standard')], validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": ""})
    rarity = SelectField('Rareté', choices=[('mythique', 'Mythique'), ('rare', 'Rare'),('unco', 'Unco'),('commune', 'Commune'),('token', 'Token')], validators=[DataRequired(message='DataRequired')])
    price = FloatField('Mise à jour du prix', validators=[DataRequired(message='Formatage pour le prix: 1.00')], render_kw={"placeholder": "1.00"})
    search = IntegerField('Nombre de recherche', validators=[DataRequired(message='Formatage pour le nombre de recherche: 1')], render_kw={"placeholder": "1"})
    file = FileField('Mise à jour image', validators=[FileRequired(message="Image Requise"), FileAllowed(['jpg', 'png'], '*.jpg ou *.png')])
    type = SelectField('Type', choices=[('artefact','Artefact'),('créature','Créature'),('enchantement','Enchantement'),('éphémère','Ephémère'),('terrain','Terrain'),('planeswalker','planeswalker'),('rituel','Rituel'), ('token','Token')], validators=[DataRequired(message='DataRequired')])
    ccm = StringField('CCM', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "1RR ou XXGBR"})
    submit = SubmitField('Mise à jour')

class RullingCard(FlaskForm):
    rulling = TextAreaField('Ajouter un rulling', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder":"Ecrivez le nouveau rulling ici..."})
    submit = SubmitField('Ajouter rulling')

class PostCard(FlaskForm):
    title = StringField('Titre du post', validators=[DataRequired(message='DataRequired'), Length(max=100)], render_kw={"placeholder": "Rédiger le titre du post ici ..."})
    content = TextAreaField('Contenu du post',  validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Rédiger le contenu du post ici ..."})
    submit = SubmitField('Ajouter Post')

class ResponseCard(FlaskForm):
    content =  TextAreaField('',validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Rédiger votre réponse ici..."} )
    submit = SubmitField('Envoyer', validators=[DataRequired(message='DataRequired')])

class PostModifyCard(FlaskForm):
    title = StringField('Modifier le titre du post', validators=[DataRequired(message='DataRequired'), Length(max=100)], render_kw={"placeholder": "Rédiger le titre du post ici ..."})
    content = TextAreaField('Modifier le contenu du post',  validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Rédiger le contenu du post ici ..."})
    submit = SubmitField('Modifier le post')

class ResponseModifyCard(FlaskForm):
    content =  TextAreaField('Modifier le contenu de la réponse',validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Rédiger votre réponse ici..."} )
    submit = SubmitField('Envoyer', validators=[DataRequired(message='DataRequired')])

class ChatMessage(FlaskForm):
    message = StringField('', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder":"Ecriver votre message ici..."})
    submit = SubmitField('Envoyer', validators=[DataRequired(message='')])


#### USER FORM #######

class Register(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(message="Nom d'utilisateur requis"), 
        Length(max=40)], render_kw={"placeholder": "Nom d'utilisateur"})
    email = EmailField('Email', validators=[DataRequired(message='Email requis'), Email()],
         render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(message='Password requis'), Length(min=4)], 
        render_kw={"placeholder": "Password"}) 
    submit = SubmitField('Créer utilisateur')

class Avatar(FlaskForm):
    file = FileField('Nouvel Avatar', validators=[FileRequired(message="Image requise"), FileAllowed(['jpg', 'png'], '*.jpg ou *.png')])
    submit = SubmitField("Modifier Avatar") 

class SellList(FlaskForm):
    edition = StringField('Edition', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": ""})
    creation_date = StringField("Date d'impression", validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Année: 2010"})
    rarity = SelectField('Rareté', choices=[('mythique', 'Mythique'), ('rare', 'Rare'),('unco', 'Unco'),('commune', 'Commune'),('token', 'Token')], validators=[DataRequired(message='DataRequired')])
    quality = SelectField('Qualité', choices=[('mint', 'Mint'), ('Nm', 'Near mint'),('exc', 'Excellent'),('good', 'Good'),('poor', 'Poor')], validators=[DataRequired(message='DataRequired')])
    price = FloatField('Prix', validators=[DataRequired(message='Formatage pour le prix: 1.00')], render_kw={"placeholder": "1.00"})
    language = SelectField('Language', choices=[('fr', 'fr'), ('eng', 'eng'),('rus', 'rus'),('china', 'china'),('ita', 'ita'),('esp', 'esp')], validators=[DataRequired(message='DataRequired')])
    submit = SubmitField('Ajouter')
    

class CreateList(FlaskForm):
    new_list = StringField('', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder":"Nom de la nouvelle liste.."})
    submit = SubmitField('Ajouter')

if __name__ == '__main__':

    form = UpdateCard().setName('test')
    print(form)