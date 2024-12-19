import cv2
import numpy as np
import datetime
import os
import time
import argparse
import warnings
import time
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")
warnings.warn("deprecated", DeprecationWarning)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
#os.chdir(os.path.dirname(__file__))
def detect_and_track_ship(yoloModel, video_path, UseFile = False):

    parser = argparse.ArgumentParser(description="abc")

    # 添加两个位置参数
    parser.add_argument('-i','--ip', type=int, default=113, help='第一个')
    parser.add_argument('-s','--save_interval', type=int, default=50, help='第二个')

    # 解析命令行参数
    args = parser.parse_args()

    Ip_num = args.ip
    device = 'cuda'
    print(f'Using device: {device}')
    cap = []
    if UseFile :
        cap = cv2.VideoCapture(video_path) #
        # cap.set(cv2.CAP_PROP_POS_FRAMES, 20*25)
    else:
        rtsp_url = f"rtsp://admin:hkhk_11O@192.168.110.165"

        cap = cv2.VideoCapture(rtsp_url)
        print(rtsp_url)

    if not cap.isOpened():
        print("Unable to open video files!")
        return

    idx = 0
    frame_interval = 2

    idx2 = 0
    save_interval = args.save_interval

    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (1024, 768))
            cv2.imshow(f"Frame_75", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # time.sleep(0.01)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = "./100.mp4"
    modelpath = "./best.pt"
    detect_and_track_ship(modelpath, video_path, False) # True usefile