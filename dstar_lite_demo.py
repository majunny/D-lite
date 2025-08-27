import sys, pygame
from function import *

# ===== 설정 =====
CELL=22; ROWS, COLS=25, 35; MARGIN=1; FPS=60
STEP_INTERVAL = 0.3   # <<< 0.3초마다 격자 한 칸 이동
PLANNER_STEPS_PER_FRAME = 1200  # 프레임당 D* Lite 처리 스텝(GUI 프리즈 방지)

# 색상
BG=(245,246,248); GRID=(220,223,230); WALL=(60,72,88)
START_COLOR=(52,152,219); GOAL_A_COLOR=(46,204,113); GOAL_B_COLOR=(241,196,15)
PATH_COLOR=(155,89,182); AGENT_COLOR=(231,76,60); TEXT_COLOR=(33,33,33)

W = COLS*CELL + (COLS+1)*MARGIN
H = ROWS*CELL + (ROWS+1)*MARGIN

# ===== 프리셋 벽 정의(원하는 대로 수정) =====
PRESET_WALLS = [
    # 중앙에 세로 얇은 벽
    {'kind':'vline', 'c': 15, 'r0': 3, 'r1': 20},
    # 위쪽 가로 얇은 벽
    {'kind':'hline', 'r': 5, 'c0': 5, 'c1': 20},
    # 좌하단 직사각형 벽(덩어리)
    {'kind':'rect', 'r0': 14, 'c0': 3, 'r1': 18, 'c1': 7},
]

pygame.init()
screen=pygame.display.set_mode((W,H+40))
clock=pygame.time.Clock()
font=pygame.font.SysFont("Arial",16)

# ---------- 상태 ----------
blocked = build_blocked_with_presets(ROWS, COLS, PRESET_WALLS)
start=(ROWS//2,2); goalA=(ROWS//2-6, COLS-4); goalB=(ROWS//2+6, COLS-4)
mode=1
planning=False
planner=None; plan_gen=None; path=[]
active_goal_name=None
agent_pos=start
step_timer=0.0
dragging=False

running=True
while running:
    dt = clock.tick(FPS)/1000.0
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE: running=False
            elif e.key==pygame.K_1: mode=1
            elif e.key==pygame.K_2: mode=2
            elif e.key==pygame.K_3: mode=3
            elif e.key==pygame.K_4: mode=4
            elif e.key==pygame.K_SPACE:
                name,goal = choose_goal_quick(blocked, start, goalA, goalB, ROWS, COLS)
                active_goal_name=name
                planner = DStarLite(blocked, start, goal, ROWS, COLS)
                plan_gen = planner.compute_generator()
                planning=True; path=[]; agent_pos=start; step_timer=0.0
            elif e.key==pygame.K_r:
                agent_pos=start; step_timer=0.0
            elif e.key==pygame.K_c:
                # 프리셋으로 다시 세팅 (벽 유지)
                blocked = build_blocked_with_presets(ROWS, COLS, PRESET_WALLS)
                start=(ROWS//2,2); goalA=(ROWS//2-6, COLS-4); goalB=(ROWS//2+6, COLS-4)
                planner=None; plan_gen=None; planning=False; path=[]; active_goal_name=None
                agent_pos=start; step_timer=0.0
        elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            rc=cell_at_pos(*e.pos, H, CELL, MARGIN, ROWS, COLS)
            if rc:
                r,c=rc
                if mode==1 and not blocked[r][c]: start=(r,c)
                elif mode==2 and not blocked[r][c]: goalA=(r,c)
                elif mode==3 and not blocked[r][c]: goalB=(r,c)
                elif mode==4: blocked[r][c]=not blocked[r][c]; dragging=True
                # 맵 변경 시 재계획 준비
                if planning:
                    name,goal = choose_goal_quick(blocked, start, goalA, goalB, ROWS, COLS)
                    active_goal_name=name
                    planner = DStarLite(blocked, start, goal, ROWS, COLS)
                    plan_gen = planner.compute_generator()
                    path=[]; step_timer=0.0
        elif e.type==pygame.MOUSEBUTTONUP and e.button==1:
            dragging=False
        elif e.type==pygame.MOUSEMOTION and dragging and mode==4:
            rc=cell_at_pos(*e.pos, H, CELL, MARGIN, ROWS, COLS)
            if rc:
                r,c=rc
                if not blocked[r][c]:
                    blocked[r][c]=True
                    if planning:
                        name,goal = choose_goal_quick(blocked, start, goalA, goalB, ROWS, COLS)
                        active_goal_name=name
                        planner = DStarLite(blocked, start, goal, ROWS, COLS)
                        plan_gen = planner.compute_generator()
                        path=[]; step_timer=0.0

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
                    name,goal = choose_goal_quick(blocked, start, goalA, goalB, ROWS, COLS)
                    active_goal_name=name
                    planner = DStarLite(blocked, start, goal, ROWS, COLS)
                    plan_gen = planner.compute_generator()
                    path=[]; step_timer=0.0
                else:
                    nxt = path[idx+1] if idx+1 < len(path) else path[-1]
                    # 한 칸 전진
                    agent_pos = nxt
                    # D* Lite 시작점 업데이트(증분성 유지)
                    planner.update_start(agent_pos)
                    # 움직였으니 최신 경로 재구성(장애물 변화 대비)
                    plan_gen = planner.compute_generator()
                    # 경로 완성되면 즉시 반영(조금만 돌려서 끊김 줄임)
                    try:
                        for _ in range(60):
                            next(plan_gen)
                    except StopIteration:
                        path = planner.get_path()
                        plan_gen=None

    draw_all(screen, blocked, path, goalA, goalB, start, agent_pos, active_goal_name, mode, ROWS, COLS, CELL, MARGIN, BG, GRID, WALL, START_COLOR, GOAL_A_COLOR, GOAL_B_COLOR, PATH_COLOR, AGENT_COLOR, TEXT_COLOR, W, H, font)

pygame.quit(); sys.exit(0)