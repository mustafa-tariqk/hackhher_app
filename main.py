# Need Python 3.7, kivy, plyer, and google_play_scraper
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import VariableListProperty
from plyer import notification
from google_play_scraper import app
import datetime
import os


class ConnectPage(GridLayout):
    """This class contains all the widgets for the first screen.
    """
    padding = VariableListProperty([50, 50, 50, 50])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3

        self.add_widget(Label())
        self.add_widget(Label(text="Do you pledge to do the following:", halign="left", font_name="DejaVuSans"))
        self.add_widget(Label())

        self.add_widget(Image(source="wash.png"))
        self.add_widget(Label(text="Wash your hands often", halign="left", font_name="DejaVuSans"))
        self.wash = CheckBox()
        self.add_widget(self.wash)

        self.add_widget(Image(source="contact.png"))
        self.add_widget(Label(text="Avoid close contact", halign="left", font_name="DejaVuSans"))
        self.contact = CheckBox()
        self.add_widget(self.contact)

        self.add_widget(Image(source="mask.png"))
        self.add_widget(Label(text="Wear a mask properly", halign="left", font_name="DejaVuSans"))
        self.mask = CheckBox()
        self.add_widget(self.mask)

        self.add_widget(Image(source="cover.png"))
        self.add_widget(Label(text="Cover coughs and sneezes", halign="left", font_name="DejaVuSans"))
        self.cover = CheckBox()
        self.add_widget(self.cover)

        self.add_widget(Image(source="clean.png"))
        self.add_widget(Label(text="Clean and disinfect", halign="left", font_name="DejaVuSans"))
        self.clean = CheckBox()
        self.add_widget(self.clean)

        self.add_widget(Image(source="monitor.png"))
        self.add_widget(Label(text="Monitor your health", halign="left", font_name="DejaVuSans"))
        self.monitor = CheckBox()
        self.add_widget(self.monitor)

        self.join = Button(text="Submit", background_color=[0, 0, 1.5, 1.5])
        self.join.bind(on_press=self.submit_button)
        self.add_widget(Label())
        self.add_widget(self.join)

    def submit_button(self, instance):
        """This function ensures the user selects all the options
        before moving forward.
        """
        if self.wash.active \
                and self.contact.active \
                and self.mask.active \
                and self.cover.active \
                and self.clean.active \
                and self.monitor.active:
            todo_app.screen_manager.current = "Info"


class InfoPage(GridLayout):
    """This class contains the widgets for the second screen.
    As well as some more information regarding dates and users"""
    padding = VariableListProperty([50, 50, 50, 50])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        today = str(datetime.date.today())

        if os.path.isfile("prev_details.txt"):  # Checks to see if the file exists.
            with open("prev_details.txt", "r") as f:
                d = f.read().split(",")
                prev_date = d[0]

                if prev_date != today:  # Checks if a day has passed.
                    days = int(d[1]) + 1
                else:
                    days = int(d[1])

                try:
                    users = app('ca.gc.hcsc.canada.covid19').get("installs")  # Finds how many people have the app.
                except ConnectionError:  # For now just looks at the Canada COVID19 app.
                    users = d[2]
        else:
            days = 0
            users = "100,000+"

        with open("prev_details.txt", "w") as f:  # Writes new information to file.
            f.write(f"{today},{days},{users}")

        self.cols = 1  # This shows text on the screen.
        self.add_widget(Label(text=f"You are on day {days} of quarantine with us. Keep it up!", font_name="DejaVuSans"))
        self.add_widget(Image(source='logo.png'))
        self.add_widget(Label(text=f"You aren't alone! There are {users} people with you!", font_name="DejaVuSans"))


class EpicApp(App):
    """This class builds the app as well as holds information regarding notifications.
    """
    def build(self):

        outside = True
        if outside:
            notification.notify(
                title="Wait!",
                message="Make the pledge to stay safe!",
            )

        self.title = "COVID To Do List"

        self.screen_manager = ScreenManager()

        self.connect_page = ConnectPage()
        screen = Screen(name="Connect")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        self.info_page = InfoPage()
        screen = Screen(name="Info")
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager


if __name__ == "__main__":
    todo_app = EpicApp()
    todo_app.run()
