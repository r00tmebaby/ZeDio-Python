from kivy.metrics import dp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextFieldRect
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDRectangleFlatButton
import threading
from kivy.uix.popup import Popup
import vlc
import sqlite3
import os
import base64


class Database:
    __lock = threading.Lock()

    __connection = None
    __session = None
    __database = None

    def __init__(self, database):
        self.__database = os.path.join(os.getcwd(), database)

    def _open(self):
        try:
            cnx = sqlite3.connect(self.__database)
            self.__connection = cnx
            self.__session = cnx.cursor()
        except:
            pass

    def _close(self):
        self.__session.close()
        self.__connection.close()

    def query(self, query: str, query_type: int = 0, args=None) -> object:
        if args is None:
            args = []
        self.__lock.acquire(True)
        self._open()
        if query_type == 1:
            self.__session.execute(query, args)
            self.__connection.commit()
            result = self.__session.lastrowid
        else:
            self.__session.execute(query)
            self.__connection.commit()
            result = self.__session.fetchall()
        self._close()
        self.__lock.release()
        return result


connection = Database("radio.db")


def encode(text: str):
    conv_bytes = bytes(text, 'utf-8')
    return base64.b64encode(conv_bytes)


def decode(text: str) -> str:
    return base64.b64decode(text).decode()


def refresh_table() -> list:
    return [[i[1], i[3], i[4]] for i in Radio.radio_list()]


class Radio:
    __total_radios = 0
    __instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    __player = __instance.media_player_new()
    __media = __instance.media_new("")

    def __init__(self, url):
        Radio.__media = Radio.__instance.media_new(url)

    @staticmethod
    def radio_start():
        Radio.__player.set_media(Radio.__media)
        Radio.__player.play()

    @staticmethod
    def radio_stop():
        Radio.__player.stop()

    @staticmethod
    def radio_list(search="Genre", order="Descending"):
        Radio.__total_radios = connection.query("Select count(id) from radios")[0][0]
        order = "desc" if order == "Descending" else "asc"
        search = search.lower()
        return [["", "", "", "", ""]] if Radio.__total_radios == 0 else \
            [[i[0], decode(i[1]), decode(i[2]), decode(i[3]), decode(i[4])] for i in
             connection.query(f"Select * from radios order by {search} {order}")]


class MainLayout(MDGridLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.radio_name = self.radio_genre = self.radio_url = self.radio_country = None
        self.radio_play_id = []
        self.cols = 1
        self.get_center_x()
        self.grid()
        self.table([
                (
                    i[0],
                    i[1],
                    i[4],
                    i[3]
                ) for i in Radio.radio_list()
            ])

    def grid(self):
        grid = MDGridLayout(cols=5, padding=10, spacing=10, size_hint=(20, None), height=40, pos_hint={'center_x': 0.5})

        self.radio_name = MDTextFieldRect(hint_text="Name")
        self.radio_url = MDTextFieldRect(hint_text="URL")
        self.radio_genre = MDTextFieldRect(hint_text="Genre")
        self.radio_country = MDTextFieldRect(hint_text="Country")

        add_radio_submit = MDRectangleFlatButton(text="Add Radio")
        add_radio_submit.bind(on_press=self.add_radio)

        grid.add_widget(self.radio_name)
        grid.add_widget(self.radio_genre)
        grid.add_widget(self.radio_country)
        grid.add_widget(self.radio_url)
        grid.add_widget(add_radio_submit)
        self.add_widget(grid)


    def table(self, data):
        self.grid = MDGridLayout(padding=10, spacing=10, size_hint=(0.9, 0.6), cols=1)
        self.data_tables = MDDataTable(
            padding=20,
            use_pagination=True,
            rows_num=10,
            pagination_menu_pos="auto",
            column_data=[
                ("#", dp(40)),
                ("Name", dp(80), self.sort_on_name),
                ("Genre", dp(50), self.sort_on_genre),
                ("Country", dp(50), self.sort_on_country),
            ],
            row_data=data,
            sorted_on="Name",
            sorted_order="DSC",
            elevation=2
        )
        self.grid.add_widget(self.data_tables)
        self.data_tables.bind(on_row_press=self.show_popup)
        self.add_widget(self.grid)

    def add_radio(self, obj):
        if len(self.radio_name.text) > 0 and \
                len(self.radio_url.text) > 0 and \
                len(self.radio_country.text) > 0 and \
                len(self.radio_genre.text) > 0:
            connection.query(f"Insert into radios (name, url, country, genre) values (?, ? , ?, ?)", 1,
                             [
                                 encode(self.radio_name.text),
                                 encode(self.radio_url.text),
                                 encode(self.radio_country.text),
                                 encode(self.radio_genre.text),
                             ]
                             )
            self.update_table()
        else:
            pass

    def play_radio(self, obj):
        if len(self.radio_play_id) == 3:
            self.popup.dismiss()
            Radio(self.radio_play_id[2]).radio_start()

    def show_popup(self, instance_table, instance_row):

        popup_layout = MDGridLayout(cols=3, padding=(15, 15), spacing=10)

        popup_layout.add_widget(MDRectangleFlatButton(text="Play", on_press=self.play_radio))
        popup_layout.add_widget(MDRectangleFlatButton(text='Close', on_press=self.close_popup))
        popup_layout.add_widget(MDRectangleFlatButton(text='Delete', on_press=self.delete_radio))

        self.radio_play_id = []
        for each in Radio.radio_list():
            if str(each[0]) == str(instance_row.text):
                self.radio_play_id = [each[0], each[1], each[2]]
                self.popup = Popup(
                    title="You have selected radio %s" % each[1],
                    content=popup_layout,
                    auto_dismiss=True,
                    size_hint=(None, None), size=(350, 120)
                )
                self.popup.open()
                return

    def close_popup(self, obj):
        self.popup.dismiss()

    def update_table(self):
        self.data_tables.clear_widgets()
        self.remove_widget(self.grid)
        self.table([
            (
                i[0],
                i[1],
                i[4],
                i[3]
            ) for i in Radio.radio_list()
        ])

    def delete_radio(self, data):
        if len(self.radio_play_id) == 3:
            connection.query(f"Delete from radios where id ={self.radio_play_id[0]}")
        self.update_table()
        self.popup.dismiss()

    def sort_on_genre(self, data):
        if data is not None:
            return sorted(data, key=lambda l: l[2])

    def sort_on_name(self, data):
        if data is not None:
            return sorted(data, key=lambda l: l[1])

    def sort_on_country(self, data):
        if data is not None:
            return sorted(data, key=lambda l: l[3])


class RadioKivy(MDApp):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    RadioKivy().run()
