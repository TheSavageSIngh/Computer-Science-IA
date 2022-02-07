from All_Imports.all_imports import *

kv = Builder.load_file("Food/food.kv")


class CustomFavoritesItem(OneLineAvatarIconListItem):
    pass


class CustomInfoItemAmount(IRightBody, MDBoxLayout):
    adaptive_width = True


class CustomSpecificDateItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()
    label_text = StringProperty()


class DisplayFoodInfo(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_item = None
        self.nutrients_dict = {
            "Calories": "Cal",
            "Fat": "g",
            "Saturated Fat": "g",
            "Trans Fat": "g",
            "Carbohydrates": "g",
            "Fibres": "g",
            "Sugars": "g",
            "Protein": "g",
            "Cholesterol": "mg",
            "Sodium": "mg",
            "Potassium": "mg",
            "Vitamin A": "iu",
            "Vitamin C": "mg",
            "Calcium": "mg",
            "Iron": "mg"
        }
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def create_info_items(self, instance):
        self.items = food_db.get_from_database()
        for item in self.items:
            item = item.to_dict()
            try:
                print(instance.text)
                if item["Name"] == instance.text:
                    self.info_item = item
            except IndexError:
                if item["Name"] == instance.text:
                    self.info_item = item
        print(self.info_item)

        order = ["Name", "Amount", "Calories", "Carbohydrates", "Fibres", "Sugars", "Fat",
                 "Saturated Fat", "Trans Fat", "Protein", "Other", "Cholesterol", "Sodium", "Potassium", "Vitamin A",
                 "Vitamin C", "Calcium", "Iron"]
        bolded = ["Name", "Calories", "Carbohydrates", "Protein", "Fat", "Other"]

        self.ids.list_for_food_info.clear_widgets()

        for nutrient in order:
            try:
                if not self.info_item[nutrient]:
                    self.info_item[nutrient] = "N/A"
                else:
                    self.info_item[nutrient] += f" {self.nutrients_dict[nutrient]}"
            except KeyError:
                pass

            if nutrient in bolded:
                if nutrient != "Other":
                    if order.index(nutrient) != 0:
                        self.ids.list_for_food_info.add_widget(CustomInfoItem(height=20))
                    self.ids.list_for_food_info.add_widget(
                        CustomInfoItem(text=nutrient, amount=self.info_item[nutrient], font_size=16, bold=True,
                                       height=40))
                else:
                    self.ids.list_for_food_info.add_widget(CustomInfoItem(height=20))
                    self.ids.list_for_food_info.add_widget(
                        CustomInfoItem(text=nutrient, font_size=16, height=40))
            else:
                self.ids.list_for_food_info.add_widget(
                    CustomInfoItem(text=f"{nutrient}", amount=self.info_item[nutrient], font_size=14, bold=False,
                                   height=40))

    def open_info_dialog(self, instance):
        self.create_info_items(instance)
        self.app.big_screen.ids.screen_manager.get_screen("food").info_dialog.open()


class Food(MDScreen):
    add_food_dialog = None
    edit_food_dialog = None
    info_dialog = None
    specific_date_items_dialog = None
    toolbar_date = toolbar_date
    print(toolbar_date)
    items = food_db.get_from_database()
    data = {
        "Search": "magnify",
        "Favorites": "heart",
        "Custom": "wrench"
    }

    def __init__(self, **kw):
        super().__init__(**kw)
        self.desired_calories = 2000
        self.display_macros = {
            "Calories": 0,
            "Carbohydrates": 0,
            "Protein": 0,
            "Fat": 0
        }
        self.food_item_list()
        self.count_macros()
        self.food_dialog_content = AddFood()
        self.edit_dialog_content = EditFood()
        self.info_dialog_content = DisplayFoodInfo()
        self.date_dialog_content = SpecificDateItems()
        self.create_add_food_dialog()
        self.create_specific_date_items_dialog()
        self.create_info_dialog()
        self.create_pie_chart(self.display_macros["Calories"])
        self.create_progress_bars()
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def food_item_list(self):
        for item in self.items:
            item = item.to_dict()
            if item["Calories"] is None:
                item["Calories"] = "N/A"
            self.ids.list_for_food.add_widget(
                SwipeToEditItem(text=item['Name'], secondary_text=item['Amount'], label_text=f"{item['Calories']}",
                                max_x=110, screen_name="food")
            )

    def selection_mode(self, instance_selection_list, mode):
        if mode:
            md_bg_color = hex_color("#cb3d4c")
            left_action_items = [["close", lambda x: self.close_selection_mode()]]
            right_action_items = [["trash-can", lambda x: self.delete_food(x)], ["dots-vertical"]]
        else:
            md_bg_color = hex_color("#0C6170")
            self.app.big_screen.ids.toolbar.title = str(self.app.big_screen.current_screen())
            left_action_items = [["menu", lambda x: self.app.big_screen.ids.nav_drawer.set_state("open")]]
            right_action_items = [["dots-vertical", lambda x: self.app.big_screen.callback(x)]]

        Animation(md_bg_color=md_bg_color, d=0.2).start(self.app.big_screen.ids.toolbar)
        self.app.big_screen.ids.toolbar.left_action_items = left_action_items
        self.app.big_screen.ids.toolbar.right_action_items = right_action_items

    def close_selection_mode(self):
        self.ids.list_for_food.unselected_all()
        self.app.big_screen.ids.toolbar.title = str(self.app.big_screen.current_screen())

    def on_selected(self, instance_selection_list, instance_selection_item):
        self.app.big_screen.ids.toolbar.title = str(
            len(instance_selection_list.get_selected_list_items())
        )

    def on_unselected(self, instance_selection_list, instance_selection_item):
        if instance_selection_list.get_selected_list_items():
            self.app.big_screen.ids.toolbar.title = str(self.app.big_screen.current_screen())

    def add_food(self, food_item_info):
        if food_item_info["Calories"] is None:
            food_item_info["Calories"] = "N/A"
        print(food_item_info["Calories"])
        self.ids.list_for_food.add_widget(
            SwipeToEditItem(text=food_item_info['Name'], secondary_text=food_item_info['Amount'],
                            label_text=f"{food_item_info['Calories']}", max_x=110, screen_name="food")
        )

    def edit_item(self, instance_label):
        self.items = food_db.search("Name", instance_label.text.replace("[", "~").replace("]", "~").split("~")[2])
        for item in self.items:
            self.item = item.to_dict()

        measurement = {"g": "Grams (g)", "serv": "Servings (serv)"}

        nutrition_inputs = self.edit_dialog_content.ids.edit_food_content.ids.nutrients_box
        for i in reversed(range(len(nutrition_inputs.children))):
            nutrition_inputs_name = nutrition_inputs.children[i].ids.nutrients_name.text
            nutrition_inputs_text = nutrition_inputs.children[i].ids.nutrition_info
            if not self.item[nutrition_inputs_name]:
                nutrition_inputs_text.text = ""
            else:
                nutrition_inputs_text.text = self.item[nutrition_inputs_name]
        self.edit_dialog_content.ids.edit_food_content.ids.food_name.text = self.item["Name"]
        self.edit_dialog_content.ids.edit_food_content.ids.food_amount.text = (self.item["Amount"].split(" "))[0]
        self.edit_dialog_content.ids.edit_food_content.ids.measurement_picker.text = \
            measurement[(self.item["Amount"].split(" "))[1]]

        self.create_edit_food_dialog(self.edit_dialog_content)
        self.edit_food_dialog.open()

    def delete_food(self, instance_selection_list):
        for i in self.ids.list_for_food.get_selected_list_items():
            self.ids.list_for_food.remove_widget(i)
            food_db.remove_from_database(i.children[1].text)
        self.update_pie_chart()

    def count_macros(self):
        self.items = food_db.get_from_database()
        self.display_macros = {
            "Calories": 0,
            "Carbohydrates": 0,
            "Protein": 0,
            "Fat": 0
        }
        for item in self.items:
            item = item.to_dict()
            for macro in self.display_macros.keys():
                if item[f"{macro}"]:
                    self.display_macros[macro] = self.display_macros[macro] + float(item[f"{macro}"])

    def create_progress_bars(self):
        for macro in self.display_macros.keys():
            try:
                data = self.get_progress_bar_data(macro)
                self.ids.progress_bar_box.add_widget(MacroProgressBar(text=f"{macro} [{data[0]} g]", value=data[1]))
            except KeyError:
                continue

    def update_progress_bars(self):
        self.count_macros()
        for macro in self.display_macros.keys():
            try:
                data = self.get_progress_bar_data(macro)
                self.ids.progress_bar_box.add_widget(
                    MacroProgressBar(text=f"{macro} [{data[0]} g]", value=data[1]))
            except KeyError:
                continue

    def create_pie_chart(self, calories):
        if calories > self.desired_calories:
            self.ids.graph_card.add_widget(MDLabel(text="You surpassed your caloric goal!"
                                                        f"\n\nCalories: {round(self.display_macros['Calories'])}",
                                                   halign="center", padding=(10, 10)))
        else:
            colors = ["#e75c6a", "#DBF5F0"]
            sizes = [(calories / self.desired_calories) * 100, 100 - (calories / self.desired_calories) * 100]
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, colors=colors, startangle=90)
            plt.title(f"Calories [{round(self.display_macros['Calories'])}]")
            ax1.axis("equal")
            fig1.patch.set_facecolor("#DBF5F0")
            self.ids.graph_card.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def update_pie_chart(self):
        self.display_macros["Calories"] = 0
        self.ids.graph_card.remove_widget(self.ids.graph_card.children[0])
        self.ids.progress_bar_box.clear_widgets()
        self.count_macros()
        self.update_progress_bars()
        if self.display_macros["Calories"] > self.desired_calories:
            self.ids.graph_card.add_widget(MDLabel(text="You surpassed your caloric goal!"
                                                        f"\nCalories: {round(self.display_macros['Calories'])}",
                                                   halign="center"))
        else:
            self.create_pie_chart(self.display_macros["Calories"])

    def get_progress_bar_data(self, macro):
        macro_percentage = {
            "Carbohydrates": 0.5,
            "Protein": 0.25,
            "Fat": 0.25
        }
        macro_calories = {
            "Carbohydrates": 4,
            "Protein": 4,
            "Fat": 9
        }
        total_required_macro_calories = self.desired_calories * macro_percentage[f"{macro}"]
        total_required_macro_grams = total_required_macro_calories/(macro_calories[f"{macro}"])
        return [round(self.display_macros[f"{macro}"]), (self.display_macros[f"{macro}"] / total_required_macro_grams) * 100]

    def switch_screen(self, next_screen):
        self.manager.current = next_screen

    def create_edit_food_dialog(self, edit_food_content):
        if not self.edit_food_dialog:
            self.edit_food_dialog = MDDialog(title="Edit Food", type="custom", content_cls=edit_food_content, buttons=[
                MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#794cec"),
                             on_release=lambda x: self.edit_food_dialog.dismiss()),
                MDRaisedButton(text="Save", md_bg_color=hex_color("#794cec"),
                               on_release=lambda x: self.get_edit_formatted_nutrients())
            ])

    def create_add_food_dialog(self):
        if not self.add_food_dialog:
            self.add_food_dialog = \
                MDDialog(type="custom", content_cls=self.food_dialog_content, md_bg_color=hex_color("#DBF5F0"),
                         buttons=[MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#37BEB0"),
                                               on_release=lambda x: self.add_food_dialog.dismiss()),
                                  MDRaisedButton(text="Save", md_bg_color=hex_color("#37BEB0"),
                                                 on_release=lambda x: self.get_formatted_nutrients())])

    def create_info_dialog(self):
        if not self.info_dialog:
            self.info_dialog = \
                MDDialog(type="custom", md_bg_color=hex_color("#DBF5F0"), content_cls=self.info_dialog_content,
                         buttons=[MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#794cec"),
                                               on_release=lambda x: self.refresh_info_dialog())])

    def refresh_info_dialog(self):
        self.info_dialog_content.ids.list_for_food_info.clear_widgets()
        self.info_dialog.dismiss()

    def confirm_edit_changes(self, edit_input):
        food_db.edit_database(edit_input['Name'], edit_input)
        for item in self.ids.list_for_food.children:
            if item.children[-1].text.lower() == edit_input["Name"].split("[")[0].strip().lower():
                self.ids.list_for_food.remove_widget(item)
                self.ids.list_for_food.add_widget(
                    SwipeToEditItem(text=edit_input['Name'], secondary_text=edit_input['Amount'],
                                    label_text=f"{edit_input['Calories']}", max_x=110, screen_name="food")
                )
                self.update_pie_chart()

    def get_formatted_nutrients(self):
        food_input = self.add_food_dialog.content_cls.format_nutrients_text()
        print("food_input", food_input)
        if food_input == -1:
            pass
        else:
            food_db.add_to_database(food_input['Name'], food_input)
            self.add_food(food_input)
            self.update_pie_chart()
        self.add_food_dialog.dismiss(force=True)

    def get_edit_formatted_nutrients(self):
        edit_input = self.edit_food_dialog.content_cls.format_edit_nutrients_text()
        print(edit_input)
        if edit_input == -1:
            pass
        else:
            self.confirm_edit_changes(edit_input)
            self.update_pie_chart()
        self.edit_food_dialog.dismiss(force=True)

    def open_date_picker(self):
        date_picker = \
            MDDatePicker(day=int(data_date[0:2]), month=int(data_date[3:5]), year=int(data_date[6:]),
                         min_year=int(data_date[6:]) - 5, max_year=int(data_date[6:]),
                         text_current_color=hex_color("#0C6170"), primary_color=hex_color("#37BEB0"),
                         text_button_color=hex_color("#0C6170"), accent_color=hex_color("#DBF5F0"),
                         text_weekday_color=hex_color("#000000"), selector_color=hex_color("#00A08D"),
                         input_field_text_color=hex_color("#212121"), text_color=hex_color("#696969"))
        date_picker.bind(on_save=self.on_date_picker_save, on_cancel=self.on_date_picker_cancel)
        date_picker.open()

    def on_date_picker_save(self, instance, value, date_range):
        self.add_specific_date_items(value)

    def on_date_picker_cancel(self, instance, value):
        pass

    def add_specific_date_items(self, specific_date):
        specific_date = specific_date.strftime("%d_%m_%Y")
        specific_items_length = food_db.search_specific_date("database", "user_foods", f"{specific_date}", "length")
        if not specific_items_length and len(self.date_dialog_content.children) < 1:
            self.date_dialog_content.add_widget(MDLabel(text="No Items to Display!", valign="center", halign="center"))
        elif specific_items_length and len(self.date_dialog_content.children) < 1:
            self.date_dialog_content.add_widget(ScrollView())
            self.date_dialog_content.children[0].add_widget(MDList())
            specific_items = food_db.search_specific_date("database", "user_foods", f"{specific_date}", "items")
            for item in specific_items:
                item = item.to_dict()
                if not item["Calories"]:
                    item["Calories"] = "N/A"
                self.date_dialog_content.children[0].children[0].add_widget(
                    CustomSpecificDateItem(text=item["Name"], secondary_text=item["Amount"],
                                           label_text=item["Calories"])
                )
        self.specific_date_items_dialog.open()

    def create_specific_date_items_dialog(self):
        if not self.specific_date_items_dialog:
            self.specific_date_items_dialog = \
                MDDialog(type="custom", md_bg_color=hex_color("#DBF5F0"), content_cls=self.date_dialog_content,
                         buttons=[MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#794cec"),
                                               on_release=lambda x: self.remove_specific_date_items())])

    def remove_specific_date_items(self):
        if len(self.date_dialog_content.children) == 1:
            self.date_dialog_content.remove_widget(self.date_dialog_content.children[0])
        self.specific_date_items_dialog.dismiss()


class SpecificDateItems(MDBoxLayout):
    pass


class MacroProgressBar(MDBoxLayout):
    text = StringProperty()
    value = NumericProperty()


class AddFoodTab(MDFloatLayout, MDTabsBase):
    pass


class EditFood(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nutrients_dict = {
            "Calories": "Cal",
            "Fat": "g",
            "Saturated Fat": "g",
            "Trans Fat": "g",
            "Carbohydrates": "g",
            "Fibres": "g",
            "Sugars": "g",
            "Protein": "g",
            "Cholesterol": "mg",
            "Sodium": "mg",
            "Potassium": "mg",
            "Vitamin A": "iu",
            "Vitamin C": "mg",
            "Calcium": "mg",
            "Iron": "mg"
        }
        self.add_custom()

    def add_custom(self):
        for name in self.nutrients_dict.keys():
            self.ids.edit_food_content.ids.nutrients_box.add_widget(
                NutritionInfoTextField(main_label=name, measurement_type=self.nutrients_dict[name]))

    def format_edit_nutrients_text(self):
        for nutrient in self.ids.edit_food_content.ids.nutrients_box.children:
            self.nutrients_dict[nutrient.ids.nutrients_name.text] = nutrient.ids.nutrition_info.text
            nutrient.ids.nutrition_info.text = ""

        for name in self.nutrients_dict.keys():
            if [False for boolean in [letter.isdigit() for letter in self.nutrients_dict[name]] if not boolean]:
                self.nutrients_dict[name] = None
        print(self.nutrients_dict)

        measurement = self.ids.edit_food_content.ids.measurement_picker.text

        food_name, food_amount = \
            self.ids.edit_food_content.ids.food_name.text.strip().title(), \
            self.ids.edit_food_content.ids.food_amount.text.strip()

        if [False for boolean in [letter.isalpha() for letter in food_name] if not boolean] or \
                [False for boolean in [letter.isdigit() for letter in food_amount] if not boolean] or \
                food_name == "" or food_amount == "" or measurement == "Measurement Type":
            create_error_dialog("Invalid Input!", "Please fill in the required fields!")
            return -1
        else:
            measurement = measurement[measurement.index("(") + 1:measurement.index(")")]
            self.nutrients_dict["Name"] = food_name
            self.nutrients_dict["Amount"] = food_amount + " " + measurement
            return self.nutrients_dict


class NutritionInfoTextField(MDBoxLayout):
    main_label = StringProperty()
    measurement_type = StringProperty()


class CustomTab(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda x: self.create_measurement_menu())

    def create_measurement_menu(self):
        items = ["Grams (g)", "Servings (serv)"]
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": i,
                "height": dp(56),
                "on_release": lambda x=i: self.menu_callback(x),
            } for i in items
        ]
        self.measurement_menu = MDDropdownMenu(
            caller=self.ids.measurement_picker,
            items=menu_items,
            width_mult=3,
        )

    def menu_callback(self, text_item):
        self.ids.measurement_picker.text = f"{text_item}"
        self.measurement_menu.dismiss()


class CustomSearchItem(OneLineListItem):
    text = StringProperty()


class SearchedItemInfo(MDBoxLayout):
    pass


class SearchedSelectAmount(MDBoxLayout):
    measurement_menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = []

    def create_measurement_menu(self):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": i,
                "height": dp(56),
                "on_release": lambda x=i: self.menu_callback(x),
            } for i in self.items
        ]
        self.measurement_menu = MDDropdownMenu(
            caller=self.ids.measurement_picker,
            items=menu_items,
            width_mult=4,
        )

    def menu_callback(self, text_item):
        self.ids.measurement_picker.text = f"{text_item}"
        self.measurement_menu.dismiss()


class SearchTab(MDBoxLayout):
    searched_item_dialog = None
    select_amount_dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_item = {
            "Name": "",
            "Energy": "",
            "Carbohydrate, by difference": "",
            "Fiber, total dietary": "",
            "Sugars, total including NLEA": "",
            "Total lipid (fat)": "",
            "Fatty acids, total saturated": "",
            "Fatty acids, total trans": "",
            "Protein": "",
            "Other": "",
            "Cholesterol": "",
            "Sodium, Na": "",
            "Potassium, K": "",
            "Vitamin A, IU": "",
            "Vitamin C, total ascorbic acid": "",
            "Calcium, Ca": "",
            "Iron, Fe": ""
        }
        self.final_info_item = {
            "Name": "",
            "Calories": "",
            "Carbohydrates": "",
            "Fibres": "",
            "Sugars": "",
            "Fat": "",
            "Saturated Fat": "",
            "Trans Fat": "",
            "Protein": "",
            "Other": "",
            "Cholesterol": "",
            "Sodium": "",
            "Potassium": "",
            "Vitamin A": "",
            "Vitamin C": "",
            "Calcium": "",
            "Iron": ""
        }
        self.serving_size = ""
        self.select_amount_dialog_content = SearchedSelectAmount()
        self.searched_item_dialog_content = SearchedItemInfo()
        self.create_search_item_info_dialog()
        self.create_select_amount_dialog()
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def set_list_food_items(self, text="", search=False):
        # get API KEY to access the database
        key = "9yVa2T2OlmILdgFdNSz2xz5uxxCcgOZn8vX2hoNV"
        # access url with specific query, with the text inputted by the user
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={key}&query={text}"
        # get all the data, and convert it into json format
        self.data = requests.get(url).json()

        # function add a CustomSearchItem for an item
        def add_item(item_info):
            self.ids.search_food_items.data.append(
                {
                    "viewclass": "CustomSearchItem",
                    "text": item_info["description"].title(),
                    "on_release": lambda x=0: self.add_to_info_screen(item_info),
                }
            )

        self.ids.search_food_items.data = []
        #
        # for item in self.data["foods"]:
        #     print(item["description"])
        #     self.ids.search_food_items.data.append(
        #         {"text": item["description"], "on_release": lambda x=0: self.add_to_info_screen(item["description"])})
        # [{"text": item["description"], "on_release": lambda x=0: self.add_to_info_screen(item["description"])}
        #  for item in self.data["foods"]]  # list to store all current display items
        # for each item in the queried data, add a CustomSearchItem
        for item in self.data["foods"]:
            # if the user is currently searching
            if search:
                # if the searched text matches the item's text, then add an item to the recycle view
                if text.lower().strip() in item["description"].lower():
                    add_item(item)

    def create_select_amount_dialog(self):
        if not self.select_amount_dialog:
            self.select_amount_dialog = MDDialog(type="custom", content_cls=self.select_amount_dialog_content, buttons=[
                MDFlatButton(text="Cancel", theme_text_color="Custom", text_color=hex_color("#794cec"),
                             on_release=lambda x: self.close_dialogs()),
                MDRaisedButton(text="Save", md_bg_color=hex_color("#794cec"),
                               on_release=lambda x: self.save_searched_item_amount())
            ])

    def create_search_item_info_dialog(self):
        if not self.searched_item_dialog:
            self.searched_item_dialog = MDDialog(type="custom", content_cls=self.searched_item_dialog_content, buttons=[
                MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#794cec"),
                             on_release=lambda x: self.refresh_search_item_dialog()),
                MDRaisedButton(text="Select Amount", md_bg_color=hex_color("#794cec"),
                               on_release=lambda x: self.select_amount_dialog.open())
            ])

    def close_dialogs(self):
        self.select_amount_dialog.dismiss()
        self.searched_item_dialog.dismiss()

    def save_searched_item_amount(self):
        amount = self.select_amount_dialog_content.ids.food_amount.text
        measurement = self.select_amount_dialog_content.ids.measurement_picker.text
        if measurement == "Measurement Picker":
            create_error_dialog("Invalid Input!", "Please fill in the required fields!")
            return -1
        measurement = measurement[measurement.index("(") + 1:measurement.index(")")]
        for nutrient_name in self.final_info_item.keys():
            if nutrient_name != "Other":
                if nutrient_name != "Name":
                    self.final_info_item[nutrient_name] = (self.final_info_item[nutrient_name].split(" "))[0]
                    if self.final_info_item[nutrient_name] == "N/A":
                        self.final_info_item[nutrient_name] = None
                    if measurement == "g":
                        if self.final_info_item[nutrient_name]:
                            self.final_info_item[nutrient_name] = \
                                str(round((float(self.final_info_item[nutrient_name]) * (int(amount) / 100))))
                            print(self.final_info_item[nutrient_name])
                    elif measurement == "serv":
                        if self.final_info_item[nutrient_name]:
                            self.final_info_item[nutrient_name] = \
                                str(round(float(self.final_info_item[nutrient_name]) *
                                          ((int(amount) * float(self.serving_size)) / 100)))
        self.final_info_item["Amount"] = amount + " " + measurement
        self.add_search_item(self.final_info_item)
        self.close_dialogs()

    def add_search_item(self, final_info_item):
        items = food_db.get_from_database()
        number = 0
        for item in items:
            item = item.to_dict()
            if final_info_item["Name"].lower() == ((item["Name"].split("["))[0]).strip().lower():
                number += 1
        if number != 0:
            final_info_item["Name"] = str(final_info_item["Name"] + f" [{number}]")
        food_db.add_to_database(final_info_item["Name"], final_info_item)
        self.app.big_screen.ids.screen_manager.get_screen("food").ids.list_for_food.add_widget(
            SwipeToEditItem(text=f"{final_info_item['Name']}", secondary_text=f"{final_info_item['Amount']}",
                            label_text=f"{final_info_item['Calories']}", max_x=110, screen_name="food")
        )
        self.app.big_screen.ids.screen_manager.get_screen("food").update_pie_chart()

    def refresh_search_item_dialog(self):
        self.searched_item_dialog_content.ids.list_for_info.clear_widgets()
        self.searched_item_dialog.dismiss()

    def format_info(self, instance):
        for nutrient_info in instance["foodNutrients"]:
            if nutrient_info["nutrientName"] == "Energy" and nutrient_info["unitName"] == "kJ":
                pass
            else:
                self.info_item[f"{nutrient_info['nutrientName']}"] = str(nutrient_info["value"]) + " " + \
                                                                     nutrient_info["unitName"].lower()
        self.info_item["Name"] = instance["description"].title()
        amounts = []
        for nutrient_name, amount in self.info_item.items():
            amounts.append(amount)
        for nutrient_name in self.final_info_item.keys():
            if nutrient_name != "Other":
                if amounts[0] != "":
                    self.final_info_item[nutrient_name] = amounts[0]
                else:
                    self.final_info_item[nutrient_name] = "N/A"
                amounts.pop(0)
        return self.final_info_item

    def add_to_info_screen(self, instance):
        try:
            self.serving_size = instance["servingSize"]
            self.select_amount_dialog_content.measurement_menu = None
            self.select_amount_dialog_content.items = ["Grams (g)", "Servings (serv)"]
            self.select_amount_dialog_content.create_measurement_menu()
        except KeyError:
            self.select_amount_dialog_content.measurement_menu = None
            self.select_amount_dialog_content.items = ["Grams (g)"]
            self.select_amount_dialog_content.create_measurement_menu()
        info_items = self.format_info(instance)
        for nutrient in info_items.keys():
            bolded = ["Name", "Calories", "Carbohydrates", "Protein", "Fat", "Other"]
            if nutrient in bolded:
                if nutrient != "Other":
                    if nutrient != "Name":
                        self.searched_item_dialog_content.ids.list_for_info.add_widget(CustomInfoItem(height=20))
                    self.searched_item_dialog_content.ids.list_for_info.add_widget(
                        CustomInfoItem(text=nutrient, amount=info_items[nutrient], font_size=16, bold=True, height=40))
                else:
                    self.searched_item_dialog_content.ids.list_for_info.add_widget(CustomInfoItem(height=20))
                    self.searched_item_dialog_content.ids.list_for_info.add_widget(
                        CustomInfoItem(text=nutrient, font_size=16, height=40))
            else:
                self.searched_item_dialog_content.ids.list_for_info.add_widget(
                    CustomInfoItem(text=f"{nutrient}", amount=info_items[nutrient], font_size=14, bold=False,
                                   height=40))
        self.searched_item_dialog.open()


class FavoritesTab(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AddFood(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.error_dialog = None
        self.nutrients_dict = {
            "Calories": "Cal",
            "Fat": "g",
            "Saturated Fat": "g",
            "Trans Fat": "g",
            "Carbohydrates": "g",
            "Fibres": "g",
            "Sugars": "g",
            "Protein": "g",
            "Cholesterol": "mg",
            "Sodium": "mg",
            "Potassium": "mg",
            "Vitamin A": "iu",
            "Vitamin C": "mg",
            "Calcium": "mg",
            "Iron": "mg"
        }
        self.add_custom()
        self.add_favorites()
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def add_custom(self):
        for name in self.nutrients_dict.keys():
            self.ids.custom_tab_content.ids.nutrients_box.add_widget(
                NutritionInfoTextField(main_label=name, measurement_type=self.nutrients_dict[name]))

    def add_favorites(self):
        favorite_items = favorites_db.get_from_database()
        for item in favorite_items:
            item = item.to_dict()
            self.ids.favorites_tab_content.ids.favorites_items.add_widget(
                CustomFavoritesItem(text=item['Name']))

    # validate and process the data for each food item
    def format_nutrients_text(self):
        # get all text from each nutrient text input
        for nutrient in self.ids.custom_tab_content.ids.nutrients_box.children:
            # add each text item to the nutrients dictionary
            self.nutrients_dict[nutrient.ids.nutrients_name.text] = nutrient.ids.nutrition_info.text.strip()
            nutrient.ids.nutrition_info.text = ""  # clear the text input box
        # check to see if any value in the dictionary is not a number (empty)
        for name in self.nutrients_dict.keys():
            if self.nutrients_dict[name].strip() == "":
                self.nutrients_dict[name] = None  # make any empty items into None (as they are optional)

        # get the measurement type from the dropdown menu
        measurement = self.ids.custom_tab_content.ids.measurement_picker.text
        # get the name and amount of the food
        food_name, food_amount = \
            self.ids.custom_tab_content.ids.food_name.text.strip().title(), \
            self.ids.custom_tab_content.ids.food_amount.text.strip()
        # error check the food name, amount and measurement to prevent invalid inputs
        if food_name == "" or food_amount == "" or measurement == "Measurement Type":
            # display an error message, stating that the inputs were invalid.
            create_error_dialog("Invalid Input!", "Please enter a valid input in the required fields!")
            # clear the food name and amount fields
            self.ids.custom_tab_content.ids.food_name.text, self.ids.custom_tab_content.ids.food_amount.text, \
            self.ids.custom_tab_content.ids.measurement_picker.text = "", "", "Measurement Type"
            return -1  # return -1 (use later to check if data was valid)
        else:
            # if the data is valid, then get the units for the measurement
            measurement = measurement[measurement.index("(") + 1:measurement.index(")")]
            # set the name and amount fields in the nutrients dictionary to the input
            self.nutrients_dict["Name"] = food_name
            self.nutrients_dict["Amount"] = food_amount + " " + measurement
            # clear the food name and amount fields
            self.ids.custom_tab_content.ids.food_name.text = ""
            self.ids.custom_tab_content.ids.food_amount.text = ""
            self.ids.custom_tab_content.ids.measurement_picker.text = "Measurement Type"
            return self.nutrients_dict  # return the nutrients dictionary for future use

    def remove_favorites(self, instance):
        favorites_db.remove_from_database(instance.text)
        self.ids.favorites_tab_content.ids.favorites_items.remove_widget(instance)

    def add_favorite_to_main(self, instance):
        favorite_name = instance.text
        favorite_items = favorites_db.search("Name", favorite_name)
        items = food_db.get_from_database()
        number = 0
        for item in items:
            item = item.to_dict()
            if favorite_name.lower() == ((item["Name"].split("["))[0]).strip().lower():
                number += 1
        for favorite_item in favorite_items:
            favorite_item = favorite_item.to_dict()
            print(favorite_item)
            if number != 0:
                favorite_item["Name"] = str(favorite_item["Name"] + f" [{number}]")
            food_db.add_to_database(favorite_item["Name"], favorite_item)
            if favorite_item["Calories"] is None:
                favorite_item["Calories"] = "N/A"
            self.app.big_screen.ids.screen_manager.get_screen("food").ids.list_for_food.add_widget(
                SwipeToEditItem(text=f"{favorite_item['Name']}", secondary_text=f"{favorite_item['Amount']}",
                                label_text=f"{favorite_item['Calories']}", max_x=110, screen_name="food")
            )
            self.app.big_screen.ids.screen_manager.get_screen("food").update_pie_chart()
            Snackbar(text=f"{favorite_name} was added to your Food Log!", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        pass
