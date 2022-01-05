

<table>
  <tr>
    <td><img src="https://i.gyazo.com/26ba304495b772bcf4efec9149a7ea3d.png"></td>
    <td><img src="https://i.gyazo.com/299cfd9193ff6d6aa0c27c93e1bb45dd.png"></td>
  </tr>
</table>

The program is a good example of how to use the <a target="_blank" href="https://www.olivieraubert.net/vlc/python-ctypes/doc/">VLC library</a>, <a href="https://www.python.org/" target="_blank">Python</a> and <a target="_blank" href="https://pypi.org/project/PySimpleGUIQt/">Pysimplegui</a> to create a good looking desktop radio application. 

It uses the https://pypi.org/project/python-vlc/ library and some of the main interfaces provided such as spectrum analyser, equaliser, audio filters, preamplifier, downloading and streaming live youtube channels, local files and radio stations.

Video: https://www.youtube.com/watch?v=KFeTPMDxn70

  <h4>Features</h4>
  <ul>
    <li>Streaming pre-set radio stations</li>
    <li>Streaming youtube videos including live streams</li>
    <li>Recording radio stations in .mp3 format and video streams in .mp4</li>
    <li>Playing recorded files</li>
    <li>10 band audio equalizer (30Hz - 16Khz)</li>
    <li>Read and display in realtime radio meta data (song name) if avilable</li>
    <li>Display youtube video and pre-set radio stations logo</li>
    <li>Display audio spectrum analyser</li>
    <li>Save favourite stations</li>
    <li>Save user equalizer</li>
    <li>Master volume (controls only the software) and mute function</li>
  </ul>


<h2>A simple radio program that can play and record your favourite radio stations as well as youtube live streams </h2>

It usses libvlc.dll (VLC) API to play the audio streams and youtube-dl for videos.



Video: https://www.youtube.com/watch?v=KFeTPMDxn70

<h4><b>Creating Executable</b></h4>
<hr>
<h5><b>Option 1:</b></h5>
<a target="_blank" href="https://cx-freeze.readthedocs.io/en/latest/setup_script.html#command"> References</a>
<br>" pip install cx_Freeze "
<br>" pip install idna "

Type: " setup.py build " or   " cxfreeze zedio.py --base-name=WIN32GUI "
<hr>
<h5><b>Option 2:</b></h5>
<a  target="_blank" href="https://pyinstaller.readthedocs.io/en/stable/"> References</a>
<br>" pip install pyinstaller "

Type: " pyinstaller --windowed --onedir zedio.py " 
