
function Networking(chatroom, since) {
    var that = this;
    that.chatroom = chatroom;

    if(since === undefined) {
        this.since = 0;
    } else {
        this.since = since;
    }

    this.initial_load = true;

    this.sock = new SockJS('/updates');

    this.hello = function(chatroom) {
    }

    this.sock.onopen = function() {
        console.log('Connected');

        return that.send('hello', {
            'latitude': window.latitude,
            'longitude': window.longitude,
            'chatroom': that.chatroom,
            'name': $('#name').val(),
        });

        that.keep_alive = setInterval(function() {
            if(window.chatroom || window.latitude) {
                that.send('still_online', {
                    'latitude': window.latitude,
                    'longitude': window.longitude,
                    'chatroom': window.chatroom,
                    'name': $('#name').val(),
                });
            }
        }, 10000);

        that.poller = setInterval(function() {
            if(window.chatroom || window.latitude) {
                that.send('get_spiels', {
                    'latitude': window.latitude,
                    'longitude': window.longitude,
                    'chatroom': window.chatroom,
                    'since': that.since,
                });
            }
        }, 30000);
    };
    this.sock.onmessage = function(e) {
        var message = JSON.parse(e.data);
        console.log("new message,", message);

        // initial login
        if(message.action == 'session') {

            if(message.channel == window.chatroom) {
                window.session_id = message.body.session_id;
                $.cookie("session", window.session_id, {expires: 1000, path: '/'});
                console.log("Logged in to "+message.channel+", session ID: " + window.session_id);
                $('#my-color').css('background', message.body.color);
                window.spiels_per_request = message.body.spiels_per_request;

                that.send('get_spiels', {
                    'latitude': window.latitude,
                    'longitude': window.longitude,
                    'chatroom': message.channel,
                    'since': that.since,
                });
            } else {
                that.send('get_spiels', {
                    'latitude': window.latitude,
                    'longitude': window.longitude,
                    'chatroom': message.channel,
                    'since': window.ui.last_message(message.channel) * 1000,
                });
            }
        }

        if(message.action == 'version') {
            var version = parseInt(message.body.version);
            if(window.teaorbit_version !== undefined && version > window.teaorbit_version) {
                window.location.reload(true);
            }
            window.teaorbit_version = parseInt(message.body.version);
        }

        // chat state
        if(message.action == 'new_spiel') {
            window.ui.touch_channel(message.room_id);
            if(message.channel == window.chatroom) {
                var spiel = message.body;
                // record scroll state before adding the message
                var manually_scrolled = window.ui.manually_scrolled();
                window.ui.add_spiel(spiel);

                if(!manually_scrolled) {
                    window.ui.scroll();
                }
            } else {
                $('#recent-channels .channel').each(function(){
                    if($(this).attr('channel') == message.channel) {
                        var elem = $(this).find('.new-count');
                        var count = parseInt(elem.html());
                        elem.html(count+1);
                    }
                });
            }
        }
        // chat state
        if(message.action == 'spiels') {
            var spiels = message.body.spiels;

            if(message.channel == window.chatroom) {
                // record scroll state before adding the message
                var manually_scrolled = window.ui.manually_scrolled();

                for(var i=0; i<spiels.length; i++) {
                    window.ui.add_spiel(spiels[i], that.initial_load);

                    if(spiels[i].date > that.since) {
                        that.since = spiels[i].date;
                    }
                }

                if(that.initial_load == true && spiels.length < window.spiels_per_request) {
                    $('#load-more').hide();
                }

                if(!manually_scrolled || that.initial_load == true) {
                    window.ui.scroll();
                }
                
                if(that.initial_load == true) {
                    $('#load-more').css('visibility', 'visible');
                }

                that.initial_load = false;
            } else {
                $('#recent-channels .channel').each(function(){
                    if($(this).attr('channel') == message.channel) {
                        $(this).find('.new-count').html(message.body.spiels.length);
                    }
                });
            }
        }

        // general activity log
        if(message.action == 'log') {
            console.log("Log: " + message.body.message);
        }

        // online users
        if(message.action == 'online') {
            if(message.channel == window.chatroom) {
                var num_online = message.body.num_online;
                var users = message.body.users;
                $('#num-online').html(num_online + " online");

                var colors = [];
                for(var i=0; i<users.length; i++) {
                    var color = '<div class="message"><div class="color" style="background-color: '+users[i].color+'"></div> <span class="name">'+users[i].name+'</span></div><br />';
                    colors.push(color);
                }

                $('#online-users').html(colors.join(''));
            }
        }

        // area info
        if(message.action == 'block') {
            var block_id = message.body.block_id;
            console.log("Block ID: " + block_id);
            window.ui.set_map_url("https://maps.googleapis.com/maps/api/staticmap?path=color:0x0000aa|fillcolor:0x6666ff|weight:5|"+block_id+"&size=512x512&sensor=false");
        }

    };
    this.sock.onclose = function() {
        console.log('Connection closed');
        window.ui.disconnected();
        clearInterval(that.keep_alive);
        clearInterval(that.poller);
        this.retry_interval = window.setTimeout(function () {
            console.log('Retrying...');
            var since = window.ui.last_spiel_date;
            window.networking = new Networking(since);
            ui.network = window.network
        }, 2000);
    };
    this.send = function(action, body) {
        var data = {
            'action': action,
            'body': body,
            'session': window.session_id,
        };
        console.log('sending,', data);
        var json_data = JSON.stringify(data);
        this.sock.send(json_data);
    };

    this.get_older_spiels = function(until) {
        that.send('get_spiels', {
            'latitude': window.latitude,
            'longitude': window.longitude,
            'chatroom': window.chatroom,
            'until': until,
        });
    };

    return this;
}
