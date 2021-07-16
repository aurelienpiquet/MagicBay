
// Turn the arrows

const downArrows = document.querySelectorAll('.down-arrow');
const buyList = document.querySelector('.buy-page-div');
const selectDeckbuilder = document.getElementById('select-list-id');

downArrows.forEach((arrow) => {
    arrow.addEventListener('click', () => {
        if (arrow.style.transform == "rotate(180deg)") {
            arrow.style.transform = "none";            
        }    
        else {
            arrow.style.transform = "rotate(180deg)";
        }
        
    })
})

selectDeckbuilder.addEventListener('change', function() {
    let index = selectDeckbuilder.value;
    console.log(index)
    if (index == '>--Selectionner une de vos listes--<') {
        collapseLists = document.querySelectorAll('.list-collapse')
        collapseLists.forEach((collapseList) => {
            collapseList.classList.remove('show');
        })
        let downArrows = document.querySelectorAll('.down-arrow');
        downArrows.forEach((downArrow) => {
            downArrow.style.transform = "none";
            console.log('on tourne')
        })
    }
    
    if (index != '>--Selectionner une de vos listes--<') {
        let list = document.getElementById('list-' + index);
        list.classList.add('show');
        let arrow = document.getElementById('img-' + index);
        if (arrow.style.transform == "rotate(180deg)") {
            arrow.style.transform = "none";            
        }    
        else {
            arrow.style.transform = "rotate(180deg)";
        }
    }

})
