import cv2

# 打开摄像头
cap = cv2.VideoCapture(1)

while True:
    # 读取一帧
    ret, frame = cap.read()
   
    # 显示图像
    cv2.imshow('Camera', frame)
   
    # 按'q'退出pyth


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()