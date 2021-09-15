from modules.database import *
from sqlalchemy import Table, Column, ForeignKey, text, column, desc, or_
from werkzeug.utils import secure_filename

import datetime

def add_card_to_db(form: list, filename) -> bool:
    """This method creates a new entries en database

    Args:
        form (list): Form from an add_Form
        filename (file): a .file from a data-storage-file

    Returns:
        bool: True if all entries were created successfully, False otherwise.
    """
    try:        
        new_card = Card(
                    name = secure_filename(form[0]),                    
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
                    path='/static/img/cards/' + str(secure_filename(filename)), 
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

def update_card_in_db(form : list) -> bool:
    """Method for updating cards data in database

    Args:
        form (list): Form from an update_Form

    Returns:
        bool: Return True if the datas were successfully updated, False otherwise.
    """
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

def delete_card_in_db(id: int) -> bool:
    """Method delete a card in database.

    Args:
        id (int): The id of the card to be deleted.

    Returns:
        bool: True if successfull, False otherwise.
    """
    try:
        card = Card.query.get(id)
        rullings = db.session.query(Rulling).filter(Rulling.id_card == card.id).all()
        if rullings:
            for rulling in rullings:
                db.session.delete(rulling)
        db.session.delete(db.session.query(Media).filter(Media.id_card == card.id).first())
        db.session.delete(db.session.query(Info).filter(Info.id_card ==card.id).first())
        deckbuilders = db.session.query(DeckBuilder_Card).filter(DeckBuilder_Card.id_card == card.id).all()
        for deckbuilder in deckbuilders:
            db.session.delete(deckbuilder)
        ratings = db.session.query(Rating).filter(Rating.id_card == card.id).all()
        if ratings:
            for rating in ratings:
                db.session.delete(rating)
        db.session.delete(card)
        db.session.commit()
        return True
    except sqlalchemy.exc.StatementError:
        return False

