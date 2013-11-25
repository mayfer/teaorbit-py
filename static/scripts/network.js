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
            console.log("Logged in, session ID: " + session_id);
            that.send('get_spiels', {'since': window.last_id});
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
