import threading
from PySimpleGUI import PySimpleGUI as sg
import vlc
import sqlite3
import os
import base64

sg.theme("DarkGrey")


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
            sg.popup_error("Database file %s can not be connected" % self.__database)

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


layout = [
    [
        sg.Col([
            [sg.Col([
                [sg.Frame("Currently Playing", [
                    [sg.T(" - ", key="_now_playing_", size=(49, 1), justification="left", font="Arial, 12"),
                     sg.B("Stop", key="_stop_radio_", visible=False, size=(5, 1))]],element_justification="left",
                          )]
            ], justification="left"),
                sg.Col([
                    [sg.Frame("Filter", layout=[
                        [
                            sg.T("Sort by"),
                            sg.DropDown(["Name", "Country", "Genre"], key="_sort_by_", default_value="Genre",
                                        readonly=True),
                            sg.T("Order by"),
                            sg.DropDown(["Descending", "Ascending"], key="_order_by_", default_value="Descending",
                                        readonly=True),
                            sg.B("Sort", key="_filter_button_")
                        ]
                    ], element_justification="right")],
                ], justification="right")],

            [sg.Table(
                font=("Ärial, 14"),
                values=[[i[1], i[3], i[4]] for i in Radio.radio_list()],
                bind_return_key=True,
                justification="left",
                key="_radios_list_",
                headings=["                 Name                   ", "     Country      ", "     Genre     "])
            ],
            [sg.Frame("Add New Station", layout=[
                [
                    sg.T("Name"), sg.I(size=(13, 1)),
                    sg.T("URL"), sg.I(size=(35, 1)),
                    sg.T("Country"), sg.I(size=(13, 1)),
                    sg.T("Genre"), sg.I(size=(13, 1)),
                    sg.B(
                        "Add",
                        key="_add_new_radio_",
                        button_color=sg.theme_button_color(),
                        size=(10, 1)), ]
            ], pad=(5, 15))],
        ], justification="center")
    ]
]

window = sg.Window(
    "ZED Radio @r00tme",
    text_justification="center",
    auto_size_text=True,
    return_keyboard_events=True,
    keep_on_top=True,
    icon="ico.ico",
    alpha_channel=0.9,
    use_default_focus=True,

).Layout(layout)

while True:
    event, values = window.Read()
    if event == sg.WIN_CLOSED:
        window.Close()
        exit()

    if event == "_add_new_radio_":
        if len(values[0].strip()) == 0 or len(values[1].strip()) == 0 or len(values[2].strip()) == 0:
            sg.popup_error("All fields are required", keep_on_top=True)
            continue
        connection.query(f"Insert into radios (name, url, country, genre) values (?, ? , ?, ?)", 1,
                         [
                             encode(values[0]),
                             encode(values[1]),
                             encode(values[2]),
                             encode(values[3]),
                         ]
                         )
        window.find_element("_radios_list_").Update(refresh_table())
    elif event == "Delete:46":
        for i in values["_radios_list_"]:
            connection.query("Delete from radios where id = ?", 1, [Radio.radio_list()[i][0]])
        window.find_element("_radios_list_").Update(refresh_table())
    elif event == "_radios_list_" and len(values["_radios_list_"]) == 1:
        selected_radio = Radio.radio_list(values["_sort_by_"], values["_order_by_"])[values['_radios_list_'][0]]
        if len(selected_radio[1].strip()) > 0:
            Radio(selected_radio[2]).radio_start()
            window.FindElement("_now_playing_").Update("%s " % selected_radio[1])
            if event == "_radios_list_":
                window.find_element("_stop_radio_").Update(visible=True)
    elif event == "_stop_radio_":
        Radio.radio_stop()
        window.find_element("_stop_radio_").Update(visible=False)
        window.find_element("_now_playing_").Update("")

    if event == "_run_background_":
        window.Close()
    if event == "_filter_button_":
        window.find_element("_radios_list_").Update(
            [i[1], i[3], i[4]] for i in Radio.radio_list(values["_sort_by_"], values["_order_by_"])
        )
