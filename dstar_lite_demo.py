import sys, pygame
from function import *

# ===== 설정 =====
CELL=22; ROWS, COLS=25, 35; MARGIN=1; FPS=60
STEP_INTERVAL = 0.3   # 0.3초마다 격자 한 칸 이동
PLANNER_STEPS_PER_FRAME = 1200  # 프레임당 D* Lite 처리 스텝

# 여러 개 도착지 프리셋 (원하는 좌표로 바꿔줘)
PRESET_GOALS = [
    (9, 9),
    (6, 12),
    (19, 24),
    (7, 24)
]

# 색상
BG=(245,246,248); GRID=(220,223,230); WALL=(60,72,88)
START_COLOR=(52,152,219)
PATH_COLOR=(155,89,182); AGENT_COLOR=(231,76,60); TEXT_COLOR=(33,33,33)

GOAL_COLORS = [
    (0, 141, 98),   # 초록
    (241, 196, 15),   # 노랑
    (250, 153, 204),   # 분홍
    (119, 109, 97),   # 갈색
    (153, 134, 179),    # 보라
]

# ===== 프리셋 벽 정의(원하는 대로 수정) =====
PRESET_WALLS = [
    # 세로 얇은 벽
    {'kind':'vline', 'c': 25, 'r0': 7, 'r1': 19},
    {'kind':'vline', 'c': 23, 'r0': 7, 'r1': 8},
    {'kind':'vline', 'c': 23, 'r0': 17, 'r1': 19},
    {'kind':'vline', 'c': 23, 'r0': 10, 'r1': 14},
    {'kind':'vline', 'c': 13, 'r0': 6, 'r1': 7},
    {'kind':'vline', 'c': 11, 'r0': 6, 'r1': 8},
    {'kind':'vline', 'c': 11, 'r0': 11, 'r1': 18},
    {'kind':'vline', 'c': 13, 'r0': 12, 'r1': 14},
    # 가로 얇은 벽
    {'kind':'hline', 'r': 8, 'c0': 13, 'c1': 22},
    {'kind':'hline', 'r': 11, 'c0': 13, 'c1': 23},
    {'kind':'hline', 'r': 15, 'c0': 13, 'c1': 23},
    {'kind':'hline', 'r': 8, 'c0': 9, 'c1': 10},
    {'kind':'hline', 'r': 10, 'c0': 9, 'c1': 11},
    {'kind':'hline', 'r': 18, 'c0': 12, 'c1': 22},
    # ---점
    {'kind':'hline', 'r': 10, 'c0': 13, 'c1': 13},
    {'kind':'hline', 'r': 10, 'c0': 15, 'c1': 15},
    {'kind':'hline', 'r': 10, 'c0': 17, 'c1': 17},
    {'kind':'hline', 'r': 10, 'c0': 19, 'c1': 19},
    {'kind':'hline', 'r': 10, 'c0': 21, 'c1': 21},
    {'kind':'hline', 'r': 17, 'c0': 13, 'c1': 13},
    {'kind':'hline', 'r': 17, 'c0': 15, 'c1': 15},
    {'kind':'hline', 'r': 17, 'c0': 17, 'c1': 17},
    {'kind':'hline', 'r': 17, 'c0': 19, 'c1': 19},
    {'kind':'hline', 'r': 17, 'c0': 21, 'c1': 21}
]

W = COLS*CELL + (COLS+1)*MARGIN
H = ROWS*CELL + (ROWS+1)*MARGIN

pygame.init()
screen=pygame.display.set_mode((W,H+40))
clock=pygame.time.Clock()
font=pygame.font.SysFont("Arial",16)

# ---------- 상태 ----------
blocked = build_blocked_with_presets(ROWS, COLS, PRESET_WALLS)
start = (ROWS//2, 2)

goals = PRESET_GOALS[:]          # 여러 목표
selected_goal_idx = 0            # 편집 모드에서 옮길 목표 인덱스 (G로 순환)
active_goal_idx = None           # 실제로 선택된(가장 가까운) 목표 인덱스

mode = 1                         # 1: start, 2: goal-편집, 4: obstacle
planning = False
planner = None; plan_gen = None; path = []
agent_pos = start
step_timer = 0.0
dragging = False

running=True
while running:
    dt = clock.tick(FPS)/1000.0
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:
                running=False

            elif e.key==pygame.K_1:
                mode=1
            elif e.key==pygame.K_2:
                mode=2
            elif e.key==pygame.K_4:
                mode=4

            elif e.key==pygame.K_g:
                # 편집 대상 목표 인덱스 순환
                if goals:
                    selected_goal_idx = (selected_goal_idx + 1) % len(goals)

            elif e.key==pygame.K_SPACE:
                # 가장 가까운 목표 자동 선택 → D* Lite 준비
                best_idx, best_goal, _ = choose_best_goal(blocked, start, goals, ROWS, COLS)
                active_goal_idx = best_idx
                if best_goal is not None:
                    planner = DStarLite(blocked, start, best_goal, ROWS, COLS)
                    plan_gen = planner.compute_generator()
                    planning=True; path=[]; agent_pos=start; step_timer=0.0
                else:
                    planning=False; plan_gen=None; path=[]

            elif e.key==pygame.K_r:
                agent_pos=start; step_timer=0.0

            elif e.key==pygame.K_c:
                # 프리셋 벽/목표로 리셋
                blocked = build_blocked_with_presets(ROWS, COLS, PRESET_WALLS)
                goals = PRESET_GOALS[:]
                planner=None; plan_gen=None; planning=False; path=[]
                active_goal_idx=None
                agent_pos=start; step_timer=0.0

        elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            rc=cell_at_pos(*e.pos, H, CELL, MARGIN, ROWS, COLS)
            if rc:
                r,c=rc
                if mode==1 and not blocked[r][c]:
                    start=(r,c)
                elif mode==2 and not blocked[r][c] and goals:
                    # 선택된 목표를 현재 칸으로 이동
                    goals[selected_goal_idx] = (r,c)
                elif mode==4:
                    blocked[r][c]=not blocked[r][c]
                    dragging=True

                # 맵/목표 변경 시 계획 다시 준비
                if planning:
                    best_idx, best_goal, _ = choose_best_goal(blocked, start, goals, ROWS, COLS)
                    active_goal_idx = best_idx
                    if best_goal is not None:
                        planner = DStarLite(blocked, start, best_goal, ROWS, COLS)
                        plan_gen = planner.compute_generator()
                        path=[]; step_timer=0.0
                    else:
                        planning=False; plan_gen=None; path=[]

        elif e.type==pygame.MOUSEBUTTONUP and e.button==1:
            dragging=False

        elif e.type==pygame.MOUSEMOTION and dragging and mode==4:
            rc=cell_at_pos(*e.pos, H, CELL, MARGIN, ROWS, COLS)
            if rc:
                r,c=rc
                if not blocked[r][c]:
                    blocked[r][c]=True
                    if planning:
                        best_idx, best_goal, _ = choose_best_goal(blocked, start, goals, ROWS, COLS)
                        active_goal_idx = best_idx
                        if best_goal is not None:
                            planner = DStarLite(blocked, start, best_goal, ROWS, COLS)
                            plan_gen = planner.compute_generator()
                            path=[]; step_timer=0.0
                        else:
                            planning=False; plan_gen=None; path=[]

    # ---- D* Lite를 프레임마다 조금씩 실행 ----
    if planning and plan_gen is not None:
        steps=0
        try:
            while steps<PLANNER_STEPS_PER_FRAME:
                next(plan_gen); steps+=1
        except StopIteration:
            path = planner.get_path()
            plan_gen=None
            step_timer=0.0

    # ---- 0.3초마다 '한 칸' 전진 ----
    if planning and path:
        if agent_pos == path[-1]:
            planning=False
        else:
            step_timer += dt
            if step_timer >= STEP_INTERVAL:
                step_timer -= STEP_INTERVAL
                # 현재 위치가 경로의 어디인지
                try:
                    idx = path.index(agent_pos)
                except ValueError:
                    # 경로 이탈 → 재계획
                    best_idx, best_goal, _ = choose_best_goal(blocked, start, goals, ROWS, COLS)
                    active_goal_idx = best_idx
                    if best_goal is not None:
                        planner = DStarLite(blocked, start, best_goal, ROWS, COLS)
                        plan_gen = planner.compute_generator()
                        path=[]; step_timer=0.0
                    else:
                        planning=False; plan_gen=None; path=[]
                else:
                    nxt = path[idx+1] if idx+1 < len(path) else path[-1]
                    # 한 칸 전진
                    agent_pos = nxt
                    # D* Lite 시작점 업데이트(증분성 유지)
                    planner.update_start(agent_pos)
                    # 움직였으니 최신 경로 재구성(장애물 변화 대비)
                    plan_gen = planner.compute_generator()
                    # 경로가 빨리 갱신되도록 약간만 더 돌려줌
                    try:
                        for _ in range(60):
                            next(plan_gen)
                    except StopIteration:
                        path = planner.get_path()
                        plan_gen=None

    draw_all(
        screen, blocked, path, goals, start, agent_pos, active_goal_idx,
        mode, ROWS, COLS, CELL, MARGIN,
        BG, GRID, WALL,
        GOAL_COLORS, START_COLOR, PATH_COLOR, AGENT_COLOR, TEXT_COLOR,
        W, H, font
    )

pygame.quit(); sys.exit(0)
