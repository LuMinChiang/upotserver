from flask import Flask, Response, request
from flask_httpauth import HTTPDigestAuth
from flask_httpauth import HTTPBasicAuth
import os
import requests
import json
from ssdp import get_xml

with open('settings.json', 'r', encoding='utf-8') as f:
    data = json.load(f) # 讀取全部
server_ip = data["server_ip"]+":"+str(data["port"])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
# auth = HTTPDigestAuth(realm="BubbleUPnP Server")
auth = HTTPBasicAuth()
# 取得 server.py 所在的資料夾路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 設定與 foobar2000 中輸入一致的帳號密碼
users = {
    data["account"]: data["password"]
}


@auth.get_password
def get_pw(username):
    return users.get(username)

# 模擬 BubbleUPnP 的設備描述檔路徑
@app.route('/DeviceDescription.xml')
@auth.login_required
def device_xml():
    # ... XML content as shown in the original response ...
    # pass # Placeholder for the XML content
    # print(BASE_DIR+data["DeviceDescription_path"])
    file_path = os.path.join(BASE_DIR, data["DeviceDescription_path"].lstrip('/'))
    # print(file_path)
    # file_path = os.path.join(BASE_DIR, 'DeviceDescription.xml')
    # with open(file_path, 'r', encoding='utf-8') as f:
    #     xml_content = f.read()
    # return Response(xml_content, mimetype='text/xml')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        # 成功時回傳 XML
        return Response(xml_content, mimetype='text/xml')
    except FileNotFoundError:
        # 找不到檔案時回傳 404
        return "錯誤：找不到 DeviceDescription.xml 檔案，請檢查檔案路徑。", 404
    except Exception as e:
        # 其他錯誤時回傳 500 並顯示原因
        return f"伺服器內部錯誤：{str(e)}", 500

# @app.route('/ConnectionManager/service.xml')
@app.route(data["ConnectionManager"]["SCPDURL"])
@auth.login_required
def get_cm_service():
    # file_path = os.path.join(BASE_DIR, 'ConnectionManager/service.xml')
    file_url = "http://"+os.path.join(data["minimserver_ip"]+":9791", data["Minim_ConnectionManager"]["SCPDURL"].lstrip('/'))
    # print(file_url)
    try:
        # 直接讀取該資料夾下的檔案
        # with open(file_path, 'r', encoding='utf-8') as f:
        #     return Response(f.read(), mimetype='text/xml')
        return get_xml(file_url).text
    except Exception as e:
        return str(e), 404

# @app.route('/ContentDirectory/service.xml')
@app.route(data["ContentDirectory"]["SCPDURL"])
@auth.login_required
def get_cd_service():
    # file_path = os.path.join(BASE_DIR, 'ContentDirectory/service.xml')
    file_url = "http://"+os.path.join(data["minimserver_ip"]+":9791", data["Minim_ContentDirectory"]["SCPDURL"].lstrip('/'))
    try:
        # 直接讀取該資料夾下的檔案
        # with open(file_path, 'r', encoding='utf-8') as f:
        #     return Response(f.read(), mimetype='text/xml')
        return get_xml(file_url).text
    except Exception as e:
        return str(e), 404

# 模擬 foobar2000 連線測試時可能存取的首頁或狀態頁
@app.route('/')
@auth.login_required
def index():
    # return "BubbleUPnP Server Emulator Running"
    resp = make_response("Connected")
    resp.headers['Server'] = 'BubbleUPnP/1.0'
    return resp

def forward_soap(target_url, trans_data, soap_action):

    # 1. 確保 SOAPACTION 格式正確 (必須有雙引號)
    if soap_action and not soap_action.startswith('"'):
        soap_action = f'"{soap_action}"'

    """將 SOAP 請求轉發給 MinimServer 並回傳結果"""
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPACTION": soap_action,
        "User-Agent": "UPnP/1.1 ohNet/1.0"
    }
    # response = requests.post(target_url, data=trans_data, headers=headers, timeout=10)
    # content = response.text
    # content = content.replace(data["minimserver_ip"]+":9790", server_ip).replace(data["minimserver_ip"]+":9791", server_ip)
    # print(content)
    #     # 直接回傳 MinimServer 的 XML 給 foobar2000
    # return Response(content, mimetype='text/xml')
    try:
        # 轉發請求
        response = requests.post(target_url, data=trans_data, headers=headers, timeout=30)

        # # --- 新增列印功能 ---
        # print("\n" + "!"*20 + " MinimServer 回傳內容 " + "!"*20)
        # print(response.text) # 這是您想看的 XML 內容
        # print("!"*60 + "\n")
        # # ------------------
        content = response.text
        content = content.replace(data["minimserver_ip"]+":9790", server_ip).replace(data["minimserver_ip"]+":9791", server_ip)
        # print(content)
        # 直接回傳 MinimServer 的 XML 給 foobar2000
        return Response(content, mimetype='text/xml')
    except Exception as e:
        print(f"轉發失敗: {e}")
        return "Internal Server Error", 500

# --- 修改後的路由 ---


# 設定 MinimServer 的實際控制位址 (請確認您的 MinimServer IP 和 UUID)
MINIM_CD_CONTROL = "http://"+data["minimserver_ip"]+":9791/"+data["Minim_ContentDirectory"]["controlURL"].lstrip('/')
MINIM_CM_CONTROL = "http://"+data["minimserver_ip"]+":9791/"+data["Minim_ConnectionManager"]["controlURL"].lstrip('/')

@app.route(data["ContentDirectory"]["controlURL"], methods=['POST'])
@auth.login_required
def content_directory_control():
    # 從 Request Header 抓取原始的 SOAPACTION
    soap_action = request.headers.get('SOAPACTION')
    # print(MINIM_CD_CONTROL)
    return forward_soap(MINIM_CD_CONTROL, request.data, soap_action)

@app.route(data["ConnectionManager"]["controlURL"], methods=['POST'])
@auth.login_required
def connection_manager_control():
    soap_action = request.headers.get('SOAPACTION')
    return forward_soap(MINIM_CM_CONTROL, request.data, soap_action)

# for streaming
@app.route('/<path:music_path>', methods=['GET'])
def proxy_stream(music_path):
    # 重新拼接回 MinimServer 的真實網址
    target_url = "http://"+data["minimserver_ip"]+f":9790/{music_path}"
    # print(target_url)
    # 串流轉發：邊抓邊傳，防止大檔案擠爆記憶體
    # if request.method == 'HEAD':
    #     r = requests.head(target_url, timeout=5)
    #     return Response("", headers=dict(r.headers))

    # def generate():
    #     r = requests.get(target_url, stream=True)
    #     for chunk in r.iter_content(chunk_size=4096):
    #         yield chunk
            
    # return Response(generate(), mimetype='audio/mpeg') # 根據實際格式調整

    # 2. 獲取用戶端發來的 Range 標頭 (這是拖曳進度條的關鍵)
    range_header = request.headers.get('Range')
    
    headers = {
        'User-Agent': 'UPnP/1.1',
        'Range': range_header if range_header else None
    }
    # 移除 None 的鍵
    headers = {k: v for k, v in headers.items() if v is not None}

    # 3. 如果是 GET 請求，進行串流
    r = requests.get(target_url, headers=headers, stream=True, timeout=10)
    
    # 複製必要的 Header，特別是 Content-Type 和 Content-Length
    headers = {
        'Content-Type': r.headers.get('Content-Type'),
        'Content-Length': r.headers.get('Content-Length'),
        'Accept-Ranges': 'bytes' # 對於 Seek (快轉) 很重要
    }
    return Response(r.iter_content(chunk_size=1024*64), headers=headers)

if __name__ == "__main__":
    # 必須運行在 58055 埠
    app.run(host='0.0.0.0', port=data["port"])
