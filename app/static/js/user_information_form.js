var yo;


$(document).ready(function() {

    // why doesn't this work?
    // for (field in ['user_email', 'user_name']) {
    //     $('#'+field).keyup(function(event) {
    //         document.getElementById('form-error-message_'+field).innerText = '12345';
    //     })
    // };

    $('#user_email').keyup(function(event) {
        document.getElementById('form-error-message_user_email').innerText = '';
    })

    $('#user_name').keyup(function(event) {
        document.getElementById('form-error-message_user_name').innerText = '';
    })
    // $("#user_email").keyup(function(event) {
    //     var user_email = document.getElementById('user_email');
    //     if (check_email_validity(user_email.value)) {
    //         user_email.setCustomValidity('');
    //     } else {
    //         user_email.setCustomValidity('Invalid field.');
    //     }
    // });


    $("#user-info-form").submit(function(event){
        event.preventDefault();
        var error = {};

        var post_url = $(this).attr("action");
        var serialized_form = $(this).serializeArray()

        var form_data = {};
        for (i = 0; i < serialized_form.length; i++) {
            form_data[serialized_form[i]['name']] = serialized_form[i]['value']
        }

        //validation
        var user_email = document.getElementById('user_email');
        if (!user_email.validity.valid) {
            if (user_email.validity.valueMissing) error['user_email'] = 'Please fill in your email address';
            else error['user_email'] = 'Please fill in a valid email address';
        }

        if (!form_data['user_name']) error['user_name'] = 'Please fill in your name';

        console.log(form_data);

        if (!$.isEmptyObject(error)) {
            mark_error(error);
            return false;
        }

        //ajax
        $.post(post_url, form_data)
        .done(function(response) {
            console.log(response);
            if (response['code'] == 200) {
                //change innerhtml later
                document.getElementById('chatsection').innerHTML = response['chatbox'];
                $("#textInput").keypress(function(e) {
                    if (e.which == 13 && $("#textInput").val().length != 0){
                        getBotResponse();
                    }
                });
                
                $("#buttonInput").click(function() {
                    if ($("#textInput").val().length != 0) {
                        getBotResponse();
                    }
                })
            } else {
                mark_error(response['error']);
            }
            
        })
        .fail(function() {
            document.getElementById('form-error-message_submit').innerText = 'Sorry, something is not right.';
        });
    });

})

mark_error = function(error) {
    for (const [key, value] of Object.entries(error)) {
        document.getElementById('form-error-message_'+key).innerText = value;
    }
}

// check_email_validity = function(user_email) {
//     var emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
//     if (user_email.match(emailRegex)) return true;
//     return false;
// }
