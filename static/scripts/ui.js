function UI() {
    var this_ui = this;
    
    this.networking = window.networking;

    this.flags = {
        chatCssUpdated: false,
        windowFocused: true,
        newMessages: 0,
    }

    this.init = function() {
        $('#chat .inner').css('margin', $('#header').outerHeight()+'px 0 '+$('#post').outerHeight()+'px 0');

        $('#post form').on('submit', function(e){
            e.preventDefault();
            var latitude = window.latitude;
            var longitude = window.longitude;
            var chatroom = window.chatroom
            var accuracy = window.gps_accuracy;
            
            if(chatroom || (latitude && longitude)) {
                $(this).find('input[name="latitude"]').val(latitude);
                $(this).find('input[name="longitude"]').val(longitude);
                $(this).find('input[name="chatroom"]').val(chatroom);
                var form = $(this).serializeJSON();
                window.networking.send('post_spiel', form);

                $(this).find('input[name="spiel"]').val('');
            }
            else {
                alert("No location data. Please allow the browser geolocation access.");
            }
        });

        var name = $.cookie("name");
        if(name) {
            $('#name').val(name);
        }
        $('#name').change(function(e){
            var name = $('input[name="name"]').val();
            $.cookie("name", name);
        });

        $('#show-map').click(function(e){
            e.preventDefault();
            this_ui.toggle_map();
        });

        $(window).focus(function(e){
            document.title = window.title;
            this_ui.flags.windowFocused = true;
            this_ui.flags.newMessages = 0;
        });
        $(window).blur(function(e){
            this_ui.flags.windowFocused = false;
        });
    }

    this.add_spiel = function(spiel) {
        var chat = $('#chat .inner');
        var row = $('<div>').addClass('row');
        var date = new Date(spiel.date);
        var color = spiel.color;
        var datestring = date.toLocaleString()
        var text;

        var message = $('<div>').addClass('message');
        if(color) {
            var color_elem = $('<span>').addClass('color').css('background', color);
            message.append(color_elem);
        }
        if(spiel.name) {
            message.append($("<span>").addClass('name').html(escapeHtml(spiel.name)));
        }
        message.append(escapeHtml(spiel.spiel));
        

        row.append(message);
        row.append( $('<div>').addClass('date').attr('title', datestring).html(spiel.date) );
        chat.append(row);

        function toHashtagUrl(hashtag) {
            return "http://teaorbit.com/" + hashtag;
        }
        row.linkify(toHashtagUrl);

        if(this.flags.chatCssUpdated == false && $('#chat').height() >= $(window).height()) {
            $('#chat').css('top', '0');
            this.flags.chatCssUpdated = true;
        }

        $('.date').timeago();
        window.last_id = spiel.id;

        if(this.flags.windowFocused == false) {
            this.flags.newMessages++;
            document.title = "(" + this.flags.newMessages + ") " + window.title;
        }

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
