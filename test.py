# ----- test.py (완성본) -----
import sys, pygame, socket
from function import *  # DStarLite, draw_all, build_blocked_with_presets, choose_best_goal, spread_fire, cell_at_pos, inb

# ===== 기본 설정 =====
CELL = 22
ROWS = 35
COLS = 70
MARGIN = 1
FPS = 60
STEP_INTERVAL = 0.3
PLANNER_STEPS_PER_FRAME = 10000
REPLAN_CHECK_INTERVAL = 0.5
REPLAN_PERIODIC_CHECK = 1.0
FIRE_STEP_INTERVAL = 1.0
AUTO_MOVE = False  # 자동계획 때 에이전트가 스스로 이동하지 않음(방향만 안내)

PRESET_START = (ROWS // 2, 2)
PRESET_GOALS = [
    (12,12), (16,12), (21,12), (25,12),
    (25,24), (21,24),
    (9,47), (29,47), (16,59), (29,59),
]

# ---- 색상 ----
BG = (245, 246, 248)
GRID = (220, 223, 230)
WALL = (60, 72, 88)
START_COLOR = (52, 152, 219)
PATH_COLOR = (155, 89, 182)
AGENT_COLOR = (231, 76, 60)
FIRE_COLOR = (231, 100, 20)
TEXT_COLOR = (33, 33, 33)
GOAL_COLORS = [
    (0, 141, 98), (241, 196, 15), (250, 153, 204),
    (119, 109, 97), (153, 134, 179),
]

# ==== 네가 쓰던 PRESET_WALLS 그대로 두기 ====
PRESET_WALLS = [{'kind': 'hline', 'r': 0, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 1, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 2, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 3, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 4, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 5, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 6, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 7, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 8, 'c0': 11, 'c1': 13}, {'kind': 'hline', 'r': 8, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 8, 'c0': 46, 'c1': 48}, {'kind': 'hline', 'r': 9, 'c0': 8, 'c1': 11}, {'kind': 'hline', 'r': 9, 'c0': 13, 'c1': 17}, {'kind': 'hline', 'r': 9, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 9, 'c0': 43, 'c1': 46}, {'kind': 'hline', 'r': 9, 'c0': 48, 'c1': 52}, {'kind': 'hline', 'r': 10, 'c0': 8, 'c1': 8}, {'kind': 'hline', 'r': 10, 'c0': 17, 'c1': 17}, {'kind': 'hline', 'r': 10, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 10, 'c0': 43, 'c1': 43}, {'kind': 'hline', 'r': 10, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 11, 'c0': 8, 'c1': 8}, {'kind': 'hline', 'r': 11, 'c0': 17, 'c1': 17}, {'kind': 'hline', 'r': 11, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 11, 'c0': 43, 'c1': 43}, {'kind': 'hline', 'r': 11, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 12, 'c0': 8, 'c1': 11}, {'kind': 'hline', 'r': 12, 'c0': 13, 'c1': 17}, {'kind': 'hline', 'r': 12, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 12, 'c0': 43, 'c1': 46}, {'kind': 'hline', 'r': 12, 'c0': 48, 'c1': 52}, {'kind': 'hline', 'r': 13, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 13, 'c0': 44, 'c1': 44}, {'kind': 'hline', 'r': 13, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 13, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 13, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 14, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 14, 'c0': 44, 'c1': 44}, {'kind': 'hline', 'r': 14, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 14, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 14, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 15, 'c0': 23, 'c1': 25}, {'kind': 'hline', 'r': 15, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 15, 'c0': 44, 'c1': 44}, {'kind': 'hline', 'r': 15, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 15, 'c0': 58, 'c1': 60}, {'kind': 'hline', 'r': 16, 'c0': 9, 'c1': 11}, {'kind': 'hline', 'r': 16, 'c0': 13, 'c1': 17}, {'kind': 'hline', 'r': 16, 'c0': 21, 'c1': 23}, {'kind': 'hline', 'r': 16, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 16, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 16, 'c0': 44, 'c1': 44}, {'kind': 'hline', 'r': 16, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 16, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 16, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 16, 'c0': 56, 'c1': 58}, {'kind': 'hline', 'r': 16, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 17, 'c0': 9, 'c1': 9}, {'kind': 'hline', 'r': 17, 'c0': 13, 'c1': 13}, {'kind': 'hline', 'r': 17, 'c0': 17, 'c1': 17}, {'kind': 'hline', 'r': 17, 'c0': 21, 'c1': 21}, {'kind': 'hline', 'r': 17, 'c0': 23, 'c1': 23}, {'kind': 'hline', 'r': 17, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 17, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 17, 'c0': 44, 'c1': 44}, {'kind': 'hline', 'r': 17, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 17, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 17, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 17, 'c0': 56, 'c1': 56}, {'kind': 'hline', 'r': 17, 'c0': 58, 'c1': 58}, {'kind': 'hline', 'r': 17, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 18, 'c0': 8, 'c1': 11}, {'kind': 'hline', 'r': 18, 'c0': 13, 'c1': 13}, {'kind': 'hline', 'r': 18, 'c0': 17, 'c1': 21}, {'kind': 'hline', 'r': 18, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 18, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 18, 'c0': 43, 'c1': 46}, {'kind': 'hline', 'r': 18, 'c0': 48, 'c1': 56}, {'kind': 'hline', 'r': 18, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 19, 'c0': 8, 'c1': 8}, {'kind': 'hline', 'r': 19, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 19, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 19, 'c0': 43, 'c1': 43}, {'kind': 'hline', 'r': 19, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 20, 'c0': 8, 'c1': 11}, {'kind': 'hline', 'r': 20, 'c0': 13, 'c1': 13}, {'kind': 'hline', 'r': 20, 'c0': 15, 'c1': 15}, {'kind': 'hline', 'r': 20, 'c0': 17, 'c1': 17}, {'kind': 'hline', 'r': 20, 'c0': 19, 'c1': 19}, {'kind': 'hline', 'r': 20, 'c0': 21, 'c1': 21}, {'kind': 'hline', 'r': 20, 'c0': 23, 'c1': 23}, {'kind': 'hline', 'r': 20, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 20, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 20, 'c0': 43, 'c1': 46}, {'kind': 'hline', 'r': 20, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 20, 'c0': 50, 'c1': 50}, {'kind': 'hline', 'r': 20, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 20, 'c0': 54, 'c1': 54}, {'kind': 'hline', 'r': 20, 'c0': 56, 'c1': 56}, {'kind': 'hline', 'r': 20, 'c0': 58, 'c1': 58}, {'kind': 'hline', 'r': 20, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 21, 'c0': 11, 'c1': 11}, {'kind': 'hline', 'r': 21, 'c0': 13, 'c1': 23}, {'kind': 'hline', 'r': 21, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 21, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 21, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 21, 'c0': 48, 'c1': 58}, {'kind': 'hline', 'r': 21, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 22, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 22, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 22, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 22, 'c0': 58, 'c1': 58}, {'kind': 'hline', 'r': 22, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 23, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 23, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 23, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 23, 'c0': 58, 'c1': 58}, {'kind': 'hline', 'r': 23, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 24, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 24, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 24, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 24, 'c0': 58, 'c1': 58}, {'kind': 'hline', 'r': 24, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 25, 'c0': 11, 'c1': 11}, {'kind': 'hline', 'r': 25, 'c0': 13, 'c1': 23}, {'kind': 'hline', 'r': 25, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 25, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 25, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 25, 'c0': 48, 'c1': 58}, {'kind': 'hline', 'r': 25, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 26, 'c0': 11, 'c1': 11}, {'kind': 'hline', 'r': 26, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 26, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 26, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 26, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 27, 'c0': 11, 'c1': 11}, {'kind': 'hline', 'r': 27, 'c0': 13, 'c1': 13}, {'kind': 'hline', 'r': 27, 'c0': 15, 'c1': 15}, {'kind': 'hline', 'r': 27, 'c0': 17, 'c1': 17}, {'kind': 'hline', 'r': 27, 'c0': 19, 'c1': 19}, {'kind': 'hline', 'r': 27, 'c0': 21, 'c1': 21}, {'kind': 'hline', 'r': 27, 'c0': 23, 'c1': 23}, {'kind': 'hline', 'r': 27, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 27, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 27, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 27, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 27, 'c0': 50, 'c1': 50}, {'kind': 'hline', 'r': 27, 'c0': 52, 'c1': 52}, {'kind': 'hline', 'r': 27, 'c0': 54, 'c1': 54}, {'kind': 'hline', 'r': 27, 'c0': 56, 'c1': 56}, {'kind': 'hline', 'r': 27, 'c0': 58, 'c1': 58}, {'kind': 'hline', 'r': 27, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 28, 'c0': 11, 'c1': 11}, {'kind': 'hline', 'r': 28, 'c0': 13, 'c1': 23}, {'kind': 'hline', 'r': 28, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 28, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 28, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 28, 'c0': 48, 'c1': 58}, {'kind': 'hline', 'r': 28, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 29, 'c0': 11, 'c1': 11}, {'kind': 'hline', 'r': 29, 'c0': 13, 'c1': 13}, {'kind': 'hline', 'r': 29, 'c0': 23, 'c1': 23}, {'kind': 'hline', 'r': 29, 'c0': 25, 'c1': 25}, {'kind': 'hline', 'r': 29, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 29, 'c0': 46, 'c1': 46}, {'kind': 'hline', 'r': 29, 'c0': 48, 'c1': 48}, {'kind': 'hline', 'r': 29, 'c0': 58, 'c1': 58}, {'kind': 'hline', 'r': 29, 'c0': 60, 'c1': 60}, {'kind': 'hline', 'r': 30, 'c0': 11, 'c1': 13}, {'kind': 'hline', 'r': 30, 'c0': 23, 'c1': 25}, {'kind': 'hline', 'r': 30, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 30, 'c0': 46, 'c1': 48}, {'kind': 'hline', 'r': 30, 'c0': 58, 'c1': 60}, {'kind': 'hline', 'r': 31, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 32, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 33, 'c0': 33, 'c1': 33}, {'kind': 'hline', 'r': 34, 'c0': 33, 'c1': 33}, {'kind': 'vline', 'c': 8, 'r0': 9, 'r1': 12}, {'kind': 'vline', 'c': 8, 'r0': 18, 'r1': 20}, {'kind': 'vline', 'c': 9, 'r0': 16, 'r1': 18}, {'kind': 'vline', 'c': 11, 'r0': 8, 'r1': 9}, {'kind': 'vline', 'c': 11, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 11, 'r0': 25, 'r1': 30}, {'kind': 'vline', 'c': 13, 'r0': 8, 'r1': 9}, {'kind': 'vline', 'c': 13, 'r0': 16, 'r1': 18}, {'kind': 'vline', 'c': 13, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 13, 'r0': 27, 'r1': 30}, {'kind': 'vline', 'c': 15, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 15, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 17, 'r0': 9, 'r1': 12}, {'kind': 'vline', 'c': 17, 'r0': 16, 'r1': 18}, {'kind': 'vline', 'c': 17, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 17, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 19, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 19, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 21, 'r0': 16, 'r1': 18}, {'kind': 'vline', 'c': 21, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 21, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 23, 'r0': 15, 'r1': 17}, {'kind': 'vline', 'c': 23, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 23, 'r0': 27, 'r1': 30}, {'kind': 'vline', 'c': 25, 'r0': 15, 'r1': 21}, {'kind': 'vline', 'c': 25, 'r0': 25, 'r1': 30}, {'kind': 'vline', 'c': 33, 'r0': 0, 'r1': 34}, {'kind': 'vline', 'c': 43, 'r0': 9, 'r1': 12}, {'kind': 'vline', 'c': 43, 'r0': 18, 'r1': 20}, {'kind': 'vline', 'c': 44, 'r0': 12, 'r1': 18}, {'kind': 'vline', 'c': 46, 'r0': 8, 'r1': 9}, {'kind': 'vline', 'c': 46, 'r0': 12, 'r1': 14}, {'kind': 'vline', 'c': 46, 'r0': 16, 'r1': 18}, {'kind': 'vline', 'c': 46, 'r0': 20, 'r1': 30}, {'kind': 'vline', 'c': 48, 'r0': 8, 'r1': 9}, {'kind': 'vline', 'c': 48, 'r0': 12, 'r1': 14}, {'kind': 'vline', 'c': 48, 'r0': 16, 'r1': 18}, {'kind': 'vline', 'c': 48, 'r0': 20, 'r1': 25}, {'kind': 'vline', 'c': 48, 'r0': 27, 'r1': 30}, {'kind': 'vline', 'c': 50, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 50, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 52, 'r0': 9, 'r1': 18}, {'kind': 'vline', 'c': 52, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 52, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 54, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 54, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 56, 'r0': 16, 'r1': 18}, {'kind': 'vline', 'c': 56, 'r0': 20, 'r1': 21}, {'kind': 'vline', 'c': 56, 'r0': 27, 'r1': 28}, {'kind': 'vline', 'c': 58, 'r0': 15, 'r1': 17}, {'kind': 'vline', 'c': 58, 'r0': 20, 'r1': 25}, {'kind': 'vline', 'c': 58, 'r0': 27, 'r1': 30}, {'kind': 'vline', 'c': 60, 'r0': 15, 'r1': 30}]
# (이미 파일에 있다면 이 주석은 무시해도 됩니다.)

# ===== 화면 크기 =====
W = COLS * CELL + (COLS + 1) * MARGIN
H = ROWS * CELL + (ROWS + 1) * MARGIN

pygame.init()
screen = pygame.display.set_mode((W, H + 40))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# ===== UDP 소켓 =====
# 1) 외부(카메라)에서 좌표 수신: "CELL r c"
POS_UDP_HOST = "127.0.0.1"
POS_UDP_PORT = 5005
pos_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pos_sock.bind((POS_UDP_HOST, POS_UDP_PORT))
pos_sock.setblocking(False)
print(f"[UDP] Listening position on {POS_UDP_HOST}:{POS_UDP_PORT}")

# 2) 다음 방향 방송: "DIR U/D/L/R"
DIR_UDP_HOST = "127.0.0.1"
DIR_UDP_PORT = 5006
dir_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ===== 유틸 =====
def auto_replan(blocked, agent_pos, goals, fire_cells, planner, ROWS, COLS):
    """가장 짧은 목표 선택 + D*Lite 준비"""
    best_idx, best_goal, best_len = choose_best_goal(blocked, agent_pos, goals, ROWS, COLS, fire_cells)
    if best_goal is not None and best_len < float('inf'):
        if planner and best_goal == planner.goal:
            planner.update_start(agent_pos)
            return best_idx, planner, planner.compute_generator()
        new_planner = DStarLite(blocked, agent_pos, best_goal, ROWS, COLS)
        # 불은 즉시 반영
        for f_pos in fire_cells:
            new_planner.update_map_change(f_pos, True)
        return best_idx, new_planner, new_planner.compute_generator()
    return None, None, None

def reset_all():
    blocked = build_blocked_with_presets(ROWS, COLS, PRESET_WALLS)
    goals = PRESET_GOALS[:]
    fire_cells = []
    start = PRESET_START
    agent_pos = start
    planner = None
    plan_gen = None
    planning = False
    auto_planning = False
    path = []
    active_goal_idx = None
    selected_goal_idx = 0
    mode = 1
    step_timer = 0.0
    fire_step_timer = 0.0
    replan_check_timer = 0.0
    periodic_replan_timer = 0.0
    dragging = False
    return (blocked, goals, fire_cells, start, agent_pos,
            planner, plan_gen, planning, auto_planning, path,
            active_goal_idx, selected_goal_idx, mode,
            step_timer, fire_step_timer, replan_check_timer, periodic_replan_timer,
            dragging)

def get_next_direction(agent_pos, path):
    """agent_pos 기준 path의 다음 칸을 보고 U/D/L/R/None 반환"""
    if not path:
        return None
    # agent_pos가 path 내부에 있으면 그 다음 칸을 기준으로
    try:
        i = path.index(agent_pos)
        if i + 1 >= len(path):
            return None
        r, c = agent_pos
        nr, nc = path[i + 1]
    except ValueError:
        # path 상에 없다면, 시작 부분 기준으로 추정
        if len(path) >= 2:
            r, c = path[0]
            nr, nc = path[1]
        else:
            return None

    dr, dc = nr - r, nc - c
    if dr == -1 and dc == 0:  # Up
        return "U"
    if dr == 1 and dc == 0:   # Down
        return "D"
    if dr == 0 and dc == -1:  # Left
        return "L"
    if dr == 0 and dc == 1:   # Right
        return "R"
    return None

# ===== 메인 =====
def main():
    (blocked, goals, fire_cells, start, agent_pos,
     planner, plan_gen, planning, auto_planning, path,
     active_goal_idx, selected_goal_idx, mode,
     step_timer, fire_step_timer, replan_check_timer, periodic_replan_timer,
     dragging) = reset_all()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # ===== 이벤트 처리 =====
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

                elif e.key == pygame.K_1:
                    mode = 1
                elif e.key == pygame.K_2:
                    mode = 2
                elif e.key == pygame.K_3:
                    mode = 3
                elif e.key == pygame.K_4:
                    mode = 4

                elif e.key == pygame.K_g:
                    if goals:
                        selected_goal_idx = (selected_goal_idx + 1) % len(goals)

                elif e.key == pygame.K_SPACE:
                    if not auto_planning:
                        auto_planning = True
                        active_goal_idx, planner, plan_gen = auto_replan(
                            blocked, agent_pos, goals, fire_cells, planner, ROWS, COLS
                        )
                        if planner is not None:
                            planning = True
                            path = []
                            step_timer = 0.0
                            print("자동 계획 모드: ON")
                        else:
                            planning = False
                            plan_gen = None
                            path = []
                            print("현재 도달 가능한 목표 없음 → 대기")
                    else:
                        auto_planning = False
                        planning = False
                        plan_gen = None
                        path = []
                        active_goal_idx = None
                        print("자동 계획 모드: OFF")

                elif e.key == pygame.K_c:
                    (blocked, goals, fire_cells, start, agent_pos,
                     planner, plan_gen, planning, auto_planning, path,
                     active_goal_idx, selected_goal_idx, mode,
                     step_timer, fire_step_timer, replan_check_timer, periodic_replan_timer,
                     dragging) = reset_all()
                    print("전체 리셋")

                elif e.key == pygame.K_r:
                    print("불 제거 + 에이전트 초기화")
                    for f_pos in fire_cells:
                        blocked[f_pos[0]][f_pos[1]] = False
                    fire_cells = []
                    agent_pos = start
                    if auto_planning:
                        if active_goal_idx is not None:
                            planner = DStarLite(blocked, agent_pos, goals[active_goal_idx], ROWS, COLS)
                            plan_gen = planner.compute_generator()
                            planning = True
                            path = []
                            step_timer = 0.0
                        else:
                            active_goal_idx, planner, plan_gen = auto_replan(
                                blocked, agent_pos, goals, fire_cells, planner, ROWS, COLS
                            )
                            if planner is not None:
                                planning = True; path = []; step_timer = 0.0
                            else:
                                planning = False; plan_gen = None; path = []

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                rc = cell_at_pos(*e.pos, H, CELL, MARGIN, ROWS, COLS)
                if rc:
                    r, c = rc
                    map_changed = False
                    if mode == 1 and not blocked[r][c] and (r, c) not in fire_cells:
                        agent_pos = (r, c); start = (r, c); map_changed = True
                    elif mode == 2 and not blocked[r][c] and (r, c) not in fire_cells:
                        goals[selected_goal_idx] = (r, c); map_changed = True
                    elif mode == 3 and (r, c) != agent_pos and (r, c) not in goals:
                        if (r, c) in fire_cells:
                            fire_cells.remove((r, c))
                            if planner: planner.update_map_change((r, c), False)
                            print("불 제거 → 재평가")
                        elif not blocked[r][c]:
                            fire_cells.append((r, c))
                            if planner: planner.update_map_change((r, c), True)
                            print("불 추가 → 재계획")
                        map_changed = True
                    elif mode == 4:
                        if (r, c) not in fire_cells:
                            blocked[r][c] = not blocked[r][c]
                            if planner: planner.update_map_change((r, c), blocked[r][c])
                            dragging = True; map_changed = True

                    if map_changed and auto_planning and planner:
                        path = []; plan_gen = planner.compute_generator(); planning = True; step_timer = 0.0

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                dragging = False

            elif e.type == pygame.MOUSEMOTION and dragging and mode == 4:
                rc = cell_at_pos(*e.pos, H, CELL, MARGIN, ROWS, COLS)
                if rc:
                    r, c = rc
                    if not blocked[r][c] and (r, c) not in fire_cells:
                        blocked[r][c] = True
                        if planner: planner.update_map_change((r, c), True)
                        if auto_planning and planner:
                            path = []; plan_gen = planner.compute_generator(); planning = True; step_timer = 0.0

        # ===== UDP: 외부 좌표 수신(CELL r c) =====
        while True:
            try:
                data, _ = pos_sock.recvfrom(1024)
            except BlockingIOError:
                break
            try:
                text = data.decode("utf-8").strip()
            except Exception:
                continue

            if text.startswith("CELL"):
                parts = text.split()
                if len(parts) == 3:
                    try:
                        rr = int(parts[1])  # row
                        cc = int(parts[2])  # col
                    except ValueError:
                        continue
                    if inb(rr, cc, ROWS, COLS) and not blocked[rr][cc] and (rr, cc) not in fire_cells:
                        agent_pos = (rr, cc)
                        start = agent_pos
                        if planner:
                            planner.update_start(agent_pos)
                        if auto_planning and planner:
                            plan_gen = planner.compute_generator()
                            planning = True
                            path = []
                            step_timer = 0.0

        # ===== 불 확산 =====
        if fire_cells and auto_planning:
            fire_step_timer += dt
            if fire_step_timer >= FIRE_STEP_INTERVAL:
                fire_step_timer -= FIRE_STEP_INTERVAL
                new_fire_cells = spread_fire(fire_cells, blocked, ROWS, COLS)
                if new_fire_cells:
                    changed = False
                    path_set = set(path) if path else set()
                    for f_pos in new_fire_cells:
                        r, c = f_pos
                        if f_pos not in fire_cells and not blocked[r][c]:
                            fire_cells.append(f_pos); blocked[r][c] = True; changed = True
                            if planner: planner.update_map_change(f_pos, True)
                    if changed and planner:
                        # 경로와 충돌 또는 다음 칸 막힘이면 즉시 재계획
                        intersects = any((f in path_set) for f in new_fire_cells)
                        next_blocked = False
                        if path:
                            try:
                                pi = path.index(agent_pos)
                                if pi + 1 < len(path):
                                    nxt = path[pi + 1]; next_blocked = nxt in new_fire_cells
                            except ValueError:
                                pass
                        if intersects or next_blocked:
                            plan_gen = planner.compute_generator(); planning = True; path = []
                            print("불 확산 영향 → 재계획")

        # ===== 자동 재탐색 / 주기적 최적 경로 재검토 =====
        if auto_planning and not planning:
            replan_check_timer += dt
            if replan_check_timer >= REPLAN_CHECK_INTERVAL:
                replan_check_timer = 0.0
                active_goal_idx, planner, plan_gen = auto_replan(
                    blocked, agent_pos, goals, fire_cells, planner, ROWS, COLS
                )
                if planner is not None:
                    planning = True; path = []; step_timer = 0.0
                    print("주기적 탐색 → 경로 발견")

        if auto_planning and planning:
            periodic_replan_timer += dt
            if periodic_replan_timer >= REPLAN_PERIODIC_CHECK:
                periodic_replan_timer = 0.0
                new_active_idx, new_planner, new_plan_gen = auto_replan(
                    blocked, agent_pos, goals, fire_cells, planner, ROWS, COLS
                )
                if new_planner is not None and new_active_idx != active_goal_idx:
                    active_goal_idx = new_active_idx; planner = new_planner; plan_gen = new_plan_gen; path = []
                    print(f"더 가까운 목표 {active_goal_idx + 1}로 전환")

        # ===== 계획 실행 =====
        if planning and plan_gen is not None:
            steps = 0
            try:
                while steps < PLANNER_STEPS_PER_FRAME:
                    next(plan_gen); steps += 1
            except StopIteration:
                path = planner.get_path(); plan_gen = None
                if not path and auto_planning:
                    print(f"목표 {active_goal_idx + 1 if active_goal_idx is not None else '?'} 실패 → 다른 목표")
                    new_active_idx, new_planner, new_plan_gen = auto_replan(
                        blocked, agent_pos, goals, fire_cells, None, ROWS, COLS
                    )
                    if new_planner is not None:
                        active_goal_idx = new_active_idx; planner = new_planner
                        plan_gen = new_plan_gen; path = []
                        print(f"새 목표 {new_active_idx + 1}로 전환")
                    else:
                        print("도달 가능한 목표 없음 → 대기"); planning = False
                step_timer = 0.0

        # ===== 에이전트 자동 이동 (가이드만 할 땐 비활성화) =====
        if AUTO_MOVE and planning and path and auto_planning:
            if agent_pos == path[-1]:
                print("목표 도달 → 정지"); planning = False; path = []
            else:
                step_timer += dt
                if step_timer >= STEP_INTERVAL:
                    step_timer -= STEP_INTERVAL
                    replan_needed = False
                    try:
                        current_path_idx = path.index(agent_pos)
                    except ValueError:
                        print("경로 이탈 → 재계획"); replan_needed = True
                        current_path_idx = -1
                    if not replan_needed and current_path_idx + 1 >= len(path):
                        print("경로 끝 → 재계획"); replan_needed = True
                    if not replan_needed:
                        next_pos = path[current_path_idx + 1]
                        if blocked[next_pos[0]][next_pos[1]]:
                            print("다음 칸 막힘 → 재계획"); replan_needed = True
                    if replan_needed:
                        if planner:
                            planner.update_start(agent_pos); plan_gen = planner.compute_generator(); path = []
                        else:
                            active_goal_idx, planner, plan_gen = auto_replan(
                                blocked, agent_pos, goals, fire_cells, None, ROWS, COLS
                            )
                        if planner and planner.get_path():
                            path = planner.get_path(); print("우회 경로 찾음")
                        else:
                            print("기존 목표 막힘 → 다른 목표 탐색")
                            active_goal_idx, planner, plan_gen = auto_replan(
                                blocked, agent_pos, goals, fire_cells, None, ROWS, COLS
                            )
                            if planner:
                                path = planner.get_path(); print(f"새 목표 {active_goal_idx + 1} 전환")
                            else:
                                planning = False; path = []; print("우회/새 경로 실패")
                        step_timer = 0.0
                    else:
                        agent_pos = path[current_path_idx + 1]
                        if planner: planner.update_start(agent_pos)

        # ===== 렌더링 직전: 다음 이동 방향 계산 + UDP 방송 =====
        direction = get_next_direction(agent_pos, path) if (auto_planning and path) else None
        dir_text = {"U":"↑ Up", "D":"↓ Down", "L":"← Left", "R":"→ Right", None:"-"}.get(direction, "-")

        if direction is not None:
            try:
                dir_sock.sendto(f"DIR {direction}".encode("utf-8"), (DIR_UDP_HOST, DIR_UDP_PORT))
            except Exception:
                pass

        # ===== 렌더링 =====
        draw_all(
            screen, blocked, path, goals, start, agent_pos, active_goal_idx, selected_goal_idx, fire_cells,
            mode, auto_planning, ROWS, COLS, CELL, MARGIN,
            BG, GRID, WALL, GOAL_COLORS, START_COLOR, PATH_COLOR, AGENT_COLOR, FIRE_COLOR, TEXT_COLOR,
            W, H, font
        )

        # 상태바 오른쪽에 방향 표시
        label = font.render(f"Next: {dir_text}", True, (20, 20, 20))
        screen.blit(label, (W - 150, H + 10))

        # 에이전트 머리 위 방향 화살표
        ax = agent_pos[1] * (CELL + MARGIN) + MARGIN + CELL // 2
        ay = agent_pos[0] * (CELL + MARGIN) + MARGIN + CELL // 2
        if direction == "U":
            pygame.draw.polygon(screen, (0, 120, 0), [(ax, ay-14), (ax-8, ay-2), (ax+8, ay-2)])
        elif direction == "D":
            pygame.draw.polygon(screen, (0, 120, 0), [(ax, ay+14), (ax-8, ay+2), (ax+8, ay+2)])
        elif direction == "L":
            pygame.draw.polygon(screen, (0, 120, 0), [(ax-14, ay), (ax-2, ay-8), (ax-2, ay+8)])
        elif direction == "R":
            pygame.draw.polygon(screen, (0, 120, 0), [(ax+14, ay), (ax+2, ay-8), (ax+2, ay+8)])

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()
