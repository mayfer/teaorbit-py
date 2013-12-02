function Spiel() {
    
    return this;
}


function Networking() {
    var that = this;

    this.session_id = '';

    this.sock = new SockJS('/updates');
    this.sock.onopen = function() {
        console.log('Connected');
        window.ui.reset();
    };
    this.sock.onmessage = function(e) {
        //console.log('message', e.data);
        var message = JSON.parse(e.data);
        console.log("Update", message);

        // initial login
        if(message.action == 'session') {
            this.session_id = message.body.session_id;
            console.log("Logged in, session ID: " + this.session_id);
            that.send('get_spiels', {
                'latitude': window.latitude,
                'longitude': window.longitude,
                'chatroom': window.chatroom,
            });
        }

        // chat state
        if(message.action == 'new_spiel') {
            var spiel = message.body;
            window.ui.add_spiel(spiel);
        }

        // general activity log
        if(message.action == 'log') {
            console.log("Log: " + message.body.message);
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
        this.retry_interval = window.setTimeout(function () {
            console.log('Retrying...');
            window.networking = new Networking();
        }, 2000);
    };
    this.send = function(action, body) {
        var json_data = JSON.stringify({
            'action': action,
            'body': body,
            'session': this.session_id,
        })
        this.sock.send(json_data);
    }
    return this;
}
