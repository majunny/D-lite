import heapq, math, pygame, random

NEI4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
INF = 10**9

def inb(r, c, ROWS, COLS): return 0 <= r < ROWS and 0 <= c < COLS
def manhattan(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ---------- 빠른 목표 선택용 A* (길이만) ----------
# 불 위치도 장애물로 간주하도록 fire_cells 인자 추가
def astar_len(blocked, start, goal, ROWS, COLS, fire_cells=None):
    if blocked[goal[0]][goal[1]]: return INF
    if fire_cells and (goal[0], goal[1]) in fire_cells: return INF
    
    g = [[INF] * COLS for _ in range(ROWS)]
    g[start[0]][start[1]] = 0
    pq = [(manhattan(start, goal), 0, start)]
    while pq:
        f, cost, (r, c) = heapq.heappop(pq)
        if (r, c) == goal: return cost
        if cost != g[r][c]: continue
        for dr, dc in NEI4:
            nr, nc = r + dr, c + dc
            if inb(nr, nc, ROWS, COLS) and not blocked[nr][nc]:
                # 불의 위치도 장애물로 간주
                if fire_cells and (nr, nc) in fire_cells:
                    continue
                ncst = cost + 1
                if ncst < g[nr][nc]:
                    g[nr][nc] = ncst
                    heapq.heappush(pq, (ncst + manhattan((nr, nc), goal), ncst, (nr, nc)))
    return INF

# ---------- D* Lite ----------
class DStarLite:
    def __init__(self, blocked, start, goal, ROWS, COLS):
        self.blocked = blocked.copy()
        self.start = start
        self.goal = goal
        self.ROWS = ROWS
        self.COLS = COLS
        self.g = [[INF] * COLS for _ in range(ROWS)]
        self.rhs = [[INF] * COLS for _ in range(ROWS)]
        self.rhs[goal[0]][goal[1]] = 0
        self.U = []
        self.km = 0
        self.last = start
        self._insert(goal, self._key(goal))

    def _key(self, s):
        r, c = s
        val = min(self.g[r][c], self.rhs[r][c])
        return (val + manhattan(self.start, s) + self.km, val)

    def _insert(self, s, k): heapq.heappush(self.U, (k, s))
    def _top_key(self): return self.U[0][0] if self.U else (INF, INF)

    def _update_vertex(self, s):
        r, c = s
        if s != self.goal:
            m = INF
            for dr, dc in NEI4:
                nr, nc = r + dr, c + dc
                if inb(nr, nc, self.ROWS, self.COLS) and not self.blocked[nr][nc]:
                    m = min(m, self.g[nr][nc] + 1)
            self.rhs[r][c] = m
        if self.g[r][c] != self.rhs[r][c]:
            self._insert(s, self._key(s))

    def _neighbors(self, s):
        r, c = s
        for dr, dc in NEI4:
            nr, nc = r + dr, c + dc
            if inb(nr, nc, self.ROWS, self.COLS) and not self.blocked[nr][nc]:
                yield (nr, nc)

    # 제너레이터: 한 스텝씩 실행해서 GUI 프리즈 방지
    def compute_generator(self):
        while self._top_key() < self._key(self.start) or \
                self.rhs[self.start[0]][self.start[1]] != self.g[self.start[0]][self.start[1]]:
            (k_old, s) = heapq.heappop(self.U)
            if k_old > self._key(s):
                self._insert(s, self._key(s))
            elif self.g[s[0]][s[1]] > self.rhs[s[0]][s[1]]:
                self.g[s[0]][s[1]] = self.rhs[s[0]][s[1]]
                for n in self._neighbors(s):
                    self._update_vertex(n)
            else:
                old_g = self.g[s[0]][s[1]]
                self.g[s[0]][s[1]] = INF
                self._update_vertex(s)
                for n in self._neighbors(s):
                    if self.rhs[n[0]][n[1]] == old_g + 1:
                        self._update_vertex(n)
            yield
        yield

    def update_start(self, new_start):
        self.km += manhattan(self.last, new_start)
        self.last = new_start
        self.start = new_start
    
    def update_map_change(self, s, is_blocked):
        r, c = s
        is_blocked_before = self.blocked[r][c]
        self.blocked[r][c] = is_blocked
        if is_blocked_before == is_blocked:
            return
        
        self.km += manhattan(self.last, self.start)
        self.last = self.start
        self._update_vertex(s)
        for n in self._neighbors(s):
            self._update_vertex(n)
        
    def get_path(self):
        path = []
        cur = self.start
        visited = set()
        while cur != self.goal:
            path.append(cur)
            visited.add(cur)
            r, c = cur
            best = None
            bestv = INF
            for dr, dc in NEI4:
                nr, nc = r + dr, c + dc
                if inb(nr, nc, self.ROWS, self.COLS) and not self.blocked[nr][nc] and self.g[nr][nc] < bestv:
                    bestv = self.g[nr][nc]
                    best = (nr, nc)
            if best is None or best in visited: return []
            cur = best
        path.append(self.goal)
        return path

# ---------- 불 확산 로직 ----------
def spread_fire(fire_cells, blocked, ROWS, COLS):
    """
    기존 불의 모든 위치에서 인접한 곳으로 불을 퍼뜨린다.
    새로운 불이 생성될 위치 좌표 목록을 반환한다.
    """
    newly_lit_cells = set()
    current_fire_set = set(fire_cells)  # 빠른 검색을 위해 set으로 변환

    for r, c in fire_cells:
        for dr, dc in NEI4:
            nr, nc = r + dr, c + dc
            # 맵 범위 내에 있고 벽이나 기존 불이 없는 곳만 퍼질 수 있음
            if inb(nr, nc, ROWS, COLS) and not blocked[nr][nc] and (nr, nc) not in current_fire_set:
                newly_lit_cells.add((nr, nc))
    
    return list(newly_lit_cells)

# ---------- 시각화 ----------
def rc_to_cellrect(r, c, CELL, MARGIN):
    x = c * (CELL + MARGIN) + MARGIN
    y = r * (CELL + MARGIN) + MARGIN
    return x, y, CELL, CELL

def rc_center(r, c, CELL, MARGIN):
    x = c * (CELL + MARGIN) + MARGIN + CELL // 2
    y = r * (CELL + MARGIN) + MARGIN + CELL // 2
    return x, y

# 함수 정의에 selected_goal_idx 와 fire_cells 인자 추가
def draw_all(screen, blocked, path, goals, start, agent_pos, active_goal_idx, selected_goal_idx, fire_cells,
             mode, ROWS, COLS, CELL, MARGIN, BG, GRID, WALL,
             GOAL_COLORS, START_COLOR, PATH_COLOR, AGENT_COLOR, FIRE_COLOR, TEXT_COLOR,
             W, H, font):
    screen.fill(BG)
    # 격자/장애물
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, GRID, rc_to_cellrect(r, c, CELL, MARGIN))
            if blocked[r][c]:
                pygame.draw.rect(screen, WALL, rc_to_cellrect(r, c, CELL, MARGIN))
    # 경로 시각화
    for r, c in path:
        x, y, _, _ = rc_to_cellrect(r, c, CELL, MARGIN)
        pygame.draw.rect(screen, PATH_COLOR, (x + 4, y + 4, CELL - 8, CELL - 8), border_radius=4)
    # 목표들
    for i, g in enumerate(goals):
        color = GOAL_COLORS[i % len(GOAL_COLORS)]
        x, y, _, _ = rc_to_cellrect(*g, CELL, MARGIN)
        pygame.draw.rect(screen, color, (x + 2, y + 2, CELL - 4, CELL - 4), border_radius=4)
        if active_goal_idx == i:
            pygame.draw.rect(screen, (0, 0, 0), (x + 1, y + 1, CELL - 2, CELL - 2), width=2, border_radius=5)
    # 시작점
    x, y, _, _ = rc_to_cellrect(*start, CELL, MARGIN)
    pygame.draw.rect(screen, START_COLOR, (x + 2, y + 2, CELL - 4, CELL - 4), border_radius=4)
    # 불
    if fire_cells:
        for r, c in fire_cells:
            cx, cy = rc_center(r, c, CELL, MARGIN)
            pygame.draw.circle(screen, FIRE_COLOR, (cx, cy), CELL // 2 - 3)
    # 에이전트
    cx, cy = rc_center(*agent_pos, CELL, MARGIN)
    pygame.draw.circle(screen, AGENT_COLOR, (cx, cy), CELL // 2 - 3)

    # 상태바
    bar = pygame.Rect(0, H, W, 40)
    pygame.draw.rect(screen, (250, 250, 250), bar)
    msg = f"[1]Start [2]Edit Goal (G to cycle) [3]Fire [4]Obstacle | [SPACE] Plan  [R] Reset  [C] Clear | Active Goal: {(active_goal_idx + 1) if active_goal_idx is not None else '-'} / {len(goals)}"
    screen.blit(font.render(msg, True, TEXT_COLOR), (10, H + 10))
    mode_label = {1: "Place START", 2: "Edit GOAL (press G to select)", 3: "Place FIRE", 4: "Draw Obstacles"}.get(mode, "")
    screen.blit(font.render(f"Mode: {mode_label}", True, TEXT_COLOR), (10, H + 22))
    pygame.display.flip()

def cell_at_pos(px, py, H, CELL, MARGIN, ROWS, COLS):
    if py > H: return None
    c = px // (CELL + MARGIN)
    r = py // (CELL + MARGIN)
    if not inb(r, c, ROWS, COLS): return None
    return (r, c)

def choose_best_goal(blocked, start, goals, ROWS, COLS, fire_cells):
    """
    여러 개 goals 중 A* 길이가 가장 짧은 목표를 고른다.
    returns: (best_idx, best_goal_rc, best_len) 또는 (None, None, INF)
    """
    best_idx, best_goal, best_len = None, None, INF
    for i, g in enumerate(goals):
        L = astar_len(blocked, start, g, ROWS, COLS, fire_cells)
        if L < best_len:
            best_len = L
            best_goal = g
            best_idx = i
    return best_idx, best_goal, best_len

# ---------- 프리셋 벽 생성 함수 ----------
def build_blocked_with_presets(ROWS, COLS, presets):
    blocked = [[False] * COLS for _ in range(ROWS)]
    def _inb(r, c): return 0 <= r < ROWS and 0 <= c < COLS

    for w in presets:
        k = w.get('kind')
        if k == 'rect':
            r0, c0, r1, c1 = w['r0'], w['c0'], w['r1'], w['c1']
            if r0 > r1: r0, r1 = r1, r0
            if c0 > c1: c0, c1 = c1, c0
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if _inb(r, c): blocked[r][c] = True
        elif k == 'hline':
            r, c0, c1 = w['r'], w['c0'], w['c1']
            if c0 > c1: c0, c1 = c1, c0
            for c in range(c0, c1 + 1):
                if _inb(r, c): blocked[r][c] = True
        elif k == 'vline':
            c, r0, r1 = w['c'], w['r0'], w['r1']
            if r0 > r1: r0, r1 = r1, r0
            for r in range(r0, r1 + 1):
                if _inb(r, c): blocked[r][c] = True
        else:
            pass
    return blocked
