import csv
from datetime import date, datetime

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import requests
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex as hex_color
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, MDList, OneLineAvatarIconListItem, OneLineListItem, IRightBody
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDTimePicker, MDDatePicker
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.swiper import MDSwiperItem
from kivymd.uix.tab import MDTabsBase
from kivy.lang import Builder


from Database.database import Database

kv = Builder.load_file("All_Imports/all_imports.kv")

today = date.today()
toolbar_date = today.strftime("%A, %b. %d, %Y")
data_date = today.strftime("%d_%m_%Y")

database = Database()
food_db = Database("database", "user_foods", data_date)
favorites_db = Database("favorites")
workout_db = Database("database", "user_workouts", data_date)
user_profile_db = Database("database", "user_profile", data_date)
user_weight_db = Database("database", "user_weight")


class CustomInfoItem(MDBoxLayout):
    text = StringProperty()
    amount = StringProperty()
    bold = BooleanProperty()
    font_size = NumericProperty()
    height = NumericProperty()


class SwipeToEditItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()
    label_text = StringProperty()
    max_x = NumericProperty()
    screen_name = StringProperty()
    counter = 0

    def __init__(self, **kw):
        super().__init__(**kw)
        self.favorites_button = MDIconButton(icon="heart", on_release=lambda x: self.add_to_favorites())
        self.edit_button = MDIconButton(icon="pencil", on_release=lambda x: self.edit_item(self.screen_name))
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def create_buttons(self, buttons):
        if self.parent.parent.name == "list_for_workouts":
            buttons.pop(-1)

        if self.state == "opened":
            for button in buttons:
                self.ids.card_layer_box.add_widget(button)
            self.counter += 1
        elif self.counter >= 1 and self.state == "closed":
            for button in buttons:
                self.ids.card_layer_box.remove_widget(button)

    def edit_item(self, screen_name):
        return self.app.big_screen.ids.screen_manager.get_screen(f"{screen_name}").edit_item(self)

    def add_to_favorites(self):
        food_screen = self.app.big_screen.ids.screen_manager.get_screen("food")
        food_input = food_db.search("Name", self.text)
        food_item, existing_favs = None, []

        for food_item in food_input:
            food_item = food_item.to_dict()

        for item in food_screen.food_dialog_content.ids.favorites_tab_content.ids.favorites_items.children:
            existing_favs.append(item.text)

        if food_item["Name"] not in existing_favs:
            favorites_db.add_to_database(food_item["Name"], food_item)
            food_screen.food_dialog_content.ids.favorites_tab_content.ids.favorites_items.add_widget(
                CustomFavoritesItem(text=self.text))
            Snackbar(text=f"{self.text} was added to your Favorites!", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        else:
            Snackbar(text=f"{self.text} is already in your Favorites!", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()


class CustomFavoritesItem(OneLineAvatarIconListItem):
    pass


class ErrorDialog(MDDialog):
    title = StringProperty()
    text = StringProperty()
    buttons = ListProperty()


def create_error_dialog(title, text):
    error_dialog = ErrorDialog(title=title, text=text, buttons=[
        MDFlatButton(text="Close", on_release=lambda x: error_dialog.dismiss())])
    error_dialog.open()
