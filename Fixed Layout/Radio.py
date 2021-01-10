from datetime import datetime
import vlc
from kivy import Config
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage
from kivy.uix.anchorlayout import AnchorLayout


def radio_list():
    import codecs
    data = codecs.open("radiosar.txt", "r", "utf-8").read().split("\n")
    construct = []
    for each_line in data:
        if len(each_line.strip()) == 0:
            continue
        radio_data = each_line.split(",")
        construct.append(tuple(i for i in radio_data))
    return construct


class Radio:
    __total_radios = 0
    __instance = vlc.Instance()
    __player = __instance.media_player_new()
    __media = None

    def __init__(self, url, name, record=False):

        if record:
            self.__media = self.__instance.media_new(
                url, "sout=#duplicate{dst=file{dst=Radio %s %s.mp3},dst=display}"
                     % (name, datetime.now().strftime("%d %b %Y - (%H-%M-%S)"))
            )
        else:
            self.__media = self.__instance.media_new(url)

    def radio_start(self):

        self.__player.set_media(self.__media)
        self.__player.play()

    def radio_stop(self):
        self.__player.stop()


class MainLayout(MDGridLayout):

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.data_tables = MDDataTable(
            padding=10,
            size_hint=(None, None),
            center_x=1,
            width=600,
            height=680,
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("#", dp(5)),
                ("Name", dp(50)),
                ("Genre", dp(30)),
                ("Country", dp(20)),
            ],
            row_data=[
                [
                    i[0],
                    ("play", [39 / 256, 174 / 256, 96 / 256, 1], i[1]),
                    i[2],
                    i[3]
                ] for i in radio_list()]
        )
        self.radio_play_id = []
        self.record = False
        self.cols = 1
        self.topWindow = MDGridLayout(cols=1, adaptive_height=True)
        self.topWindow.add_widget(self.new_top())
        self.add_widget(self.topWindow)
        self.table()

    def table(self):
        self.add_widget(self.data_tables)
        self.data_tables.bind(on_row_press=self.play_radio)

    def new_top(self, color=None):
        if color is None:
            color = [131 / 255, 223 / 255, 25 / 255, .9]
        new_top = MDGridLayout(
            cols=4,
            size_hint=(None, None),
            center_x=1,
            width=600,
            height=70
        )
        new_top.md_bg_color = [200 / 255, 200 / 255, 200 / 255, .7]

        if len(self.radio_play_id) == 0:
            return new_top

        new_top.add_widget(AsyncImage(
            source=self.radio_play_id[5]
        ))

        new_top.add_widget(MDLabel(
            text="%s " % self.radio_play_id[1],
            theme_text_color="Custom",
            halign="right",
            text_color=[223 / 255, 102 / 255, 0, 1],
            font_style="H5",
        )
        )
        new_top.add_widget(MDIconButton(
            icon="record",
            user_font_size="48sp",
            theme_text_color="Custom",
            text_color=color,
            on_press=self.start_record)
        )
        new_top.add_widget(MDIconButton(
            icon="stop",
            user_font_size="48sp",
            theme_text_color="Custom",
            on_press=self.stop_record)
        )
        return new_top

    def play_radio(self, obj, obj2):

        if obj2.text in [i[1] for i in radio_list()]:
            self.radio_play_id = [i for i in radio_list() if i[1] == obj2.text][0]

            self.radio = Radio(self.radio_play_id[4], self.radio_play_id[1])
            try:
                self.radio.radio_start()
            except:
                return
            self.topWindow.clear_widgets()
            self.topWindow.add_widget(self.new_top())

    def start_record(self, obj):
        if len(self.radio_play_id) > 0:
            self.topWindow.clear_widgets()
            self.topWindow.add_widget(self.new_top([1, 0, 0, 1]))
            self.radio = Radio(self.radio_play_id[4], self.radio_play_id[1], record=True)
            self.radio.radio_start()
            self.record = True

    def stop_record(self, obj):
        if self.record:
            self.topWindow.clear_widgets()
            self.topWindow.add_widget(self.new_top())
            self.record = False
        self.radio.radio_stop()

    def close_popup(self, obj):
        self.popup.dismiss()

    def update_table(self):
        self.data_tables.clear_widgets()
        self.remove_widget(self.grid)
        self.table()


class RadioKivy(MDApp):
    Window.size = (600, 760)

    def build(self):
        return MainLayout()


if __name__ == '__main__':
    RadioKivy().run()
