import cv2
cap = cv2.VideoCapture('./img/划痕导演剪辑版 3 版/../../划痕导演剪辑版 3 版.mov')
# 或者直接用绝对路径
cap = cv2.VideoCapture('/Users/harry/划痕导演剪辑版 3 版.mov')

# 尝试读取帧 34
cap.set(cv2.CAP_PROP_POS_FRAMES, 34)
ret, img = cap.read()

print(f'读取帧 34: ret={ret}, img shape={img.shape if img is not None else None}')

# 顺便测试帧 0 和帧 138
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
ret0, img0 = cap.read()
print(f'读取帧 0: ret={ret0}, img shape={img0.shape if img0 is not None else None}')

cap.set(cv2.CAP_PROP_POS_FRAMES, 138)
ret138, img138 = cap.read()
print(f'读取帧 138: ret={ret138}, img shape={img138.shape if img138 is not None else None}')

cap.release()