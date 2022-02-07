from All_Imports.all_imports import *


kv = Builder.load_file("Big_Screen/big_screen.kv")


# object class for full screen including toolbar and navigation drawer
class BigScreen(MDBoxLayout):
    menu_dialog = None  # initialize variable for dialog_box

    # upon initialization, create navigation drawer and toolbar
    def __init__(self, **kw):
        super().__init__(**kw)
        # dictionary for items and their icons in the navigation drawer
        icons_item = {
            "home": ["Home", "main"],
            "food": ["Food", "food"],
            "dumbbell": ["Fitness", "fitness"],
            "chart-line": ["Charts and Graphs", "charts_and_graphs"],
            "face-profile": ["My Profile", "user_profile"],
        }
        # add items to navigation drawer (using the custom class ItemDrawer)
        for icon_name in icons_item.keys():
            self.ids.content_drawer.ids.list_for_nav_drawer.add_widget(
                ItemDrawer(icon=icon_name, text=icons_item[icon_name][0], next_screen=icons_item[icon_name][1])
            )
        # create menu for extra functionality
        self.create_menu()

    # function to create MDDropdownMenu object
    def create_menu(self):
        items = ["Help", "Database", "Goals"]
        # add OneLineListItem objects to dictionary with specific text
        menu_items = [{"viewclass": "OneLineListItem", "text": i,
                       "height": dp(56), "on_release": lambda x=i: self.menu_callback(),
                       } for i in items]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=3)  # create the menu object

    # function to open menu upon button press
    def callback(self, instance):
        self.menu.caller = instance
        self.menu.open()

    # function to open dialog when item in menu is pressed
    def menu_callback(self):
        self.menu.dismiss()  # dismiss the menu, and open the dialog
        # create menu_dialog box if none has been created yet
        if not self.menu_dialog:
            self.menu_dialog = MDDialog(title="Help", buttons=[MDFlatButton(text="Close")])
        self.menu_dialog.open()  # open dialog box

    # function to return the "display name" of the screen that the user is on
    def current_screen(self):
        screens = {
            "main": "Home",
            "food": "Food",
            "fitness": "Fitness",
            "charts_and_graphs": "Charts and Graphs",
            "user_profile": "My Profile"
        }
        return screens[self.ids.screen_manager.current]

    # function to switch screen (uses variable instead of creating many functions)
    def switch_screen(self, next_screen):
        self.ids.screen_manager.current = next_screen
        self.ids.toolbar.title = self.current_screen()  # change toolbar title to name of current screen


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    next_screen = StringProperty()


class DrawerList(ThemableBehavior, MDList):
    pass
