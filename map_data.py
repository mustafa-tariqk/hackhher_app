import requests
import json
import datetime


class MapData:
    """
    Despite its name, only thing it does is handle basic initialization of the API.
    todo: consider scrapping this entirely and put everything in Forecast Data class
    """
    def __init__(self):
        self.pri_key = 'pri_accac5af9d5b40c2818b758e1a8dfd03'
        self.url = f"https://besttime.app/api/v1/"
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

    def full_forecast(self):
        """
        Test code to make sure it's working
        """
        print(self.data)

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
    ForecastData.auth_check(new_forecast)
    print(ForecastData.safety_rec(new_forecast))
