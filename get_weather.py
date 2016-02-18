import ftplib
from xml.etree import ElementTree

def main():
    PredictionData = "IDQ10923.xml"
    ftpGetFiles(PredictionData)
    with open('weatherdata.xml', 'rt') as f:
        tree = ElementTree.parse(f)

    print(type(tree))
    dict = {}
    air_min_temp = tree.findall("./forecast/area/forecast-period/element[@type='air_temperature_minimum']")
    air_max_temp = tree.findall("./forecast/area/forecast-period/element[@type='air_temperature_maximum']")
    prob_rain = tree.findall("./forecast/area/forecast-period/text[@type='probability_of_precipitation']")

    count = 0
    for i in range(0, 6):
        dict[count] = {'Min_Air_Temp': air_min_temp[count].text, 'Max_Air_Temp': air_max_temp[count].text, 'Rain_chance': prob_rain[count].text}
        count += 1

    print(dict)


def ftpGetFiles(retriveFile):
    BOMURL = 'ftp.bom.gov.au'
    ftp = ftplib.FTP(BOMURL)
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    weatherFile = open('weatherdata.xml', 'wb')
    ftp.retrbinary('RETR %s' % retriveFile, weatherFile.write)
    ftp.close()

if __name__ == '__main__':
    main()