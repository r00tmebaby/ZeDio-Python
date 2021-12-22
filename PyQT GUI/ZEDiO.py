import os.path
import time
from datetime import datetime
import configparser
import PySimpleGUI
import PySimpleGUI as sg
import pafy
import requests
import images
import player
from sys import platform as PLATFORM

pafy.backend = "youtube-dl"

# REF: https://wiki.videolan.org/VLC_command-line_help
vlc_config = \
    """
            --verbose=0 
            --audio-visual=visual
            --effect-kaiser-param=-20.45667456745454670
            --effect-fft-window=kaiser
            --effect-width=70
            --effect-height=50
            --spect-color=127
            --no-spect-show-bands
            --no-visual-peaks
            --no-video
            --no-xlib
            --spect-radius=20
    """

dirs = ["Download", "Settings"]

band_params = ["30Hz", "60Hz", "125Hz", "250Hz", "500Hz", "1Khz", "2Khz", "4Khz", "8Khz", "16Khz"]

vlc_dlls = [
    ["win", os.environ['WINDIR'] + "\\System32\\", ["libvlc.dll", "libvlccore.dll", "axvlc.dll"]],
    # ["darwin", os.environ['DARWIN'] + "\\System32\\", ["lib\\libvlc.dylib", "lib\libvlccore.dll"]],
]

preset_equalizers = [
    ["Flat", [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]],
    ["Acoustic", [14, 14, 12, 10, 11, 11, 12, 12, 12, 11]],
    ["Electronic", [16, 16, 13, 10, 8, 11, 10, 10, 12, 15]],
    ["Latino", [13, 12, 10, 10, 8, 8, 8, 10, 12, 15]],
    ["Piano", [12, 12, 10, 12, 12, 10, 12, 12, 13, 13]],
    ["Pop", [8, 8, 10, 11, 13, 13, 12, 10, 9, 9]],
    ["Rock", [15, 14, 13, 12, 10, 10, 11, 12, 13, 14]],
    ["Bass Booster", [20, 17, 11, 8, 0, 5, 9, 10, 13, 13]],
    ["Zedio", [20, 10, 8, 8, 9, 10, 13, 13, 15, 20]]
]


def get_list(string: str):
    check = string.split(",")
    return check if len(check) == 10 else [10 for i in range(10)]


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def create_directories():
    for each_dir in dirs:
        if not os.path.isdir(each_dir):
            os.mkdir(each_dir)
    settings_file = os.path.join(dirs[1], "settings.ini")
    default_settings = """[Settings]
radio_list = https://r00tme.cp.uk/api/radio-python.txt
theme= DarkGrey13
saved_equalizer = 10,10,10,10,10,10,10,10,10,10
    """
    if not os.path.isfile(settings_file):
        with open(settings_file, "a+") as set_file:
            set_file.write(default_settings)


create_directories()
config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(os.path.join(dirs[1], "settings.ini"))
sg.theme(config.get("Settings", "theme"))


# def convert_audio(video_file, audio_file):
#   video_clip = VideoFileClip(video_file)
#   audio_clip = video_clip.audio.write_audiofile(audio_file)
#   video_clip.close()
#   audio_clip.close()


def name(array: list) -> str:
    return array[0]


def genre(array: list) -> str:
    return array[1]


def country(array: list) -> str:
    return array[2]


def get_records() -> list:
    files = os.listdir(dirs[0])
    files_data = []
    for each_file in files:
        data = each_file.split(".")[0].split("-")
        if len(data) == 5:
            files_data.append([data[0], data[1], data[2], data[3], data[4], each_file])
    files_data.sort(reverse=True)
    if len(files_data) == 0:
        return [["" for i in range(3)]]
    else:
        return [[
            files_data[i][0],
            "%s:%s:%s" % (files_data[i][2], files_data[i][3], files_data[i][4]),
            files_data[i][1],
            os.path.join(dirs[0], files_data[i][5]),
            file_size(os.path.join(dirs[0], files_data[i][5]))
        ] for i in range(len(files_data))]


class Radios:
    all_list = []
    temporary_list = []

    def __init__(self, file_path: str, remote=True):
        temp_radio_list = []
        if remote:
            try:
                rows = requests.get(file_path).text.split("\n")
            except FileExistsError:
                raise FileExistsError("Radios url does not exist or can not be accessed")
        else:
            if os.path.isfile(os.path.join(dirs[1], file_path)):
                with open(os.path.join(dirs[1], file_path), "r") as file:
                    rows = file.readlines()
            else:
                raise FileExistsError("Favourites file does not exist")
        for i in rows:
            if len(i.strip()) > 0:
                cols = i.split(",")
                if len(cols) == 5:
                    temp_radio_list.append(cols)

        self.all_list = temp_radio_list
        self.temporary_list = self.all_list.sort(key=name)

    def filter(self, st_filter: str = "") -> None:
        """
        Use the search field to sort the temporary list by names

        :param st_filter: Reads the search field from the GUI and sort the table based on the string

        """
        if len(st_filter.strip()) > 0:
            self.temporary_list = [self.all_list[i] for i in range(len(self.all_list)) if
                                   st_filter.lower() in self.all_list[i][0].lower()]
        else:
            self.temporary_list = [self.all_list[i] for i in range(len(self.all_list))]


radios = Radios(config.get("Settings", "radio_list"))
fav_radios = Radios("favourites.dat", remote=False)
fav_radios.filter()
radios.filter()

fav_layout = [[sg.Col(layout=[
    [sg.Col(layout=[
        [sg.Frame("Add Radio Station", [
            [
                sg.Col(
                    [
                        [
                            sg.T("Name"), sg.I(key="_add_radio_name_", size=(35, 1)),
                            sg.T("Genre"), sg.I(key="_add_radio_genre_", size=(15, 1)),
                            sg.T("Country"), sg.I(key="_add_radio_country_", size=(15, 1))
                        ],
                    ], justification="r", element_justification="r", expand_x=True,
                ),
            ],
            [
                sg.Col(
                    [
                        [sg.T("URL"), sg.I(key="_add_radio_link_", expand_x=True)]
                    ], expand_x=True
                )
            ],
            [
                sg.Col(
                    [
                        [sg.B("Add Radio", key="_add_new_radio_")]
                    ], justification="r",
                )
            ]
        ], expand_x=True)]], expand_x=True)],
    [sg.Table(
        font="Arial, 14",
        values=[[i[0], i[1], i[2]] for i in fav_radios.temporary_list]
        if len(fav_radios.temporary_list) > 0
        else [["", "", ""]],
        justification="left",
        key="_fav_radios_list_",
        row_height=30,
        right_click_menu=["&", ['Remove from favourites']],
        bind_return_key=True,
        num_rows=20,
        expand_x=True,
        headings=["Name            ", "Genre      ", "Country   "])
    ]
], justification="center", expand_x=True)]]

records_layout = [[sg.Col(layout=[
    [sg.Table(
        font="Arial, 14",
        values=[[get_records()[i][k] for k in range(len(get_records()[i]))] for i in range(len(get_records()))],
        justification="left",
        key="_records_list_",
        row_height=30,
        right_click_menu=["&", ['Refresh', 'Open Location', 'Delete record']],
        bind_return_key=True,
        num_rows=20,
        expand_x=True,
        headings=["Radio          ", "Time      ", "Date        "])
    ]
], justification="center", expand_x=True)]]

equalizer_layout = [sg.Col(layout=[
    [sg.Frame("Equalizer", layout=[
        [sg.Col([[
            sg.T("Preset EQ"),
            sg.DropDown(
                values=[preset_equalizers[i][0] for i, values in enumerate(preset_equalizers)],
                readonly=True,
                change_submits=True,
                bind_return_key=True,
                enable_events=True,
                key="_equalizer_preset_",
                size=(20, 1),
                default_value="Flat")
        ]]),
            sg.B("Save", key="_save_equalizer_"),
            sg.B("Load", key="_load_equalizer_"),
        ],
        [sg.Frame(band_params[i], layout=[
            [sg.Slider(
                range=(0, 20),
                size=(10, 15),
                default_value=float(get_list(config.get("Settings", "saved_equalizer"))[i]),
                orientation="v",
                change_submits=True,
                text_color="#00A615",
                font="Helvetica, 11",
                pad=(2, 2),
                key="_eq_band_%s" % i)]
        ], pad=(5, 10), background_color="#037080", font="Helvetica, 8") for i in range(10)
         ]
    ], size=(100, 20), element_justification="center", background_color="#282A2F", pad=(10, 10))]
], justification="center", element_justification="center", pad=(10, 10))]

play_layout = [[sg.Col([
    [sg.Col(
        [[sg.Image(data=images.zedio, key="_radio_logo_", expand_y=True, expand_x=True)]],
        size=(165, 165), background_color="#282A2F"),
        sg.Col([
            [sg.Col(
                [
                    [
                        sg.Frame("Currently Playing", [
                            [
                                sg.Canvas(key="_radio_spectrum_", size=(60, 40)),
                                sg.T(" - ", key="_now_playing_", size=(24, 1), justification="left", font="Arial, 14",
                                     text_color="#1D95A7"),
                                sg.B(image_data=images.record, image_size=(40, 40), key="_record_radio_",
                                     button_color=("#E5E5E5", "#81352A"),
                                     disabled=True),
                                sg.B(image_data=images.stop, image_size=(40, 40), key="_stop_radio_",
                                     button_color=("#E5E5E5", "#000"),
                                     disabled=True)
                            ]
                        ], element_justification="right", expand_x=True)
                    ]
                ],
                justification="left",
                element_justification="left",
                expand_x=True
            )],
            [sg.Col([
                [sg.Frame("Filter", layout=[[
                    sg.I(key="_search_name_", size=(20, 1)),
                    sg.T("Sort by"),
                    sg.DropDown(
                        ["Name", "Genre", "Country"],
                        key="_sort_by_",
                        default_value="Name",
                        change_submits=True,
                        readonly=True,
                    ),
                    sg.T("Order by"),
                    sg.DropDown(
                        ["Desc", "Asc"],
                        key="_order_by_",
                        change_submits=True,
                        default_value="Desc",
                        readonly=True,
                        pad=(10, 10),
                    )],
                ], expand_x=True)]], expand_x=True, expand_y=True, )
            ],
        ], element_justification="left", justification="left", expand_y=True, expand_x=True)],

    [sg.Col(layout=[
        [sg.Table(
            font="Arial, 14",
            values=[[i[0], i[1], i[2]] for i in radios.temporary_list],
            bind_return_key=True,
            justification="left",
            key="_radios_list_",
            row_height=30,
            num_rows=40,
            headings=["Name", "Genre", "Country"])
        ]
    ])],
], element_justification="center")]]

tabs = [[sg.TabGroup(layout=[[
    sg.Tab(title="Player", layout=play_layout),
    sg.Tab(title="Favourites", layout=fav_layout),
    sg.Tab(title="Records", layout=records_layout),
    sg.Tab(title="Settings", layout=[equalizer_layout])
]])]]

gui_window = sg.Window(
    "ZEDiO     🎧 v1.0 @r00tme   🕑 21/12/2021     ",
    text_justification="center",
    auto_size_text=True,
    return_keyboard_events=True,
    keep_on_top=True,
    icon="ico.ico",
    right_click_menu=["&", ['Add to favourites', 'Refresh Radios']],
    alpha_channel=0.9,
    size=(700, 700),
    use_default_focus=True,

).Layout(tabs).finalize()


def save_equalizer(values: sg.ObjToString) -> None:
    """
    Reads the equalizer settings from GUI and save them in the settings.ini
    :param values: GUI event object
    """
    new_eq = ""
    coma = ","
    for i in range(10):
        if i == 9:
            coma = ""
        new_eq += "%s%s" % (int(values["_eq_band_%s" % i]), coma)
    config.set(dirs[1], "saved_equalizer", new_eq)
    with open(os.path.join(dirs[1], "settings.ini"), 'w') as configfile:
        config.write(configfile)


def add_favourite(radio_data: list):
    """
    Adding a new radio to favourites
    :param radio_data: List that contains radio data [Name, Genre, Country, URL]
    """
    with open(os.path.join(dirs[1], "favourites.dat"), "a+") as file:
        file.write("%s,%s,%s,%s,%s\n" % (radio_data[0], radio_data[1], radio_data[2], radio_data[3], radio_data[4]))
    fav_radios.temporary_list.append(radio_data)
    gui_window['_fav_radios_list_'].update([[i[0], i[1], i[2]] for i in fav_radios.temporary_list])


def play_radio(values_str: str, record = False) -> None:
    """
    Plays the selected radio and updates the main gui buttons
    :param values_str: GUI event object
    """

    image_index = 4

    if "_fav" in values_str:
        Media.selected_radio = fav_radios.temporary_list[values[values_str][0]]
    elif "_rec" in values_str:
        Media.selected_radio = get_records()[values[values_str][0]]
        Media.selected_radio.append(
            [radios.temporary_list[i][4] for i in range(len(radios.temporary_list))
             if Media.selected_radio[0] == radios.temporary_list[i][0]]
        )
        image_index = 5
    elif "_rad" in values_str:
        Media.selected_radio = radios.temporary_list[values[values_str][0]]

    play.refresh()
    play.current = Media(Media.selected_radio[3])
    play.current.radio_start()

    if not record:
        gui_window['_radio_logo_'].update(data=play.current.selected_radio[image_index])

    gui_window['_now_playing_'].update("%s" % play.current.song)
    gui_window.find_element("_now_playing_").Update(text_color="#1D95A7")
    gui_window.find_element("_stop_radio_").Update(disabled=False)
    gui_window.find_element("_record_radio_").Update(disabled=False)


class Media:
    __instance = player.Instance(vlc_config)
    if __instance is not None:
        __player = __instance.media_player_new()
    __media = None
    __url = None
    __record = False
    __flat_file = False

    band_count = player.libvlc_audio_equalizer_get_band_count()
    selected_radio = None
    v_player = None

    song = "..."

    def __init__(self, url: str, record=False, flat_file=False):
        """
        :param url: string -> Video or audio link
        :param record: bool -> Switch to record or play functionality
        """
        if record:
            if not os.path.isdir(dirs[0]):
                os.mkdir(dirs[0])
            if "youtu" in url:
                try:
                    audio = pafy.new(url)
                    best = audio.getbest()
                    file_name = dirs[0] + "/%s-%s" % (audio.author, datetime.now().strftime("%d %b %Y-%H-%M-%S"))
                    best.download("%s.%s" % (file_name, best.extension))

                except:
                    sg.PopupError(
                        "ERROR: Can not record the stream",
                        no_titlebar=True,
                        keep_on_top=True,
                        auto_close=True
                    )
            else:
                self.__media = self.__instance.media_new(
                    url.strip(), "sout=#duplicate{dst=file{dst=" + dirs[0] + "/%s-%s.mp3},dst=display}"
                                 % (self.selected_radio[0], datetime.now().strftime("%d %b %Y-%H-%M-%S"))
                )
        else:
            self.__media = self.__instance.media_new(url.strip())
        self.__flat_file = flat_file
        self.__url = url
        self.__record = record

    def radio_start(self) -> None:
        """
        Start playing the chosen link
        Checks the current platform and switch the method to add the spectrum equalizer into the GUI
        Checks the current platform and switch the method to change the logo image
        Checks the file metadata and saves it in the instance variable song
        Checks the link and switch the players if it is a video
        """
        self.radio_stop()

        if not self.__flat_file:
            if "youtu" in self.selected_radio[3].lower():
                try:
                    audio = pafy.new(self.__url)
                except:
                    sg.PopupError(
                        "ERROR: This live stream recording is not available.",
                        no_titlebar=True,
                        keep_on_top=True,
                        auto_close=True
                    )
                    return
                best = audio.getbest()
                self.v_player = player.MediaPlayer(best.url, "streamlink", vlc_config)

                if PLATFORM.startswith('linux'):
                    self.v_player.set_xwindow(gui_window['_radio_logo_'].Widget.winfo_id())
                else:
                    self.v_player.set_hwnd(gui_window['_radio_logo_'].Widget.winfo_id())
                self.v_player.play()

                self.song = audio.author
            else:
                if PLATFORM.startswith('linux'):
                    self.__player.set_xwindow(gui_window['_radio_spectrum_'].Widget.winfo_id())
                else:
                    self.__player.set_hwnd(gui_window['_radio_spectrum_'].Widget.winfo_id())
                self.__player.set_media(self.__media)
                self.__player.play()
                self.__media.get_mrl()
                self.__media.parse()
                time.sleep(0.2)
                self.song = self.selected_radio[0] if self.__media.get_meta(12) is None else self.__media.get_meta(12)

    def set_equalizer(self, equalizer_amp=None) -> None:
        """
        Set Equalizer set 10 scale parametric equalizer to the player in real time
        Possible range 30hz-16khz with -20 to 20 scale amplification

        @parameter: equalizer_amp of type list of 10 integers in range -20 to 20
        30  60  125 250 500  1000  2000  4000  8000  16000     in Hertz
        [0,  0,    0,    0,    0,     0,      0,       0,        0,        0   ]   amplification from -20 to 20

        """

        if equalizer_amp is None:
            equalizer_amp = [0 for i in range(10)]

        equalizer_freq = []
        equalizer_band = player.libvlc_audio_equalizer_get_band_count()
        equalizer = player.AudioEqualizer()
        for band_id in range(equalizer_band):
            try:
                amp = equalizer_amp[band_id]
            except IndexError:
                amp = 0
            equalizer.set_amp_at_index(amp, band_id)
            equalizer_freq.append(player.libvlc_audio_equalizer_get_band_frequency(band_id))

        if self.v_player is not None:
            self.v_player.set_equalizer(equalizer)
        elif self.__player is not None:
            self.__player.set_equalizer(equalizer)

    def radio_stop(self) -> None:
        """Stops the currently playing radio"""
        self.__player.stop()
        if self.v_player is not None:
            self.v_player.stop()


class Play:
    """
    Keeps the currently playing instance
    """
    current = None

    def refresh(self) -> None:
        if self.current is not None:
            self.current.radio_stop()


play = Play()

while True:
    event, values = gui_window.Read()

    if event == sg.WIN_CLOSED:
        gui_window.Close()
        break
    try:
        gui_window.find_element("_radios_list_").Update(radios.filter(values['_search_name_']))
    except PySimpleGUI.ErrorElement:
        continue

    if play.current is not None and (event == "_equalizer_preset_" or '_eq_band' in event):
        play.current.set_equalizer([values['_eq_band_%s' % i] for i in range(10)])
    if event == "_equalizer_preset_":
        get_equalizer = [preset_equalizers[i][1] for i in range(len(preset_equalizers)) if
                         preset_equalizers[i][0] == values['_equalizer_preset_']][0]
        for i, res in enumerate(get_equalizer):
            gui_window['_eq_band_%s' % i].update(int(res))

    if values['_sort_by_'] == "Genre":
        radios.temporary_list.sort(key=genre)
    elif values['_sort_by_'] == "Country":
        radios.temporary_list.sort(key=country)
    elif values['_sort_by_'] == "Name":
        radios.temporary_list.sort(key=name)

    radios.temporary_list = radios.temporary_list if values['_order_by_'] == "Desc" else radios.temporary_list[::-1]
    gui_window['_radios_list_'].update([[i[0], i[1], i[2]] for i in radios.temporary_list])

    if event == "_fav_radios_list_" and len(values["_fav_radios_list_"]) == 1 and fav_radios.temporary_list:
        play_radio("_fav_radios_list_")
    elif event == "_radios_list_" and len(values["_radios_list_"]) == 1:
        play_radio("_radios_list_")
    elif (event == "Remove from favourites" or event == "Delete:46") \
            and len(values["_fav_radios_list_"]) == 1 \
            and len(fav_radios.temporary_list) > 0:
        del fav_radios.temporary_list[values["_fav_radios_list_"][0]]
        with open(os.path.join(dirs[1], "favourites.dat"), "w") as file:
            for each in fav_radios.temporary_list:
                file.write("%s,%s,%s,%s,%s" % (each[0], each[1], each[2], each[3], each[4]))
        gui_window['_fav_radios_list_'].update([[i[0], i[1], i[2]] for i in fav_radios.temporary_list])

    elif event == "Add to favourites" and len(values['_radios_list_']) == 1:
        add_favourite(radios.temporary_list[values['_radios_list_'][0]])
    elif event == "_add_new_radio_":
        if len(values['_add_radio_name_']) > 1 and \
                len(values['_add_radio_link_']) > 10 and \
                len(values['_add_radio_genre_']) > 1 and \
                len(values['_add_radio_country_']) > 1:
            add_favourite(
                [
                    values['_add_radio_name_'],
                    values['_add_radio_genre_'],
                    values['_add_radio_country_'],
                    values['_add_radio_link_'],
                    images.zedio
                ])
    elif event == "_stop_radio_":
        play.refresh()
        gui_window.find_element("_now_playing_").Update(text_color="#1D95A7")
        gui_window.find_element("_stop_radio_").Update(disabled=True)
        gui_window.find_element("_record_radio_").Update(disabled=True)
        gui_window.find_element("_now_playing_").Update("")
        Media.selected_radio = None

        # Fixme --
        # for files in os.listdir("Download"):
        #    if files.endswith(".mp4"):
        #        convert_audio(os.path.join("Download", files), os.path.join("Download", files.replace(".mp4", "mp3")))

    elif event == "_save_equalizer_":
        save_equalizer(values)
    elif event == "_record_radio_":
        if Media.selected_radio is not None:
            play.refresh()
            play.current = Media(play.current.selected_radio[3], record=True)
            play.current.radio_start()

            gui_window.find_element("_now_playing_").Update(text_color="#E96767")
            gui_window.find_element("_stop_radio_").Update(disabled=False)
            gui_window.find_element("_record_radio_").Update(disabled=True)
    elif len(values['_records_list_']) == 1:
        selected_record = get_records()[values['_records_list_'][0]]
        if event == "_records_list_":
            if get_records()[values['_records_list_'][0]][0] != "":
                play_radio("_records_list_", record=True)
        elif event in ["Delete record", "Delete:46"]:
            try:
                playing = False
                if play.current is not None:
                    if play.current.selected_radio[3] == selected_record[3]:
                        sg.PopupError("Can not delete radio while playing", no_titlebar=True, keep_on_top=True)
                if os.path.isfile(selected_record[3]) and not playing:
                    os.remove(selected_record[3])
                    gui_window['_records_list_'].update(
                        [[get_records()[i][k] for k in range(len(get_records()[i]))] for i in range(len(get_records()))]
                    )
            except:
                sg.PopupError("Can not be deleted at the moment", no_titlebar=True, keep_on_top=True)

    if event == "Open Location":
        os.popen("explorer " + dirs[0])

    if play.current is not None and (event == "_equalizer_preset_" or '_eq_band' in event):
        play.current.set_equalizer([values['_eq_band_%s' % i] for i in range(10)])
    if play.current is not None and event == "_load_equalizer_":
        play.current.set_equalizer([values['_eq_band_%s' % i] for i in range(10)])
    if event == "Refresh":
        gui_window['_records_list_'].update(
            [[get_records()[i][k] for k in range(len(get_records()[i]))] for i in range(len(get_records()))]
        )
