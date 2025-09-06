# ----- camera_sender.py -----
import cv2
import time
import socket
from ultralytics import YOLO

# ===== 설정 =====
MODEL_PATH = "runs/detect/custom_model2/weights/best.pt"   # 학습 모델 경로
CONF_THRES = 0.7
CAM_INDEX = 0

# Pygame 맵 크기 (test.py와 동일해야 함)
ROWS, COLS = 35, 70
BOARD_W, BOARD_H = 1400, 700   # 카메라 프레임을 맞출 가상의 보드 크기

# UDP 설정
UDP_HOST = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ===== 모델 / 카메라 로드 =====
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("카메라를 열 수 없습니다.")

print("[INFO] 카메라 시작. 'q' 누르면 종료.")

last_cell = None
last_change_t = 0
DWELL_SEC = 0.2   # 좌표 안정화 시간 (초)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    # YOLO 감지
    results = model.predict(source=frame, conf=CONF_THRES, verbose=False)
    boxes = results[0].boxes
    if boxes is not None and len(boxes) > 0:
        # 가장 확률 높은 객체 선택
        best = boxes[boxes.conf.argmax().item()]

        x1, y1, x2, y2 = map(int, best.xyxy[0])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # 화면 → 격자 변환
        h, w, _ = frame.shape
        gx = int(cx / w * COLS)
        gy = int(cy / h * ROWS)
        candidate_cell = (gy, gx)

        # 좌표 안정화 + 전송
        now = time.time()
        if candidate_cell != last_cell and now - last_change_t > DWELL_SEC:
            rr, cc = candidate_cell  # row, col
            msg = f"CELL {rr} {cc}".encode("utf-8")
            sock.sendto(msg, (UDP_HOST, UDP_PORT))
            print(f"[SEND] CELL {rr} {cc}")
            last_cell = candidate_cell
            last_change_t = now

        # 디버그 표시
        annotated = results[0].plot()
        cv2.circle(annotated, (cx, cy), 5, (0, 255, 0), -1)
        cv2.putText(annotated, f"CELL {gy},{gx}", (cx+10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        annotated = frame

    cv2.imshow("Camera Sender", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
