from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO
from flask import request, jsonify

import threading

import json
import requests


app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on("position_update")
def handle_position_update(data):
    # 处理位置更新
    socketio.emit(
        "update_ship",
        {
            "ship_name": data["ship_name"],
            "position": data["position"],
            "status": "正常",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )

# 模拟接收网络数据的函数
def receive_network_data():
    while True:
        # 模拟数据，实际应用中替换为真实的网络数据接收代码
        data = {
            "ship_name": "远宁998",
            "position": {"x": 150, "y": 100},
            "status": "正常",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        socketio.emit("update_ship", data)
        time.sleep(0.1)  # 每5秒更新一次


def receive_udp_data():
    # UDP服务器配置
    UDP_IP = "0.0.0.0"
    UDP_PORT = 40001

    # 创建UDP服务器
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 设置 socket 选项允许地址重用
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass  # 某些系统可能不支持 SO_REUSEPORT

    # 设置超时，这样可以定期检查是否需要退出
    sock.settimeout(1.0)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"UDP服务器启动在端口 {UDP_PORT}")

    while True:
        try:
            # 接收数据
            data, addr = sock.recvfrom(1024)
            print(f"recv {UDP_PORT} {data}")

            try:
                ship_data = json.loads(data.decode("utf-8"))
                socketio.emit("update_ship", ship_data)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
            except Exception as e:
                print(f"处理数据时出错: {e}")

        except Exception as e:
            print(f"接收错误: {e}")
            time.sleep(0.1)



    <script>

    </script>

"""

@app.route("/")
def index():
    # 初始加载时获取第一页的数据
    data, total_count = get_latest_data(
        connect_to_database(), currentPage=1, per_page=10
    )
    total_pages = (total_count + 10 - 1) // 10
    return render_template_string(HTML_TEMPLATE, currentPage=1, totalPages=total_pages)




if __name__ == "__main__":
        # 启动网络数据接收线程
    # network_thread = threading.Thread(target=receive_udp_data)
    # network_thread = threading.Thread(target=receive_network_data)
    # network_thread.daemon = True
    # network_thread.start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)