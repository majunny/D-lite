import sys, pygame, random
from function import *

# ===== 설정 =====
CELL = 22
ROWS = 25
COLS = 35
MARGIN = 1
FPS = 60
STEP_INTERVAL = 0.3  # 0.3초마다 격자 한 칸 이동
PLANNER_STEPS_PER_FRAME = 1200  # 프레임당 D* Lite 처리 스텝

# 여러 개 도착지 프리셋 (원하는 좌표로 바꿔줘)
PRESET_GOALS = [
    (9, 9),
    (6, 12),
    (19, 24),
    (7, 24)
]

# 색상
BG = (245, 246, 248)
GRID = (220, 223, 230)
WALL = (60, 72, 88)
START_COLOR = (52, 152, 219)
PATH_COLOR = (155, 89, 182)
AGENT_COLOR = (231, 76, 60)
FIRE_COLOR = (231, 100, 20)
TEXT_COLOR = (33, 33, 33)

GOAL_COLORS = [
    (0, 141, 98),   # 초록
    (241, 196, 15),   # 노랑
    (250, 153, 204),   # 분홍
    (119, 109, 97),    # 갈색
    (153, 134, 179),    # 보라
]

# ===== 프리셋 벽 정의(원하는 대로 수정) =====
PRESET_WALLS = [
    # 세로 얇은 벽
    {'kind': 'vline', 'c': 25, 'r0': 7, 'r1': 19},
    {'kind': 'vline', 'c': 23, 'r0': 7, 'r1': 8},
    {'kind': 'vline', 'c': 23, 'r0': 17, 'r1': 19},
    {'kind': 'vline', 'c': 23, 'r0': 10, 'r1': 14},
    {'kind': 'vline', 'c': 13, 'r0': 6, 'r1': 7},
    {'kind': 'vline', 'c': 11, 'r0': 6, 'r1': 8},
    {'kind': 'vline', 'c': 11, 'r0': 11, 'r1': 18},
    {'kind': 'vline', 'c': 13, 'r0': 12, 'r1': 14},
    # 가로 얇은 벽
    {'kind': 'hline', 'r': 8, 'c0': 13, 'c1': 22},
    {'kind': 'hline', 'r': 11, 'c0': 13, 'c1': 23},
    {'kind': 'hline', 'r': 15, 'c0': 13, 'c1': 23},
    {'kind': 'hline', 'r': 8, 'c0': 9, 'c1': 10},
    {'kind': 'hline', 'r': 10, 'c0': 9, 'c1': 11},
    {'kind': 'hline', 'r': 18, 'c0': 12, 'c1': 22},
    # ---점
    {'kind': 'hline', 'r': 10, 'c0': 13, 'c1': 13},
    {'kind': 'hline', 'r': 10, 'c0': 15, 'c1': 15},
    {'kind': 'hline', 'r': 10, 'c0': 17, 'c1': 17},
    {'kind': 'hline', 'r': 10, 'c0': 19, 'c1': 19},
    {'kind': 'hline', 'r': 10, 'c0': 21, 'c1': 21},
    {'kind': 'hline', 'r': 17, 'c0': 13, 'c1': 13},
    {'kind': 'hline', 'r': 17, 'c0': 15, 'c1': 15},
    {'kind': 'hline', 'r': 17, 'c0': 17, 'c1': 17},
    {'kind': 'hline', 'r': 17, 'c0': 19, 'c1': 19},
    {'kind': 'hline', 'r': 17, 'c0': 21, 'c1': 21}
]

W = COLS * CELL + (COLS + 1) * MARGIN
H = ROWS * CELL + (ROWS + 1) * MARGIN

pygame.init()
screen = pygame.display.set_mode((W, H + 40))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

def main():
    # ---------- 상태 ----------
    blocked = build_blocked_with_presets(ROWS, COLS, PRESET_WALLS)
    start = (ROWS // 2, 2)  # 고정된 시작점
    agent_pos = start  # 에이전트의 현재 위치
    fire_cells = []  # 불의 위치를 리스트로 관리 (여러 개 가능)

    goals = PRESET_GOALS[:]  # Multiple goals
    selected_goal_idx = 0  # Index of the goal to move in edit mode (cycle with G)
    active_goal_idx = None  # Index of the goal actually selected (closest)

    mode = 1  # 1: start, 2: goal-edit, 3: fire, 4: obstacle
    planning = False
    planner = None
    plan_gen = None
    path = []
    step_timer = 0.0
    dragging = False

    fire_step_timer = 0.0
    FIRE_STEP_INTERVAL = 1.0  # 불이 1.0초마다 퍼짐

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
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
                    # Cycle through the goal indices for editing
                    if goals:
                        selected_goal_idx = (selected_goal_idx + 1) % len(goals)

                elif e.key == pygame.K_SPACE:
                    # Auto-select the closest goal → prepare D* Lite
                    best_idx, best_goal, _ = choose_best_goal(blocked, agent_pos, goals, ROWS, COLS, fire_cells)
                    active_goal_idx = best_idx
                    if best_goal is not None:
                        planner = DStarLite(blocked, agent_pos, best_goal, ROWS, COLS)
                        if fire_cells:
                            for f_pos in fire_cells:
                                planner.update_map_change(f_pos, True)
                        plan_gen = planner.compute_generator()
                        planning = True
                        path = []
                        step_timer = 0.0
                    else:
                        planning = False
                        plan_gen = None
                        path = []
                
                # C 키: 전체 리셋
                elif e.key == pygame.K_c:
                    print("전체 리셋합니다.")
                    blocked = build_blocked_with_presets(ROWS, COLS, PRESET_WALLS)
                    goals = PRESET_GOALS[:]
                    fire_cells = []
                    
                    planner = None
                    plan_gen = None
                    planning = False
                    path = []
                    active_goal_idx = None
                    agent_pos = start
                    step_timer = 0.0

                # R 키: 불만 지우고 에이전트 위치 초기화
                elif e.key == pygame.K_r:
                    print("불을 지우고 에이전트 위치를 초기화합니다.")
                    # 불이 있던 위치의 blocked 상태를 False로 되돌리기
                    for f_pos in fire_cells:
                        blocked[f_pos[0]][f_pos[1]] = False
                    fire_cells = []
                    
                    # 에이전트 위치 초기화
                    agent_pos = start
                    
                    planner = None
                    plan_gen = None
                    planning = False
                    path = []
                    step_timer = 0.0
                    active_goal_idx = None
                    
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                rc = cell_at_pos(*e.pos, H, CELL, MARGIN, ROWS, COLS)
                if rc:
                    r, c = rc
                    if mode == 1 and not blocked[r][c] and (r, c) not in fire_cells:
                        agent_pos = (r, c)
                        start = (r, c) # 시작점도 함께 변경
                    elif mode == 2 and not blocked[r][c] and goals and (r, c) not in fire_cells:
                        # Move the selected goal to the current square
                        goals[selected_goal_idx] = (r, c)
                    elif mode == 3 and (r, c) != agent_pos and (r, c) not in goals:
                        if (r, c) in fire_cells:
                            # 불 제거
                            fire_cells.remove((r, c))
                            blocked[r][c] = False
                            if planning:
                                planner.update_map_change((r, c), False)
                                plan_gen = planner.compute_generator()
                        elif not blocked[r][c]:
                            # 불 추가
                            fire_cells.append((r, c))
                            blocked[r][c] = True
                            if planning:
                                planner.update_map_change((r, c), True)
                                plan_gen = planner.compute_generator()
                    elif mode == 4:
                        if (r, c) in fire_cells:
                            pass # 불 객체는 벽으로 막을 수 없음
                        else:
                            is_blocked_before = blocked[r][c]
                            blocked[r][c] = not blocked[r][c]
                            dragging = True
                            if planning:
                                planner.update_map_change((r, c), blocked[r][c])
                                plan_gen = planner.compute_generator()

        # 불 객체 이동 로직
        if fire_cells and planning:
            fire_step_timer += dt
            if fire_step_timer >= FIRE_STEP_INTERVAL:
                fire_step_timer -= FIRE_STEP_INTERVAL
                
                # 한 번에 모든 불의 인접 칸으로 퍼짐
                new_fire_cells = spread_fire(fire_cells, blocked, ROWS, COLS)
                if new_fire_cells:
                    # 새로운 불들을 리스트에 추가하고 D* Lite 플래너에 알림
                    for f_pos in new_fire_cells:
                        if f_pos not in fire_cells and not blocked[f_pos[0]][f_pos[1]]:
                            fire_cells.append(f_pos)
                            blocked[f_pos[0]][f_pos[1]] = True
                            planner.update_map_change(f_pos, True)
                    
                    # 불이 퍼졌으므로 최적 경로 재계획
                    planner.update_start(agent_pos)
                    plan_gen = planner.compute_generator()

        # ---- D* Lite를 프레임마다 조금씩 실행 ----
        if planning and plan_gen is not None:
            steps = 0
            try:
                while steps < PLANNER_STEPS_PER_FRAME:
                    next(plan_gen)
                    steps += 1
            except StopIteration:
                path = planner.get_path()
                plan_gen = None
                step_timer = 0.0
        
        # ---- 0.3초마다 '한 칸' 전진 ----
        if planning and path:
            if agent_pos == path[-1]:
                planning = False
            else:
                step_timer += dt
                if step_timer >= STEP_INTERVAL:
                    step_timer -= STEP_INTERVAL
                    # 현재 위치가 경로의 어디인지
                    try:
                        idx = path.index(agent_pos)
                        # 다음 칸이 장애물이 됐는지 확인하고, 그렇다면 즉시 재계획
                        if idx + 1 < len(path) and blocked[path[idx+1][0]][path[idx+1][1]]:
                            print("경로가 막혔습니다. 재계획 중...")
                            # 현재 위치에서 재계획을 시작
                            planner.update_start(agent_pos)
                            plan_gen = planner.compute_generator()
                            path = []
                            step_timer = 0.0
                            continue # 다음 루프를 즉시 시작해서 움직이지 않게 함
                    except ValueError:
                        # 경로 이탈 → 재계획
                        best_idx, best_goal, _ = choose_best_goal(blocked, agent_pos, goals, ROWS, COLS, fire_cells)
                        active_goal_idx = best_idx
                        if best_goal is not None:
                            planner = DStarLite(blocked, agent_pos, best_goal, ROWS, COLS)
                            if fire_cells:
                                for f_pos in fire_cells:
                                    planner.update_map_change(f_pos, True)
                            plan_gen = planner.compute_generator()
                            path = []
                            step_timer = 0.0
                        else:
                            planning = False
                            plan_gen = None
                            path = []
                    
                    # 경로에 문제가 없다면 한 칸 전진
                    if path:
                        nxt = path[idx + 1] if idx + 1 < len(path) else path[-1]
                        if nxt in fire_cells:
                            # 다음 위치가 불이라면 이동하지 않고 재계획
                            print("불이 경로에 나타났습니다. 재계획 중...")
                            planner.update_start(agent_pos)
                            plan_gen = planner.compute_generator()
                            path = []
                            step_timer = 0.0
                            continue
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
                            plan_gen = None

        draw_all(
            screen, blocked, path, goals, start, agent_pos, active_goal_idx, selected_goal_idx, fire_cells,
            mode, ROWS, COLS, CELL, MARGIN,
            BG, GRID, WALL,
            GOAL_COLORS, START_COLOR, PATH_COLOR, AGENT_COLOR, FIRE_COLOR, TEXT_COLOR,
            W, H, font
        )

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()
