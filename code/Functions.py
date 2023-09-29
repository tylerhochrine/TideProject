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
            response = urllib.request.urlopen('https://google.com', timeout=1)
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
def get_current_water_level(dtmTime, tideHeight):
    noaa_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8443970&product" \
               "=water_level&datum=STND&time_zone=lst_ldt&units=english&format=json "

    if dtmTime != '':
        dtmNow = datetime.today()

        print(dtmTime, tideHeight, dtmNow)

        # remaining minutes and seconds until the minute is divisible by 6
        intSleepMinutes = 5 - (dtmNow.minute % 6)
        intSleepSeconds = 60 - dtmNow.second

        time.sleep(intSleepMinutes * 60 + intSleepSeconds)

        response = requests.get(noaa_url)

        # loops until the api updates the data
        while response.json()['data'][0]['t'] == dtmTime:
            # sleeps for 5 seconds if data is still equal to previous data so as to not call API too much
            time.sleep(5)

            response = requests.get(noaa_url)

    # runs immediately if not run before
    else:
        response = requests.get(noaa_url)

    dtmTime = response.json()['data'][0]['t']
    tideHeight = float(response.json()['data'][0]['v'])

    return (dtmTime, tideHeight)
