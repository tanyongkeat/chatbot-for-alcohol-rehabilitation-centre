function show_edit_space(id, category) {
    var index = id.split("_")[1];
    var editable_display = document.getElementById(category+'-display_'+index);
    editable_display.style.display = "None";
    var editable_edit = document.getElementById(category+'-edit_'+index);
    editable_edit.style.display = "block";

    var editable_content = document.getElementById(category+'-e_'+index);
    editable_content.focus();
    var strLength = editable_content.value.length * 2;
    editable_content.setSelectionRange(strLength, strLength);
}

function cancel_edit_space(id, category) {
    var index = id.split("_")[1];
    var editable_display = document.getElementById(category+'-display_'+index);
    editable_display.style.display = "block";
    var editable_edit = document.getElementById(category+'-edit_'+index);
    editable_edit.style.display = "None";

    var editable_content = document.getElementById(category+'-e_'+index);
    editable_content.value = editable_content.getAttribute('ori_value');
}
