
function Networking(since) {
    var that = this;

    if(since === undefined) {
        this.since = 0;
    } else {
        this.since = since;
    }

    this.sock = new SockJS('/updates');
    this.sock.onopen = function() {
        console.log('Connected');
        that.send('hello', {
            'latitude': window.latitude,
            'longitude': window.longitude,
            'chatroom': window.chatroom,
            'name': $('#name').val(),
        });

        setInterval(function() {
            if(window.chatroom || window.latitude) {
                that.send('still_online', {
                    'latitude': window.latitude,
                    'longitude': window.longitude,
                    'chatroom': window.chatroom,
                });
            }
        }, 60000);
    };
    this.sock.onmessage = function(e) {
        //console.log('message', e.data);
        var message = JSON.parse(e.data);
        console.log("new message,", message);

        // initial login
        if(message.action == 'session') {
            window.session_id = message.body.session_id;
            $.cookie("session", window.session_id, {expires: 1000, path: '/'});
            console.log("Logged in, session ID: " + window.session_id);
            that.send('get_spiels', {
                'latitude': window.latitude,
                'longitude': window.longitude,
                'chatroom': window.chatroom,
                'since': that.since,
            });
        }

        // chat state
        if(message.action == 'new_spiel') {
            var spiel = message.body;
            var notify = true;
            window.ui.add_spiel(spiel, notify);
        }
        // chat state
        if(message.action == 'initial_spiels') {
            var spiels = message.body.spiels;
            for(var i=0; i<spiels.length; i++) {
                var notify = false;
                window.ui.add_spiel(spiels[i], notify);
            }

            window.ui.scroll();
        }

        // general activity log
        if(message.action == 'log') {
            console.log("Log: " + message.body.message);
        }

        // online users
        if(message.action == 'online') {
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
        this.retry_interval = window.setTimeout(function () {
            console.log('Retrying...');
            var since = window.last_spiel_date;
            window.networking = new Networking(since);
            console.log("Since", since);
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

    this.get_older_messages = function() {
    };

    return this;
}
