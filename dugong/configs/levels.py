
LEVELS = {
    '1': {
        'map':  '''wwlmmmllll
                   lwllmflrcl
                   lwwwwflrll
                   lllhwflrll
                   llllwflrll
                   llrrbrrrll
                   llrfwwwhll
                   llrfffwwll
                   lcrlmllwwl
                   lllmmmllww''',
        'units': [
            # player 1
            (
                ('marksman', 1, 7),
                ('general', 1, 8),
                ('catapult', 2, 6),
                ('swordsman', 2, 7),
                ('earthgolem', 2, 8),
            ),
            # player 2
            (
                ('marksman', 8, 2),
                ('general', 8, 1),
                ('swordsman', 7, 2),
                ('earthgolem', 7, 1),
            ),
        ],
        'season': 'summer',
        'background': 'land',
    },

    'road_test': {
        'map':   '''lrrrrrrrrl
                    lrlllrllrl
                    lrrrrrrrrl
                    lrlllrllrl
                    lrlllrllrl
                    lrlllrllrl
                    lrrrrrrrrl
                    llllllllll
                    llllllllll
                    llllllllll''',
        'units': [
        ],
        'season': 'summer',
        'background': 'land',
    },

    'river_test': {
        'map':   '''lwwwwwwwwl
                    lwwwwwwwwl
                    llllwwllll
                    lrlllwllrl
                    lrlrrbrrrl
                    lrlrlbllrl
                    wbwbwwllll
                    lrlrlwwlll
                    lrrrrbbrrr
                    lllllwwlll''',
        'units': [
        ],
        'season': 'summer',
        'background': 'land',
    },

    'monochrome_test': {
        'map':   '''lwwwwwwwwl
                    lwwwwwwwwl
                    rrrrwwllrr
                    lrlrlwllrl
                    lrrrrbrrrl
                    lrlrrbrlrl
                    wbwbwwllcl
                    lrlrlwwlll
                    lrrrrbbrrr
                    llhllwwlll''',
        'units': [
        ],
        'season': 'monochrome',
        'background': 'land',
    },

    'big_map_test': {
        'map':   '''lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrrrrrrrrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lrlllrllrllrrrrrrrrllrrrrrrrrllrrrrrrrrl
                    lllllllllllrrrrrrrrllrrrrrrrrllrrrrrrrrl''',
        'units': [
            # player 1
            (
                ('marksman', 0, 1),
            ),
        ],
        'season': 'summer',
        'background': 'land',
    },

    'attack_test': {
        'map':   '''lllll
                    lrrll
                    lffll
                    lmmll
                    lllll''',
        'units': [
            # player 1
            (
                ('marksman', 0, 1),
                ('general', 1, 1),
                ('catapult', 2, 1),
                ('swordsman', 3, 1),
                ('earthgolem', 4, 1),
            ),
            # player 2
            (
                ('marksman', 0, 2),
                ('general', 1, 2),
                ('catapult', 2, 2),
                ('swordsman', 3, 2),
                ('earthgolem', 4, 2),
            ),
        ],
        'season': 'summer',
        'background': 'land',
    },
}

ABBREVIATIONS = {
    'l': 'land',
    'f': 'forest',
    'r': 'road',
    'b': 'bridge',
    'm': 'mountain',
    'w': 'water',
    'h': 'house',
    'c': 'castle',
}

