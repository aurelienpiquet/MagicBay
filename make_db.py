

#### des exemples a mettre dans la db


add_card_to_db(name = 'black lotus', price = 1.50, rating = 1, img = 'blacklotus.jpg')
add_card_to_db(name = 'lotus petal', price = 1.50, rating = 1, img = 'lotuspetal.jpg')
add_card_to_db(name = 'dark ritual', price = 1.50, rating = 1, img = 'darkritual.jpg')
add_card_to_db(name = 'lightning bolt', price = 1.50, rating = 1, img = 'lightningbolt.jpg')
add_card_to_db(name = 'counterspell', price = 1.50, rating = 1, img = 'counterspell.jpg')

<script>
function script_delete(event, name, id) {
  event.preventDefault();
  window.confirm('Supprimer la carte {{ name }}?') ? 
    window.location.href = "{{ url_for('delete_page', id=id, name=name) }}" :
    null;
};
</script>