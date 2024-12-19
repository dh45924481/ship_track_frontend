from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO
from flask import request, jsonify
import pymysql
import threading
import time
import socket
import json
import requests


app = Flask(__name__)
socketio = SocketIO(app)


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
    # UDP_IP = "127.0.0.1"
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


def send_post_request(url, headers, payload):
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # 返回响应状态码和内容
        return response.status_code, response.text

    except requests.exceptions.RequestException as e:
        return None, str(e)


def scheduled_task(url, headers, payload):
    status_code, response_text = send_post_request(url, headers, payload)
    print(url, "状态码:", status_code)
    print("响应内容:", response_text)
    # 重新设置定时器，每 10 秒调用一次 send_post_request
    threading.Timer(10, scheduled_task).start()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>船舶管理系统</title>
    <link rel="stylesheet" href="./static/css/swiper-bundle.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="./static/js/swiper-bundle.min.js"></script>
    <style>
    /* 原有样式保持不变 */
    body {
      font-family: 'Arial', sans-serif;
      background-color: #f2f2f2;
      margin: 0;
      padding: 0;
    }

    .header {
      background-color: #006400;
      color: white;
      padding: 10px;
      display: flex;
      justify-content: space-between;
    }

    .navigation {
      border: 1px solid #ccc;
      margin: 20px;
      padding: 20px;
      border-radius: 5px;
      position: relative;
      background-color: white;
    }

    /* 上游闸门对中 */
    #sy_duizhong {
    position: absolute;
    top: 170px; /* 垂直居中 */
    left: 200px; /* 靠左对齐 */
    transform: translateY(-50%); /* 调整按钮自身的垂直居中 */
    writing-mode: vertical-rl; /* 文本垂直排列 */
    }

    /* 上游闸室出空 */
    #sy_chukong{
      position: absolute;
      top: 170px; /* 垂直居中 */
      left: 100px; /* 靠左对齐 */
      transform: translateY(-50%); /* 调整按钮自身的垂直居中 */
      writing-mode: vertical-rl; /* 文本垂直排列 */
    }

    /* 下游闸室出空 */
    #xy_chukong{
      position: absolute;
      top: 170px; /* 垂直居中 */
      right: 100px; /* 靠左对齐 */
      transform: translateY(-50%); /* 调整按钮自身的垂直居中 */
      writing-mode: vertical-rl; /* 文本垂直排列 */
    }

    /* 下游闸门对中 */
    #xy_duizhong {
    position: absolute;
    top: 170px; /* 垂直居中 */
    right: 200px; /* 靠左对齐 */
    transform: translateY(-50%); /* 调整按钮自身的垂直居中 */
    writing-mode: vertical-rl; /* 文本垂直排列 */
    }

    /* 上游起点 */
    #sy_qidian{
      position: absolute;
      left: 20px;
      top: 250px;
    }

    /* 下游漂浮物 */
    #xy_piaofuwu{
      position: absolute;
      right: 20px;
    }

    /* 下游起点 */
    #xy_qidian{
      position: absolute;
      right: 20px;
      top: 250px;
    }

    /* 下游超警戒线 */
    #xy_jingjie{
      position: absolute;
      right: 270px;
      top: 250px;
    }

    /* 上游超警戒线 */
    #sy_jingjie{
      position: absolute;
      left: 270px;
    }

    /* 下游左-系缆识别 */
    #xyz_xilan{
      position: absolute;
      right: 500px;
      top: 250px;
    }

    /* 下游右-系缆识别 */
    #xyy_xilan{
      position: absolute;
      right: 500px;
    }

    /* 上游左-系缆识别 */
    #syz_xilan{
      position: absolute;
      left: 500px;
      top: 250px;
    }

    /* 上游右-系缆识别 */
    #syy_xilan{
      position: absolute;
      left: 500px;
    }


    /* 下游闸门行人检测 */
    #openDoorSafe_Downstream{
      position: absolute;
      right: 270px;
    }

    /* 上游闸门行人检测 */
    #openDoorSafe_Upstream{
      position: absolute;
      left: 270px;
      top: 250px;
    }

     /* 换缆提醒 */
    #huanlan{
      position: absolute;
      left: 680px;
      top: 250px;
    }


    .button-group {
      display: flex;
      justify-content: space-between;
      margin-bottom: 20px;
    }

    .button {
      background-color: #4CAF50;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-weight: 600;
      transition: background-color 0.3s ease;
    }

    .button:hover {
        background-color: #45a049;
    }

    /* 添加状态指示器样式 */
    .status-indicator {
      position: absolute;
      top: -5px;
      right: -5px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background-color: #f44336;
      transition: background-color 0.3s ease;
    }

    .status-normal {
      background-color: #4CAF50;
    }

    .status-warning {
      background-color: #ff9800;
    }

    .status-error {
      background-color: #f44336;
    }

    .ship-buttons {
      position: relative;
      min-height: 100px;
      border: 1px dashed #ccc;
      margin: 50px 250px;
      padding: 10px;
      background-color: white;
    }

    .ship-button {
      position: absolute;
      border: 1px solid #4CAF50;
      background-color: white;
      color: #4CAF50;
      padding: 5px 15px;
      border-radius: 3px;
      cursor: move;
      user-select: none;
      z-index: 1;
      transition: opacity 0.3s ease;
    }

    .ship-button.dragging {
      opacity: 0.5;
      z-index: 1000;
    }

    /* 添加信息面板样式 */
    .info-panel {
      position: fixed;
      right: 20px;
      top: 20px;
      background-color: white;
      border: 1px solid #ccc;
      padding: 10px;
      border-radius: 5px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
      max-width: 300px;
      z-index: 99;
      transition: opacity 0.3s ease;
    }

    .info-panel h3 {
        margin-top: 0;
    }

    .info-panel p {
        margin-bottom: 0;
    }

    .ship-buttons {
        position: relative;
        min-height: 100px;
        border: 1px dashed #ccc;
        margin: 50px 250px;
        padding: 10px;
        background-color: white;
    }

    .ship-button {
        position: absolute;
        border: 1px solid #4CAF50;
        background-color: white;
        color: #4CAF50;
        padding: 5px 15px;
        border-radius: 3px;
        cursor: move;
        user-select: none;
        z-index: 1;
        transition: opacity 0.3s ease;
    }

    .ship-button.dragging {
        opacity: 0.5;
        z-index: 1000;
    }

    .ship-buttons img {
        width: 100%;
        height: auto;
        transition: transform 0.3s ease;
    }

    .ship-buttons img:hover {
        transform: scale(1.1);
    }

    .ship-buttons .ship-button {
        position: absolute;
        border: 1px solid #4CAF50;
        background-color: white;
        color: #4CAF50;
        padding: 5px 15px;
        border-radius: 3px;
        cursor: move;
        user-select: none;
        z-index: 1;
        transition: opacity 0.3s ease;
    }

    .ship-buttons .ship-button.dragging {
        opacity: 0.5;
        z-index: 1000;
    }

    .ship-buttons .ship-button img {
        width: 100%;
        height: auto;
        transition: transform 0.3s ease;
    }

    .ship-buttons .ship-button img:hover {
        transform: scale(1.1);
    }

    .info-panel.hidden {
      display: none;
     }

    .query-form {
        max-width: 100%;
        margin: 0 auto;
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #f9f9f9;
    }

    .query-form label {
        margin-right: 5px; /* 增加标签与输入框之间的间距 */
        font-weight: bold;
    }

    .query-form .input-container {
        display: flex; /* 启用 Flexbox 布局 */
        align-items: center; /* 垂直居中对齐 */
    }

    .query-form input[type="datetime-local"],
    .query-form select,
    .query-form input[type="text"] {
        margin-right: 5px;
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 4px;
        box-sizing: border-box;
    }

    .query-form .form-row {
        display: flex; /* 启用 Flexbox 布局以放置输入和按钮容器 */
        justify-content: space-between; /* 使其在行中分开对齐 */
        align-items: center; /* 垂直居中对齐 */
        height: 36px; /* 统一高度，确保对齐 */
    }

    .query-form .button-container {
        margin-top: -3px;
        margin-right: 230px;

    }

    .query-form button {
        padding: 5px 20px;
        margin-right: 20px;
        background-color: #45a049;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        height: 36px;
    }

    .query-form button:hover {
        background-color: #0056b3;
    }


    /* 原有表格样式 */
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      background-color: white;
    }

    th,
    td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: center;
    }

    th {
      background-color: #4CAF50;
      color: white;
      text-align: center;
    }

    tr:nth-child(even) {
      background-color: #f2f2f2;
    }

    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }

    .page-button {
      background-color: #4CAF50;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      margin: 0 5px;
      transition: background-color 0.3s ease;
    }

    .page-button:hover {
      background-color: #45a049;
    }

    /* 模态框样式 */
    .modal {
        display: none; /* 默认隐藏 */
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        background-color: rgba(0,0,0,0.4);
    }

    .modal-content {
        background-color: #fefefe;
        margin: 15% auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
        max-width: 800px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: opacity 0.3s ease;
    }

    .close-button {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        transition: color 0.3s ease;
    }

    .close-button:hover,
    .close-button:focus {
        color: black;
        text-decoration: none;
        cursor: pointer;
    }

    .modal-images {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .modal-images img {
        max-width: 100%;
        margin: 10px 0;
        transition: transform 0.3s ease;
    }
    .modal-images img:hover {
        transform: scale(1.1);
    }
    .swiper-container {
            width: 100%;
            height: 100%;
        }
        .swiper-slide img {
    width: 100%;
    height: auto;
    display: block;

  </style>
</head>
<body>
    <div class="header">
        <div>船舶运河智慧船闸</div>
        <div id="datetime"></div>
    </div>

    <div class="info-panel" id="infoPanel" style="display: none;">
        <h3>船舶信息</h3>
        <div id="shipInfo"></div>
    </div>

    <div class="navigation">

        <button class="button" id="sy_piaofuwu"">上游漂浮物检测</button>
        <button class="button" id="syy_xilan">上游右-系缆识别</button>
        <button class="button" id="xyy_xilan">下游右-系缆识别</button>
        <button class="button" id="huanlan">换缆提醒</button>
        <button class="button" id="sy_duizhong">上游闸门对中识别</button>
        <button class="button" id="sy_chukong">上游出空检测</button>
        <button class="button" id="xy_piaofuwu">下游漂浮物检测</button>
        <button class="button" id="openDoorSafe_Downstream">下游闸门上方行人检测</button>
        <button class="button" id="sy_jingjie">上游超警戒线检测</button>

        <div class="ship-buttons" id="shipContainer">
            <!-- 船舶按钮将通过JavaScript动态添加 -->
        </div>

        <button class="button" id="openDoorSafe_Upstream">上游闸门上方行人检测</button>
        <button class="button" id="xy_qidian" style="visibility: hidden;">下游起点检测</button>
        <button class="button" id="syz_xilan">上游左-系缆识别</button>
        <button class="button" id="xyz_xilan">下游左-系缆识别</button>
        <button class="button" id="sy_qidian" style="visibility: hidden;">上游起点检测</button>
        <button class="button" id="xy_jingjie">下游超警戒线检测</button>
        <button class="button" id="xy_duizhong">下游闸门对中识别</button>
        <button class="button" id="xy_chukong">下游出空检测</button>

    </div>

    <div class="query-form">
        <form id="queryForm">
            <div class="form-row">
                <div class="input-container">
                    <label for="startTime">开始时间:</label>
                    <input type="datetime-local" id="startTime" name="startTime">
                    <label for="endTime">结束时间:</label>
                    <input type="datetime-local" id="endTime" name="endTime">
                    <label for="monitorPoint">方向点位:</label>
                    <select id="monitorPoint" name="monitorPoint">
                        <option value="201">201</option>
                        <option value="202">202</option>
                        <option value="101">101</option>
                        <option value="102">102</option>
                    </select>
                    <label for="direction">上下行:</label>
                    <select id="direction" name="direction">
                        <option value="upstream">上行</option>
                        <option value="downstream">下行</option>
                    </select>
                    <label for="shipName">船名:</label>
                    <input type="text" id="shipName" name="shipName">
                </div>
                <div class="button-container">
                    <button type="submit">查询</button>
                    <button type="reset">重置</button>
                </div>
            </div>
        </form>
    </div>


    <table id="shipTable">
        <thead>
            <tr>
                <th>序号</th>
                <th>编号</th>
                <th>方向点位</th>
                <th>时间</th>
                <th>船舶号码</th>
                <th>状态</th>
                <th>详情</th>
            </tr>
        </thead>
        <tbody>
            <!-- 表格内容将通过JavaScript动态更新 -->
        </tbody>
    </table>

    <!-- 模态框结构 -->
    <div id="detailModal" class="modal">
    <div class="modal-content">
        <span class="close-button">&times;</span>
        <div class="swiper-container">
            <div class="swiper-wrapper">
                <!-- 图片将通过JavaScript动态插入 -->
            </div>
            <!-- 添加导航按钮 -->
            <div class="swiper-button-next"></div>
            <div class="swiper-button-prev"></div>
            <!-- 添加分页器 -->
            <div class="swiper-pagination"></div>
        </div>
    </div>
</div>

    <script>
        // 初始化Socket.IO客户端
        var socket = io();

        // 从模板中获取初始的 currentPage 和 totalPages
        var currentPage = {{currentPage}};
        var totalPages = {{totalPages}};

        // 模拟船舶数据，实际应用中应从服务器获取
        const ships = [
            { name: "远宁998", x: 10, y: 10, status: "正常" },
            { name: "运沙船", x: 10, y: 80, status: "警告" }
        ];

        function createShipButtons() {
            const container = document.getElementById('shipContainer');
            ships.forEach(ship => {
                const button = document.createElement('button');
                button.className = 'ship-button';
                button.textContent = ship.name;
                button.style.left = ship.x + 'px';
                button.style.top = ship.y + 'px';

                const statusIndicator = document.createElement('div');
                statusIndicator.className = 'status-indicator';
                button.appendChild(statusIndicator);

                container.appendChild(button);
                setupDragListeners(button);
            });
        }

        document.getElementById('queryForm').addEventListener('submit', function(event) {
            event.preventDefault(); // 阻止表单默认提交行为

            const startTime = document.getElementById('startTime').value;
            const endTime = document.getElementById('endTime').value;
            const monitorPoint = document.getElementById('monitorPoint').value;
            const shipName = document.getElementById('shipName').value;

            // 发送请求到服务器
            fetch('/query_ships', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    startTime: startTime,
                    endTime: endTime,
                    monitorPoint: monitorPoint,
                    shipName: shipName
                })
            })
            .then(response => response.json())
            .then(data => {
                // 处理服务器返回的数据，更新表格
                updateTable(data);
            })
            .catch(error => console.error('Error fetching data:', error));
        });



        // 创建下游出空事件判断，0表示当前闸室出空，按钮为绿色，1表示当前闸室未出空按钮为红色
        function createxychukong() {
            setInterval(() => {
                fetch('/getOut208')
                    .then(response => response.json())
                    .then(data => {
                        console.log('下游:', data.data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const xy_chukongbutton = document.getElementById('xy_chukong');
                                                data.data.forEach(data => {
                            //console.log('1111:', data.type);
                            if (data.type == 0) {
                                xy_chukongbutton.style.backgroundColor = "green";
                            } else {
                                xy_chukongbutton.style.backgroundColor = "red";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        // 创建上游出空事件判断，0表示当前闸室出空，按钮为绿色，1表示当前闸室未出空按钮为红色
        function createsychukong() {
            setInterval(() => {
                fetch('/getOut210')
                    .then(response => response.json())
                    .then(data => {
                        console.log('上游:', data.data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const sy_chukongbutton = document.getElementById('sy_chukong');
                        data.data.forEach(data => {
                            //console.log('1111:', data.type);
                            if (data.type == 0) {
                                sy_chukongbutton.style.backgroundColor = "green";
                            } else {
                                sy_chukongbutton.style.backgroundColor = "red";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        // 创建对中事件判断，1表示当前闸门对中，按钮为绿色，0表示当前闸门未对中，按钮为红色
        function createxyduizhong() {
            setInterval(() => {
                fetch('/getOut115')
                    .then(response => response.json())
                    .then(data => {
                        console.log('下游对中:', data.data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const xy_duizhongbutton = document.getElementById('xy_duizhong');
                        data.data.forEach(data => {
                            console.log('1111:', data.status);
                            if (data.status == 1) {
                                xy_duizhongbutton.style.backgroundColor = "green";
                            } else {
                                xy_duizhongbutton.style.backgroundColor = "red";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function createOpenDoorSafeUpButtons() {
            setInterval(() => {
                fetch('/openDoorSafe_up')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('openDoorSafe_Upstream');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(person => {
                            // const button = document.createElement('button');
                            // button.className = 'person-button';
                            if (person.has_person_1 == 1 || person.has_person_2 == 1) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                            // container.appendChild(button);
                            // setupDragListeners(button);
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function createOpenDoorSafeDownButtons() {
            setInterval(() => {
                fetch('/openDoorSafe_down')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('openDoorSafe_Downstream');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(person => {
                            // const button = document.createElement('button');
                            // button.className = 'person-button';
                            if (person.has_person_1 == 1 || person.has_person_2 == 1) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                            // container.appendChild(button);
                            // setupDragListeners(button);
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function create_syy_xilanButtons() {
            setInterval(() => {
                fetch('/openDoorEvent_syy')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('syy_xilan');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.type == 0) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function create_syz_xilanButtons() {
            setInterval(() => {
                fetch('/openDoorEvent_syz')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('syz_xilan');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.type == 0) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function create_xyy_xilanButtons() {
            setInterval(() => {
                fetch('/openDoorEvent_xyy')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('xyy_xilan');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.type == 0) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function create_xyz_xilanButtons() {
            setInterval(() => {
                fetch('/openDoorEvent_xyz')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('xyz_xilan');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.type == 0) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function createdangerdatasyButtons() {
            setInterval(() => {
                fetch('/dist_danger_sy')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('sy_jingjie');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.dist_danger == 0) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function createdangerdataxyButtons() {
            setInterval(() => {
                fetch('/dist_danger_xy')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('xy_jingjie');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.dist_danger == 0) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function create_floating_Buttons_sy() {
            setInterval(() => {
                fetch('/gate_floating_monitoring_sy')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('sy_piaofuwu');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.has_floater == 1) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function create_floating_Buttons_xy() {
            setInterval(() => {
                fetch('/gate_floating_monitoring_xy')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('xy_piaofuwu');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.has_floater == 1) {
                                button.style.backgroundColor = "red";
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 5000); // 每5秒查询一次
        }

        function create_cable_Buttons() {
            setInterval(() => {
                fetch('/change_cable')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server data:', data); // 打印数据以检查结构
                        if (!data || !data.data || !Array.isArray(data.data)) {
                            console.error('Invalid data format:', data);
                            return;
                        }
                        const button = document.getElementById('huanlan');
                        // container.innerHTML = ''; // 清空容器内容
                        data.data.forEach(data => {
                            if (data.huanlan_flag == 1) {
                                button.style.backgroundColor = "red";
                                setTimeout(() => {
                                    button.style.backgroundColor = "green";
                                }, 300000);
                            } else {
                                button.style.backgroundColor = "green";
                            }
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, ); // 每5秒查询一次
        }

        // 更新时间显示
        function updateDateTime() {
            const now = new Date();
            const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
            const formatted = `${now.getFullYear()}/${(now.getMonth()+1).toString().padStart(2,'0')}/${now.getDate().toString().padStart(2,'0')} ${days[now.getDay()]} ${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`;
            document.getElementById('datetime').textContent = formatted;
        }

        // 设置拖拽监听器
        function setupDragListeners(button) {
            let isDragging = false;
            let currentX;
            let currentY;
            let initialX;
            let initialY;
            let xOffset = 0;
            let yOffset = 0;

            button.addEventListener('mousedown', dragStart);
            button.addEventListener('mousemove', drag);
            button.addEventListener('mouseup', dragEnd);
            button.addEventListener('mouseleave', dragEnd);

            function dragStart(e) {
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;

                if (e.target === button) {
                    isDragging = true;
                    button.classList.add('dragging');
                }
            }

            function drag(e) {
                if (isDragging) {
                    e.preventDefault();
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;

                    xOffset = currentX;
                    yOffset = currentY;

                    const container = document.getElementById('shipContainer');
                    const containerRect = container.getBoundingClientRect();

                    const buttonRect = button.getBoundingClientRect();
                    const maxX = containerRect.width - buttonRect.width;
                    const maxY = containerRect.height - buttonRect.height;

                    currentX = Math.max(0, Math.min(currentX, maxX));
                    currentY = Math.max(0, Math.min(currentY, maxY));

                    button.style.left = currentX + 'px';
                    button.style.top = currentY + 'px';

                    // 发送位置更新到服务器
                    socket.emit('position_update', {
                        ship_name: button.textContent,
                        position: {x: currentX, y: currentY}
                    });
                }
            }

            function dragEnd() {
                initialX = currentX;
                initialY = currentY;
                isDragging = false;
                button.classList.remove('dragging');
            }
        }

        // 处理接收到的船舶更新数据
        socket.on('update_ship', function(data) {
            const button = Array.from(document.getElementsByClassName('ship-button')).find(btn => btn.textContent === data.ship_name);

            if (button) {
                // 更新位置
                if (data.position) {
                    button.style.left = data.position.x + 'px';
                    button.style.top = data.position.y + 'px';
                }

                // 更新状态指示器
                const indicator = button.querySelector('.status-indicator');
                if (indicator) {
                    indicator.className = 'status-indicator status-' + data.status.toLowerCase();
                }

                // 更新信息面板
                updateInfoPanel(data);

                // 更新表格
                // updateTable(data);
                updateTable(1);
            }
        });

        // 更新信息面板
        function updateInfoPanel(data) {
            const panel = document.getElementById('infoPanel');
            const info = document.getElementById('shipInfo');

            info.innerHTML = `
                <p>船名: ${data.ship_name}</p>
                <p>状态: ${data.status}</p>
                <p>更新时间: ${data.timestamp}</p>
            `;

            panel.style.display = 'block';
            setTimeout(() => panel.style.display = 'none', 3000);
        }

        function updateTable(currentPage) {
            currentPage = currentPage || 1;
            console.log('Updating table for currentPage:', currentPage);
            fetch('/get_data?currentPage=' + currentPage )
                .then(response => response.json())
                .then(data => {
                    console.log('Server data:', data); // 打印数据以检查结构
                    if (!data || !Array.isArray(data.data)) {
                        console.error('Invalid data format:', data);
                        return;
                    }

                    totalPages = data.total_pages; // 更新总页数
                    const tbody = document.querySelector('#shipTable tbody');
                    tbody.innerHTML = ''; // Clear existing data
                    data.data.forEach(row => {
                        const tr = document.createElement('tr');
                        const fields = ['id', 'name', 'direction', 'create_time', 'ship_number', 'status'];
                        fields.forEach(fieldName => {
                            const td = document.createElement('td');
                            td.textContent = row[fieldName] || ''; // 使用 || '' 处理可能不存在的字段
                            tr.appendChild(td);
                        });

                        // 添加最后一列“打开详情”
                        const detailTd = document.createElement('td');
                        const detailLink = document.createElement('button');
                        detailLink.textContent = '详情';
                        detailLink.dataset.id = row.id; // 保存单元格序号到数据属性
                        detailLink.addEventListener('click', () => openDetailModal(detailLink.dataset.id));
                        detailTd.appendChild(detailLink);
                        tr.appendChild(detailTd);
                        tbody.appendChild(tr);
                    });
                    addPaginationButtons(totalPages, currentPage); // 更新分页按钮
                })
                .catch(error => console.error('Error fetching data:', error));
        }

        // 显示详情
        function showDetails(shipName) {
            alert(`显示 ${shipName} 的详细信息`);
        }

        let originalImages = [];
        function openDetailModal(id) {
    fetch(`/get_images?id=${id}`)
        .then(response => response.json())
        .then(data => {
            console.log('Server images:', data); // 打印数据以检查结构
            if (!data || !Array.isArray(data.images)) {
                console.error('Invalid images format:', data);
                return;
            }

            const modal = document.getElementById('detailModal');
            const modalImages = document.getElementById('modalImages');
            modalImages.style.display = 'flex';
            modalImages.style.flexDirection = 'row';
            modalImages.innerHTML = ''; // 清空现有图片

            originalImages = data.images.map(imageUrl => imageUrl); // 保存原始图片列表

            // 创建 Swiper 容器
            const swiperWrapper = document.createElement('div');
            swiperWrapper.className = 'swiper-wrapper';
            modalImages.appendChild(swiperWrapper);

            data.images.forEach(imageUrl => {
                const slide = document.createElement('div');
                slide.className = 'swiper-slide';

                const img = document.createElement('img');
                img.src = '/static/images/Snipaste_2024-12-06_14-55-18.png';
                img.style.maxWidth = '100%';
                img.style.margin = '10px';
                img.style.transition = 'max-width 0.3s ease'; // 添加过渡效果
                slide.appendChild(img);

                swiperWrapper.appendChild(slide);

                // 添加点击事件监听器
                img.addEventListener('click', function() {
                    // 清空之前的图片
                    modalImages.innerHTML = '';

                    // 创建 Swiper 容器
                    const swiperWrapper = document.createElement('div');
                    swiperWrapper.className = 'swiper-wrapper';
                    modalImages.appendChild(swiperWrapper);

                    originalImages.forEach(imageUrl => {
                        const slide = document.createElement('div');
                        slide.className = 'swiper-slide';

                        const img = document.createElement('img');
                        img.src = '/static/images/Snipaste_2024-12-06_14-55-18.png'; // 使用实际图片URL
                        img.style.maxWidth = '100%'; // 调整最大宽度
                        img.style.margin = '10px';
                        img.style.transition = 'max-width 0.3s ease'; // 添加过渡效果
                        slide.appendChild(img);

                        swiperWrapper.appendChild(slide);
                    });

                    // 初始化 Swiper
                    new Swiper(modalImages, {
                        slidesPerView: 1,
                        spaceBetween: 30,
                        loop: true,
                        pagination: {
                            el: '.swiper-pagination',
                            clickable: true,
                        },
                        navigation: {
                            nextEl: '.swiper-button-next',
                            prevEl: '.swiper-button-prev',
                        },
                    });

                    modal.style.display = 'block'; // 显示模态框
                });
            });

            // 初始化 Swiper
            new Swiper(modalImages, {
                slidesPerView: 1,
                spaceBetween: 30,
                loop: true,
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
            });

            modal.style.display = 'block'; // 显示模态框
        })
        .catch(error => console.error('Error fetching images:', error));
}

        function closeModal() {
    const modal = document.getElementById('detailModal');
    modal.style.display = 'none';
}

        document.addEventListener('DOMContentLoaded', function() {
    var swiper = new Swiper('#modalImages', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
    });
    // 关闭模态框的功能
    var modal = document.getElementById('detailModal');
    var closeButton = document.querySelector('.close-button');

    closeButton.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }
});

        // 添加分页按钮
        const paginationContainer = document.createElement('div');
        paginationContainer.className = 'pagination';
        document.body.appendChild(paginationContainer);

        function addPaginationButtons(totalPages, currentPage) {
            paginationContainer.innerHTML = '';

            // 第一页/共多少页
            const pageInfo = document.createElement('span');
            pageInfo.textContent = `第 ${currentPage} 页 / 共 ${totalPages} 页`;
            paginationContainer.appendChild(pageInfo);

            // 首页按钮
            const firstButton = document.createElement('button');
            firstButton.textContent = '首页 ';
            firstButton.disabled = currentPage === 1;
            firstButton.addEventListener('click', () => {
                if (currentPage !== 1) {
                    currentPage = 1;
                    updateTable(currentPage);
                    addPaginationButtons(totalPages, currentPage);
                }
            });

            paginationContainer.appendChild(firstButton);

            // 上一页按钮
            const prevButton = document.createElement('button');
            prevButton.textContent = '上一页 ';
            prevButton.disabled = currentPage === 1;
            prevButton.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    updateTable(currentPage);
                    addPaginationButtons(totalPages, currentPage);
                }
            });
            paginationContainer.appendChild(prevButton);

            // 下一页按钮
            const nextButton = document.createElement('button');
            nextButton.textContent = '下一页 ';
            nextButton.disabled = currentPage === totalPages;
            nextButton.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    currentPage++;
                    updateTable(currentPage);
                    addPaginationButtons(totalPages, currentPage);
                }
            });
            paginationContainer.appendChild(nextButton);

            // 尾页按钮
            const lastButton = document.createElement('button');
            lastButton.textContent = '尾页 ';
            lastButton.disabled = currentPage === totalPages;
            lastButton.addEventListener('click', () => {
                if (currentPage !== totalPages) {
                    currentPage = totalPages;
                    updateTable(currentPage);
                    addPaginationButtons(totalPages, currentPage);
                }
            });
            paginationContainer.appendChild(lastButton);

            // 跳转输入框
            const gotoInput = document.createElement('input');
            gotoInput.type = 'number';
            gotoInput.min = 1;
            gotoInput.max = totalPages;
            gotoInput.value = currentPage;
            gotoInput.addEventListener('change', () => {
                const pageNumber = parseInt(gotoInput.value, 10);
                if (pageNumber >= 1 && pageNumber <= totalPages) {
                    currentPage = pageNumber;
                    updateTable(currentPage);
                    addPaginationButtons(totalPages, currentPage);
                }
            });
            paginationContainer.appendChild(gotoInput);

            // 跳转按钮
            const gotoButton = document.createElement('button');
            gotoButton.textContent = '跳转 ';
            gotoButton.addEventListener('click', () => {
                const pageNumber = parseInt(gotoInput.value, 10);
                if (pageNumber >= 1 && pageNumber <= totalPages) {
                    currentPage = pageNumber;
                    updateTable(currentPage);
                    addPaginationButtons(totalPages, currentPage);
                }
            });
            paginationContainer.appendChild(gotoButton);
        }

        // 初始化
        createShipButtons();
        createOpenDoorSafeUpButtons();
        createOpenDoorSafeDownButtons();
        create_syy_xilanButtons();
        create_syz_xilanButtons();
        create_xyy_xilanButtons();
        create_xyz_xilanButtons();
        createdangerdatasyButtons();
        createdangerdataxyButtons();
        create_floating_Buttons_sy();
        create_floating_Buttons_xy();


        setInterval(updateDateTime, 1000);
        updateDateTime();
        setInterval(() => updateTable(currentPage), 100000);
        updateTable(currentPage);
        // 出空事件初始化
        createxychukong();
        createsychukong();
        // 对中事件初始化
        createxyduizhong();
        create_cable_Buttons();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    # 初始加载时获取第一页的数据
    data, total_count = get_latest_data(
        connect_to_database(), currentPage=1, per_page=10
    )
    total_pages = (total_count + 10 - 1) // 10
    return render_template_string(HTML_TEMPLATE, currentPage=1, totalPages=total_pages)


def connect_to_database():
    # 连接数据库
    connection = pymysql.connect(
        host="47.116.5.151",
        user="root",
        password="123456",
        database="jiance",
        port=13308,
        cursorclass=pymysql.cursors.DictCursor,
        # charset='utf8mb4',
    )
    return connection


@app.route("/get_images", methods=["GET"])
def get_images():
    id = request.args.get("id")
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT pic1, pic2, pic3 FROM tbl_boat_result_114 WHERE id = %s"""
            cursor.execute(sql, (id,))
            result = cursor.fetchone()

        if result:
            images = [result[col] for col in ["pic1", "pic2", "pic3"] if result[col]]
            return jsonify({"images": images})
        else:
            return jsonify({"images": []}), 404
    finally:
        connection.close()


@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_PATH, filename)


@app.route("/query_ships", methods=["POST"])
def query_ships():
    data = request.get_json()
    startTime = data.get("startTime")
    endTime = data.get("endTime")
    monitorPoint = data.get("monitorPoint")
    shipName = data.get("shipName")
    connection = connect_to_database()

    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT id,direction,name,create_time FROM tbl_boat_result_114 WHERE create_time BETWEEN '{startTime}' AND '{endTime}'"""
            if monitorPoint:
                sql += f" AND direction = '{monitorPoint}'"
            if shipName:
                sql += f" AND name = '{shipName}'"
            cursor.execute(sql)
            result = cursor.fetchall()
            return jsonify(result)
    except Exception as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": str(e)})


# tbl_inout_result 船舶信息异常检测接口（船舶吃水，船舶尺寸）
def get_ShipIn_Warn_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/getShipInWarn", methods=["GET"])
def getShipInWarn():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_ShipIn_Warn_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def post_getShipInWarn():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_ShipIn_Warn_data(connection)
        payload = {
            "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",
            "shipLockId": "4028858a15a6af970115a819f247007e",
            "source": "sys_user",
            "sourceId": "2",
            "shipLockNumber": "gzch",
            "deviceId": 2,
            "shipName": "运沙船",
            "mmsi": "ca123",
            "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",
        }
        url = "http://124.70.197.189:8080/shipInDeal/putIntoGear"
        headers = {"Content-Type": "application/json"}
        status_code, response_text = send_post_request(url, headers, payload)
        print(url, "状态码:", status_code)
        print("响应内容:", response_text)
        # scheduled_task(url,headers,payload)
        # 主程序继续运行其他任务
        # while True:
        # time.sleep(1)  # 防止主程序退出
        # return jsonify({payload})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tbl_inout_result 船舶入档推送接口
def get_put_Into_Gear_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/putIntoGear", methods=["GET"])
def putIntoGear():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_put_Into_Gear_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def post_put_Into_Gear():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_put_Into_Gear_data(connection)
        payload = {
            "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",
            "shipLockId": "4028858a15a6af970115a819f247007e",
            "source": "sys_user",
            "sourceId": "2",
            "shipLockNumber": "gzch",
            "deviceId": 2,
            "shipName": "运沙船",
            "mmsi": "ca123",
            "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",
        }
        url = "http://124.70.197.189:8080/shipInDeal/putIntoGear"
        headers = {"Content-Type": "application/json"}
        status_code, response_text = send_post_request(url, headers, payload)
        print(url, "状态码:", status_code)
        print("响应内容:", response_text)
        # scheduled_task(url,headers,payload)
        # 主程序继续运行其他任务
        # while True:
        # time.sleep(1)  # 防止主程序退出
        # return jsonify({payload})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tbl_inout_result 船舶卡口检测接口（出闸）
def get_out_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/getOut", methods=["GET"])
def Out():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def post_Out():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data(connection)
        payload = {
            "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",
            "source": "sys_user",
            "sourceId": "2",
            "data": "{'speed':'10','isSpeed':1}",
            "shipLockNumber": "gzch",
            "deviceId": 2,
            "shipLockId": "ZZ02",
            "sort": 1,
            "shipName": "运沙船",
            "mmsi": "ca123",
            "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",
        }
        url = "http://124.70.197.189:8080/shipInDeal/getOut"
        headers = {"Content-Type": "application/json"}
        status_code, response_text = send_post_request(url, headers, payload)
        print(url, "状态码:", status_code)
        print("响应内容:", response_text)
        # scheduled_task(url,headers,payload)
        # 主程序继续运行其他任务
        # while True:
        # time.sleep(1)  # 防止主程序退出
        # return jsonify({payload})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tbl_inout_result 最后一艘船船闸中间速度
def get_outTime_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out_time = cursor.fetchall()
            # connection.close()
            return out_time
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/getOutTime", methods=["GET"])
def OutTime():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_outTime_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def post_OutTime():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_outTime_data(connection)
        payload = {
            "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",
            "source": "sys_user",
            "sourceId": "2",
            "data": "{'speed':'3',distance:40}",
            "shipLockNumber": "gzch",
            "deviceId": 2,
            "shipLockId": "ZZ02",
            "sort": 1,
            "shipName": "运沙船",
            "mmsi": "ca123",
            "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",
        }
        url = "http://124.70.197.189:8080/shipInDeal/getOutTime"
        headers = {"Content-Type": "application/json"}
        status_code, response_text = send_post_request(url, headers, payload)
        print(url, "状态码:", status_code)
        print("响应内容:", response_text)
        # scheduled_task(url,headers,payload)
        # 主程序继续运行其他任务
        # while True:
        # time.sleep(1)  # 防止主程序退出
        # return jsonify({payload})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tbl_inout_result 船舶出空信号接口
def get_allOut_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            person_monitoring = cursor.fetchall()
            # connection.close()
            return person_monitoring
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/allOut", methods=["GET"])
def allOut():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_allOut_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def post_allOut():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_allOut_data(connection)
        payload = {
            "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",
            "shipLockId": "4028858a15a6af970115a819f247007e",
            "source": "sys_user",
            "sourceId": "2",
            "shipLockNumber": "gzch",
            "deviceId": 2,
            "shipName": "运沙船",
            "mmsi": "ca123",
            "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",
        }
        url = "http://124.70.197.189:8080/shipInDeal/allOut"
        headers = {"Content-Type": "application/json"}
        status_code, response_text = send_post_request(url, headers, payload)
        print(url, "状态码:", status_code)
        print("响应内容:", response_text)
        # scheduled_task(url,headers,payload)
        # 主程序继续运行其他任务
        # while True:
        # time.sleep(1)  # 防止主程序退出
        # return jsonify({payload})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tb_gate_person_monitoring 船舶进闸安全检测接口（行人识别，漂浮物识别，超警戒线识别）
def get_up_gate_person_monitoring_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT id,gate_id,has_person_1,has_person_2 FROM tb_gate_person_monitoring WHERE gate_id = 2 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            up_person_monitoring = cursor.fetchall()
            # connection.close()
            return up_person_monitoring
    except Exception as e:
        print(f"Error inserting data: {e}")


def get_down_gate_person_monitoring_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT id,gate_id,has_person_1,has_person_2 FROM tb_gate_person_monitoring WHERE gate_id = 1 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            down_person_monitoring = cursor.fetchall()
            # connection.close()
            return down_person_monitoring
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/openDoorSafe_up", methods=["GET"])
def up_openDoorSafe():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_up_gate_person_monitoring_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


@app.route("/openDoorSafe_down", methods=["GET"])
def down_openDoorSafe():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_down_gate_person_monitoring_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def post_openDoorSafe():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_up_gate_person_monitoring_data(connection)

        payload = {
            # "isSafe": not any(d["has_person_1"] or d["has_person_2"] for d in data),
            "isSafe": False,
            "type": 9,
            "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",
            "shipLockId": "4028858a15a6af970115a819f247007e",
            "source": "sys_user",
            "sourceId": "2",
            "shipLockNumber": "gzch",
            "deviceId": 2,
            "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",
        }
        url = "http://124.70.197.189:8080/openDoorDeal/openDoorSafe"
        headers = {"Content-Type": "application/json"}
        status_code, response_text = send_post_request(url, headers, payload)
        print(url, "状态码:", status_code)
        print("响应内容:", response_text)
        # scheduled_task(url,headers,payload)
        # 主程序继续运行其他任务
        # while True:
        # time.sleep(1)  # 防止主程序退出
        # return jsonify({payload})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tb_mooring_security tbl_rope_result 船舶进闸事件检测接口
def get_openDoorEvent_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 202 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/openDoorEvent", methods=["GET"])
def openDoorEvent():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_syy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def post_openDoorEvent():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data(connection)
        payload = {
            # "isSafe": not any(d["has_person_1"] or d["has_person_2"] for d in data),
            "isSafe": False,
            "type": 11,
            "shipLockRoomId": "DC4A2F8A87387215E04010AC0C053EF3",
            "shipLockId": "4028858a15a6af970115a819f247007e",
            "source": "sys_user",
            "sourceId": "2",
            "shipLockNumber": "gzch",
            "deviceId": 2,
            "pics": "https://www.58pic.com/newpic/71001853.png,https://www.58pic.com/newpic/71001853.png",
        }
        url = "http://124.70.197.189:8080/openDoorDeal/openDoorEvent"
        headers = {"Content-Type": "application/json"}
        status_code, response_text = send_post_request(url, headers, payload)
        print(url, "状态码:", status_code)
        print("响应内容:", response_text)
        # scheduled_task(url,headers,payload)
        # 主程序继续运行其他任务
        # while True:
        #     time.sleep(1)  # 防止主程序退出
        # return jsonify({payload})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tbl_boat_result
def get_latest_data(connection, currentPage=1, per_page=10):
    try:
        offset = (currentPage - 1) * per_page
        # 查询最近的十艘船记录
        with connection.cursor() as cursor:
            sql = f"""SELECT COUNT(*) as total_count FROM tbl_boat_result_114"""
            cursor.execute(sql)
            total_count = cursor.fetchone()["total_count"]
            sql = f"""SELECT id,direction,name,create_time FROM tbl_boat_result_114 ORDER BY create_time DESC LIMIT {per_page} OFFSET {offset}"""
            cursor.execute(sql)
            recent_ships = cursor.fetchall()
            # connection.close()
            return recent_ships, total_count
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/get_data", methods=["GET"])
def get_data():
    try:
        currentPage = int(request.args.get("currentPage", 1))
        per_page = 10
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data, total_count = get_latest_data(connection, currentPage, per_page)
        total_pages = (total_count + per_page - 1) // per_page  # 计算总页数
        return jsonify({"data": data, "total_pages": total_pages})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_syy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 202 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/openDoorEvent_syy", methods=["GET"])
def openDoorEvent_syy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_syy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_syz(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 201 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/openDoorEvent_syz", methods=["GET"])
def openDoorEvent_syz():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_syz(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_xyy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 102 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/openDoorEvent_xyy", methods=["GET"])
def openDoorEvent_xyy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_xyy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_xyz(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 101 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/openDoorEvent_xyz", methods=["GET"])
def openDoorEvent_xyz():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_xyz(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def dist_danger_data_sy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT line_type2,dist_danger FROM tb_warning_monitor WHERE lock_id = 2 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            dist_danger = cursor.fetchall()
            # connection.close()
            return dist_danger
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/dist_danger_sy", methods=["GET"])
def dist_danger_sy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = dist_danger_data_sy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def dist_danger_data_xy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT line_type2,dist_danger FROM tb_warning_monitor WHERE lock_id = 1 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            dist_danger = cursor.fetchall()
            # connection.close()
            return dist_danger
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/dist_danger_xy", methods=["GET"])
def dist_danger_xy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = dist_danger_data_xy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def gate_floating_sy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT has_floater FROM tb_gate_floating_monitoring WHERE gate_id = 2 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            floating = cursor.fetchall()
            # connection.close()
            return floating
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/gate_floating_monitoring_sy", methods=["GET"])
def gate_floating_monitoring_sy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = gate_floating_sy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def gate_floating_xy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT has_floater FROM tb_gate_floating_monitoring WHERE gate_id = 1 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            floating = cursor.fetchall()
            # connection.close()
            return floating
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/gate_floating_monitoring_xy", methods=["GET"])
def gate_floating_monitoring_xy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = gate_floating_xy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def change_cable_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT huanlan_flag FROM tb_mooring_security ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            cable = cursor.fetchall()
            # connection.close()
            return cable
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/change_cable", methods=["GET"])
def change_cable():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = change_cable_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_out_data_208(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result WHERE lock_id = 208 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/getOut208", methods=["GET"])
def Out208():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data_208(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


#   检测上游是否出空
def get_out_data_210(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result WHERE lock_id = 210 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/getOut210", methods=["GET"])
def Out210():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data_210(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


#   检测下游闸门是否对中
def get_out_data_115(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tb_gate_alignment WHERE lock_id = 115 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@app.route("/getOut115", methods=["GET"])
def Out115():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data_115(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


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


if __name__ == "__main__":
    # 启动网络数据接收线程
    # network_thread = threading.Thread(target=receive_udp_data)
    # network_thread = threading.Thread(target=receive_network_data)
    # network_thread.daemon = True
    # network_thread.start()
    post_openDoorSafe()
    post_openDoorEvent()
    post_allOut()
    post_OutTime()
    post_Out()

    # 启动Flask应用
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
