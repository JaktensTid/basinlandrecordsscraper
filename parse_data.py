import re

get_location = lambda twp_rng_sec: {'twp': twp_rng_sec[0],
                                    'rng': twp_rng_sec[1],
                                    'sec': twp_rng_sec[2]}
empty = dict(zip(['twp', 'rng', 'sec', 'aliquot'], [None] * 4))


def parse_geolocation_lea(record):
    geolocation = record['sec_twp_rng']
    if not geolocation:
        return empty
    for divided in geolocation.split('|'):
        splited = divided.split(' ')
        if splited and len(splited) > 1:
            return {**get_location(splited[0].split('-')),
                   **{'aliquot': ''.join(splited[1:]).replace('of', ' ')}}
        elif splited:
            return {**get_location(splited[0].split('-')), **{'aliquot': None}}
        else:
            return empty

def parse_geolocation_eddy(record):
    if record['brief_legal']:
        geolocation = record['brief_legal'].replace('SEC', '').strip()
        sec_twp_rng = re.findall(r'(\d{1,2})(,\s*\d+)*( | & ).{1,3}-.{1,3}-.{1,3}', geolocation)
        if not sec_twp_rng:
            sec_twp_rng = re.findall(r'.{1,3}-.{1,3}-.{1,3}', geolocation)
        lot = ''.join(re.findall(r'(LT|LOT) \d{1,4}', geolocation)).split(' ')[-1]
        blk = ''.join(re.findall(r'(BLK|BLOCK) \d{1,4}', geolocation)).split(' ')[-1]
        sec_hyphen, twp, rng = ''.join(sec_twp_rng).split(' ')[-1].split('-')
        for sec in ''.join(sec_twp_rng).split(','):
            sec = sec.strip()
            if '-' not in sec:
                return {'lot' : lot,
                       'blk' : blk,
                       'sec' : sec, 'twp' : twp, 'rng' : rng}
        return {'lot' : lot,
                       'blk' : blk,
                       'sec' : sec_hyphen, 'twp' : twp, 'rng' : rng}

