import cv2
import numpy as np
from ctypes import *
def get_camera():
    capl=cv2.VideoCapture(1)
    capr=cv2.VideoCapture(2)
    capl.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    capr.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    capl.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    capr.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    discard_frames = 10
    for _ in range(discard_frames):
        _, _ = capl.read(), capr.read()
        retl, framel = capl.read()
        retr, framer = capr.read()
    gamma = 1.5
    lut=np.array([((i/255.0)**gamma)*255 for i in np.arange(0,256)]).astype("uint8")
    framer=cv2.LUT(framer, lut)
    framel = cv2.LUT(framel, lut)
    ret_p=POINTER(c_bool)
    ret_p.contents=False
    ret_q=POINTER(c_bool)
    ret_q.contents=False
    return framel, framer, capl, capr, ret_p, ret_q

def release_camera(capl, capr):
    capl.release()
    capr.release()

def get_frame():
    capl=cv2.VideoCapture(1)
    capr=cv2.VideoCapture(2)
    capl.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    capr.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    capl.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    capr.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    retl, framel = capl.read()
    retr, framer = capr.read()
    # discard_frames = 10
    # for _ in range(discard_frames):
    #     _, _ = capl.read(), capr.read()
    #     retl, framel = capl.read()
    #     retr, framer = capr.read()
    # gamma = 1.5
    # lut=np.array([((i/255.0)**gamma)*255 for i in np.arange(0,256)]).astype("uint8")
    # framer=cv2.LUT(framer, lut)
    # framel = cv2.LUT(framel, lut)
    ret_p=POINTER(c_bool)
    ret_p.contents=False
    ret_q=POINTER(c_bool)
    ret_q.contents=False
    return framel, framer, capl, capr

# import cv2

# # 创建一个 VideoCapture 对象
# cap = cv2.VideoCapture(2)
# cap1=cv2.VideoCapture(1)

# # 使用循环来持续获取摄像头的帧
# while True:
#     # 读取一帧
#     ret, frame = cap.read()
#     ret1,frame1=cap1.read()

#     # 如果读取成功，显示这一帧
#     if ret and ret1:
#         cv2.imshow('Camera', frame)
#         cv2.imshow('Camera1',frame1)

#     # 如果按下 'q' 键，退出循环
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # 释放 VideoCapture 对象
# cap.release()

# # 关闭所有 OpenCV 窗口
# cv2.destroyAllWindows()

# import cv2

# # 创建一个 VideoCapture 对象
# cap = cv2.VideoCapture(1)

# # 使用循环来持续获取摄像头的帧
# while True:
#     # 读取一帧
#     ret, frame = cap.read()

#     # 如果读取成功，显示这一帧
#     if ret:
#         cv2.imshow('Camera', frame)

#     # 如果按下 'q' 键，退出循环
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # 释放 VideoCapture 对象
# cap.release()

# # 关闭所有 OpenCV 窗口
# cv2.destroyAllWindows()