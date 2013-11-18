UI = {
    init: function(){},
    add_messages: function(messages) {
        var chat = $('#chat .inner');
        for(var i=0; i<messages.length; i++) {
            var row = $('<div>').addClass('row');
            var date = new Date(messages[i].date*1000);
            var datestring = date.toLocaleString()
            var message;
            if(messages[i].name) {
                message = "<span class='name'>" + escapeHtml(messages[i].name) + "</span> " + escapeHtml(messages[i].message);
            } else {
                message = escapeHtml(messages[i].message);
            }
            row.append( $('<div>').addClass('message').html(message) );
            row.append( $('<div>').addClass('date').attr('title', datestring).html(messages[i].date) );
            chat.append(row);
            $('.date').timeago();
        }
        if(messages.length > 0) {
            window.last_id = messages[messages.length-1].id;
        } else {
            window.last_id = 0;
        }
        scroll();
    },
}
