import requests
import json
import datetime
import urllib.request
import csv


# todo: add a town class and move toronto_status there
def toronto_status_update():
    """
    Needs to be run on startup, or at the start of a location risk calculation.
    Use data from https://open.toronto.ca/dataset/covid-19-cases-in-toronto/
    to find out about the area's weekly covid-19 infection data
    Only data from the beginning of last month will be stored.
    However, historical data can also be used to determine area risk score separately from location risk score.
    """
    if datetime.datetime.today().weekday() == 0:  # The dataset will update if called on a Monday
        print("Updating dataset...")
        url = 'https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=csv'
        # Download data from Toronto's open dataset on covid-19 everytime it's ran
        urllib.request.urlretrieve(url, r'C:\Users\ADMIN\PycharmProjects\HackHer\COVID19 cases.csv')
        data = {}  # Read the .csv dataset and convert to json for simplicity
        with open('COVID19 cases.csv') as csvFile:
            csvReader = csv.DictReader(csvFile)
            for rows in csvReader:
                id = rows['Episode Date']
                date = id.split('-')
                if int(date[1]) >= datetime.datetime.today().month - 1:  # Only takes in data from the last month
                    try:  # The code will sort by neighbourhood
                        data[rows['Neighbourhood Name']][rows['_id']] = rows
                    except KeyError:  # If that neighbourhood's dictionary has not yet been initialized
                        data[rows['Neighbourhood Name']] = {}
                        data[rows['Neighbourhood Name']][rows['_id']] = rows

        with open('covid.json', 'w') as jsonFile:
            jsonFile.write(json.dumps(data, indent=4))
        print("Data successfully updated")
    else:
        print("Data will be updated on Monday")

    with open('covid.json', 'r') as f:
        data = json.load(f)

    infection_data = {'neighbourhood': [],
                      'count': []}
    message = "In the past month, there are:\n"
    for town in data:
        risk = len(data[town])

        infection_data['neighbourhood'].append(town.lower())  # Generate data file necessary to create the heatmap
        infection_data['count'].append(risk)

        message += f"{risk} new cases in {town}\n"

    with open('neighbourhood_data', 'w') as f:
        f.write(json.dumps(infection_data, indent=4))
    print(message)


class MapData:
    """
    Despite its name, only thing it does is handle basic initialization of the API.
    todo: consider scrapping this entirely and put everything in Forecast Data class
    """

    def __init__(self):
        self.pri_key = 'pri_accac5af9d5b40c2818b758e1a8dfd03'
        self.url = "https://besttime.app/api/v1/"
        self.payload = {}
        self.headers = {}

    def auth_check(self):
        response = requests.request("GET", self.url + "keys/" + self.pri_key, headers=self.headers, data=self.payload)
        print(response.text.encode('utf8'))


class ForecastData(MapData):
    """
    This class takes inheritance from the MapData class.
    Handles API calls as well as methods which interprets data from those calls.
    todo: integrate with google maps in the app to generate a heat map
    """

    def __init__(self, name: str, address: str):
        super().__init__()
        self.name = name
        self.address = address
        self.params = {
            'api_key_private': self.pri_key,
            'venue_name': self.name,
            'venue_address': self.address
        }
        self.response = requests.request("POST", self.url + "forecasts", params=self.params)
        self.live_response = requests.request("POST", self.url + "forecasts/live", params=self.params)

        self.data = json.loads(self.response.text)
        self.live_data = json.loads(self.live_response.text)
        toronto_status_update()

    def full_forecast(self):
        """
        Test code to make sure it's working
        """
        return self.data

    def safety_rec(self):
        """
        Using the available data from the API, the program will judge if it is safe to head there or not
        todo: Use local infection data to make further judgement
        """
        forecasted_busyness = self.live_data["analysis"]["venue_forecasted_busyness"]
        peak_intensity = self.data["analysis"][0]["peak_hours"][0]["peak_intensity"]
        if self.data["analysis"][0]["surge_hours"]["most_people_come"] == datetime.datetime.hour:
            return "It is not advisable to arrive at the establishment at this time\n" \
                   f"It is known to peak at {peak_intensity} at this time"

        else:
            if not self.live_data["analysis"]["venue_live_busyness_available"]:
                return "Not much is known about this establishment currently.\n " \
                       f"However, it is known to be having {forecasted_busyness} customers at this time of day"
            busyness = self.live_data["analysis"]["venue_live_busyness"]
            return f"The establishment is having {busyness} people. However, we still advise to go with mask on."


if __name__ == '__main__':
    new_forecast = ForecastData("McDonalds", "Sector 1E Kalamboli Panvel")
    toronto_status_update()
