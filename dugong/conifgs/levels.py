
_LEVELS = {
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
}

class InvalidDataException(Exception):
    pass

def get_levels():
    import copy
    '''Format info a little, check for integrity and return.'''
    # transform to more friendly for game format
    # format map from multiline string to 2d array of letters
    levels_info = copy.deepcopy(_LEVELS)
    for name, level in levels_info.items():
        level['map'] = [list(line.lstrip().rstrip()) for line in level['map'].split('\n')]
        # all rows should be the same size
        for row in level['map']:
            if len(row) != len(level['map'][0]):
                raise InvalidDataException('not all rows in map "%s" have same width' % name)
    return levels_info


