import requests
import xml.etree.cElementTree as ET
import time
import os, codecs
tree = ET.parse("browse.xml")
root = tree.getroot()
root_tag = root.tag
if os.path.isfile("radios.txt"):
    os.remove("radios.txt")
new_file = codecs.open("radios.txt", "a+", "utf-8")
count = 0
prev_url = ""
for form in root.findall("./body/"):
    if int(form.attrib.get("bitrate")) > 64:
        count += 1
        time.sleep(.1)
        current_url = requests.get(form.attrib.get("URL"), allow_redirects=True).text.split("\n")[0]

        if str(current_url).endswith(".m3u"):
            try:
                get_ur = requests.get(current_url, allow_redirects=True).text.split("\n")
                for each in get_ur:
                    if each.startswith("http"):
                        current_url = each
            except:
                continue
        if current_url == prev_url:
            continue

        text_string = form.attrib.get("text")
        name = text_string.replace("Radio", "")
        name = name[0:name.find("(")-1]
        genre = text_string[text_string.find("(")+1:text_string.find(")")]
        string = u"(\n" \
                 "\"%s\",\n" \
                 "\"%s\",\n" \
                 "\"%s\",\n" \
                 "\"%s\",\n" \
                 "\"%s\",\n" \
                 "\"%s\"\n" \
                 "\n),\n\n" % \
                 (
                     count,
                     name,
                     genre,
                     "UK",
                     current_url,
                     form.attrib.get("image")
                 )

        new_file.write(string)
        string = ""
        prev_url = current_url
