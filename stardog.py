# https://lawlesst.github.io/notebook/rdflib-stardog.html

# for some reason, trying to authenticate using SPARQLWrapper fails with a 500 error
# the URL SPARQLWrapper uses is 'http://localhost:5820/lawntest/query?results=json&output=json&reasoning=true&format=json&query=PREFIX+lawn%3A+%3Chttp%3A//www.semanticweb.org/dean/SemanticLawnWatering%23%3E%0ASELECT+%2A+%7B+%3Fs+lawn%3Awater_required+%3Fo+%7D'
# the headers are {'Authorization': "Basic b'YWRtaW46YWRtaW4='", 'Accept': 'application/sparql-results+json,text/javascript,application/json', 'User-agent': 'sparqlwrapper 1.7.5 (rdflib.github.io/sparqlwrapper)'}
# THIS IS A SPARQLWrapper BUG WITH PYTHON 3, PULL REQUEST ISSUED

'''
STARDOG chosen as it integrates triple store with OWL 2 and SWRL reasoning and provides standard SPARQL HTTP endpoint capabilities.
'''

import subprocess
import urllib.error
import urllib.request

import requests
from SPARQLWrapper import SPARQLWrapper, JSON

class StardogException(Exception):
    pass


# STARDOG_QUERY_ENDPOINT = "http://localhost:5820/{database}/query?reasoning=true&query="
STARDOG_QUERY_ENDPOINT = "http://localhost:5820/{database}/query"

QUADRANT_SNAPSHOT_INSERT = '''PREFIX qd: <http://www.semanticweb.org/trevor/quickdata#>
INSERT DATA {
  qd:QuadrantSnapshot_X a qd:QuadrantSnapshot.
}'''

WATER_REQUIRED_QUERY =  '''PREFIX lawn: <http://www.semanticweb.org/dean/SemanticLawnWatering#>
SELECT * { ?s lawn:water_required ?o }'''


def start_on_windows(disable_security=True):
    # this will block until shut down
    command_line = ['cmd', '/c', '%STARDOG_HOME%\\bin\\stardog-admin', 'server', 'start']
    if disable_security:
        command_line.append('--disable-security')
    subprocess.run(command_line)


def stop_on_windows():
    subprocess.run(['cmd', '/c', '%STARDOG_HOME%\\bin\\stardog-admin', 'server', 'stop'])


def get_sparql_endpoint(database):
    return STARDOG_QUERY_ENDPOINT.format(database=database)


def query_stardog(query_string, sparql_endpoint):
    '''
    :param query_string:
    :param database:
    :return:
    '''
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.addParameter('reasoning', 'true')
    # sparql.setHTTPAuth('BASIC')
    # sparql.setCredentials('admin', 'admin')
    sparql.setMethod('POST')
    sparql.setQuery(query_string)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results
    except urllib.error.URLError:
        raise StardogException('Could not access Stardog SPARQL endpoint - ' + sparql_endpoint)
    # results = sparql.query().convert()['results']['bindings']


def query_with_requests_module():
    QUERY = 'http://localhost:5820/lawntest/query?results=json&output=json&reasoning=true&format=json&query=PREFIX+lawn%3A+%3Chttp%3A//www.semanticweb.org/dean/SemanticLawnWatering%23%3E%0ASELECT+%2A+%7B+%3Fs+lawn%3Awater_required+%3Fo+%7D'
    headers = {'Accept': 'application/sparql-results+json,text/javascript,application/json'}
    response = requests.get(QUERY, headers=headers, auth=('admin', 'admin'))
    print(response.status_code)
    print(response.json())


def print_query_results(results):
    results = results['results']['bindings']
    for row in results:
        for key in ['s', 'p', 'o']:
            if key in row:
                print('{}: {}'.format(key, row[key]))
        # print(row)
        print('---')


if __name__ == '__main__':
    sparql_endpoint_url = get_sparql_endpoint('lawntest')
    results = query_stardog(WATER_REQUIRED_QUERY, sparql_endpoint_url)
    print_query_results(results)
    # query_with_requests_module()
    # query_water_required()
    # sensor_data = get_sensor_data_from_dweet(DWEET_URL)
    # print(sensor_data)
