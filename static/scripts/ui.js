function UI() {
    var this_ui = this;

    this.last_spiel_date = 0;
    this.first_spiel_date = 2147483648000;

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
        if(window.localStorage) {
            if(val === undefined) {
                return JSON.parse(window.localStorage.getItem(key));
            } else {
                window.localStorage.setItem(key, JSON.stringify(val));
            }
        } else {
            console.log("No local storage available");
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
        if(window.webkitNotifications !== undefined) {
            window.webkitNotifications.requestPermission();
        }
    }
    
    this.setup_audio = function() {
        $('<audio id="notification"><source src="'+window.static_url+'notification.ogg" type="audio/ogg"><source src="'+window.static_url+'notification.mp3" type="audio/mpeg"><source src="'+window.static_url+'notification.wav" type="audio/wav"></audio>').appendTo('body');

        var mute = this_ui.global_cookie('mute');
        if(mute === true) {
            this_ui.mute();
        } else {
            this_ui.unmute();
        }
        $('#audio').bind('touchend click', function(e){
            e.preventDefault();
            if(this_ui.flags.mute === true) {
                this_ui.unmute()
            } else {
                this_ui.mute()
            }
        });
    }

    this.init = function(client) {
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
            $('#loader').show();
            navigator.geolocation.getCurrentPosition(function(position){
                window.latitude = position.coords.latitude;
                window.longitude = position.coords.longitude;
                window.gps_accuracy = position.coords.accuracy;

                window.networking = Networking();
                $('#loader').hide();
            }, function(error){
                $('#loader .inner .title').html('<span class="error">Failed</span> getting location');
                $('#loader .inner .details').html('You probably have location services turned off.');
            });
        }


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
                $('#type-here').focus();
            } else {
                //alert("No location data. Please allow the browser geolocation access.");
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

        $('<div>').attr('id', 'online-users').appendTo('body');
        $('#num-online').bind('click touchstart', function(e){
            e.preventDefault();
            var online_elem = $('#num-online');
            var offset = online_elem.offset();
            $('#online-users')
                .css({
                    'position': 'absolute',
                    'top': (offset.top + online_elem.height()) + 'px',
                    'left': (offset.left - 100) + 'px',
                    'width': (online_elem.outerWidth() + $('#show-map').outerWidth() + 100) + "px",
                })
                .toggle();
        });

        $.timeago.settings.allowFuture = true;
        $('textarea').autosize();
        $('textarea').keydown(function (e) {
            this_ui.align_chat_window();
            this_ui.scroll();

            // enter key
            if (e.keyCode == 13 && !e.shiftKey) {
                $(this.form).submit();
                e.preventDefault();
                e.stopPropagation();
            }
         });
        $('input, textarea').bind('touchstart', function(e){
            $(this).focus();
        });
    }

    this.align_chat_window = function() {
        $('#chat').css('margin', $('#header').outerHeight()+'px 0 '+$('#post').outerHeight()+'px 0');
    }

    this.init_web_only_features = function() {
        this.align_chat_window();
    }

    this.init_ios_native_features = function() {
        function connectWebViewJavascriptBridge(callback) {
            if (window.WebViewJavascriptBridge) {
                callback(WebViewJavascriptBridge)
            } else {
                document.addEventListener('WebViewJavascriptBridgeReady', function() {
                    callback(WebViewJavascriptBridge)
                }, false)
            }
        }

        connectWebViewJavascriptBridge(function(bridge) {

            /* Init your app here */

            bridge.init(function(message, responseCallback) {
                alert('Received message: ' + message)   
                if (responseCallback) {
                    responseCallback("Right back atcha")
                }
            })
            bridge.send('Hello from the javascript')
            bridge.send('Please respond to this', function responseCallback(responseData) {
                console.log("Javascript got its response", responseData)
            })
        })
    }

    this.show_recent_channels = function() {
        var container = $('#channels .inner').html('');
        var recent_channels = this.global_cookie('recent_channels');
        if(recent_channels) {
            $.each(recent_channels, function(channel, enabled) {
                if(enabled == true) {
                    var channelelem = $('<div>')
                        .addClass('channel')
                        .data('channel', channel);

                    var nameelem = $('<a>')
                        .attr('href', '/'+channel)
                        .html('#'+channel)
                        .appendTo(channelelem);

                    if(channel == window.chatroom) {
                        $('<span>').addClass('current').html("[current]").appendTo(channelelem);
                    } else {
                        $('<a>').addClass('remove').html("&times;").appendTo(channelelem).click(function(e){
                            e.preventDefault();
                            var channel = $(this).parents('.channel').data('channel');
                            delete recent_channels[channel];
                            this_ui.global_cookie('recent_channels', recent_channels);
                            $(this).parents('.channel').remove();

                        });
                    }
                    channelelem.appendTo(container);

                }
            });
        }
    }

    this.add_spiel = function(spiel, is_initial_load) {
        var chat = $('#chat .inner');
        var row = $('<div>').addClass('row');
        var date = new Date(spiel.date);
        var color = spiel.color;
        var datestring = date.toLocaleString()
        var text;

        if(is_initial_load === undefined) {
            is_initial_load = false;
        }

        if(is_initial_load === false && this.flags.windowFocused == false && this.flags.mute == false) {
            if(this.flags.windowFocused == false) {
                this.flags.newMessages++;
                document.title = "(" + this.flags.newMessages + ") " + window.title;
            }
            if(window.webkitNotifications !== undefined) {
                var havePermission = window.webkitNotifications.checkPermission();
                if (havePermission == 0) {
                    // 0 is PERMISSION_ALLOWED
                    var message = '';
                    if(spiel.name) {
                        message += '['+spiel.name+'] '
                    }
                    message += spiel.spiel;

                    var notification = window.webkitNotifications.createNotification(
                        window.static_url + 'assets/icon-144x144.png',
                        '#'+window.chatroom,
                        message
                    );

                    notification.onclick = function () {
                        window.focus();
                        notification.close();
                    }
                    notification.show();
                    setTimeout(function(){
                        notification.close();
                    }, 3000);
                } else {
                    $('#notification')[0].play();
                }
            } else {
                $('#notification')[0].play();
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

        var is_new_message = (this_ui.last_spiel_date < spiel.date);
        if(is_new_message) {
            this_ui.last_spiel_date = spiel.date;
            chat.append(row);
        } else {
            this_ui.first_spiel_date = spiel.date;
            chat.prepend(row);
        }

        row.linkify(toHashtagUrl);
        row.find('time').timeago();


        if(this.flags.chatCssUpdated == false && $('#chat').height() >= $(window).height() - $('#post').height()) {
            $('#chat').css('top', '0');
            this.flags.chatCssUpdated = true;
        }
    }

    this.scroll = function() {
        var chat = $('#chat');
        //chat.scrollTop(chat[0].scrollHeight);
        $("#chat").animate({ scrollTop: $('#chat')[0].scrollHeight-1}, 200);
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
            var toggler_elem = $('#show-map');
            var offset = toggler_elem.offset();
            $('#map-expanded')
                .css({
                    'position': 'absolute',
                    'top': (offset.top + toggler_elem.height()) + 'px',
                    'right': '0',
                })
    }

    this.private_message = function() {
    }

    this.disconnected = function() {
        $('#num-online').html("disconnected");
    }

    return this;
}
