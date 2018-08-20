from random import choice
from time import time

from flask import Flask, render_template, request, json
from flask_socketio import SocketIO, emit, disconnect
import logging

logFormatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
for handler in (logging.FileHandler('log.txt'), logging.StreamHandler()):
    handler.setFormatter(logFormatter)
    logger.addHandler(handler)

settings = {
    'columns': 9,
    'rows': 4,
    'missingSeatIndexes': [8, 35],
    'aisleAfterColumn': 3
}
names = []
stations = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    r = request
    logger.info('Student page requested from %s, %s', r.remote_addr, r.user_agent)
    return render_template('student.html', settings=json.dumps(settings), names=names)


@app.route('/teacher')
def teacher():
    r = request
    logger.info('Teacher page requested from %s, %s', r.remote_addr, r.user_agent)
    return render_template('teacher.html', settings=json.dumps(settings), stationJson=json.dumps(stations))


@socketio.on('connect')
def connect():
    r = request
    logger.info('Connection from %s, %s, %s', r.remote_addr, r.sid, r.user_agent)


@socketio.on('disconnect')
def disconnect_request():
    r = request
    logger.info('Disconnected: %s, %s', r.remote_addr, r.sid)
    matches = [item for item in stations.items() if r.sid == item[1].get('sid')]
    if matches:
        station_index, station = matches[0]
        clearStation(station)
        emit('clear_station', station_index, broadcast=True)


@socketio.on('set_names')
def set_names(message):
    r = request
    ip = r.remote_addr
    logger.info('set_names from %s, %s', ip, r.sid)
    emit('set_names', message, broadcast=True)
    global names
    names = []
    assign_seats = message['assignSeats']

    def skip_missing(start):
        while start in settings['missingSeatIndexes']:
            start += 1
        return start

    si = skip_missing(0)
    for line in message['names'].split('\n'):
        name = line.strip()
        names.append(name)
        if assign_seats:
            station = {'ip': ip, 'nickname': '', 'name': name}
            stations[si] = station
            broadcast_seated(station, si)
            si = skip_missing(si + 1)


@socketio.on('seat')
def seat(message):
    nickname = message['nickname']
    name = message['name']
    si = message['seatIndex']
    ip = request.remote_addr
    logger.info('%s seat %s %s to %d', ip, name, nickname, si)
    existing_different_index = [i for i, station in stations.items() if station.get('name') == name and i != si]
    if existing_different_index:
        del stations[existing_different_index[0]]
    station = {'ip': ip, 'sid': request.sid, 'nickname': nickname, 'name': name}
    stations[si] = station
    broadcast_seated(station, si)


@socketio.on('random_set')
def random_set(random_calls_limit):
    logger.info('Random calls limit set to %d', random_calls_limit)
    for station in stations.values():
        if station.get('name'):
            station['callsLeft'] = random_calls_limit


@socketio.on('random_call')
def random_call(ignore):
    eligible = [(k, v) for k, v in stations.items() if v.get('callsLeft', 0) > 0]
    if not eligible:
        return -1
    chosen = choice(eligible)
    chosen[1]['callsLeft'] -= 1
    logger.info('%s %s called randomly', chosen[1].get('nickname', ''), chosen[1]['name'])
    return chosen[0]


def broadcast_seated(station, seat_index):
    emit('seated', {'seatIndex': seat_index, 'station': station}, broadcast=True)


@socketio.on('set_status')
def set_status(message):
    si = message['seatIndex']
    station = stations.get(si)
    if station:
        done = message['done']
        need_help = message['needHelp']
        logging.info('set_status %s: done: %s, need help: %s', message['name'], done, need_help)
        now = time()
        station['done'] = now if done else None
        station['needHelp'] = now if need_help else None
        ss_msg = {'seatIndex': si, 'station': station}
        emit('status_set', ss_msg, broadcast=True)


def clearStation(station):
    for key in ('nickname', 'name', 'needHelp', 'done'):
        if key in station:
            del station[key]


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
