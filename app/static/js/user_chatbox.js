var message_counter = 0;
apology_text = "I am sorry that it wasn\'t helpful.";
appreciation_text = "I am happy to help!";
error_message = "Sorry, something is not right."

contact_admin = 'None, contact admin';
selection_responses = {[contact_admin]: 'You can email testing@gmail.com for more info'};



$(document).ready(function() {
    chatboxInit();
})

function chatboxInit() {
    $("#textInput").keyup(function(e) {
        $("#textInput").val($('#textInput').val().replace(/\n/, ''));
        if ((e.keyCode === 10 || e.which == 13) && $("#textInput").val().length != 0){
            document.activeElement.blur();
            getBotResponse();
        }
    });
    
    $("#buttonInput").click(function() {
        if ($("#textInput").val().length != 0) {
            getBotResponse();
        }
    })

    $('#textInput').focus(function() {
        $('#userInput').addClass('userInput_focus');
    })

    $('#textInput').focusout(function() {
        $('#userInput').removeClass('userInput_focus');
    })

    autoResize(document.getElementById('textInput'));

    preventZoomOnInput();
}


var limit_reached = false;

function autoResize(target) {
    var hack = document.getElementById('hack');
    // hack.style.maxWidth = (Math.floor(target.offsetWidth) - 2*10 - 1) + 'px';

    if (document.getElementById('chatbox').offsetHeight <= 130 || limit_reached) {
        limit_reached = true;
        target.style.height = 'auto';
        return;
    }

    hack.innerHTML=target.value.replace(/\n/, '');

    if ((! target.value) && (detectBrowser() != 'Firefox')) {
        target.style.height = 'auto';
    } else {
        target.style.height = (Math.min(hack.offsetHeight, 54) + 0.99) + 'px';
    }
}

function getBotResponse() {
    var current_message_counter = message_counter;
    message_counter += 1;

    var raw_text = $("#textInput").val();
    $("#textInput").val("");

    document.getElementById('hack').innerHTML = "";
    autoResize(document.getElementById('textInput'));

    sendMessage(raw_text, 'user', current_message_counter);
    // https://img.icons8.com/office/23/fa314a/dots-loading--v3.png
    // static/img/loading.gif
    // var botTextObj = sendMessage('<img src="https://img.icons8.com/office/23/fa314a/dots-loading--v3.png"/>', 'bot', current_message_counter);
    var botTextObj = sendMessage('<div class="loader"><span></span><span></span><span></span></div>', 'bot', current_message_counter);
    reply(raw_text, botTextObj, current_message_counter);
}

function selection_clicked(obj) {
    var selection_text = obj.innerText;
    sendMessage(selection_responses[selection_text], 'bot', '');
}

function reply(utterence, target, current_message_counter) {
    $.post('/reply', {
        'utterence': utterence
    }).done(function(response_all) {
        thumbsdownId = "thumbsdown_" + current_message_counter;
        thumbsupId = "thumbsdown_" + current_message_counter;
        userMessageId = "userText_" + current_message_counter;
        document.getElementById(userMessageId).setAttribute('message_id', response_all['id']);
        
        response = response_all['prediction'];
        if (response.length == 1) {
            var thumbsdown_icon = 'thumbsdown fa fa-thumbs-down fa-lg';
            var thumbsup_icon = 'thumbsup fa fa-thumbs-up fa-lg';

            target.innerHTML = 
            `
            <span>
                <span>
                    ${response[0]['reply']}
                </span>
                <div class='thumbs_container'>
                    <!-- <input class="thumbsdown" id="${thumbsdownId}" type="image" alt='thumbs down' src="https://img.icons8.com/material-sharp/15/fa314a/thumbs-down.png" onclick="getPredictedWrongMessage(this.id, 'negative')"> -->
                    <!-- <input class="thumbsup" id="${thumbsupId}" type="image" alt='thumbs up' src="https://img.icons8.com/material-rounded/15/26e07f/thumb-up.png" onclick="getPredictedWrongMessage(this.id, 'positive')"> -->
                    <button class="${thumbsdown_icon}" id="${thumbsdownId}" type="button" 
                        onclick="sendMessage('&#128078;', 'user', '');getPredictedWrongMessage(this.id, 'negative')">
                    <button class="${thumbsup_icon}" id="${thumbsupId}" type="button" 
                        onclick="sendMessage('&#128077;', 'user', '');getPredictedWrongMessage(this.id, 'positive')">                    
                </div>
            </span>
            `;
            scroll(target);
        } else {
            selectionBox = document.createElement('div');
            selectionBox.className = 'selection-box';
            target.innerHTML = `<span><span>${"Sorry, I am still learning and not that capable yet, are you asking about one of these? Or you can rephrase your question."}</span></span>`;
            response[response.length] = {'reply': selection_responses[contact_admin], 'nearest_message': contact_admin};
            var selection;
            var selections = [];
            for (i = 0; i < response.length; i++){
                selection = document.createElement('div');
                selection_responses[response[i]['nearest_message']] = response[i]['reply'];
                selection.className = 'selection';
                selection.innerHTML = `<span>${response[i]['nearest_message']}</span>`;
                selectionBox.appendChild(selection);
                selections.push(selection);
            }
            
            target.append(selectionBox);

            selection.classList.toggle('rejected');
            selection.id = 'contactAdminSelection_' + current_message_counter;
            scroll(selection);

            selections.forEach(item => {
                item.firstChild.addEventListener('click', event => sendMessage(event.target.innerHTML, 'user', ''));
            });

            selection.firstChild.onclick = function() {
                getPredictedWrongMessage(this.parentNode.id, 'negative');
            };


            // selections.forEach(item => { ####previously used
            // 	item.addEventListener('click', event => selection_clicked(event.target));
            // });
            for (i = 0; i < selections.length-1; i++) {
                var item = selections[i];
                item.firstChild.addEventListener('click', event => selection_clicked(event.target));
            }

        }

    }).fail(function() {
        target.querySelector('span span').innerHTML = error_message;
    });
}

function scroll(id) {
    var temp = (typeof(id) == 'object')? id: document.getElementById(id);
    temp.scrollIntoView({block: 'start', behavior: 'smooth'});
}

function sendMessage(message, subject, current_message_counter) {
    var textId = `${subject}Text_${current_message_counter}`;
    var message_box = document.createElement('div');
    message_box.className = subject + 'Text';
    message_box.id = textId;
    message_box.innerHTML = `<span><span>${message}</span></span>`;

    var areas = document.getElementsByClassName('area');
    var last_area = areas[areas.length-1];
    current_area_class = subject + 'Area';
    if (last_area.classList.contains(current_area_class)) {
        last_area.append(message_box);
    } else {
        new_area = document.createElement('div');
        new_area.className = 'area';
        new_area.classList.toggle(current_area_class);
        new_area.append(message_box);
        $("#chatbox").append(new_area);
    }
    
    scroll(message_box);
    return message_box;
}

function getPredictedWrongMessage(id, feedback) {
    console.log(id);
    var index = id.split("_")[1];
    var predictedWrongMessageId = "userText_"+index;
    var predictedWrongMessage = document.getElementById(predictedWrongMessageId);
    var db_message_id = predictedWrongMessage.getAttribute('message_id');
    var wrongResponseId = "botText_"+index;

    var apology;
    if (feedback=='negative') {
        apology = sendMessage(apology_text, 'bot', 'none');
    } else {
        apology = sendMessage(appreciation_text, 'bot', 'none');
    }

    $.post('/capture', {
        'message_id': db_message_id, 
        'feedback': feedback
    }).done(function(response) {
        // if (feedback=='positive') {
        // 	predictedWrongMessage.querySelector("span span").style.backgroundColor='green';
        // } else {
        // 	predictedWrongMessage.querySelector("span span").style.backgroundColor='red';
        // }
        
        to_remove = document.getElementById(id);
        if (!id.includes('contactAdminSelection')) {
            to_remove = to_remove.parentNode
        }
        to_remove.parentNode.removeChild(to_remove);
        if (feedback=='negative') {
            sendMessage('You can email testing@gmail.com for more info or try to rephrase your question to help me understand it better.', 'bot', 'none')
        }
    }).fail(function() {
        apology.innerHTML = "<span><span>I am sorry, something is wrong. Feedback is not captured.</span></span>"
    });
    
    scroll(apology);
}