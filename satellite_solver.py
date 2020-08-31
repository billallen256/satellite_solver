# vim: expandtab tabstop=4 shiftwidth=4

import logging
import sys

from datetime import datetime, timezone

from pyorbital.orbital import Orbital

logger = logging.getLogger('satellite_solver')
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(_log_handler)
logger.setLevel(logging.INFO)

def new_temp_orbital():
    return {'satellite': None, 'line1': None, 'line2': None}

def tle_file_to_orbitals(tle_file):
    orbitals = []
    stages = ['satellite', 'line1', 'line2']
    current_stage = 0
    temp_orbital = new_temp_orbital()

    for line in tle_file:
        stage = stages[current_stage]
        temp_orbital[stage] = line.strip()

        if stage == 'line2':
            try:
                new_orbital = Orbital(**temp_orbital)
            except NotImplementedError:
                logger.warning('Only LEO orbits supported. Skipping {}'.format(temp_orbital['satellite']))
            else:
                orbitals.append(new_orbital)
            finally:
                temp_orbital = new_temp_orbital()

        current_stage = (current_stage + 1) % len(stages)

    return orbitals

def parse_timestamp(utc_timestamp):
    return datetime.strptime(utc_timestamp, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)

def find_orbitals_near(orbitals, latitude, longitude, utc_datetime):
    matches = []

    for orbital in orbitals:
        try:
            lon, lat, alt = orbital.get_lonlatalt(utc_datetime)
        except NotImplementedError as e:
            logger.warning('Skipping {}: {}'.format(orbital.satellite_name, str(e)))
        else:
            lat_near = abs(lat - latitude) < 1
            lon_near = abs(lon - longitude) < 1

            if lat_near and lon_near:
                matches.append({'satellite': orbital.satellite_name, 'latitude': lat, 'longitude': lon, 'altitude': alt})

    return matches

def main():
    tle_filename = sys.argv[1]
    latitude = float(sys.argv[2])
    longitude = float(sys.argv[3])
    utc_timestamp = sys.argv[4]   # YYYYmmddHHMMSS

    utc_datetime = parse_timestamp(utc_timestamp)

    with open(tle_filename, 'r') as tle_file:
        orbitals = tle_file_to_orbitals(tle_file)

    logger.info("Loaded {} TLE's".format(len(orbitals)))
    logger.info('Looking for satellites over {}, {} around {}'.format(latitude, longitude, utc_datetime))

    matches = find_orbitals_near(orbitals, latitude, longitude, utc_datetime)

    for match in matches:
        logger.info('Match: {satellite} {latitude} {longitude} {altitude}'.format(**match))

    if len(matches) == 0:
        logger.info('No matches')

if __name__ == "__main__":
    main()
