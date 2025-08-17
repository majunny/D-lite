import sys, math, heapq, pygame

# ===== 설정 =====
CELL=22; ROWS, COLS=25, 35; MARGIN=1; FPS=60
STEP_INTERVAL = 0.3   # <<< 0.3초마다 격자 한 칸 이동
PLANNER_STEPS_PER_FRAME = 1200  # 프레임당 D* Lite 처리 스텝(GUI 프리즈 방지)

# 색상
BG=(245,246,248); GRID=(220,223,230); WALL=(60,72,88)
START=(52,152,219); GOAL_A=(46,204,113); GOAL_B=(241,196,15)
PATH=(155,89,182); AGENT=(231,76,60); TEXT=(33,33,33)

NEI4=[(1,0),(-1,0),(0,1),(0,-1)]
INF=10**9

def inb(r,c): return 0<=r<ROWS and 0<=c<COLS
def manhattan(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

# ---------- 빠른 목표 선택용 A* (길이만) ----------
def astar_len(blocked, start, goal):
    if blocked[goal[0]][goal[1]]: return INF
    g = [[INF]*COLS for _ in range(ROWS)]
    g[start[0]][start[1]] = 0
    pq = [(manhattan(start,goal), 0, start)]
    while pq:
        f, cost, (r,c) = heapq.heappop(pq)
        if (r,c)==goal: return cost
        if cost!=g[r][c]: continue
        for dr,dc in NEI4:
            nr, nc = r+dr, c+dc
            if inb(nr,nc) and not blocked[nr][nc]:
                ncst = cost+1
                if ncst < g[nr][nc]:
                    g[nr][nc]=ncst
                    heapq.heappush(pq,(ncst+manhattan((nr,nc),goal), ncst, (nr,nc)))
    return INF

# ---------- D* Lite ----------
class DStarLite:
    def __init__(self, blocked, start, goal):
        self.blocked=blocked; self.start=start; self.goal=goal
        self.g=[[INF]*COLS for _ in range(ROWS)]
        self.rhs=[[INF]*COLS for _ in range(ROWS)]
        self.rhs[goal[0]][goal[1]]=0
        self.U=[]; self.km=0; self.last=start
        self._insert(goal, self._key(goal))

    def _key(self,s):
        r,c=s
        val=min(self.g[r][c], self.rhs[r][c])
        return (val + manhattan(self.start,s) + self.km, val)

    def _insert(self,s,k): heapq.heappush(self.U,(k,s))
    def _top_key(self): return self.U[0][0] if self.U else (INF,INF)

    def _update_vertex(self, s):
        r,c=s
        if s!=self.goal:
            m=INF
            for dr,dc in NEI4:
                nr,nc=r+dr,c+dc
                if inb(nr,nc) and not self.blocked[nr][nc]:
                    m=min(m, self.g[nr][nc]+1)
            self.rhs[r][c]=m
        if self.g[r][c]!=self.rhs[r][c]:
            self._insert(s, self._key(s))

    def _neighbors(self,s):
        r,c=s
        for dr,dc in NEI4:
            nr,nc=r+dr,c+dc
            if inb(nr,nc) and not self.blocked[nr][nc]:
                yield (nr,nc)

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

    def get_path(self):
        path=[]; cur=self.start; visited=set()
        while cur!=self.goal:
            path.append(cur); visited.add(cur)
            r,c=cur; best=None; bestv=INF
            for dr,dc in NEI4:
                nr,nc=r+dr,c+dc
                if inb(nr,nc) and not self.blocked[nr][nc] and self.g[nr][nc]<bestv:
                    bestv=self.g[nr][nc]; best=(nr,nc)
            if best is None or best in visited: return []
            cur=best
        path.append(self.goal); return path

# ---------- 시각화 ----------
def rc_to_cellrect(r,c):
    x=c*(CELL+MARGIN)+MARGIN; y=r*(CELL+MARGIN)+MARGIN
    return x,y,CELL,CELL

def rc_center(r,c):
    x=c*(CELL+MARGIN)+MARGIN + CELL//2
    y=r*(CELL+MARGIN)+MARGIN + CELL//2
    return x,y

W = COLS*CELL + (COLS+1)*MARGIN
H = ROWS*CELL + (ROWS+1)*MARGIN

pygame.init()
screen=pygame.display.set_mode((W,H+40))
clock=pygame.time.Clock()
font=pygame.font.SysFont("Arial",16)

# ---------- 상태 ----------
blocked=[[False]*COLS for _ in range(ROWS)]
start=(ROWS//2,2); goalA=(ROWS//2-6, COLS-4); goalB=(ROWS//2+6, COLS-4)
mode=1
planning=False
planner=None; plan_gen=None; path=[]
active_goal_name=None
agent_pos=start
step_timer=0.0
dragging=False

def draw_all():
    screen.fill(BG)
    # 격자/장애물
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, GRID, rc_to_cellrect(r,c))
            if blocked[r][c]:
                pygame.draw.rect(screen, WALL, rc_to_cellrect(r,c))
    # 경로 시각화
    for r,c in path:
        x,y,_,_ = rc_to_cellrect(r,c)
        pygame.draw.rect(screen, PATH, (x+4,y+4,CELL-8,CELL-8), border_radius=4)
    # 목표/시작
    for g,col in [(goalA,GOAL_A),(goalB,GOAL_B)]:
        x,y,_,_=rc_to_cellrect(*g)
        pygame.draw.rect(screen,col,(x+2,y+2,CELL-4,CELL-4),border_radius=4)
    x,y,_,_=rc_to_cellrect(*start)
    pygame.draw.rect(screen,START,(x+2,y+2,CELL-4,CELL-4),border_radius=4)
    # 에이전트(격자 중심에 원)
    cx,cy=rc_center(*agent_pos)
    pygame.draw.circle(screen, AGENT, (cx,cy), CELL//2-3)

    # 상태바
    bar=pygame.Rect(0,H,W,40); pygame.draw.rect(screen,(250,250,250),bar)
    msg=f"[1]Start [2]GoalA [3]GoalB [4]Obstacle | [SPACE] Plan  [R] Reset  [C] Clear | Active Goal: {active_goal_name or '-'}"
    screen.blit(font.render(msg,True,TEXT),(10,H+10))
    mode_msg={1:"Place START",2:"Place GOAL A",3:"Place GOAL B",4:"Draw Obstacles"}[mode]
    screen.blit(font.render(f"Mode: {mode_msg}",True,TEXT),(10,H+22))
    pygame.display.flip()

def cell_at_pos(px,py):
    if py>H: return None
    c=px//(CELL+MARGIN); r=py//(CELL+MARGIN)
    if not inb(r,c): return None
    return (r,c)

def choose_goal_quick():
    lenA = astar_len(blocked, start, goalA)
    lenB = astar_len(blocked, start, goalB)
    if lenA <= lenB: return ("A", goalA)
    else: return ("B", goalB)

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
                name,goal = choose_goal_quick()
                active_goal_name=name
                planner = DStarLite(blocked, start, goal)
                plan_gen = planner.compute_generator()
                planning=True; path=[]; agent_pos=start; step_timer=0.0
            elif e.key==pygame.K_r:
                agent_pos=start; step_timer=0.0
            elif e.key==pygame.K_c:
                blocked=[[False]*COLS for _ in range(ROWS)]
                start=(ROWS//2,2); goalA=(ROWS//2-6, COLS-4); goalB=(ROWS//2+6, COLS-4)
                planner=None; plan_gen=None; planning=False; path=[]; active_goal_name=None
                agent_pos=start; step_timer=0.0
        elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            rc=cell_at_pos(*e.pos)
            if rc:
                r,c=rc
                if mode==1 and not blocked[r][c]: start=(r,c)
                elif mode==2 and not blocked[r][c]: goalA=(r,c)
                elif mode==3 and not blocked[r][c]: goalB=(r,c)
                elif mode==4: blocked[r][c]=not blocked[r][c]; dragging=True
                # 맵 변경 시 재계획 준비
                if planning:
                    name,goal = choose_goal_quick()
                    active_goal_name=name
                    planner = DStarLite(blocked, start, goal)
                    plan_gen = planner.compute_generator()
                    path=[]; step_timer=0.0
        elif e.type==pygame.MOUSEBUTTONUP and e.button==1:
            dragging=False
        elif e.type==pygame.MOUSEMOTION and dragging and mode==4:
            rc=cell_at_pos(*e.pos)
            if rc:
                r,c=rc
                if not blocked[r][c]:
                    blocked[r][c]=True
                    if planning:
                        name,goal = choose_goal_quick()
                        active_goal_name=name
                        planner = DStarLite(blocked, start, goal)
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
                    name,goal = choose_goal_quick()
                    active_goal_name=name
                    planner = DStarLite(blocked, start, goal)
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

    draw_all()

pygame.quit(); sys.exit(0)
