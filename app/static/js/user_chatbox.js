var message_counter = 0;
var primary_lang = '{{ primary_lang }}';
var used_lang = primary_lang;

// apology_text = {
//     'en': "I am sorry that it wasn\'t helpful.", 
//     'ms': "apology_text ms", 
//     'zh-cn': "apology_text zh-cn", 
//     'ta': "apology_text ta"
// };
// appreciation_text = {
//     'en': "I am happy to help!", 
//     'ms': "app_t ms", 
//     'zh-cn': "app_t zh-cn", 
//     'ta': "app_t ta"
// };
// confirmation_text = {
//     'en': "Sorry, I am still learning and not that capable yet, are you asking about one of these? Or you can rephrase your question.", 
//     'ms': "confirmation text ms", 
//     'zh-cn': "confirmation text zh-cn", 
//     'ta': "confirmation text ta"
// };
// contact_information_text = {
//     'en': "You can email testing@gmail.com for more info or try to rephrase your question to help me understand it better.", 
//     'ms': "contact info text ms", 
//     'zh-cn': "contact info text zh-cn", 
//     'ta': "contact info text ta"
// };
// error_message = {
//     'en': "Sorry, something is not right.", 
//     'ms': "error message ms", 
//     'zh-cn': "error message zh-cn", 
//     'ta': "error message ta"
// };
// contact_admin = {
//     'en': 'None, contact admin', 
//     'ms': 'contact admin ms', 
//     'zh-cn': 'contact admin zh-cn', 
//     'ta': 'contact admin ta'
// }

apology_text = get_apology_text();
appreciation_text = get_appreciation_text();
confirmation_text = get_confirmation_text();
contact_information_text = get_contact_information_text();
error_message = get_error_message();
contact_admin = get_contact_admin();
selection_responses = {[contact_admin]: 'You can email testing@gmail.com for more info'}; // not used

const message_loader = '<div class="loader"><span></span><span></span><span></span></div>';



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

    getBotResponse(raw_text='opening dummy', opening=true)
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

function sanitize(string) {
    return document.createElement('div').appendChild(document.createTextNode(string)).parentNode.innerHTML;
}

function getBotResponse(raw_text='', opening=false) {
    var is_selection = (raw_text.length != 0) | opening // to prevent feedback mechanism from being added

    var current_message_counter = message_counter;
    message_counter += 1;
    if (!is_selection) {
        var raw_text = $("#textInput").val();
        raw_text = sanitize(raw_text);
        $("#textInput").val("");
    
        document.getElementById('hack').innerHTML = "";
        autoResize(document.getElementById('textInput'));
    }

    if (!opening) sendMessage(raw_text, 'user', current_message_counter);
    // https://img.icons8.com/office/23/fa314a/dots-loading--v3.png
    // static/img/loading.gif
    // var botTextObj = sendMessage('<img src="https://img.icons8.com/office/23/fa314a/dots-loading--v3.png"/>', 'bot', current_message_counter);
    var botTextObj = sendMessage(message_loader, 'bot', current_message_counter);
    reply(raw_text, botTextObj, current_message_counter, is_selection, opening);
}

var haha;
function selection_clicked(obj, is_selection=false) {
    haha = obj;
    var selection_text = obj.innerText;
    // sendMessage(selection_responses[selection_text], 'bot', '');
    if (is_selection) {
        var sibling_nodes = obj.parentNode.parentNode.childNodes;
        sibling_nodes.forEach(clearAllEvent);
    }
    getBotResponse(selection_text);
}

const timer = ms => new Promise(res => setTimeout(res, ms))

async function reply(utterence, target, current_message_counter, is_selection, opening=false) {
    const ti = document.getElementById("textInput")
    ti.disabled = true;
    const old_placeholder = ti.placeholder;
    ti.placeholder = 'thinking...';

    await $.post('/reply', {
        'utterence': utterence, 
        'is_selection': is_selection, 
        'opening': opening
    }).done(function(response_all) {
        thumbsdownId = "thumbsdown_" + current_message_counter;
        thumbsupId = "thumbsdown_" + current_message_counter;
        userMessageId = "userText_" + current_message_counter;
        if (!opening) document.getElementById(userMessageId).setAttribute('message_id', response_all['id']);
        used_lang = response_all['lang'];
        
        response = response_all['prediction'];
        returned_selections = response_all['selections'];
        unique_selection = response_all['unique_selection'];

        if (returned_selections.length == 0) {
            // var thumbsdown_icon = 'thumbsdown fa fa-thumbs-down fa-lg';
            // var thumbsup_icon = 'thumbsup fa fa-thumbs-up fa-lg';

            // var thumbs_container = ''
            // if (!is_selection) {
            //     thumbs_container = 
            //     `
            //     <div class='thumbs_container'>
            //         <!-- <input class="thumbsdown" id="${thumbsdownId}" type="image" alt='thumbs down' src="https://img.icons8.com/material-sharp/15/fa314a/thumbs-down.png" onclick="getPredictedWrongMessage(this.id, 'negative')"> -->
            //         <!-- <input class="thumbsup" id="${thumbsupId}" type="image" alt='thumbs up' src="https://img.icons8.com/material-rounded/15/26e07f/thumb-up.png" onclick="getPredictedWrongMessage(this.id, 'positive')"> -->
            //         <button class="${thumbsdown_icon}" id="${thumbsdownId}" type="button" 
            //             onclick="sendMessage('&#128078;', 'user', '');getPredictedWrongMessage(this.id, 'negative')">
            //         <button class="${thumbsup_icon}" id="${thumbsupId}" type="button" 
            //             onclick="sendMessage('&#128077;', 'user', '');getPredictedWrongMessage(this.id, 'positive')">                    
            //     </div>
            //     `
            // }

            // target.innerHTML = 
            // `
            // <span>
            //     <span>
            //         ${response[0]['reply']}
            //     </span>
            //     ${thumbs_container}
            // </span>
            // `;
            // scroll(target);
            sendMultipleMessages(response, target, is_selection, current_message_counter);

        } else {
            selectionBox = document.createElement('div');
            selectionBox.className = 'selection-box';

            // it is not necessary to preload confirmation_text, we can return it as response, but this is done earlier, so...
            var prompt_message = confirmation_text[used_lang];
            var confusion = response.length == 0;
            if (!confusion) prompt_message = response[0]['reply'];
            target.innerHTML = `<span><span>${prompt_message}</span></span>`;

            response = returned_selections; // lazy to change name
            if (!is_selection) {
                response[response.length] = {'reply': selection_responses[contact_admin], 'nearest_message': contact_admin[used_lang]};
            }

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

            if (!is_selection) {
                selection.classList.toggle('rejected');
                selection.id = 'contactAdminSelection_' + current_message_counter;
                selection.firstChild.addEventListener('click', event => sendMessage(event.target.innerHTML, 'user', ''));
            }

            scroll(selection);

            // selections.forEach(item => {
            //     item.firstChild.addEventListener('click', event => sendMessage(event.target.innerHTML, 'user', ''));
            // });

            if (!is_selection) {
                selection.firstChild.onclick = function() {
                    getPredictedWrongMessage(this.parentNode.id, 'negative');
                };
            }


            // selections.forEach(item => { ####previously used
            // 	item.addEventListener('click', event => selection_clicked(event.target));
            // });
            var loop_i = selections.length;
            if (!is_selection) loop_i = selections.length-1;
            for (i = 0; i < loop_i; i++) {
                var item = selections[i];
                item.firstChild.addEventListener('click', event => selection_clicked(event.target, unique_selection)); // is_selection||!confusion
            }

        }

    }).fail(function(response) {
        console.log(response);
        target.querySelector('span span').innerHTML = error_message[used_lang];
        scroll(target);
    });

    ti.placeholder = old_placeholder;
    ti.disabled = false;
}

async function sendMultipleMessages(response, target, is_selection, current_message_counter) {
    // careful, there will be several botText with the same id
    var thumbsdown_icon = 'thumbsdown fa fa-thumbs-down fa-lg';
    var thumbsup_icon = 'thumbsup fa fa-thumbs-up fa-lg';
    var response_message = response[0]['reply'].split('___n__');
    
    for (var i = 0; i < response_message.length-1; i++) {
        var current_message = response_message[i].trim()
        await timer(current_message.split(' ').length * 60000/250);
        sendMessage(current_message, 'bot', 'none', target);
        scroll(target);
    }
    var last_message = response_message[response_message.length-1].trim();
    await timer(last_message.split(' ').length * 60000/375);

    var thumbs_container = ''
    if (!is_selection) {
        thumbs_container = 
        `
        <div class='thumbs_container'>
            <!-- <input class="thumbsdown" id="${thumbsdownId}" type="image" alt='thumbs down' src="https://img.icons8.com/material-sharp/15/fa314a/thumbs-down.png" onclick="getPredictedWrongMessage(this.id, 'negative')"> -->
            <!-- <input class="thumbsup" id="${thumbsupId}" type="image" alt='thumbs up' src="https://img.icons8.com/material-rounded/15/26e07f/thumb-up.png" onclick="getPredictedWrongMessage(this.id, 'positive')"> -->
            <button class="${thumbsdown_icon}" id="${thumbsdownId}" type="button" 
                onclick="sendMessage('&#128078;', 'user', '');getPredictedWrongMessage(this.id, 'negative')">
            <button class="${thumbsup_icon}" id="${thumbsupId}" type="button" 
                onclick="sendMessage('&#128077;', 'user', '');getPredictedWrongMessage(this.id, 'positive')">                    
        </div>
        `
    }

    target.innerHTML = 
    `
    <span>
        <span>
            ${last_message}
        </span>
        ${thumbs_container}
    </span>
    `;
    scroll(target);
}

function clearAllEvent(old_element) {
    if (!old_element.classList.contains('rejected')) {
        var new_element = old_element.cloneNode(true);
        new_element.classList.add('no-event');
        old_element.parentNode.replaceChild(new_element, old_element);
    }
}

function scroll(id) {
    var temp = (typeof(id) == 'object')? id: document.getElementById(id);
    temp.scrollIntoView({block: 'start', behavior: 'smooth'});
}

function sendMessage(message, subject, current_message_counter, position=null) {
    var textId = `${subject}Text_${current_message_counter}`;
    var message_box = document.createElement('div');
    message_box.className = subject + 'Text';
    message_box.id = textId;
    message_box.innerHTML = `<span><span>${message}</span></span>`;

    var areas = document.getElementsByClassName('area');
    var last_area = areas[areas.length-1];
    current_area_class = subject + 'Area';
    if (last_area.classList.contains(current_area_class)) {
        if (position) position.parentNode.insertBefore(message_box, position);
        else last_area.append(message_box);
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
        apology = sendMessage(apology_text[used_lang], 'bot', 'none');
    } else {
        apology = sendMessage(appreciation_text[used_lang], 'bot', 'none');
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
            sendMessage(contact_information_text[used_lang], 'bot', 'none')
        }
    }).fail(function() {
        apology.innerHTML = "<span><span>I am sorry, something is wrong. Feedback is not captured.</span></span>"
    });
    
    scroll(apology);
}