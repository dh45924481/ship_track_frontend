import requests
import json

# 请求URL
url = "http://124.70.197.189:8080/shipInDeal/getShipInWarn"

# 请求头
headers = {
    "Content-Type": "application/json"
}

# 请求参数
payload = {
    "shipLockRoomId":"DC4A2F8A87387215E04010AC0C053EF3","shipLockId":"4028858a15a6af970115a819f247007e","source":"sys_user",
    "sourceId":"2",
    "data":"{'length':'10','width':'10','ton':'11','isOut':1,'isTon':0}",
    "shipLockNumber":"5",
    "deviceId":2,
    "sort":1,
    "shipName":"长江推2668",
    "mmsi":"ca123",
    "pics":"https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png"
}

try:
    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 打印响应状态码和内容
    print("状态码:", response.status_code)
    print("响应内容:", response.text)

except requests.exceptions.RequestException as e:
    print("请求发生错误:", e)