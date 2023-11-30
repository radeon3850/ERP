// sweet-alert after closed of order client
function showConfirmation1(orderId) {
    Swal.fire({
        title: 'Вы уверенны?',
        text: "Закрыть заказ клиента!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#5cb360',
        cancelButtonColor: '#e94441',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!'
    }).then((result) => {
        if (result.isConfirmed) {
            const data = {
                q: orderId
            };

            fetch('/order_finish_work', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // refrech check-box button
                    $('#closecustomCheck').prop('checked', true).prop('disabled', true);
                    $('#closedisabledbutton').prop('disabled', true);
                } else if (result.redirect) {
                    window.location.href = result.redirect;  // redirec next page
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });
    // change collor of button
    $('.swal2-cancel').removeClass('bg-gradient-danger').addClass('bg-gradient-primary btn').text('Нет, отменить!');

    // change text collor
    $('.swal2-confirm').removeClass('bg-gradient-success').addClass('bg-gradient-primary btn').text('Да, Закрыть!');
}


    function showConfirmation(orderId) {
    Swal.fire({
        title: 'Вы уверенны?',
        text: "Утвердить заказ клиента!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#5cb360',
        cancelButtonColor: '#e94441',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!'
    }).then((result) => {
        if (result.isConfirmed) {
            const data = {
                q: orderId
            };
            fetch('/approved', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // Update checkbox and button state
                    $('#customCheck').prop('checked', true).prop('disabled', true);
                    $('#disabledbutton').prop('disabled', true);
                } else if (result.redirect) {
                    window.location.href = result.redirect;  // Redirection to another page
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });

    // Change the text of the cancel button
    $('.swal2-cancel').removeClass('bg-gradient-danger').addClass('bg-gradient-primary btn').text('Нет, отменить!');

    // Change the confirmation button text
    $('.swal2-confirm').removeClass('bg-gradient-success').addClass('bg-gradient-primary btn').text('Да, утвердить заказ!');
}

