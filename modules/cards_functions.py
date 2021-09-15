from modules.imports import *
from modules.database import *
from modules.login import *
from modules.form import *
from modules.conversion_functions import *


from __main__ import app

####################### FUNCTION DECKBUILDER ########################
def create_list(datas: list) ->  bool:
    #[name, date, id_type, id_user]
    try:
        new_deckbuilder = DeckBuilder(name=datas[0], date=datas[1], id_type=datas[2], id_user=datas[3])
        db.session.add(new_deckbuilder)
        db.session.commit()
        return True
    except sqlalchemy.exc.StatementError:
        return False

def add_card_to_list(datas: list) -> bool:
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

def add_card_to_sell_list(datas: list) -> bool:
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
        return False

