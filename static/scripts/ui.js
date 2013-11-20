UI = {

    init: function() {
        $('#chat .inner').css('margin', $('#header').outerHeight()+'px 0 '+$('#post').outerHeight()+'px 0');

        $('#post form').on('submit', function(e){
            e.preventDefault();
            var latitude = window.latitude;
            var longitude = window.longitude;
            var accuracy = window.gps_accuracy;
            
            if(!latitude || !longitude) {
                alert("No location data. Please allow the browser geolocation access.");
            } else if(accuracy > 200) {
                alert("Location data not accurate enough.");
            } else {
                $(this).find('input[name="latitude"]').val(latitude);
                $(this).find('input[name="longitude"]').val(longitude);
                $(this).find('input[name="session"]').val(window.network.session_id);
                var form = $(this).serializeJSON();
                window.network.send('post_spiel', form);

                $(this).find('input[name="message"]').val('');
            }
        });
    },

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
