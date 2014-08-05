function UI() {
    var this_ui = this;

    if(window.require) {
        this_ui.gui = require('nw.gui'); 
        this_ui.nw = this_ui.gui.Window.get();
        var nativeMenuBar = new this_ui.gui.Menu({ type: "menubar" });
        try {
            nativeMenuBar.createMacBuiltin("tea orbit");
            this_ui.nw.menu = nativeMenuBar;
        } catch (ex) {
        }
    }

    this.last_spiel_date = 0;
    this.first_spiel_date = 2147483648000;
    this.added_spiel_ids = [];

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
        try {
            key = "global:" + key;
            if(val === undefined) {
                return window.localStorage.getItem(key);
            } else {
                return window.localStorage.setItem(key, val);
            }
            
        } catch(err) {
            if($.cookie('teaorbit:global')) {
                var cookie = JSON.parse($.cookie('teaorbit:global'));
            } else {
                var cookie = {};
            }

            if(val === undefined) {
                if(key in cookie) {
                    return cookie[key];
                } else {
                    return undefined;
                }
            } else {
                cookie[key] = val;
                return $.cookie('teaorbit:global', JSON.stringify(cookie), { expires: 1000, path: '/' });
            }
        }
    }

    this.channel_cookie = function(key, val) {

        try {
            key = "chatroom:" + window.chatroom + ":" + key;
            if(val === undefined) {
                return window.localStorage.getItem(key);
            } else {
                return window.localStorage.setItem(key, val);
            }
        } catch(err) {

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

    
        $('#load-more').on('click', function(e) {
            e.preventDefault();
            window.networking.send('get_spiels', {
                'latitude': window.latitude,
                'longitude': window.longitude,
                'chatroom': window.chatroom,
                'until': this_ui.first_spiel_date,
            });
        });


        $('#post form').on('submit', function(e){
            e.preventDefault();
            var latitude = window.latitude;
            var longitude = window.longitude;
            var chatroom = window.chatroom
            var accuracy = window.gps_accuracy;
            
            if(chatroom || (latitude && longitude)) {
                var spiel_id = uuid();
                $(this).find('input[name="latitude"]').val(latitude);
                $(this).find('input[name="longitude"]').val(longitude);
                $(this).find('input[name="chatroom"]').val(chatroom);
                $(this).find('input[name="spiel_id"]').val(spiel_id);
                var form = $(this).serializeJSON();
                window.networking.send('post_spiel', form);

                $(this).find('textarea[name="spiel"]').val('').trigger('autosize.resize');
                $('#type-here').focus();
            } else {
                //alert("No location data. Please allow the browser geolocation access.");
            }
        });

        var name = this_ui.channel_cookie("name");
        if(name) {
            $('#name').val(name);
        }
        $('#name').change(function(e){
            var name = $('input[name="name"]').val();
            this_ui.channel_cookie("name", name);
        });

        $('#show-channels').bind('click touchstart', function(e){
            e.preventDefault();
            this_ui.toggle_channels(e);
        });

        var focused = function(e){
            document.title = window.title;
            this_ui.flags.windowFocused = true;
            this_ui.flags.newMessages = 0;
            if(this_ui.nw) {
                this_ui.nw.setBadgeLabel("");
            }
        }

        var blurred = function(e){
            this_ui.flags.windowFocused = false;
        }

        $(window).focus(focused);
        $(window).blur(blurred);

        if(this_ui.nw) {
            this_ui.nw.on('focus', focused);
            this_ui.nw.on('blur', blurred);
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
                    'width': (online_elem.outerWidth() + $('#show-channels').outerWidth() + 100) + "px",
                })
                .toggle();
        });

        $.timeago.settings.allowFuture = true;
        $('textarea').autosize();
        $('textarea').keydown(function (e) {
            // enter key
            if (e.keyCode == 13 && !e.shiftKey) {
                $(this.form).submit();
                e.preventDefault();
                e.stopPropagation();
            }

            this_ui.align_chat_window();
            if(!this_ui.manually_scrolled() || e.keyCode == 13) {
                this_ui.scroll();
            }
         });
        $('input, textarea').bind('touchstart', function(e){
            $(this).focus();
        });
        $('.new-channel input').keydown(function (e) {
            // enter key
            if (e.keyCode == 13 && !e.shiftKey) {
                window.location = "/"+$(this).val();
                e.preventDefault();
                e.stopPropagation();
            }
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


        if(spiel.id && this.added_spiel_ids.indexOf(spiel.id) != -1) {
            // message already added
            console.log("message already added");
        } else {
            this.added_spiel_ids.push(spiel.id);

            if(is_initial_load === undefined) {
                is_initial_load = false;
            }

            if(is_initial_load === false && this.flags.windowFocused == false && this.flags.mute == false) {
                this.flags.newMessages++;
                document.title = "(" + this.flags.newMessages + ") " + window.title;
                if(this_ui.nw) {
                    this_ui.nw.setBadgeLabel(this.flags.newMessages.toString());
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
            

            var date_elem = $('<time>').addClass('date').attr('datetime', datestring).attr('timestamp', spiel.date).html(datestring);

            row.append(message);
            row.append(date_elem);

            if(this_ui.last_spiel_date < spiel.date) {
                this_ui.last_spiel_date = spiel.date;
                chat.append(row);
            } else if(this_ui.first_spiel_date > spiel.date) {
                this_ui.first_spiel_date = spiel.date;
                chat.prepend(row);
            } else {
                // find where to add the message
                var rows = $($('#chat .row').get().reverse());
                var found = false;
                rows.each(function(index, message_elem){
                    if(rows[index+1]) {
                        var elem = $(rows[index]);
                        var next_elem = $(rows[index+1]);
                        var timestamp = parseInt(elem.find('time').attr('timestamp'));
                        var next_timestamp = parseInt(next_elem.find('time').attr('timestamp'));
                        if(spiel.date < timestamp && spiel.date >= next_timestamp) {
                            console.log("Oddly timed message received", spiel);
                            row.insertBefore($(rows[index]));
                            found = true;
                        }
                    }
                });
                if(found == false) {
                    console.log("Couldn't place message", spiel);
                }
            }

            row.linkify(toHashtagUrl);
            row.find('time').timeago();


            if(this.flags.chatCssUpdated == false && $('#chat').height() >= $(window).height() - $('#post').height()) {
                $('#chat').css('top', '0');
                this.flags.chatCssUpdated = true;
            }
        }
    }

    this.scroll = function() {
        var chat = $('#chat');
        //chat.scrollTop(chat[0].scrollHeight);
        $("#chat").animate({ scrollTop: $('#chat')[0].scrollHeight-1}, 200);
    }

    this.scroll_up = function() {
        $("#chat").animate({ scrollTop: 0}, 200);
    }

    this.manually_scrolled = function() {
        var chat = $('#chat')[0]
        if(chat.scrollTop == 0) {
            return true;
        } else if(chat.scrollHeight == chat.scrollTop + $(chat).height()) {
            return false;
        } else {
            return true;
        }
    }

    this.reset = function() {
        $('#chat .inner').html('');
    }
    this.set_map_url = function(url) {
        $('.map').attr('src', url);
    }
    this.toggle_channels = function(e) {
        $('#channels').toggleClass('show');
        $('#show-channels').toggleClass('show');
        var toggler_elem = $('#show-channels');
        var offset = toggler_elem.offset();
        $('#channels')
            .css({
                'position': 'absolute',
                'top': (offset.top + toggler_elem.height()) + 'px',
                'right': '0',
            })
        $('#channels input').focus();
        e.stopPropagation();
    }

    this.private_message = function() {
    }

    this.disconnected = function() {
        $('#num-online').html("disconnected");
    }

    return this;
}
