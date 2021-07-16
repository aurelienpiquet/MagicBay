
function removeFlashes() {
    myVar = setTimeout(function() {     
        flash_messages = document.querySelector('.ul-flash');
        if (flash_messages) {
            flash_messages.style.opacity = '0';
            flash_messages.style.transform = 'translateY(-100px)';
            setTimeout(function() {
                flash_messages.style.position = 'absolute';
                flash_messages.style.top = '0';
            }, 1000)
        }

    }, 2000);
}     


