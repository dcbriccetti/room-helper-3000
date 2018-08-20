const stations = new Array(settings.rows * settings.columns);
let selectedSeatIndex = null;

$(document).ready(() => {
    const socket = io.connect();

    socket.on('seated', msg => {
        function clearNameElsewhere(newSeatIndex, clearName) {
            stations.forEach((station, i) => {
                if (i !== newSeatIndex && station.name === clearName) {
                    station.ip = station.nickname = station.name = station.done = station.needHelp = null;
                }
            });
        }

        clearNameElsewhere(msg.seatIndex, msg.station.name);
        stations[msg.seatIndex] = msg.station;
    });

    socket.on('clear_station', seatIndex => {stations[seatIndex] = null;});

    socket.on('status_set', msg => {
        stations[msg.seatIndex].done = msg.station.done;
        stations[msg.seatIndex].needHelp = msg.station.needHelp;
    });

    $('#set-names').click(event => {
        socket.emit('set_names', {names: $('#names').val(), assignSeats: $('#assign-seats').is(':checked')});
    });

    $('#random-set').click(event => {
        socket.emit('random_set', Number($('#random-set-number').val()));
    });

    $('#choose').click(event => {
        socket.emit('random_call', null, (i) => selectedSeatIndex = i === -1 ? null : i);
    });
});
