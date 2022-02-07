from All_Imports.all_imports import *

kv = Builder.load_file("Main_Window/main_window.kv")


class MainWindow(MDScreen):
    def switch_screen(self, next_screen):
        self.manager.current = next_screen
        self.parent.parent.parent.ids.toolbar.title = self.parent.parent.parent.current_screen()
