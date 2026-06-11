from ssdpy import SSDPClient
import xml.etree.ElementTree as ET
import html
import requests
import json
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# loop every xml element
# for debug purpose
def xmlfile(root):
    print(root.tag, root.text)
    for child in root:
        xmlfile(child,)
    return


def find_device(ip):

    client = SSDPClient()
    # 搜尋所有裝置
    devices = client.m_search("urn:schemas-upnp-org:device:MediaServer:1")
    alldevice = []
    for device in devices:
        if ip in device["location"]:
        # if "192.168.51.150:979" in device["location"]:
            # print(device)
            alldevice.append(device)
            # return device
            # location = device["location"]
    return alldevice

def get_xml(url):
    headers = {
        'User-Agent': 'UPnP/1.1 ohNet/1.0', # 模仿伺服器回傳的 server 標籤
        'Accept': 'text/xml, application/xml'
    }
    return requests.get(url, headers=headers, timeout=5)

# minimserver_ip=""
with open('settings.json', 'r', encoding='utf-8') as f:
    data = json.load(f) # 讀取全部
# print(data)

all_device = find_device(data["minimserver_ip"]+":9791")
# print(all_device)
location = all_device[0]["location"]
# location = "http://192.168.51.10:9791/560f11e9-5638-41f5-9cbd-6280184e3ad2/Upnp/device.xml"
# print(location)

response = get_xml(location)
# save minimserver's DeviceDescription.xml
file_path = BASE_DIR+"/files/Minim_DeviceDescription.xml"
file_path = Path(file_path)
# 關鍵步驟：建立父資料夾
# parents=True: 自動建立所有層級的父資料夾
# exist_ok=True: 如果資料夾已存在，不會報錯
file_path.parent.mkdir(parents=True, exist_ok=True)
with file_path.open("w", encoding="utf-8") as file:
    file.write(response.text)

root = ET.fromstring(response.content)#.find("./{urn:schemas-upnp-org:device-1-0}device)")
device = root.find("{urn:schemas-upnp-org:device-1-0}device")
# print(root.tag)
# print(root.text)
device.find("{urn:schemas-upnp-org:device-1-0}friendlyName").text = data["friendlyName"]
device.find("{urn:schemas-upnp-org:device-1-0}manufacturer").text = data["manufacturer"]
device.find("{urn:schemas-upnp-org:device-1-0}modelName").text = data["modelName"]
device.find("{urn:schemas-upnp-org:device-1-0}UDN").text = data["UDN"]
services = device.find("{urn:schemas-upnp-org:device-1-0}serviceList").findall("{urn:schemas-upnp-org:device-1-0}service")

data["Minim_ConnectionManager"]["SCPDURL"] = services[0].find("{urn:schemas-upnp-org:device-1-0}SCPDURL").text
data["Minim_ConnectionManager"]["controlURL"] = services[0].find("{urn:schemas-upnp-org:device-1-0}controlURL").text
data["Minim_ConnectionManager"]["eventSubURL"] = services[0].find("{urn:schemas-upnp-org:device-1-0}eventSubURL").text
services[0].find("{urn:schemas-upnp-org:device-1-0}SCPDURL").text = data["ConnectionManager"]["SCPDURL"]
services[0].find("{urn:schemas-upnp-org:device-1-0}controlURL").text = data["ConnectionManager"]["controlURL"]
services[0].find("{urn:schemas-upnp-org:device-1-0}eventSubURL").text = data["ConnectionManager"]["eventSubURL"]

data["Minim_ContentDirectory"]["SCPDURL"] = services[1].find("{urn:schemas-upnp-org:device-1-0}SCPDURL").text
data["Minim_ContentDirectory"]["controlURL"] = services[1].find("{urn:schemas-upnp-org:device-1-0}controlURL").text
data["Minim_ContentDirectory"]["eventSubURL"] = services[1].find("{urn:schemas-upnp-org:device-1-0}eventSubURL").text
services[1].find("{urn:schemas-upnp-org:device-1-0}SCPDURL").text = data["ContentDirectory"]["SCPDURL"]
services[1].find("{urn:schemas-upnp-org:device-1-0}controlURL").text = data["ContentDirectory"]["controlURL"]
services[1].find("{urn:schemas-upnp-org:device-1-0}eventSubURL").text = data["ContentDirectory"]["eventSubURL"]


# save Minimserver service's urls to settings.json
with open('settings.json', 'w', encoding='utf-8') as f:
    # 使用 indent 參數讓 JSON 格式化以便閱讀
    json.dump(data, f, indent=4, ensure_ascii=False)

# print(services)
# xmlfile(root)
tree = ET.ElementTree(root)
file_path = BASE_DIR+"/files/DeviceDescription.xml"
tree.write(file_path, encoding="utf-8", xml_declaration=True)
