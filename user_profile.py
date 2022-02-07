from All_Imports.all_imports import *

kv = Builder.load_file("User_Profile/user_profile.kv")


class AddWeightInfo(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda x: self.create_weight_measurement_menu())

    def create_weight_measurement_menu(self):
        items = ["Pounds (lbs)", "Kilograms (kg)"]
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": i,
                "height": dp(56),
                "on_release": lambda x=i: self.weight_menu_callback(x),
            } for i in items
        ]
        self.weight_measurement_menu = MDDropdownMenu(
            caller=self.ids.measurement_value,
            items=menu_items,
            width_mult=3,
        )

    def weight_menu_callback(self, text_item):
        self.ids.measurement_value.text = f"{text_item}"
        self.weight_measurement_menu.dismiss()


class AddHeightInfo(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda x: self.create_height_measurement_menu())

    def create_height_measurement_menu(self):
        items = ["Inches (in)", "Centimetres (cm)"]
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": i,
                "height": dp(56),
                "on_release": lambda x=i: self.height_menu_callback(x),
            } for i in items
        ]
        self.height_measurement_menu = MDDropdownMenu(
            caller=self.ids.measurement_value,
            items=menu_items,
            width_mult=3,
        )

    def height_menu_callback(self, text_item):
        self.ids.measurement_value.text = f"{text_item}"
        self.height_measurement_menu.dismiss()


class UserProfile(MDScreen):
    add_profile_info_dialog = None
    toolbar_date = toolbar_date
    input_button_data = {
        'Weight': 'weight',
        'Height': 'human-male-height',
    }

    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_profile_items()
        self.check_BMI()
        self.profile_info_dialog_content = MDLabel()
        self.create_add_profile_info_dialog()

    def check_BMI(self):
        items = user_profile_db.get_user_profile_info()
        height_dates, weight_dates = [], []
        for item in items:
            item = item.to_dict()
            if "Height" in item.keys():
                height_dates.append(item["Entry_Date"])
            elif "Weight" in item.keys():
                weight_dates.append(item["Entry_Date"])

        max_height_date = max(height_date for height_date in height_dates)
        year, month, day = max_height_date.year, max_height_date.month, max_height_date.day
        max_height_date = datetime(day=day, month=month, year=year).strftime("%b. %d, %y")

        max_weight_date = max(weight_date for weight_date in weight_dates)
        year, month, day = max_weight_date.year, max_weight_date.month, max_weight_date.day
        max_weight_date = datetime(day=day, month=month, year=year).strftime("%b. %d, %y")

        print(max_height_date, max_weight_date)

        for profile_item in self.ids.user_profile_items.children:
            if max_height_date == profile_item.secondary_text and profile_item.text == "Height":
                if profile_item.label_text.strip().split(" ")[1] != "cm":
                    height = float(profile_item.label_text.strip().split(" ")[0]) * 2.54
                else:
                    height = float(profile_item.label_text.strip().split(" ")[0])
            if max_weight_date == profile_item.secondary_text and profile_item.text == "Weight":
                if profile_item.label_text.strip().split(" ")[1] != "kg":
                    weight = float(profile_item.label_text.strip().split(" ")[0]) * 0.453592
                else:
                    weight = float(profile_item.label_text.strip().split(" ")[0])

        BMI = round((weight / height / height) * 10000)

        user_weight_db.add_to_database("user_weight", {"Weight": weight})

        for profile_item in self.ids.user_profile_items.children:
            if profile_item.text == "BMI":
                self.ids.user_profile_items.remove_widget(profile_item)

        self.ids.user_profile_items.add_widget(
            UserProfileItem(text="BMI", secondary_text=f"{round(weight)}kg, {round(height)}cm", label_text=f"{BMI}", icon="percent-outline")
        )

    def add_profile_items(self):
        items = user_profile_db.get_user_profile_info()
        for item in items:
            item = item.to_dict()
            year, month, day = item["Entry_Date"].year, item["Entry_Date"].month, item["Entry_Date"].day
            item_date = datetime(day=day, month=month, year=year).strftime("%b. %d, %y")
            input_type = [item_key for item_key in item.keys() if item_key != "Entry_Date"]
            self.ids.user_profile_items.add_widget(
                UserProfileItem(
                    text=input_type[0], secondary_text=item_date,
                    label_text=item[input_type[0]], icon=self.input_button_data[input_type[0]]
                )
            )

    def create_add_profile_info_dialog(self):
        self.add_profile_info_dialog = None
        self.add_profile_info_dialog = \
            MDDialog(type="custom", title="Enter New Values", content_cls=self.profile_info_dialog_content,
                     md_bg_color=hex_color("#DBF5F0"), buttons=[
                         MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#37BEB0"),
                                           on_release=lambda x: self.add_profile_info_dialog.dismiss()),
                         MDRaisedButton(text="Save", md_bg_color=hex_color("#37BEB0"),
                                             on_release=lambda x: self.save_user_profile_input())])

    def callback(self, instance):
        if instance.icon == "weight":
            self.profile_info_dialog_content = AddWeightInfo()
            self.create_add_profile_info_dialog()
        elif instance.icon == "human-male-height":
            self.profile_info_dialog_content = AddHeightInfo()
            self.create_add_profile_info_dialog()

        self.add_profile_info_dialog.open()

    def save_user_profile_input(self):
        add_profile_info = self.profile_info_dialog_content.ids
        amount = add_profile_info.input_value.text
        measurement = add_profile_info.measurement_value.text

        if amount == "" or measurement == "Measurement":
            create_error_dialog("Invalid Inputs!", "Please enter valid inputs for all the fields!")
            self.profile_info_dialog_content.ids.input_value = ""
            self.profile_info_dialog_content.ids.measurement = "Measurement"
            self.add_profile_info_dialog.dismiss()
            return -1
        else:
            measurement = measurement[measurement.index("(") + 1:measurement.index(")")]
            self.add_new_entry(self.profile_info_dialog_content.ids.input_value.hint_text, amount, measurement)
            self.profile_info_dialog_content.ids.input_value = ""
            self.profile_info_dialog_content.ids.measurement = "Measurement"
            self.add_profile_info_dialog.dismiss()

    def add_new_entry(self, input_type, amount, measurement):
        input_data = {f"{input_type}": amount + " " + measurement, "Entry_Date": datetime.today()}
        print(input_data)
        user_profile_db.add_to_database(input_type, input_data)

        year, month, day = input_data["Entry_Date"].year, input_data["Entry_Date"].month, input_data["Entry_Date"].day
        item_date = datetime(day=day, month=month, year=year).strftime("%b. %d, %y")

        for profile_item in self.ids.user_profile_items.children:
            if profile_item.secondary_text == item_date and profile_item.text == input_type:
                self.ids.user_profile_items.remove_widget(profile_item)

        self.ids.user_profile_items.add_widget(
            UserProfileItem(text=input_type, secondary_text=item_date, label_text=input_data[input_type],
                            icon=self.input_button_data[input_type])
        )

        self.check_BMI()


class UserProfileItem(MDBoxLayout):
    text = StringProperty()
    secondary_text = StringProperty()
    label_text = StringProperty()
    icon = StringProperty()
