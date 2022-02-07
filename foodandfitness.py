from kivy.config import Config

from All_Imports.all_imports import *
from Big_Screen.big_screen import BigScreen
from Charts_and_Graphs.charts_and_graphs import ChartsAndGraphs
from Fitness.fitness import Fitness
from Food.food import Food
from Main_Window.main_window import MainWindow
from User_Profile.user_profile import UserProfile

Window.size = (360, 800)


# class for custom screen manager with all screens implemented in it
class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # list for all screens (objects) and their names
        screens = [MainWindow(name="main"), Food(name="food"), Fitness(name="fitness"),
                   ChartsAndGraphs(name="charts_and_graphs"), UserProfile(name="user_profile")]
        # add each screen into the screen manager
        for screen in screens:
            self.add_widget(screen)


class FoodAndFitnessApp(MDApp):
    def build(self):
        # print(Config.get("kivy", "default_font"))
        # Config.set("kivy", "default_font", ["Montserrat", "data/fonts/Montserrat-Regular.otf", "data/fonts/Montserrat-Italic.otf", "data/fonts/Montserrat-Bold.otf", "data/fonts/Montserrat-BoldItalic.otf"])
        self.big_screen = BigScreen()
        return self.big_screen


if __name__ == "__main__":
    FoodAndFitnessApp().run()
