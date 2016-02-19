import ftplib
from xml.etree import ElementTree
import bs4
import requests


def get_weather_dict():
    prediction_data = "IDQ10923.xml"
    ftpGetFiles(prediction_data)
    with open('weatherdata.xml', 'rt') as f:
        tree = ElementTree.parse(f)

    print(type(tree))
    dict = {}
    air_min_temp = tree.findall("./forecast/area/forecast-period/element[@type='air_temperature_minimum']")
    air_max_temp = tree.findall("./forecast/area/forecast-period/element[@type='air_temperature_maximum']")
    prob_rain = tree.findall("./forecast/area/forecast-period/text[@type='probability_of_precipitation']")

    count = 0
    for i in range(0, 1):
        dict[count] = {'Min_Air_Temp': air_min_temp[count].text, 'Max_Air_Temp': air_max_temp[count].text, 'Rain_chance': prob_rain[count].text}
        count += 1

    dict[0]['Evapotranspiration'] = getEvapotranspiration()

    return dict[0]


def getEvapotranspiration():
    result = requests.get('http://www.bom.gov.au/watl/eto/tables/qld/daily.shtml')
    soup = bs4.BeautifulSoup(result.text, "html5lib")

    allitems = soup.find_all('tr')

    item =  allitems[len(allitems)-10]
    count = 0
    for i in item:
        count += 1
        if count == 3:
            evap =  i.text
    return evap

def ftpGetFiles(retriveFile):
    BOMURL = 'ftp.bom.gov.au'
    ftp = ftplib.FTP(BOMURL)
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    weatherFile = open('weatherdata.xml', 'wb')
    ftp.retrbinary('RETR %s' % retriveFile, weatherFile.write)
    ftp.close()

if __name__ == '__main__':
    print(get_weather_dict())