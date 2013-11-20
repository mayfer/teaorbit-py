function Networking() {
    var that = this;
    var session_id;

    this.sock = new SockJS('/updates');
    this.sock.onopen = function() {
        console.log('Connected');
    };
    this.sock.onmessage = function(e) {
        //console.log('message', e.data);
        var message = JSON.parse(e.data);
        console.log("Update", message);

        // initial login
        if(message.action == 'session') {
            session_id = message.body.session_id;
            console.log("Logged in, session ID: " + session_id);
        }

        // chat state
        if(message.action == 'new_spiel') {
            var spiel = message.body;
            UI.add_spiel(spiel);
        }

        // general activity log
        if(message.action == 'log') {
            console.log("Log: " + message.body.message);
        }
    };
    this.sock.onclose = function() {
        console.log('Connection closed');
    };
    this.send = function(action, body) {
        var json_data = JSON.stringify({
            'action': action,
            'body': body,
        })
        this.sock.send(json_data);
    }
    return this;
}
