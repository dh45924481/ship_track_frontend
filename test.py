from flask import Flask, render_template_string
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
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        socketio.emit('update_ship', data)
        time.sleep(5)  # 每5秒更新一次


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
                ship_data = json.loads(data.decode('utf-8'))
                socketio.emit('update_ship', ship_data)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
            except Exception as e:
                print(f"处理数据时出错: {e}")

        except Exception as e:
            print(f"接收错误: {e}")
            time.sleep(5)


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>船舶管理系统</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        /* 原有样式保持不变 */
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }
        .header {
            background: linear-gradient(to right, #006400, #008000);
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
        }

        /* 添加状态指示器样式 */
        .status-indicator {
            position: absolute;
            top: -5px;
            right: -5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #gray;
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
            margin: 10px 0;
            padding: 10px;
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
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            max-width: 300px;
        }

        /* 原有表格样式 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
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
        <div class="button-group">
            <button class="button">起点检测</button>
            <button class="button">闸上上行人入检测</button>
            <button class="button">深浮物检测</button>
        </div>

        <div class="ship-buttons" id="shipContainer">
            <!-- 船舶按钮将通过JavaScript动态添加 -->
        </div>

        <div class="button-group">
            <button class="button">闸门双开放置</button>
            <button class="button">闸上上行人入检测</button>
            <button class="button">通过锁检测</button>
        </div>
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
        </tbody>        function createShipButtons() {
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
            const button = Array.from(document.getElementsByClassName('ship-button'))
                               .find(btn => btn.textContent === data.ship_name);

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
                updateTable();
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

        // 更新表格
        // function updateTable(data) {
        //     const tbody = document.querySelector('#shipTable tbody');
        //     const row = document.createElement('tr');

        //     row.innerHTML = `
        //         <td>${tbody.children.length + 1}</td>
        //         <td>${Date.now().toString().slice(-3)}</td>
        //         <td>实时位置更新</td>
        //         <td>${data.timestamp}</td>
        //         <td>${data.ship_name}</td>
        //         <td>${data.status}</td>
        //         <td><button onclick="showDetails('${data.ship_name}')">查看详情</button></td>
        //     `;

        //     tbody.insertBefore(row, tbody.firstChild);

             // 保持最多显示10行
        //     while (tbody.children.length > 10) {
        //         tbody.removeChild(tbody.lastChild);
        //     }
        // }

        function updateTable() {
            fetch('/get_data')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.querySelector('#shipTable tbody');
                    tbody.innerHTML = ''; // Clear existing data
                    data.forEach(row => {
                        const tr = document.createElement('tr');
                        row.forEach(cellData => {
                            const td = document.createElement('td');
                            td.textContent = cellData;
                            tr.appendChild(td);
                        });
                        tbody.appendChild(tr);
                    });
                })
                .catch(error => console.error('Error fetching data:', error));
        }

        // 显示详情
        function showDetails(shipName) {
            alert(`显示 ${shipName} 的详细信息`);
        }

        // 初始化
        createShipButtons();
        setInterval(updateDateTime, 1000);
        updateDateTime();
        setInterval(updateTable, 100000);
        updateTable();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


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


def connect_to_database():
    # 连接数据库
    connection = pymysql.connect(
        host='47.116.5.151',
        user='root',
        password='123456',
        database='jiance',
        port=13308,
        cursorclass=pymysql.cursors.DictCursor,
        # charset='utf8mb4',
    )
    return connection

# tbl_boat_result
def get_latest_data(connection):
    try:
        # 查询最近的十艘船记录
        with connection.cursor() as cursor:
            sql = """SELECT direction,name FROM tbl_boat_result_114 ORDER BY create_time DESC LIMIT 20"""
            cursor.execute(sql)
            recent_ships = cursor.fetchall()
            # connection.close()
            return recent_ships
    except Exception as e:
        print(f"Error inserting data: {e}")

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_latest_data(connection)
        return jsonify(data)
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        connection.close()



@socketio.on('position_update')
def handle_position_update(data):
    # 处理位置更新
    socketio.emit('update_ship', {
        'ship_name': data['ship_name'],
        'position': data['position'],
        'status': '正常',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    # 启动网络数据接收线程
    network_thread = threading.Thread(target=receive_udp_data)
    # network_thread = threading.Thread(target=receive_network_data)
    network_thread.daemon = True
    network_thread.start()

    # 启动Flask应用
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)