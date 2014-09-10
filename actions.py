from messages import VersionView, SpielsView, SpielView, KeepAliveView
from common import json_encode, json_decode, unix_now, unix_now_ms

def hello(conn, message):
    conn.add_online(connection=conn, room_id=message.room_id, session_id=conn.session_id, name=message.name)

def still_online(conn, message):
    player = conn.db.get_player(conn.session_id)
    if player is None:
        player = conn.db.add_player(conn.session_id)

    if conn.session_id in conn.room_sessions[message.room_id].keys():
        conn.current_session.last_active = unix_now_ms()
        conn.current_session.name = message.name
    else:
        conn.add_online(conn, message.room_id, conn.session_id, name=message.name)
    ack_dto = KeepAliveView()
    conn.send_obj(ack_dto)

def get_spiels(conn, message):
    spiel_models = conn.db.get_spiels_by_room_id(message.room_id, since=message.since, until=message.until)
    spiels = [ SpielView(name=spiel.spiel, spiel=spiel.spiel, date=spiel.date, color=spiel.color) for spiel in spiel_models ]

    if message.until is not None or len(spiels) != 0:
        spiels_dto = SpielsView(spiels)
        conn.send_obj(spiels_dto)

def get_spiels_count(conn, message):
    spiel_models = conn.db.get_spiels_by_room_id(message.room_id, since=message.since, until=message.until)
    spiels = [ SpielView.from_model(spiel, message.room_id) for spiel in spiel_models ]

    spiels_dto = SpielsView(spiels)
    conn.send_obj(spiels_dto)

def post_spiel(conn, message):
    if message.spiel:
        date = unix_now_ms()
        player = conn.db.get_player(conn.session_id)
        color = player.color

        spiel_dto = SpielView(name=message.name, spiel=message.spiel, date=date, color=color)
        conn.notify_recipients(message.room_id, spiel_dto)
        conn.db.post_spiel(message.room_id, spiel_dto)

        conn._update_name(message.name)

def post_private_spiel(conn, message):
    if message.spiel:
        date = unix_now_ms()
        player = conn.db.get_player(conn.session_id)
        color = player.color

        spiel_dto = SpielView(name=message.name, spiel=message.spiel, latitude=message.latitude, longitude=message.longitude, date=date, color=color)
        conn.notify_recipient(message.to_id, spiel_dto)
        conn.db.post_private_spiel(message.to_id, spiel_dto)
