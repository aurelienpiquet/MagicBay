    // Pour Modal Messenger

    const btnMessengers = document.querySelectorAll('.btn-messenger');
    const modalMessengerTitle = document.querySelector('#modalMessengerTitle');
    const modalBody = document.querySelector('.modal-body');
    const btnSend = document.getElementById('btn-send-message');
    let receiver = "";
    
    btnMessengers.forEach((btnMessenger) => {
        btnMessenger.addEventListener('click', () => {
            
            modalMessengerTitle.innerText = "Contactez l'utilisateur " + btnMessenger.getAttribute('name-seller');
            modalBody.placeholder = "Exemple de message : Bonjour, votre carte " + btnMessenger.getAttribute('id-card') + " m'interesse. ";
            modalBody.value = "";
            receiver = btnMessenger.getAttribute('name-seller');
            })
        })
             //btn du modal
    
    btnSend.addEventListener('click', () => {
        console.log('hello')
        let content = modalBody.value;
        if (content != "" && content != null) {
            $.post('/message', { content : content , receiver : receiver})
            $('#modalMessenger').modal('hide');
        }
        modalBody.value = "";
        receiver = "";
        content = "";
    })