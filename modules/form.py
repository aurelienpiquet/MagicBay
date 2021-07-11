from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError

def FileSizeLimit(max_size_in_mb):
    max_bytes = max_size_in_mb*1024*1024
    def file_length_check(form, field):
        if len(field.data.read()) > max_bytes:
            raise ValidationError(f"File size must be less than {max_size_in_mb}MB")
    
    return file_length_check


class Post(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(message='DataRequired'), Length(max=40)])
    body = TextAreaField('Post',  validators=[DataRequired(message='DataRequired')])
    submit = SubmitField('Ajoûter Post')

class Comments(FlaskForm):
    body =  CKEditorField('Commentaire', validators=[DataRequired(message='DataRequired')])
    submit = SubmitField('Ajoûter Commentaire', validators=[DataRequired(message='DataRequired')])

class AddCard(FlaskForm):
    name = StringField('Nom de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Nom"})
    edition = StringField('Edition de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Edition"})
    creation_date = DateField('Date de création', format='%Y-%m-%d', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Date"})
    legality = StringField('Légalité de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Legalité"})
    rarity = StringField('Rareté de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Rareté"})
    price = FloatField('Prix de la nouvelle carte en €', validators=[DataRequired(message='Formatage pour le prix: 1.00')], render_kw={"placeholder": "1.00"})
    file = FileField('Image de la nouvelle carte', validators=[FileRequired(), FileAllowed(['jpg', 'png'], '*.jpg ou *.png')])
    submit = SubmitField('Ajoûter Carte')

    #def validate_enddate_field(form, field):
    #if field.data < form.creation_date.data:
    #    raise ValidationError("End date must not be earlier than start date.")

#class UpdateCard(FlaskForm):
#    name = StringField('Nom de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Nom"})
#    edition = StringField('Edition de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Edition"})
#    creation_date = DateField('Date de création', format='%Y-%m-%d', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Date"})
#    legality = StringField('Légalité de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Legalité"})
#    rarity = StringField('Rareté de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Rareté"})
#    price = FloatField('Mise à jour du prix', validators=[DataRequired(message='Formatage pour le prix: 1.00')], render_kw={"placeholder": "1.00"})
#    search = IntegerField('Nombre de recherche', validators=[DataRequired(message='Formatage pour le nombre de recherche: 1')], render_kw={"placeholder": "1"})
#    file = FileField('Mise à jour image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], '*.jpg ou *.png')])
#    submit = SubmitField('Mise à jour')

class UpdateCard(FlaskForm):
    name = StringField('Nom de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Nom"})
    edition = StringField('Edition de la nouvelle carte', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Edition"})
    creation_date = DateField('Date de création', format='%Y-%m-%d', validators=[DataRequired(message='DataRequired')], render_kw={"placeholder": "Date"})
    legality = SelectField('Légalité', choices=['Rareté','rare','unco','commune'], validators=[DataRequired(message='DataRequired')])
    rarity = SelectField('Rareté', choices=['Rareté','rare','unco','commune'], validators=[DataRequired(message='DataRequired')])
    price = FloatField('Mise à jour du prix', validators=[DataRequired(message='Formatage pour le prix: 1.00')], render_kw={"placeholder": "1.00"})
    search = IntegerField('Nombre de recherche', validators=[DataRequired(message='Formatage pour le nombre de recherche: 1')], render_kw={"placeholder": "1"})
    file = FileField('Mise à jour image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], '*.jpg ou *.png')])
    submit = SubmitField('Mise à jour')

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
