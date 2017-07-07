get_location = lambda twp_rng_sec: {'twp': twp_rng_sec[0],
                                    'rng': twp_rng_sec[1],
                                    'sec': twp_rng_sec[2]}
empty = dict(zip(['twp', 'rng', 'sec', 'aliquot'], [None] * 4))


def parse_geolocation(record):
    geolocation = record['sec_twp_rng']
    if not geolocation:
        yield empty
        return
    for divided in geolocation.split('|'):
        splited = divided.split(' ')
        if splited and len(splited) > 1:
            yield {**get_location(splited[0].split('-')),
                   **{'aliquot': ''.join(splited[1:]).replace('of', ' ')}}
        elif splited:
            yield {**get_location(splited[0].split('-')), **{'aliquot': None}}
        else:
            yield empty