import requests
import json

# 请求URL
url = "http://124.70.197.189:8080/shipInDeal/getShip"

# 请求头
headers = {
    "Content-Type": "application/json"
}

# 请求参数
payload = {
    "shipName": "运沙船",          # 船名
    "mmsi": "ca123",           # Mmsi号
    "shipLockId": "ZZ02",            # 船闸Id
    "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",      # 闸室Id
    "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",  # 图片数组
    "source": "sys_user",           # 数据来源
    "sourceId": "2",      # 数据来源Id
    "deviceId": 2,  # 检测设备数组
    "sort": 1,                    # 顺序
    "data": "{'height': '10','isHeight': 1,'speed': '10','isSpeed': 1}",
    "shipLockNumber": "gzch"     # 闸次号
}

try:
    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 打印响应状态码和内容
    print("状态码:", response.status_code)
    print("响应内容:", response.text)

except requests.exceptions.RequestException as e:
    print("请求发生错误:", e)