class Polls {
    constructor(socket) {
        $('#show-multi-text').hide();
        $('#show-multi-text').click(() => {
            $('#show-multi-text').hide();
            $('#multiple-question-text').show();
        });
        $('#multiple-question-text').change(() => {
            $('#multiple-question-text').hide();
            $('#show-multi-text').show();
            $('#multiple-question-select option').remove();
            const questions = $('#multiple-question-text').val().split('\n');
            questions.forEach(line => {
                $('#multiple-question-select').append(`<option value="${line}">${line}</option>`);
            });
            $('#multiple-question-select').change();
        });

        $('#multiple-question-select').change(() => {
            $('#question-text').val($('#multiple-question-select').val());
        });
        const pollTabPrefix = 'poll-tab-';  // In tab IDs in teacher.html
        const enablePoll = $('#enable-poll');
        enablePoll.click(() => {
            if (enablePoll.is(':checked')) {
                this.updateNumAnswersDisplay();
                const activePollTabId = $('#poll li a.active').attr('id');
                socket.emit('start_poll', activePollTabId.substring(pollTabPrefix.length), $('#question-text').val(),
                    $('#multi-answers').val().split('\n').filter(line => line.trim().length > 0));
            } else {
                ['#show-here', '#show-in-chart'].forEach(sel => {
                    if ($(sel).is(':checked')) $(sel).trigger('click');
                });
                $('#num-answers').text($('#answers tbody tr').remove());
                this.updateNumAnswersDisplay();
                socket.emit('stop_poll');
                stations.forEach(station => delete station.answer);
                sketch.loop();
            }
        });
        function show(what, show) {show ? $(what).show() : $(what).hide();}

        $('#show-here').change(() => show('#answers', $('#show-here').is(':checked')));
        $('#show-in-chart').change(() => {
            showAnswersInStations = $('#show-in-chart').is(':checked');
            sketch.loop();
        });

        socket.on('answer-poll', msg => {
            const station = stations[msg.seatIndex];
            if (! $('#show-here').is(':checked') && ! $('#show-in-chart').is(':checked')) {
                station.answer = msg.answer;
                sketch.loop();
                $(`#answer-${msg.seatIndex}`).remove();
                let insertBefore;
                $('#answers table tbody').children().each((i, tr) => {
                    const tds = $(tr).children();
                    if (!insertBefore && tds[0].textContent > station.name) {
                        insertBefore = $(tr);
                    }
                });
                const newRow = $(`<tr id="answer-${msg.seatIndex}"><td>${station.name}</td><td>${msg.answer}</td></tr>`);
                if (insertBefore)
                    newRow.insertBefore(insertBefore);
                else
                    newRow.appendTo($('#answers table tbody'));
                this.updateNumAnswersDisplay();
            } else console.log(`Ignoring poll response from ${station.name}: ${msg.answer}`)
        });

        this.updateNumAnswersDisplay();
    }

    updateNumAnswersDisplay() {
        const numAnswers = $('#answers tbody tr').length;
        $('#num-answers').text(numAnswers);
        $('#num-answers-plural').text(numAnswers === 1 ? '' : 's');
        const showAnswers = $('#show-answers');
        if (numAnswers > 0) showAnswers.show(); else showAnswers.hide();
    }
}
