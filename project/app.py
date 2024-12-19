from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
from udp_handler import receive_udp_data

# 创建Flask应用实例
app = Flask(__name__)
# 创建SocketIO实例，用于实时通信
socketio = SocketIO(app)

# 主页路由
@app.route('/')
def index():
    return render_template('index.html')

# WebSocket事件处理：接收位置更新
@socketio.on('position_update')
def handle_position_update(data):
    # 处理从前端接收到的位置更新，并广播给所有客户端
    socketio.emit('update_ship', {
        'ship_name': data['ship_name'],
        'position': data['position'],
        'status': '正常',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    })

# 应用入口
if __name__ == '__main__':
    # 启动UDP接收线程
    network_thread = threading.Thread(target=receive_udp_data, args=(socketio,))
    network_thread.daemon = True  # 设置为守护线程
    network_thread.start()
    
    # 启动Flask应用
    socketio.run(app, debug=True)