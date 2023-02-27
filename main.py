import asyncio
import itertools
import os
import shutil
import json
import sys
import threading
import multiprocessing
import time
from random import randint

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

from kivymd.uix.label import MDLabel
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.tab import MDTabsBase, MDTabs

# from android.storage import app_storage_path
# settings_path = app_storage_path()



Window.size = (300, 608)


class Tab(MDFloatLayout, MDTabsBase):
    """Class implementing content for a tab."""
    main_widget = None

    def __init__(self, **kwargs):
        super(Tab, self).__init__(**kwargs)
        al = AnchorLayout(anchor_y='top', anchor_x='left',padding=15)
        self.main_widget = GridLayout(cols=1, size_hint_y=0.4)
        al.add_widget(self.main_widget)
        self.add_widget(al)

    def add_label(self, text):
        label = MDLabel(font_style='H5', size_hint=(1,0.1), text=text)
        self.main_widget.add_widget(label)


class MainWindow(Screen):
    pass


class ProfileWindow(Screen):
    pass


class CreateProfileForm(Screen):
    pass


class WindowManager(ScreenManager):

    prof_info = {
        'photo': 'static/images/incognito.png',
        'name': 'none',
        'surname': 'none',
        'lastname': 'none',
        'age': 0,
        'is_working': False,
        'job_place': 'none',
        'position': 'none',
        'phone': 'none',
    }
    index = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.index = self.__get_index()

    def __exit(self):
        sys.exit()

    def create_list_widget(self, text, secondary_text):
        w = TwoLineListItem(text=text, secondary_text=secondary_text)
        w.bind(on_release=lambda x: self.show_student_info(w.text[0]))
        self.ids.main_profiles.add_widget(w)

    def show_student_info(self, index):
        with open(f'data/profiles/{index}/prof.json', 'r', encoding='utf-8') as prof:
            prof.seek(0)
            data = json.load(prof)

            self.ids.profile_photo.source = data['photo']

            self.create_tab('Основаная информация', [data['name'], data['surname'], data['lastname']])
            is_work = "работает" if data['is_working'] else "не работает"
            self.create_tab('Иформация о работе', [str(data['age']), is_work, data['job_place'], data['position'], data['phone']])

        self.current = 'profile'

    def create_tab(self, title, texts):
        tab = Tab(title=title)
        for text in texts:
            tab.add_label(text)
        self.ids.profile_mdtabs.add_widget(tab)

    # def clear_tabs(self):
    #     self.ids.profile.remove_widget(self.ids.profile_mdtabs)

    def update_list(self):
        for i in range(len(self.ids.main_profiles.children), self.index):
            with open(f'data/profiles/{i}/prof.json', 'r', encoding='utf-8') as prof:
                prof.seek(0)
                d = json.load(prof)
                text = str(i) + " " + d['name'] + " " + d['surname']
                secondary_text = d['age'] + " лет " + "работает" if d['is_working'] else "не работает"
                self.create_list_widget(text, secondary_text)


    def __get_index(self):
        with open('data/info.txt', 'r+', encoding='utf-8') as info:
            return int(info.read())

    def __set_index(self):
        with open('data/info.txt', 'r+', encoding='utf-8') as info:
            info.write(f'{self.index + 1}')

    def create_profile(self):
        # dir create
        if not os.path.exists(f'data/profiles/{self.index}'):
            os.makedirs(f'data/profiles/{self.index}')

        # photo adding
        file_ext = os.path.splitext(self.prof_info['photo'])[1]
        new_path = f'data/profiles/{self.index}/photo{file_ext}'
        shutil.copy(self.prof_info['photo'], new_path)
        self.prof_info['photo'] = new_path

        # text info adding
        with open(f'data/profiles/{self.index}/prof.json', 'w+', encoding='utf-8') as prof:
            json.dump(self.prof_info, prof)
        self.__set_index()
        self.index = self.__get_index()


    def file_manager_open(self):
        self.file_manager.show('C:/Users/gasim/Downloads')  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''

        self.ids.form_photo.source = path
        WindowManager.prof_info['photo'] = path

        self.exit_manager()

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'DeepPurple'
        return Builder.load_file("main.kv")

    def on_start(self):
        self.root.update_list()

if __name__ == "__main__":
    MainApp().run()
