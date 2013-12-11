function UI() {
    var this_ui = this;

    function toHashtagUrl(hashtag) {
        var full = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '');
        return full + '/' + hashtag;
    }

    this.flags = {
        chatCssUpdated: false,
        windowFocused: true,
        newMessages: 0,
    }

    this.global_cookie = function(key, val) {
        if(val === undefined) {
            return JSON.parse(window.localStorage.getItem(key));
        } else {
            window.localStorage.setItem(key, JSON.stringify(val));
        }
    }

    this.cookie = function(key, val) {
        if($.cookie('teaorbit')) {
            var cookie = JSON.parse($.cookie('teaorbit'));
        } else {
            var cookie = {};
        }

        if(val === undefined) {
            if(window.chatroom in cookie && key in cookie[window.chatroom]) {
                return cookie[window.chatroom][key];
            } else {
                return undefined;
            }
        } else {
            if(!(window.chatroom in cookie)) {
                cookie[window.chatroom] = {}
            }
            cookie[window.chatroom][key] = val;
            return $.cookie('teaorbit', JSON.stringify(cookie), { expires: 1000, path: '/' });
        }
    }

    this.mute = function() {
        $('#audio').addClass('icon-volume-mute').removeClass('icon-volume-medium');
        this_ui.flags.mute = true;
        this_ui.global_cookie('mute', this_ui.flags.mute);
    }
    this.unmute = function() {
        $('#audio').addClass('icon-volume-medium').removeClass('icon-volume-mute');
        this_ui.flags.mute = false;
        this_ui.global_cookie('mute', this_ui.flags.mute);
    }
    
    this.setup_audio = function() {
        $('<audio id="notification"><source src="/static/notification.ogg" type="audio/ogg"><source src="/static/notification.mp3" type="audio/mpeg"><source src="/static/notification.wav" type="audio/wav"></audio>').appendTo('body');

        var mute = this_ui.global_cookie('mute');
        if(mute === true) {
            this_ui.mute()
        } else {
            this_ui.unmute()
        }
        $('#audio').bind('touchstart click', function(e){
            e.preventDefault();
            if(this_ui.flags.mute === true) {
                this_ui.unmute()
            } else {
                this_ui.mute()
            }
        });
    }

    this.init = function() {
        this.setup_audio();

        if(window.chatroom) {
            window.networking = Networking();

            window.latitude = 0;
            window.longitude = 0;
            window.gps_accuracy = 0;

            $('#loader').hide();
            var recent = this.global_cookie('recent_channels');
            if(!recent){ recent = {}; }
            recent[window.chatroom] = true;
            this.global_cookie('recent_channels', recent);
        } else {
            navigator.geolocation.getCurrentPosition(function(position){
                window.latitude = position.coords.latitude;
                window.longitude = position.coords.longitude;
                window.gps_accuracy = position.coords.accuracy;

                window.networking = Networking();
                $('#loader').hide();
            });
        }

        $('#chat, #channels').css('margin', $('#header').outerHeight()+'px 0 '+$('#post').outerHeight()+'px 0');


        $('#type-here').keydown(function(e) {
            if (e.keyCode == 13) {
                e.preventDefault();
                $(this.form).submit();
             }
        });

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

                $(this).find('textarea[name="spiel"]').val('').trigger('autosize.resize');
            }
            else {
                alert("No location data. Please allow the browser geolocation access.");
            }
        });

        var name = this_ui.cookie("name");
        if(name) {
            $('#name').val(name);
        }
        $('#name').change(function(e){
            var name = $('input[name="name"]').val();
            this_ui.cookie("name", name);
        });

        $('#show-map').bind('click touchstart', function(e){
            e.preventDefault();
            this_ui.toggle_map();
        });

        $('#channels .toggle').bind('click touchstart', function(e){
            e.preventDefault();
            $(this).toggleClass('expanded');
            if($(this).hasClass('expanded')) {
                this_ui.global_cookie('channels_expanded', true);
            } else {
                $('#channels').css('top', '');
                this_ui.global_cookie('channels_expanded', false);
            }
            $('#channels .inner').toggle(0, function(){
                if($('#channels').height() >= ($(window).height() - $('#header').height() - $('#post').height() )) {
                    $('#channels').css('top', '0px');
                }
            });

        });

        $(window).focus(function(e){
            document.title = window.title;
            this_ui.flags.windowFocused = true;
            this_ui.flags.newMessages = 0;
        });
        $(window).blur(function(e){
            this_ui.flags.windowFocused = false;
        });

        this.show_recent_channels();
        var show_channels = this_ui.global_cookie('channels_expanded');
        if(show_channels) {
            $('#channels .toggle').click();
        }

        var online_elem = $('#num-online');
        var offset = online_elem.offset();
        $('<div>').attr('id', 'online-users').css({
            'position': 'absolute',
            'top': (offset.top + online_elem.height()) + 'px',
            'left': (offset.left) + 'px',
            'width': (online_elem.outerWidth() + $('#show-map').outerWidth()) + "px",
        }).appendTo('body');
        $('#num-online').click(function(e){
            e.preventDefault();
            $('#online-users').toggle();
        });

        $.timeago.settings.allowFuture = true;
        $('textarea').autosize();
    }

    this.show_recent_channels = function() {
        var container = $('#channels .inner').html('');
        var recent_channels = this.global_cookie('recent_channels');
        $.each(recent_channels, function(channel, enabled) {
            if(enabled == true) {
                var channelelem = $('<div>').addClass('channel');

                var nameelem = $('<span>').html('#'+channel).appendTo(channelelem);

                if(channel == window.chatroom) {
                    $('<span>').addClass('current').html("[current]").appendTo(channelelem);
                } else {
                    //var remove = $('<a>').attr('href', '#').addClass('remove').html("&times;").appendTo(channelelem);
                }
                channelelem.appendTo(container);

            }
        });
        var removes = container.find('.remove');
        removes.bind('click', function(e){
            var channel = $(this).data('name');
            delete recent_channels[channel];
            this_ui.global_cookie('recent_channels', recent_channels);

        });
        container.linkify(toHashtagUrl);
    }

    this.add_spiel = function(spiel, notify) {
        var chat = $('#chat .inner');
        var row = $('<div>').addClass('row');
        var date = new Date(spiel.date);
        var color = spiel.color;
        var datestring = date.toLocaleString()
        var text;

        if(notify === undefined) {
            notify == false;
        }

        if(notify === true && this.flags.windowFocused == false && this.flags.mute == false) {
            $('#notification')[0].play();
            if(this.flags.windowFocused == false) {
                this.flags.newMessages++;
                document.title = "(" + this.flags.newMessages + ") " + window.title;
            }
        }

        var message = $('<div>').addClass('message');
        if(color) {
            var color_elem = $('<span>').addClass('color').css('background', color);
            message.append(color_elem);
        }
        if(spiel.name) {
            message.append($("<span>").addClass('name').html(escapeHtml(spiel.name)));
        }
        message.append(escapeHtml(spiel.spiel));
        

        var date_elem = $('<time>').addClass('date').attr('datetime', datestring).data('timestamp', spiel.date).html(datestring);

        row.append(message);
        row.append(date_elem);
        chat.append(row);

        row.linkify(toHashtagUrl);
        row.find('time').timeago();


        if(this.flags.chatCssUpdated == false && $('#chat').height() >= $(window).height()) {
            $('#chat').css('top', '0');
            this.flags.chatCssUpdated = true;
        }

        if(window.last_spiel_date < spiel.date) {
            window.last_spiel_date = spiel.date;
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
