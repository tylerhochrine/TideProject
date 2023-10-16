from datetime import datetime, timedelta
import requests
import time
import multiprocessing
import urllib.request


def wait_for_internet_connection():
    while True:
        print('trying to connect')
        try:
            print('connecting...')
            urllib.request.urlopen('https://google.com', timeout=1)
            print('connection successful')
            return
        except Exception as e:
            print(str(e))
            pass


# function to get the current water level from the API
# ~6-7 minute delay due to NOAA record keeping
# dtmTime will be 0 if not run before, otherwise it will be equal to the most recent water level record
# function will sleep until the current minute is divisible by 6
# data will only return once NOAA has updated the data
def get_current_water_level(data):
    noaa_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8443970&product" \
               "=water_level&datum=STND&time_zone=lst_ldt&units=english&format=json"
    response = requests.get(noaa_url)

    data['dtmTime'] = response.json()['data'][0]['t']
    data['tideHeight'] = float(response.json()['data'][0]['v'])

    return data


def get_air_temp(data):
    noaa_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8443970&product" \
               "=air_temperature&datum=STND&time_zone=lst_ldt&units=english&format=json"
    response = requests.get(noaa_url)

    print(float(response.json()['data'][0]['v']))

    data['airTemp'] = round(float(response.json()['data'][0]['v']))

    return data


def get_data(data):    
    if data['dtmTime'] != '':
        dtmNow = datetime.today()

        print(data, dtmNow)

        # remaining time until the minute is divisible by 6
        intSleepMinutes = 5 - (dtmNow.minute % 6)
        intSleepSeconds = 60 - dtmNow.second

        time.sleep(intSleepMinutes * 60 + intSleepSeconds)

        tempTime = data['dtmTime']

        # loops until the api updates the data
        while get_current_water_level(data)['dtmTime'] == tempTime:
            # sleeps for 10 seconds if data is unchanged to not call API too much
            time.sleep(10)

    data = get_current_water_level(data)
    data = get_air_temp(data)

    return data


def get_time():
    curr_time = time.strftime("%I:%M", time.localtime())
    ltime = [int(x) for x in curr_time if x != ':']
    
    return ltime
    