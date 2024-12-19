import socket
import json
import time

def receive_udp_data(socketio):
    # UDP服务器配置
    UDP_IP = "127.0.0.1"  # 本地地址
    UDP_PORT = 40001      # 监听端口
    
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass  # Windows系统不支持SO_REUSEPORT
    
    # 设置超时和绑定地址
    sock.settimeout(1.0)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"UDP服务器启动在端口 {UDP_PORT}")
    
    # 持续接收数据
    while True:
        try:
            # 接收UDP数据
            # data, addr = sock.recvfrom(1024)
            # print(f"收到数据: {data}")

            try:
                # 解析JSON数据
                # ship_data = json.loads(data.decode('utf-8'))
                # 通过WebSocket发送给所有客户端
                ship_data = {
                    "ship_name": "远宁998",
                    "position": {"x": 150, "y": 100},
                    "status": "正常",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                print(f"收到数据: {ship_data}")
                socketio.emit('update_ship', ship_data)
                time.sleep(5)  # 等待5秒后重试
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
            except Exception as e:
                print(f"处理数据时出错: {e}")
                
        except Exception as e:
            print(f"接收错误: {e}")
            time.sleep(5)  # 出错时等待5秒后重试