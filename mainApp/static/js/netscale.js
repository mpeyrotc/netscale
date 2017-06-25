function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function submitEmail(email_address) {
    $(document).ready(function () {
        $.ajax({
            type: "POST",
            url: "add-email",
            data: {
                'csrfmiddlewaretoken': getCookie('csrftoken'),
                'email_address': email_address},
            dataType: "json",
            cache: false
        });
    });
}

function submitContacts(contacts) {
    console.log(JSON.stringify(contacts));
    $(document).ready(function () {
        $.ajax({
            type: "POST",
            url: "add-contacts",
            data: {
                'csrfmiddlewaretoken': getCookie('csrftoken'),
                'results': JSON.stringify(contacts)},
            dataType: "json",
            cache: false
        });
    });
}
