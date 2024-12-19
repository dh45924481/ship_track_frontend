# coding=utf-8
from HCNetSDK import *
from PlayCtrl import *
from ctypes import create_string_buffer, cast, POINTER, string_at, Structure

import cv2
import torch
from paddleocr import PaddleOCR, draw_ocr
from ultralytics import YOLO
import numpy as np
import supervision as sv
from supervision.draw.color import Color
from datetime import datetime
import os
import time
import argparse
from PIL import Image, ImageDraw, ImageFont
import re
import Levenshtein
import socket
import logging

import pymysql
import pymysql.cursors

SAVE_PATH = r'D:\Project\ship_data240'
SAVE_PATH_BAK = r'D:\Project\ship_data240\bak'

def connect_to_database():
    # 连接数据库
    connection = pymysql.connect(
        host='192.168.168.104',
        user='root',
        password='123456',
        database='jiance',
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        # charset='utf8mb4',
    )
    return connection

# tbl_boat_result
def insert_into_database(connection, timestamp, direction, name, pic1, pic2, pic3, pic4, pic5):
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO tbl_boat_result_240 (create_time, direction, name, pic1, pic2, pic3, pic4, pic5)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (timestamp, direction, name, pic1, pic2, pic3, pic4, pic5))
        connection.commit()
    except Exception as e:
        print(f"Error inserting data: {e}")

# Hycz147258.
import warnings
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")
warnings.warn("deprecated", DeprecationWarning)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.chdir(os.path.dirname(__file__))
logging.getLogger('paddleocr').setLevel(logging.WARNING)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logging.getLogger().setLevel(logging.WARNING)  # 设置全局日志级别
logging.getLogger('ppocr').setLevel(logging.WARNING)  # 设置特定于 PaddleOCR 的日志级别

import threading
import shutil

class UDPReceiver:
    def __init__(self, port=7000):
        self.port = port
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.setblocking(False)
        self.sock.bind((self.ip, self.port))

    def start(self):
        receiver_thread = threading.Thread(target=self.receive_messages)
        receiver_thread.start()

    def receive_messages(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.port))
        print(f"Server is listening for UDP messages from clients on port {self.port}")
        while self.running:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Received message from client {addr}: {message}")
            # Here you can process the received message as needed
        sock.close()

class UDPSender:
    def __init__(self, ip="255.255.255.255", port=8000):
        self.ip = ip
        self.port = port

    def send_message(self, message: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # 发送两次消息
        for _ in range(2):
            sock.sendto(message.encode('utf-8'), (self.ip, self.port))
            time.sleep(0.1)

        sock.close()

def get_maxid(folder_path):
    curr_id = 0
    latest_date = None

    for filename in os.listdir(folder_path):
        # 匹配ID和日期
        match = re.search(r'ID(\d+)_(\d{4}-\d{2}-\d{2})', filename)
        if match:
            id_num = int(match.group(1))
            date_str = match.group(2)
            curr_date = datetime.strptime(date_str, '%Y-%m-%d')

            # 如果是第一个文件或找到更新的日期
            if latest_date is None or curr_date > latest_date:
                latest_date = curr_date
                curr_id = id_num
            # 如果是同一天的文件，比较ID大小
            elif curr_date == latest_date:
                curr_id = max(curr_id, id_num)

    return curr_id

def savepic(frame, Ip_num, ObjectID, f=None):
    # current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3]
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    # frame_filename = os.path.join(r'../ship_data', f'{ObjectID}_{current_time}_{Ip_num}.jpg')
    frame_filename = os.path.join(SAVE_PATH, f'{ObjectID}_{current_time}_{Ip_num}.jpg')
    cv2.imwrite(frame_filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if f:
        print(frame_filename, file=f)
    else:
        print(frame_filename)

def is_polygon_inside_box(polygon, x1, y1, x2, y2):
    """
    检查多边形是否完全位于给定的矩形框内。

    :param polygon: 多边形顶点列表，例如 [[x1, y1], [x2, y2], ...]
    :param x1: 矩形框的左上角x坐标
    :param y1: 矩形框的左上角y坐标
    :param x2: 矩形框的右下角x坐标
    :param y2: 矩形框的右下角y坐标
    :return: 如果多边形完全在矩形框内，返回True；否则，返回False
    """
    for point in polygon:
        x, y = point
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            return False
    return True

# 定义绘制中文文本的函数
def draw_chinese_text(frame, text, position, font_path="SimHei.ttf", font_size=30, color=(0, 0, 255)):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size)
    color_rgb = (color[2], color[1], color[0])
    draw.text(position, text, font=font, fill=color_rgb)
    frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return frame


from typing import List, Tuple
def load_ship_names(file_path: str) -> List[str]:
    """
    从文件中加载船名列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 去除每行末尾的换行符并过滤掉空行
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"读取船名文件出错: {e}")
        return []
# 在程序启动时加载船名列表
SHIP_NAMES = load_ship_names('shipname.txt')


def count_chars(text: str) -> tuple:
    # 统计字符串的中文，数字，字母个数
    # text = "长江2510AB"
    # cn, num, en = count_chars(text)
    # print(f"汉字:{cn}, 数字:{num}, 字母:{en}")  # 汉字:2, 数字:4, 字母:2
    cn = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    num = sum(c.isdigit() for c in text)
    en = sum(c.isalpha() and c.isascii() for c in text)
    return cn, num, en

def filter_letters(text: str) -> str:
    # 过滤掉字符串中的英文字母
    result = ''
    for c in text:
        if c.isascii() and c.isalpha():  # 是英文字母就跳过
            continue
        result += c
    return result

def find_best_match(text: str, ship_names: List[str], threshold: float = 0.625) -> Tuple[str, float]:
    """
    使用Levenshtein距离找出最匹配的船名
    Args:
        text: 待匹配的文本
        ship_names: 船名列表
        threshold: 相似度阈值
    Returns:
        最匹配的船名和相似度
    """
    # 存储当前找到的最佳匹配船名，初始值为 None
    best_match = None
    # 存储当前找到的最佳匹配相似度，初始值为 0.0
    highest_ratio = 0

    for ship_name in ship_names:
        # 使用Levenshtein.ratio()计算相似度
        # ratio = Levenshtein.ratio(text, ship_name)
        # 计算待匹配文本 text 与当前船名之间的 Levenshtein 距离。
        distance = Levenshtein.distance(text, ship_name)
        if distance == 0:
            # 完全匹配，提前终止
            best_match = ship_name
            highest_ratio = 1
            break
        # max_len：取待匹配文本和当前船名的最大长度
        max_len = max(len(text), len(ship_name))


        ratio = 1.0 if max_len == 0 else 1 - (distance / max_len)
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = ship_name

    if highest_ratio >= threshold:
        return best_match, highest_ratio
    return None, 0.0


def post_process_ship_name(ocr_result, threshold: float = 0.625):
    """
    对OCR识别结果进行后处理
    """
    if not ocr_result:
        return None

    # 常见的省份前缀
    province_prefixes = ['苏', '皖', '鲁', '豫', '浙', '赣']

    # 常见的类型后缀
    type_suffixes = ['货', '机', '驳', '拖', '油']

    # 数字模式
    number_pattern = r'\d+'
     # 添加字符映射
    char_map = {
        '办': '苏', '准': '淮', '线': '货', '菜': '货', '汪': '江', '茶': '苏',
        '篮': '货', '!': '1', '！': '1', 'I': '1', 'l': '1', 'i': '1',
        'Q': '0', 'o': '0', 'O': '0', 'D': '0', 'c': '0', 'C': '0',
        'E': '3', 'P': '9', 'p': '9', 'q': '9', 'a': '0', 'A': '4',
        'S': '5', 's': '5', 'g': '9', 'Z': '2', 'z': '2', 'b': '6',
        'G': '6', 'B': '8', '贷': '货', '莎': '苏', '劳': '苏', '花': '苏', '洞': '润','黎':'集',
    }

    char_del = '#'

    processed_results = []
    for line in ocr_result:
        polygon, (text, conf) = line

        # 置信度过滤
        if conf < threshold:
            continue

        if not any('\u4e00' <= char <= '\u9fa5' for char in text):
            continue

        # 过滤掉明显不是船名的文本
        # if any(x in text for x in ['Camera', 'ID:', '2024-', '11月', '星期', ':', '.']):  # '月', '日',
        if any(x in text for x in ['Camera', '-', '2024-', '11-', ':']):  # '月', '日',
            continue

         # 对文本进行字符替换
        corrected_text = ''
        for char in text:
            corrected_text += char_map.get(char, char)
        text = corrected_text

        # 基本规则检查
        if len(text) >= 3:  # 船名通常大于4个字符
            if text[0].isdigit() and text[1].isdigit() and '\u4e00' <= text[-1] <= '\u9fff':
                text = text[::-1]

            best_match, ratio = find_best_match(text, SHIP_NAMES)
            if best_match:
                processed_results.append((polygon, (best_match, conf * ratio)))
                continue

    # 如果有多个结果，选择置信度最高的
    if processed_results:
        processed_results.sort(key=lambda x: x[1][1], reverse=True)
        return processed_results[0]
    return None

def process_ship_images(image_paths: List[str], ocr, f2) -> str:
    """
    Process a list of images to recognize the ship name.  如果最后没有达到识别门限，就用所有的识别字符拼接后再比对，
    Args:
        image_paths: List of image file paths.
        ocr: Initialized PaddleOCR instance
    Returns:
        The most probable ship name with the highest accumulated confidence.
    """
    ship_name_confidences = {}  # Dictionary to store ship names and their cumulative confidences
    rec_results = []
    for img_path in image_paths:
        # Perform OCR on the image
        # result = ocr.ocr(img_path, det=True, cls=True)
        print('\n', img_path, 40*'*', file=f2)
        frame = cv2.imread(img_path)
        if frame is None:
            continue

        # Perform OCR
        # det=>True 表示启用文本检测, cls->True 表示 启用文本方向
        result = ocr.ocr(frame, det=True, cls=True)
        prlt_temp = ''
        if result is not None:
            for idx in range(len(result)):
                res = result[idx]
                if res is not None:
                    continue
                # Apply post-processing to each result
                print(res, file=f2)
                processed_result = post_process_ship_name(res)
                if processed_result:
                    # Unpack the processed result
                    polygon, (text, conf) = processed_result
                    text = str(text)  # Ensure text is string for dict key
                    prlt_temp = img_path, (text, conf)
                    print(text, conf, file=f2)

                    # Accumulate confidences
                    if text in ship_name_confidences:
                        ship_name_confidences[text] += float(conf)
                    else:
                        ship_name_confidences[text] = float(conf)

                    # Draw detection box and text
                    polygon = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(frame, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)

                    # Calculate text position and draw
                    text_position = (int(polygon[0][0][0]), int(polygon[0][0][1]) - 70)
                    frame = draw_chinese_text(frame, text, text_position,
                                            font_path="./simsun.ttc", font_size=50,
                                            color=(255, 255, 255))

        # Save processed image
        file_name = os.path.splitext(img_path)[0]
        new_file_path = f"{file_name}_7777.jpg"
        new_file_path = new_file_path.replace(SAVE_PATH, SAVE_PATH_BAK)
        cv2.imwrite(new_file_path, frame)
        if prlt_temp =='':
            prlt_temp = img_path, (0, 0)
        rec_results.append(prlt_temp)

    if ship_name_confidences:
        # Sort and return most probable ship name
        sorted_ship_names = sorted(ship_name_confidences.items(),
                                 key=lambda x: x[1], reverse=True)
        return sorted_ship_names[0][0], rec_results

    return None, rec_results

def process_files(folder_path,yolomodel, ocr,):
    # bak_folder = os.path.join(folder_path, 'bak')
    # 收集并按ID分组
    id_files = {}
    for f in sorted(os.listdir(folder_path)):
        if f.startswith('ID') and os.path.isfile(os.path.join(folder_path, f)):
            try:
                id_num = int(f[2:5])  # 提取ID数字
                if id_num not in id_files:
                    id_files[id_num] = []
                id_files[id_num].append(f)
            except:
                continue

    if not id_files:
        return

    # 获取排序后的ID列表
    ids = sorted(id_files.keys())

    today = datetime.now().strftime('%Y-%m-%d')
    f2 = open(today+"_reg4.txt",'a',encoding='utf-8')
    print("\n\n",100*'*', file=f2)
    connection = connect_to_database()

    # # 检查最大ID的文件组是否超时
    # if len(ids) > 0:
    #     id_num = ids[-1]
    #     files = id_files[id_num]
    #     newest_time = max(os.path.getmtime(os.path.join(folder_path, f)) for f in files)

    #     if time.time() - newest_time > 120:  # 2分钟超时
    #         process_ids = ids  # 超时处理所有ID
    #     else:
    #         process_ids = ids[:-1]  # 未超时处理除最新ID外的所有ID

    process_ids = ids

    for id_num in process_ids:
        files = id_files[id_num]
        print(f"处理ID{id_num}的文件: ",70*'*')
        print(f"处理ID{id_num}的文件: ",70*'*',file=f2)

        # 构建完整的图片路径列表
        image_paths = [os.path.join(folder_path, f) for f in files]

        # 调用OCR处理
        ship_name, rec_results = process_ship_images(image_paths, ocr, f2)
        print(f"识别到的船名ID:{id_num:03}: {ship_name}",)
        print(f"识别到的船名ID:{id_num:03}: {ship_name}", file=f2)
        print("\n\n",100*'*', file=f2)
        f2.flush()
        try :
            if len(rec_results) <= 5:
                pass
            else:
                # 1. 按照置信度conf降序排序,取前5个
                sorted_by_conf = sorted(rec_results, key=lambda x: x[1][1], reverse=True)[:5]
                # 2. 对前5个按照图片路径名称排序
                rec_results = sorted(sorted_by_conf, key=lambda x: x[0])
            smb_path = "/run/user/1000/gvfs/smb-share:server=192.168.168.104,share=sharedfolder/upload/ship"
            file_idx = 0
            for file, (text, conf) in rec_results: #for file in image_paths:
                # 获取文件名
                filename = os.path.basename(file)
                # 目标文件路径
                target_path = os.path.join(smb_path, filename)
                # target_path = os.path.join('/home/hys/桌面/tmp', filename)
                try:
                    # 复制文件到 Samba 共享
                    if file_idx == 5:
                        break
                    file_idx = file_idx + 1
                    shutil.copy(file, target_path)
                    print(f"Copied: {filename}")
                except Exception as e:
                    print(f"Failed to copy {filename}: {e}")

            frame = cv2.imread(image_paths[0])
            width = frame.shape[1]
            # results = yolomodel.track(frame, persist=True, verbose=False)
            results = yolomodel.predict(frame)
            detections = sv.Detections.from_ultralytics(results[0])
            position = 0
            for detection in detections:
                x1, y1, x2, y2 = map(int, detection[0])
                position = 0 if (x1 + x2)/2 > width/2 else 1
                print(f"ID: {detection[4]}, Position: {position}")

            # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%fc")[:-3]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # direction = 1
            name =  ship_name
            while len(files) < 5:
                files.append('')
            insert_into_database(connection, timestamp, position, name, files[0], files[1], files[2], files[3], files[4])

            # 移动文件到bak文件夹
            for f in image_paths:
                dst = f.replace(SAVE_PATH, SAVE_PATH_BAK)
                shutil.move(f, dst)

            # 发送船名
            # if ship_name:
                # udp_sender.send_message(ship_name)
        except Exception as e:
            print(f"错误: {e}")


def start_monitor(folder_path):

    yolomodel = YOLO(modelpath).to(device)
    logger.debug("Initializing PaddleOCR...")
    ocr4model = PaddleOCR(
        det_model_dir='./inference/ch_PP-OCRv4_det_server_infer/',
        # rec_model_dir='./inference/ch_PP-OCRv4_rec_infer/',
        rec_model_dir='./inference/ch_PP-OCRv4_rec_server_infer/',  # ok
        use_angle_cls=True,
        lang='ch',
        # use_gpu=False
    )
    logger.debug("PaddleOCR initialized successfully.")

    def test_ocr(image_path):
        logger.debug(f"Processing image: {image_path}")
        result1 = ocr4model.ocr(image_path, det=True, cls=True)
        logger.debug(f"OCR result: {result}")
        return result1

    # 初始化UDP发送器
    # udp_sender = UDPSender(ip="255.255.255.255", port=8000)

    while True:
        try:
            process_files(folder_path,yolomodel,ocr4model)
            time.sleep(10)
        except Exception as e:
            print(f"错误: {e}")

def detect_and_track_ship(model, ocr4model, video_path, UseFile = False):
    parser = argparse.ArgumentParser(description="abc")

    # 添加两个位置参数
    parser.add_argument('-i','--ip', type=int, default=239, help='')
    parser.add_argument('-s','--save_interval', type=int, default=60, help='')
    args = parser.parse_args()
    Ip_num = args.ip

    # curr_id = get_maxid('../ship_data/') + 1
    curr_id = get_maxid(SAVE_PATH)
    cap = []
    if UseFile :
        cap = cv2.VideoCapture(video_path) #
        # cap.set(cv2.CAP_PROP_POS_FRAMES, 20*25)
    else:
        rtsp_url = f"rtsp://admin:hkhk_119@192.168.168.{Ip_num}"
        # if Ip_num == 113:
        #     rtsp_url = "rtsp://admin:hycz147258@192.168.168.113/Streaming/Channels/103"

        cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Unable to open video files!")
        return

    today = datetime.now().strftime('%Y-%m-%d')
    f = open(today+"log.txt",'a',encoding='utf-8')
    print("\n\n",100*'*', file=f)

    idx = 0
    frame_interval = 2
    idx_frame = 0

    idx2 = 0
    save_interval = args.save_interval
    save_interval = 30
    while True:
        ret, frame = cap.read()
        # ret = 1
        # frame = cv2.imread('../ship_data/2024-10-20-21-04-58.395_112.jpg')
        idx = (idx + 1) % frame_interval
        if not ret:
            print("*********ret is none!**********")
            if UseFile :
                cap = cv2.VideoCapture(video_path) #
            else:
                cap = cv2.VideoCapture(rtsp_url)
            continue #break

        if idx != 1:
            continue

        idx2 = (idx2 + 1) % save_interval
        idx_frame = (idx_frame + 1) % 60
        LINE_X = frame.shape[1]/2

        object_id_last = 0

        try:
            # cv2.line(frame, (LINE_X, 0), (LINE_X,frame.shape[0]), (0, 255, 0), 2)
            # frame = cv2.resize(frame, (1024, 768))
            results = model.track(frame, persist=True, verbose=False)
            # results = model.predict(frame, conf=0.5, device=device, verbose=False)

            detections = sv.Detections.from_ultralytics(results[0])
            for detection in detections:
                x1, y1, x2, y2 = map(int, detection[0])  # 使用索引 0 获取坐标
                # if (y1 + y2) / 2 < 300:
                #     continue
                confidence = float(detection[2])  # 使用索引 2 获取置信度
                class_id = int(detection[3])  # 使用索引 3 获取类别 ID
                object_id = detection[4] if detection[4] is not None else '-1'  # 使用索引 4 获取ID（若存在）
                class_name = detection[5].get('class_name', '')  # 使用索引 5 获取类别名称

                # 计算中心点
                # center_x = (x1 + x2) / 2
                # # 检查是否在检测线附近
                # if abs(center_x - LINE_X) < 50:
                #     # 只在首次进入检测区域时判断方向
                #     if server_id not in first_positions:
                #         # 根据首次进入时的位置判断方向
                #         direction = "Entering" if center_y < LINE_Y else direction = "Leaving"
                #         first_positions[server_id] = direction

                # if object_id != object_id_last:
                #     process_files(SAVE_PATH,yolomodel,ocr4model)

                if (class_id == 0 or class_id == 1) and idx2 == 0:
                    label = f"ID{object_id+curr_id:03}"
                    savepic(frame, f'{Ip_num}_666', label)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (240, 150, 60), 2)
                    cv2.putText(frame, label, (x2 - 80, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 240, 200), 2)

                    # 调用抓图，抓一幅图片，
                    # dev.manual_snap(Ip_num, label)

                    # if class_id == 0 and idx2 == 0:
                    result = ocr4model.ocr(frame, det=True, cls=True)
                    print(50*'*', file=f)
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    print(current_time, file=f)

                    if result is None:
                        print("OCR 结果为 None。")
                    else:
                        for idx in range(len(result)):
                            res = result[idx]
                            if res is not None:
                                # 应用后处理
                                processed_result = post_process_ship_name(res)

                                if processed_result:
                                    polygon, (text, conf) = processed_result
                                    print(text, file=f)
                                    # 绘制检测框和文本的代码
                                    polygon = np.array(polygon, dtype=np.int32)
                                    if is_polygon_inside_box(polygon, x1, y1, x2, y2):
                                        polygon = polygon.reshape((-1, 1, 2))
                                        cv2.polylines(frame, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)
                                        text_position = (int(polygon[0][0][0]), int(polygon[0][0][1]) - 70)
                                        frame = draw_chinese_text(frame, text, text_position, font_path="./simsun.ttc", font_size=50, color=(255, 255, 255))
                        # savepic(frame, Ip_num, label,f)
                        frame = cv2.resize(frame, (1024, 768))
                        cv2.imshow(f"Frame_{Ip_num}", frame)

            f.flush()
            if idx_frame == 0 :
                frame = cv2.resize(frame, (1024, 768))
                cv2.imshow(f"Frame_{Ip_num}", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    cap.release()
    f.close()
    cv2.destroyAllWindows()
def ShowOcrRlt(ocr, img_path, det=True):
    result = ocr.ocr(img_path, det=det, cls=True)
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line)



class NET_DVR_JPEGPARA(Structure):
    _fields_ = [
        ("wPicSize", c_ushort),
        ("wPicQuality", c_ushort)
    ]

class devClass:
    def __init__(self):
        self.hikSDK, self.playM4SDK = self.LoadSDK()
        self.iUserID = -1
        self.alarmHandle = -1
        self.msg_callback_func = MSGCallBack_V31(self.g_fMessageCallBack_Alarm)

    def LoadSDK(self):
        hikSDK = None
        playM4SDK = None
        try:
            print("netsdkdllpath: ", netsdkdllpath)
            hikSDK = load_library(netsdkdllpath)
            playM4SDK = load_library(playM4dllpath)
        except OSError as e:
            print('动态库加载失败', e)
        return hikSDK, playM4SDK

    def g_fMessageCallBack_Alarm(self, lCommand, pAlarmer, pAlarmInfo, dwBufLen, pUser):
        if lCommand == ALARM_LCOMMAND_ENUM.COMM_UPLOAD_FACESNAP_RESULT.value:
            struFaceSnap = cast(pAlarmInfo, LPNET_VCA_FACESNAP_RESULT).contents

            # 事件时间
            dwYear = (struFaceSnap.dwAbsTime >> 26) + 2000
            dwMonth = (struFaceSnap.dwAbsTime >> 22) & 15
            dwDay = (struFaceSnap.dwAbsTime >> 17) & 31
            dwHour = (struFaceSnap.dwAbsTime >> 12) & 31
            dwMinute = (struFaceSnap.dwAbsTime >> 6) & 63
            dwSecond = (struFaceSnap.dwAbsTime >> 0) & 63
            strAbsTime = f"{dwYear}_{dwMonth}_{dwDay}_{dwHour}_{dwMinute}_{dwSecond}"

            # 获取当前时间戳
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

            if struFaceSnap.dwFacePicLen > 0:
                buff1 = string_at(struFaceSnap.pBuffer1, struFaceSnap.dwFacePicLen)
                filepath = f'./pic/face_{timestamp}.jpg'
                with open(filepath, 'wb') as fp:
                    fp.write(buff1)
                print(f"已保存抓拍图像: {filepath}")

            if struFaceSnap.dwBackgroundPicLen > 0:
                buff2 = string_at(struFaceSnap.pBuffer2, struFaceSnap.dwBackgroundPicLen)
                filepath = f'./pic/background_{timestamp}.jpg'
                with open(filepath, 'wb') as fp:
                    fp.write(buff2)
                print(f"已保存背景图像: {filepath}")
        return True

    def SetSDKInitCfg(self):
        if sys_platform == 'windows':
            basePath = os.getcwd().encode('gbk')
            strPath = basePath + b'\lib'
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            print('strPath: ', strPath)
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value,
                                                 byref(sdk_ComPath)):
                print('NET_DVR_SetSDKInitCfg: 2 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                                 create_string_buffer(strPath + b'\libcrypto-1_1-x64.dll')):
                print('NET_DVR_SetSDKInitCfg: 3 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                                 create_string_buffer(strPath + b'\libssl-1_1-x64.dll')):
                print('NET_DVR_SetSDKInitCfg: 4 Succ')
        else:
            strPath = os.getcwd().encode('utf-8') + b'\lib'
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value,
                                                 byref(sdk_ComPath)):
                print('NET_DVR_SetSDKInitCfg: 2 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                                 create_string_buffer(strPath + b'/libcrypto.so.1.1')):
                print('NET_DVR_SetSDKInitCfg: 3 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                                 create_string_buffer(strPath + b'/libssl.so.1.1')):
                print('NET_DVR_SetSDKInitCfg: 4 Succ')

    def GeneralSetting(self):
        # 设置日志
        self.hikSDK.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)

        # 注册回调函数
        self.hikSDK.NET_DVR_SetDVRMessageCallBack_V31(self.msg_callback_func, None)
        # 设置抓图参数
        jpegPara = NET_DVR_JPEGPARA()
        jpegPara.wPicSize = 0xff  # 使用当前码流分辨率s
        jpegPara.wPicQuality = 0  # 图片质量最好

        if not self.hikSDK.NET_DVR_SetDVRConfig(
            self.iUserID,
            3013,  # NET_DVR_SET_JPEGPARA的值
            1,  # 通道号
            byref(jpegPara),
            sizeof(jpegPara)
        ):
            print(f"设置抓图参数失败, 错误码: {self.hikSDK.NET_DVR_GetLastError()}")

    def LoginDev(self, ip, username, pwd):
        struLoginInfo = NET_DVR_USER_LOGIN_INFO()
        struLoginInfo.bUseAsynLogin = 0
        struLoginInfo.sDeviceAddress = ip
        struLoginInfo.wPort = 8000
        struLoginInfo.sUserName = username
        struLoginInfo.sPassword = pwd
        struLoginInfo.byLoginMode = 0

        struDeviceInfoV40 = NET_DVR_DEVICEINFO_V40()

        self.iUserID = self.hikSDK.NET_DVR_Login_V40(byref(struLoginInfo), byref(struDeviceInfoV40))
        if self.iUserID < 0:
            print("Login failed, error code: %d" % self.hikSDK.NET_DVR_GetLastError())
            self.hikSDK.NET_DVR_Cleanup()
        else:
            print('登录成功，设备序列号：%s' % str(struDeviceInfoV40.struDeviceV30.sSerialNumber, encoding="utf8").rstrip('\x00'))

    def SetupAlarm(self):
        struAlarmParam = NET_DVR_SETUPALARM_PARAM()
        struAlarmParam.dwSize = sizeof(NET_DVR_SETUPALARM_PARAM)
        struAlarmParam.byLevel = 1  # 布防优先级：0- 一等级（高），1- 二等级（中），2- 三等级（低）
        struAlarmParam.byAlarmInfoType = 1  # 智能交通报警信息上传类型：0- 老报警信息，1- 新报警信息
        struAlarmParam.byDeployType = 1  # 布防类型：0-客户端布防，1-实时布防

        self.alarmHandle = self.hikSDK.NET_DVR_SetupAlarmChan_V41(self.iUserID, byref(struAlarmParam))
        if self.alarmHandle < 0:
            print(f"布防失败, 错误码: {self.hikSDK.NET_DVR_GetLastError()}")
        else:
            print("布防成功")



    def manual_snap(self, Ip_num, ObjectID, f=None):
        """手动触发一次抓图"""
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3]
        # frame_filename = os.path.join(r'../ship_data', f'{ObjectID}_{current_time}_{Ip_num}.jpg')
        #filename = f'./pic/manual_snap_{timestamp}.jpg'
        filename = os.path.join(SAVE_PATH, f'{ObjectID}_{timestamp}_{Ip_num}_catch.jpg')

        # 抓图
        if not self.hikSDK.NET_DVR_CaptureJPEGPicture(
            self.iUserID,
            1,  # 通道号
            byref(NET_DVR_JPEGPARA()),
            filename.encode()
        ):
            print(f"抓图失败, 错误码: {self.hikSDK.NET_DVR_GetLastError()}")
        else:
            print(f"抓图成功：{filename}")

    def StopAlarm(self):
        if self.alarmHandle > -1:
            self.hikSDK.NET_DVR_CloseAlarmChan_V30(self.alarmHandle)
            print("布防已停止")

    def LogoutDev(self):
        if self.iUserID > -1:
            self.hikSDK.NET_DVR_Logout(self.iUserID)
            print("设备已登出")


if __name__ == "__main__":

    if not os.path.exists('./SdkLog_Python'):
        os.makedirs('./SdkLog_Python')


    bak_folder = os.path.join(SAVE_PATH, 'bak')
    if not os.path.exists(bak_folder):
        os.makedirs(bak_folder)

    # dev = devClass()
    # dev.SetSDKInitCfg()
    # dev.hikSDK.NET_DVR_Init()
    # dev.GeneralSetting()
    # dev.LoginDev(ip=b'192.168.168.240', username=b"admin", pwd=b"hkhk_11O")
    # dev.SetupAlarm()


    video_path = "./test113.mp4"
    modelpath = "./best_boat13.pt"

    device = 'cuda' if torch.cuda.is_available() else 'cpu'  #device = 'cuda' #
    print(f'Using device: {device}')

    yolomodel = YOLO(modelpath).to(device)
    ocr4model = PaddleOCR(
        det_model_dir='./inference/ch_PP-OCRv4_det_server_infer/',
        # rec_model_dir='./inference/ch_PP-OCRv4_rec_infer/',
        rec_model_dir='./inference/ch_PP-OCRv4_rec_server_infer/',  # ok
        use_angle_cls=True,
        lang='ch',
        # use_gpu=False
    )
    # folder_path = SAVE_PATH
    # monitor_thread = threading.Thread(target=start_monitor, args=(folder_path,))
    # monitor_thread.daemon = True
    # monitor_thread.start()

    detect_and_track_ship(yolomodel, ocr4model, video_path, True) # True usefile
    # process_files('/home/hys/ship_data_bak/test/',yolomodel,ocr4model)




# # 使用示例
# if __name__ == "__main__":
#     folder_path = "your_folder_path"  # 替换为你的文件夹路径

#     monitor_thread = threading.Thread(target=start_monitor, args=(folder_path,))
#     monitor_thread.daemon = True
#     monitor_thread.start()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("程序退出")
