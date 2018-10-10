settingsTemplate = {
    'teacherName': 'Dave Briccetti',  # Change this
    'missingSeatIndexes': [],
    'chatEnabled': False,
    'sharesEnabled': False,
    'checksEnabled': False,
    'statuses': [
        ['needHelp',   '?', 'Need Help'],
        ['haveAnswer', 'A', 'Have Answer'],
        ['done',       'D', 'Done']
    ],
    'chatDelayMs': 5000,
    'allowedSharesDomains': ['repl.it', 'editor.p5js.org']
}

room1 = {
    'columns': 9,
    'rows': 4,
    'missingSeatIndexes': [8, 35],
    'aisleAfterColumn': 3,
}

room2 = {
    'columns': 3,
    'rows': 2,
}

settings = settingsTemplate
settings.update(room1)
