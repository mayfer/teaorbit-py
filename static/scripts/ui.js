function UI() {
    var this_ui = this;
    
    this.networking = window.networking;

    this.flags = {
        chatCssUpdated: false,
    }

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
                $(this).find('input[name="session"]').val(window.session_id);
                $(this).find('input[name="chatroom"]').val(window.chatroom);
                var form = $(this).serializeJSON();
                window.networking.send('post_spiel', form);

                $(this).find('input[name="spiel"]').val('');
            }
        });

        $('#show-map').click(function(e){
            e.preventDefault();
            this_ui.toggle_map();
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

        if(this.flags.chatCssUpdated == false && $('#chat').height() >= $(window).height()) {
            $('#chat').css('top', '0');
            this.flags.chatCssUpdated = true;
        }

        $('.date').timeago();
        window.last_id = spiel.id;
        this_ui.scroll();
    }

    this.scroll = function() {
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    }

    this.reset = function() {
        $('#chat .inner').html('');
    }
    this.set_map_url = function(url) {
        $('.map').attr('src', url);
    }
    this.toggle_map = function() {
        $('#map-expanded').toggleClass('show');
        $('#show-map').toggleClass('show');
    }

    return this;
}
