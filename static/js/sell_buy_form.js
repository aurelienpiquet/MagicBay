const formAdd = document.getElementById('form-add-card');
const inputIdDeckbuilder = document.getElementById('id_input_deckbuilder')
const inputSearched = document.getElementById('input-search-list')
formAdd.addEventListener('submit', () => {
    inputIdDeckbuilder.value = selectDeckbuilder.value;
})