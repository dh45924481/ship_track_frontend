import socket
import threading
import time
class DataStruct:
    def __init__(self, seq_no=0, length=0, width=0, height=0, total_count=0):
        self.seq_no = seq_no          # 序号
        self.length = length          # 长
        self.width = width            # 宽
        self.height = height          # 高
        self.total_count = total_count # 总个数

    def pack(self):
        """将数据打包成字节流，用于网络发送"""
        import struct
        # 使用网络字节序(大端)打包
        return struct.pack('!IIIII',
            self.seq_no,
            self.length,
            self.width,
            self.height,
            self.total_count
        )

    @staticmethod
    def unpack(data):
        """从字节流解包数据"""
        import struct
        values = struct.unpack('!IIIII', data)
        return DataStruct(
            seq_no=values[0],
            length=values[1],
            width=values[2],
            height=values[3],
            total_count=values[4]
        )

    def __str__(self):
        return f"序号:{self.seq_no} 长:{self.length} 宽:{self.width} 高:{self.height} 总数:{self.total_count}"



# UDP接收和发送的类
class UDPReceiverAndSender:
    def __init__(self, recv_port=2000, send_port=4000):
        # 接收端初始化
        self.recv_port = recv_port
        # self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.recv_sock.bind(('', recv_port))
        self.running = True

        # 发送端初始化
        self.send_port = send_port
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def start_receive(self):
        """启动接收线程"""
        self.recv_thread = threading.Thread(target=self.receive_messages)
        self.recv_thread.start()

    def receive_messages(self):
        """接收消息的循环"""
        print(f"开始监听端口 {self.recv_port}")
        while self.running:
            try:
                data, addr = self.recv_sock.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"收到来自 {addr}: {message}")
            except Exception as e:
                print(f"接收错误: {e}")

    def send_message(self, message, ip="127.0.0.1"):
        """发送消息"""
        try:
            self.send_sock.sendto(message.encode('utf-8'), (ip, self.send_port))
            print(f"已发送: {message} {self.send_port}")
        except Exception as e:
            print(f"发送错误: {e}")

    def send_data(self, message, ip="127.0.0.1"):
        """发送消息"""
        try:
            self.send_sock.sendto(message.encode('utf-8'), (ip, self.send_port))
            print(f"已发送: {message}")
        except Exception as e:
            print(f"发送错误: {e}")

    def send_data(self, packed_data, ip="127.0.0.1"):
        """发送打包后的结构体数据"""
        try:
            # 直接发送packed_data，不需要encode因为已经是字节流
            self.send_sock.sendto(packed_data, (ip, self.send_port))
            print(f"已发送数据包，大小: {len(packed_data)}字节 {self.send_port}")
        except Exception as e:
            print(f"发送错误: {e}")


    def stop(self):
        """停止接收"""
        self.running = False
        self.recv_sock.close()
        self.send_sock.close()


import json
import time
from dataclasses import dataclass
from datetime import datetime
@dataclass
class Position:
    x: float
    y: float

@dataclass
class ShipData:
    ship_name: str
    position: Position
    status: str
    timestamp: str

    def to_json(self):
        return {
            "ship_name": self.ship_name,
            "position": {
                "x": self.position.x,
                "y": self.position.y
            },
            "status": self.status,
            "timestamp": self.timestamp
        }

    def pack(self):
        return json.dumps(self.to_json()).encode('utf-8')

# 创建数据
def create_ship_data():
    return ShipData(
        ship_name="远宁998",
        position=Position(x=150, y=100),
        status="正常",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


# 使用示例
if __name__ == "__main__":
    # 创建实例
    udp = UDPReceiverAndSender(recv_port=2000, send_port=40001)

    # # 启动接收线程
    # udp.start_receive()

    # 创建数据
    # data = DataStruct(
    #     seq_no=1,
    #     length=100,
    #     width=50,
    #     height=30,
    #     total_count=10
    # )
    # packed_data = data.pack()
    # 创建新的数据实例
    data = create_ship_data()

    try:
        # 主循环发送消息
        while True:
            data.position.x = data.position.x + 1
            # 打印修改后的数据
            print(data.to_json())
            packed_data = data.pack()
            udp.send_data(packed_data)

            # msg = input("输入要发送的消息(输入q退出): ")
            # if msg.lower() == 'q':
            #     break
            # udp.send_message(msg)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n程序终止")
    finally:
        udp.stop()