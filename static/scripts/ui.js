function UI() {
    var this_ui = this;

    this.init = function() {
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

                $(this).find('input[name="spiel"]').val('');
            }
        });
    }

    this.add_spiel = function(spiel) {
        var chat = $('#chat .inner');
        var row = $('<div>').addClass('row');
        var date = new Date(spiel.date*1000);
        var datestring = date.toLocaleString()
        var text;
        if(spiel.name) {
            text = "<span class='name'>" + escapeHtml(spiel.name) + "</span> " + escapeHtml(spiel.spiel);
        } else {
            text = escapeHtml(spiel.spiel);
        }
        row.append( $('<div>').addClass('message').html(text) );
        row.append( $('<div>').addClass('date').attr('title', datestring).html(spiel.date) );
        chat.append(row);
        $('.date').timeago();
        window.last_id = spiel.id;
        this_ui.scroll();
    }

    this.scroll = function() {
        $(document).scrollTop($(document).height());
    }

    this.reset = function() {
        $('#chat .inner').html('');
    }

    return this;
}
