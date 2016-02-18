import json
import urllib.request
import datetime
import stardog

DATABASE_NAME = 'lawntest'
LAWNTEST_QUERY_ENDPOINT = stardog.get_sparql_endpoint(DATABASE_NAME)
TIMES_OF_DAY = {'Morning', 'Midday', 'Afternoon'}
LAWNTEST_SPARQL_PREFIX = 'PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>'

REPLACE_CURRENT_DAY_QUERY = LAWNTEST_SPARQL_PREFIX + '''
DELETE {lawn:CurrentDay lawn:isDay ?previousDay}
INSERT {lawn:CurrentDay lawn:isDay {day}}
WHERE {lawn:CurrentDay lawn:isDay ?previousDay}'''

DWEET_URL = "http://dweet.io/get/latest/dweet/for/lawnbot1"
DWEET_EXAMPLE_JSON = '{"this":"succeeded","by":"getting","the":"dweets","with":[{"thing":"lawnbot1","created":"2015-12-17T03:01:55.561Z","content":{"water_valve_2":0,"soil_humidity":52.98,"water_valve_1":0,"temperature":23.44,"water_flow_1":0,"water_flow_2":0,"humidity":40,"illuminance":15,"soil_temp":26.53,"version":2,"soil_fork_2":0,"gypsum1":0,"gypsum2":0,"soil_fork_1":0,"id":"lawnbot1"}}]}'


# quadrant ids are assumed to be quad<num> e.g. quad1, quad2 etc.
def get_dict_key_for_gypsum(quadrant_id):
    number = quadrant_id[4:]
    return 'gypsum' + number


def get_dict_key_for_soil_fork(quadrant_id):
    number = quadrant_id[4:]
    return 'soil_fork_' + number


def get_sensor_data_from_dweet(dweet_url):
    response = urllib.request.urlopen(dweet_url)
    string = response.read().decode('utf-8')
    data = json.loads(string)

    if data.get('this', None) == 'succeeded':
        return data['with'][0]['content']
    else:
        raise Exception('Request to DWEET failed')


def get_example_sensor_data_from_string(string=DWEET_EXAMPLE_JSON):
    data = json.loads(string)
    return data['with'][0]['content']


def make_yard_snapshot_id(yard_id, day, time_of_day):
    return '{}Day{}{}'.format(yard_id, day, time_of_day)


def make_quadrant_snapshot_id(quadrant_id, day, time_of_day):
    return '{}Day{}{}'.format(quadrant_id, day, time_of_day)


def make_query_does_yard_snapshot_exist(yard_id, day_number, time_of_day):
    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
SELECT ?snapshot {{?snapshot lawn:hasDay {day_number} .
?snapshot lawn:hasTimeOfReading "{time_of_day}" .
lawn:{yard_id} lawn:hasQuadrantSnapshot ?snapshot}}'''.format(yard_id=yard_id,
                                                                  day_number=day_number,
                                                                  time_of_day=time_of_day)
    return query


def make_query_does_quadrant_snapshot_exist(quadrant_id, day_number, time_of_day):
    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
SELECT ?snapshot {{?snapshot lawn:hasDay {day_number} .
?snapshot lawn:hasTimeOfReading "{time_of_day}" .
lawn:{quadrant_id} lawn:hasQuadrantSnapshot ?snapshot}}'''.format(quadrant_id=quadrant_id,
                                                                  day_number=day_number,
                                                                  time_of_day=time_of_day)
    return query


def make_query_create_yard_snapshot(yard_id, day_number, time_of_day):
    snapshot_id = make_yard_snapshot_id(yard_id, day_number, time_of_day)
    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
INSERT DATA {{ lawn:{snapshot_id} rdf:type lawn:YardSnapshot;
                                           rdf:type owl:NamedIndividual;
                                           lawn:hasDay {day_number};
                                           lawn:hasTimeOfReading "{time_of_day}" .
             lawn:{yard_id} lawn:hasYardSnapshot lawn:{snapshot_id} }}'''.format(snapshot_id=snapshot_id,
                                                                                 yard_id=yard_id,
                                                                                 day_number=day_number,
                                                                                 time_of_day=time_of_day)
    return query


def make_query_create_quadrant_snapshot(quadrant_id, day_number, time_of_day):
    snapshot_id = make_quadrant_snapshot_id(quadrant_id, day_number, time_of_day)
    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
INSERT DATA {{ lawn:{snapshot_id} rdf:type lawn:QuadrantSnapshot;
                                           rdf:type owl:NamedIndividual;
                                           lawn:hasDay {day_number};
                                           lawn:hasTimeOfReading "{time_of_day}" .
             lawn:{quadrant_id} lawn:hasQuadrantSnapshot lawn:{snapshot_id} }}'''.format(snapshot_id=snapshot_id,
                                                                                         quadrant_id=quadrant_id,
                                                                                         day_number=day_number,
                                                                                         time_of_day=time_of_day)
    return query


def make_query_delete_yard_snapshot_data_readings(yard_id, day_number, time_of_day):
    snapshot_id = make_yard_snapshot_id(yard_id, day_number, time_of_day)
    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
DELETE WHERE {{lawn:{snapshot_id} lawn:hasYardAmbientTemperatureReading ?x}};
DELETE WHERE {{lawn:{snapshot_id} lawn:hasYardAmbientHumidityReading ?x}};
DELETE WHERE {{lawn:{snapshot_id} lawn:hasYardSoilHumidityReading ?x}};
DELETE WHERE {{lawn:{snapshot_id} lawn:hasYardSoilTemperatureReading ?x}};
DELETE WHERE {{lawn:{snapshot_id} lawn:hasYardIlluminanceReading ?x}};'''.format(snapshot_id=snapshot_id)
    return query


def make_query_delete_quadrant_snapshot_data_readings(quadrant_id, day_number, time_of_day):
    snapshot_id = make_quadrant_snapshot_id(quadrant_id, day_number, time_of_day)
    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
DELETE WHERE {{lawn:{snapshot_id} lawn:hasSuperficialSoilMoisture ?x}};
DELETE WHERE {{lawn:{snapshot_id} lawn:hasDeepSoilMoisture ?x}}'''.format(snapshot_id=snapshot_id)
    return query


def make_query_insert_yard_snapshot_data_readings(yard_id, day_number, time_of_day, data):
    snapshot_id = make_yard_snapshot_id(yard_id, day_number, time_of_day)
    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
INSERT DATA {{lawn:{snapshot_id} lawn:hasYardAmbientTemperatureReading {temperature}}};
INSERT DATA {{lawn:{snapshot_id} lawn:hasYardAmbientHumidityReading {humidity}}};
INSERT DATA {{lawn:{snapshot_id} lawn:hasYardSoilHumidityReading {soil_humidity}}};
INSERT DATA {{lawn:{snapshot_id} lawn:hasYardSoilTemperatureReading {soil_temperature}}};
INSERT DATA {{lawn:{snapshot_id} lawn:hasYardIlluminanceReading {illuminance}}}'''.format(snapshot_id=snapshot_id,
                                                                                            temperature=data['temperature'],
                                                                                            humidity=data['humidity'],
                                                                                            soil_humidity=data['soil_humidity'],
                                                                                            soil_temperature=data['soil_temp'],
                                                                                            illuminance=data['illuminance'])
    return query


def make_query_insert_quadrant_snapshot_data_readings(quadrant_id, day_number, time_of_day, data):
    snapshot_id = make_quadrant_snapshot_id(quadrant_id, day_number, time_of_day)
    gypsum_key = get_dict_key_for_gypsum(quadrant_id)
    soil_fork_key = get_dict_key_for_soil_fork(quadrant_id)

    gypsum_value = data[gypsum_key]
    soil_fork_value = data[soil_fork_key]

    query = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
DELETE WHERE {{lawn:{snapshot_id} lawn:hasSuperficialSoilMoisture ?x}};
DELETE WHERE {{lawn:{snapshot_id} lawn:hasDeepSoilMoisture ?x}};
INSERT DATA {{lawn:{snapshot_id} lawn:hasSuperficialSoilMoisture {soil_fork}}};
INSERT DATA {{lawn:{snapshot_id} lawn:hasDeepSoilMoisture {gypsum}}}'''.format(snapshot_id=snapshot_id,
                                                                               soil_fork=soil_fork_value,
                                                                               gypsum=gypsum_value)
    return query


def put_quadrant_snapshot(quadrant_id, day_number, time_of_day, sensor_data):
    # ONTOLOGY NEEDS TO BE CHANGED SO THAT hasDay has range int
    # if the quadrant snapshot individual doesn't exist, create it
    # check if it exists

    # initial insertion
    query_create = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
INSERT DATA {lawn:Q1_d0_morning rdf:type lawn:QuadrantSnapshot}'''
    query_has_day = '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
INSERT DATA {lawn:Q1_d0_morning lawn:hasDay 0}'''
    # if the quadrant snapshot has data, delete and replace it, otherwise just insert it

    pass


def query_quadrant_snapshots(quadrant_id):
    pass


def get_current_day_number():
    # isoweekday() returns 7 for Sunday = 0 mod 7
    return datetime.date.today().isoweekday() % 7


if __name__ == '__main__':
    data = get_example_sensor_data_from_string()
    print('***')
    print(make_query_create_quadrant_snapshot('quad1', 0, 'Morning'))
    print('***')
    print(make_query_insert_yard_snapshot_data_readings('townsvilleYard', 0, 'Morning', data))
    print('***')
    print(make_query_insert_quadrant_snapshot_data_readings('quad1', 0, 'Morning', data))
    print('***')
    print(make_query_create_quadrant_snapshot('quad1', 0, 'Midday'))
    # json.loads()
    sparql_endpoint_url = stardog.get_sparql_endpoint('lawntest')
    for yard in ['townsvilleYard']:
        for day in range(7):
            for time_of_day in TIMES_OF_DAY:
                query = make_query_create_yard_snapshot(yard, day, time_of_day)
                try:
                    stardog.query_stardog(query, sparql_endpoint_url)
                except stardog.StardogException:
                    exit()
                print('OKAY {}{}{}'.format(yard, day, time_of_day))