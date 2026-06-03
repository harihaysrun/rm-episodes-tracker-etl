const buttons = document.querySelectorAll('.add-button');

buttons.forEach(button => {
    button.addEventListener('click', function() {
        const epId = this.getAttribute('data-ep-id');

        fetch('/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ep_id: epId })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success: ', data);
            window.location.href = data.redirect_url
        })
        .catch(error => {
            console.error('Error: ', error);
        });
    });
});