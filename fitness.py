from All_Imports.all_imports import *

kv = Builder.load_file("Fitness/fitness.kv")


class DisplayWorkoutInfo(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_item = None
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def create_info_items(self, instance):
        self.items = workout_db.get_from_database()
        for item in self.items:
            item = item.to_dict()
            item["Duration"] = f"{round(item['Duration'])} mins"
            item["Burned_Calories"] = f"{item['Burned_Calories']} Cals"
            if item["Exercise_Name"] == instance.text:
                self.info_item = item

        order = ["Exercise_Name", "Duration", "Burned_Calories", "MET"]
        bolded = ["Exercise_Name", "Burned_Calories"]

        self.ids.list_for_workout_info.clear_widgets()

        for info in order:
            if info in bolded:
                if order.index(info) != 0:
                    self.ids.list_for_workout_info.add_widget(CustomInfoItem(height=20))
                self.ids.list_for_workout_info.add_widget(
                    CustomInfoItem(text=f"{info.replace('_', ' ')}", amount=f"{self.info_item[info]}", font_size=14,
                                   bold=True, height=40)
                )
            else:
                self.ids.list_for_workout_info.add_widget(
                    CustomInfoItem(text=f"{info.replace('_', ' ')}", amount=f"{self.info_item[info]}", font_size=14,
                                   bold=False, height=40)
                )

    def open_info_dialog(self, instance):
        self.create_info_items(instance)
        self.app.big_screen.ids.screen_manager.get_screen("fitness").info_dialog.open()


class AddWorkout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exercise_data = {}
        self.read_exercise_list()
        Clock.schedule_once(lambda x: self.create_category_picker())
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def read_exercise_list(self):
        file_path = "Database/exercises_with_met.csv"

        with open(file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            categories = {'bicycling': [],
                          'conditioning exercise': [],
                          'dancing': [],
                          'fishing and hunting': [],
                          'home activities': [],
                          'home repair': [],
                          'inactivity quiet or light': [],
                          'lawn and garden': [],
                          'miscellaneous': [],
                          'music playing': [],
                          'occupation': [],
                          'running': [],
                          'self care': [],
                          'sports': [],
                          'transportation': [],
                          'walking': [],
                          'water activities': [],
                          'winter activities': [],
                          'volunteer activities': []}

            for row in csv_reader:
                categories[row[0]].append([row[1], row[2]])
        self.exercise_data = categories

    def set_list_exercises_category(self, category_name=""):
        def add_exercise_item(name, met_value):
            self.ids.workout_search_bar.data.append(
                {
                    "viewclass": "OneLineListItem",
                    "text": name,
                    "on_release": lambda x=0: self.get_info(name, met_value),
                }
            )

        self.ids.workout_search_bar.data = []

        if category_name.lower() not in ["category", "all categories"]:
            for exercise in self.exercise_data[category_name.lower()]:
                add_exercise_item(exercise[0].title(), exercise[1])
        elif category_name.lower() == "all categories":
            for category in self.exercise_data.keys():
                for exercise in self.exercise_data[category]:
                    add_exercise_item(exercise[0].title(), exercise[1])

    def set_list_exercises_search(self, category_name="", exercise_name="", search=False):
        def add_exercise_item(name, met_value):
            self.ids.workout_search_bar.data.append(
                {
                    "viewclass": "OneLineListItem",
                    "text": name,
                    "on_release": lambda x=0: self.get_info(name, met_value),
                }
            )

        self.ids.workout_search_bar.data = []

        if category_name.lower() in ["category", "all categories"]:
            for category in self.exercise_data.keys():
                for exercise in self.exercise_data[category]:
                    if exercise_name.lower() in exercise[0].lower():
                        add_exercise_item(exercise[0].title(), exercise[1])
        else:
            for exercise in self.exercise_data[category_name.lower()]:
                if exercise_name.lower() in exercise[0].lower():
                    add_exercise_item(exercise[0].title(), exercise[1])

    def get_info(self, exercise_name, met_value):
        fitness_screen = self.app.big_screen.ids.screen_manager.get_screen("fitness")
        fitness_screen.add_time_calories_dialog_content.ids.exercise_name.text = exercise_name
        fitness_screen.add_time_calories_dialog_content.ids.met_value.text = met_value
        return fitness_screen.add_time_dialog.open()

    def create_category_picker(self):
        items = ['Bicycling', 'Conditioning Exercise', 'Dancing', 'Fishing And Hunting', 'Home Activities',
                 'Home Repair', 'Inactivity Quiet Or Light', 'Lawn And Garden', 'Miscellaneous', 'Music Playing',
                 'Occupation', 'Running', 'Self Care', 'Sports', 'Transportation', 'Walking', 'Water Activities',
                 'Winter Activities', 'Volunteer Activities', "All Categories"]

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": i,
                "height": dp(56),
                "on_release": lambda x=i: self.menu_callback(x),
            } for i in items
        ]
        self.category_picker_menu = MDDropdownMenu(
            caller=self.ids.category_picker,
            items=menu_items,
            position="bottom",
            width_mult=3,
        )

    def menu_callback(self, text_item):
        self.ids.category_picker.text = f"{text_item}"
        self.set_list_exercises_category(text_item)
        self.category_picker_menu.dismiss()


class AddTime(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = 0
        self.end_time = 0
        self.current_time = datetime.strptime(f"{(datetime.now()).strftime('%H:%M:%S')}", "%H:%M:%S").time()
        self.start_time_dialog = \
            MDTimePicker(primary_color=hex_color("#DBF5F0"), accent_color=hex_color("#A4E5E0"),
                         text_button_color=hex_color("#0C6170"), selector_color=hex_color("#37BEB0"))
        self.end_time_dialog = \
            MDTimePicker(primary_color=hex_color("#DBF5F0"), accent_color=hex_color("#A4E5E0"),
                         text_button_color=hex_color("#0C6170"), selector_color=hex_color("#37BEB0"))

    def open_start_time_picker(self):
        self.start_time_dialog.set_time(self.current_time)
        self.start_time_dialog.bind(on_save=self.get_time)
        self.start_time_dialog.open()

    def open_end_time_picker(self):
        self.end_time_dialog.set_time(self.current_time)
        self.end_time_dialog.bind(on_save=self.get_time)
        self.end_time_dialog.open()

    def get_time(self, instance, time):
        if instance == self.start_time_dialog:
            self.start_time = time
        elif instance == self.end_time_dialog:
            self.end_time = time

    def get_intensity(self):
        return self.ids.intensity_picker.text

    def get_exercise_and_met(self):
        return {"Exercise_Name": self.ids.exercise_name.text, "MET": self.ids.met_value.text}


class Fitness(MDScreen):
    add_workout_dialog = None
    add_time_dialog = None
    edit_time_dialog = None
    info_dialog = None
    toolbar_date = toolbar_date
    items = workout_db.get_from_database()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.workout_time_goal = 90
        self.total_workout_time = 0
        self.estimated_burned_calories = (5 * 3.5 * 73 / 200) * self.workout_time_goal
        self.total_burned_calories = 0
        self.workout_list()
        self.workout_dialog_content = AddWorkout()
        self.add_time_calories_dialog_content = AddTime()
        self.edit_time_calories_dialog_content = AddTime()
        self.info_dialog_content = DisplayWorkoutInfo()
        self.create_add_workout_dialog()
        self.create_add_time_and_calories_burned_dialog()
        self.count_time_and_calories()
        self.add_time_pie_chart()
        self.add_burned_calories_pie_chart()
        self.create_info_dialog()
        Clock.schedule_once(lambda x: self.get_app())

    def get_app(self):
        self.app = MDApp.get_running_app()

    def workout_list(self):
        for item in self.items:
            item = item.to_dict()
            self.ids.list_for_workouts.add_widget(
                SwipeToEditItem(text=f"{item['Exercise_Name']}", secondary_text=f"{round(item['Duration'])} mins",
                                label_text=f"{item['Burned_Calories']}", max_x=65, screen_name="fitness")
            )

    def selection_mode(self, instance_selection_list, mode):
        if mode:
            md_bg_color = hex_color("#cb3d4c")
            left_action_items = [["close", lambda x: self.close_selection_mode()]]
            right_action_items = [["trash-can", lambda x: self.delete_workout(x)], ["dots-vertical"]]
        else:
            md_bg_color = hex_color("#0C6170")
            self.app.big_screen.ids.toolbar.title = str(self.app.big_screen.current_screen())
            left_action_items = [["menu", lambda x: self.app.big_screen.ids.nav_drawer.set_state("open")]]
            right_action_items = [["dots-vertical", lambda x: self.app.big_screen.callback(x)]]

        Animation(md_bg_color=md_bg_color, d=0.2).start(self.app.big_screen.ids.toolbar)
        self.app.big_screen.ids.toolbar.left_action_items = left_action_items
        self.app.big_screen.ids.toolbar.right_action_items = right_action_items

    def close_selection_mode(self):
        self.ids.list_for_workouts.unselected_all()
        self.app.big_screen.ids.toolbar.title = str(self.app.big_screen.current_screen())

    def on_selected(self, instance_selection_list, instance_selection_item):
        self.app.big_screen.ids.toolbar.title = str(
            len(instance_selection_list.get_selected_list_items())
        )

    def on_unselected(self, instance_selection_list, instance_selection_item):
        if instance_selection_list.get_selected_list_items():
            self.app.big_screen.ids.toolbar.title = str(self.app.big_screen.current_screen())

    def create_add_workout_dialog(self):
        if not self.add_workout_dialog:
            self.add_workout_dialog = \
                MDDialog(type="custom", md_bg_color=hex_color("#DBF5F0"), content_cls=self.workout_dialog_content,
                         buttons=[MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#37BEB0"),
                                               on_release=lambda x: self.add_workout_dialog.dismiss())])

    def create_add_time_and_calories_burned_dialog(self):
        if not self.add_time_dialog:
            self.add_time_dialog = MDDialog(type="custom", md_bg_color=hex_color("#DBF5F0"),
                                            content_cls=self.add_time_calories_dialog_content, buttons=[
                    MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#37BEB0"),
                                 on_release=lambda x: self.add_time_dialog.dismiss()),
                    MDRaisedButton(text="Save", md_bg_color=hex_color("#37BEB0"),
                                   on_release=lambda x: self.add_workout())
                ])

    def create_edit_time_and_calories_burned_dialog(self, edit_time_and_calories_burned_content):
        if not self.edit_time_dialog:
            self.edit_time_dialog = MDDialog(type="custom", md_bg_color=hex_color("#DBF5F0"),
                                             content_cls=edit_time_and_calories_burned_content, buttons=[
                    MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#37BEB0"),
                                 on_release=lambda x: self.edit_time_dialog.dismiss()),
                    MDRaisedButton(text="Save", md_bg_color=hex_color("#37BEB0"),
                                   on_release=lambda x: self.finalize_edit())
                ])

    def get_time_calories_info(self, dialog_name, dialog_content):
        start_time = dialog_content.start_time
        end_time = dialog_content.end_time
        exercise_info = dialog_content.get_exercise_and_met()

        if not start_time or not end_time:
            dialog_name.dismiss(force=True)
            create_error_dialog("Invalid Times!", "Please pick a value for the time fields!")
            return -1

        if start_time >= end_time:
            dialog_name.dismiss(force=True)
            create_error_dialog("Invalid Times!", "Please enter a valid range of times!")
            return -1

        start_time = \
            datetime(hour=int(str(start_time)[:2]), minute=int(str(start_time)[3:5]), second=int(str(start_time)[6:]),
                     day=int(data_date[0:2]), month=int(data_date[3:5]), year=int(data_date[6:]))
        end_time = \
            datetime(hour=int(str(end_time)[:2]), minute=int(str(end_time)[3:5]), second=int(str(end_time)[6:]),
                     day=int(data_date[0:2]), month=int(data_date[3:5]), year=int(data_date[6:]))

        total_time = end_time - start_time
        exercise_info["Duration"] = total_time
        exercise_info["Duration"] = exercise_info["Duration"].seconds / 60
        items = user_weight_db.get_from_database()
        for item in items:
            item = item.to_dict()
            self.weight = item["Weight"]
        # (MET * 3.5 * weight (kg) )/ 200 = calories burned per min
        exercise_info["Burned_Calories"] = float(exercise_info["MET"]) * 3.5 * self.weight / 200
        exercise_info["Burned_Calories"] = round(exercise_info["Burned_Calories"] * exercise_info["Duration"])
        return exercise_info

    def add_workout(self):
        workout_item = self.get_time_calories_info(self.add_workout_dialog, self.add_time_calories_dialog_content)
        print(workout_item)
        if workout_item != -1:
            workout_db.add_to_database(workout_item["Exercise_Name"], workout_item)
            self.ids.list_for_workouts.add_widget(
                SwipeToEditItem(
                    text=f"{workout_item['Exercise_Name']}", secondary_text=f"{round(workout_item['Duration'])} mins",
                    label_text=f"{workout_item['Burned_Calories']}", max_x=65, screen_name="fitness")
            )
            self.update_pie_charts()
        self.add_time_dialog.dismiss()
        self.add_workout_dialog.dismiss()

    def delete_workout(self, instance_selection_list):
        for item in self.ids.list_for_workouts.get_selected_list_items():
            self.ids.list_for_workouts.remove_widget(item)
            workout_db.remove_from_database(item.children[1].text)
        self.update_pie_charts()

    def edit_item(self, instance_label):
        self.items = workout_db.search("Exercise_Name", instance_label.text)
        for item in self.items:
            self.item = item.to_dict()
            print(self.item)

        self.edit_time_calories_dialog_content.ids.exercise_name.text = self.item["Exercise_Name"]
        self.edit_time_calories_dialog_content.ids.met_value.text = self.item["MET"]

        self.create_edit_time_and_calories_burned_dialog(self.edit_time_calories_dialog_content)
        self.edit_time_dialog.open()

    def finalize_edit(self):
        workout_item = self.get_time_calories_info(self.edit_time_dialog, self.edit_time_calories_dialog_content)
        print(workout_item)
        if workout_item != -1:
            workout_db.edit_database(workout_item["Exercise_Name"], workout_item)
            for item in self.ids.list_for_workouts.children:
                if item.children[-1].text.lower() == workout_item["Exercise_Name"].lower():
                    self.ids.list_for_workouts.remove_widget(item)
                    self.ids.list_for_workouts.add_widget(
                        SwipeToEditItem(text=f"{workout_item['Exercise_Name']}",
                                        seconRary_text=f"{workout_item['Duration']} mins",
                                        label_text=f"{workout_item['Burned_Calories']}", max_x=65,
                                        screen_name="fitness")
                    )
            self.update_pie_charts()

    def count_time_and_calories(self):
        items = workout_db.get_from_database()
        for item in items:
            item = item.to_dict()
            self.total_workout_time += item["Duration"]
            self.total_burned_calories += item["Burned_Calories"]

    def add_time_pie_chart(self):
        colors = ["#e75c6a", "#DBF5F0"]
        sizes = [(self.total_workout_time / self.workout_time_goal) * 100,
                 100 - (self.total_workout_time / self.workout_time_goal) * 100]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, colors=colors, startangle=90)
        plt.title(f"Time [{round(self.total_workout_time)}]")
        ax1.axis("equal")
        fig1.patch.set_facecolor("#DBF5F0")
        self.ids.graph_card.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def add_burned_calories_pie_chart(self):
        colors = ["#e75c6a", "#DBF5F0"]
        sizes = [(self.total_burned_calories / self.estimated_burned_calories) * 100,
                 100 - (self.total_burned_calories / self.estimated_burned_calories) * 100]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, colors=colors, startangle=90)
        plt.title(f"Cals Burned [{round(self.total_burned_calories)}]")
        ax1.axis("equal")
        fig1.patch.set_facecolor("#DBF5F0")
        self.ids.graph_card.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def update_pie_charts(self):
        self.total_workout_time = 0
        self.total_burned_calories = 0
        self.count_time_and_calories()
        self.ids.graph_card.clear_widgets()
        self.add_time_pie_chart()
        self.add_burned_calories_pie_chart()

    def create_info_dialog(self):
        if not self.info_dialog:
            self.info_dialog = MDDialog(type="custom", content_cls=self.info_dialog_content, buttons=[
                MDFlatButton(text="Close", theme_text_color="Custom", text_color=hex_color("#794cec"),
                             on_release=lambda x: self.refresh_info_dialog())
            ])

    def refresh_info_dialog(self):
        self.info_dialog_content.ids.list_for_workout_info.clear_widgets()
        self.info_dialog.dismiss()

