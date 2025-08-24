import heapq, math, pygame

NEI4=[(1,0),(-1,0),(0,1),(0,-1)]
INF=10**9

def inb(r,c, ROWS, COLS): return 0<=r<ROWS and 0<=c<COLS
def manhattan(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

# ---------- 빠른 목표 선택용 A* (길이만) ----------
def astar_len(blocked, start, goal, ROWS, COLS):
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
            if inb(nr,nc, ROWS, COLS) and not blocked[nr][nc]:
                ncst = cost+1
                if ncst < g[nr][nc]:
                    g[nr][nc]=ncst
                    heapq.heappush(pq,(ncst+manhattan((nr,nc),goal), ncst, (nr,nc)))
    return INF

# ---------- D* Lite ----------
class DStarLite:
    def __init__(self, blocked, start, goal, ROWS, COLS):
        self.blocked=blocked; self.start=start; self.goal=goal
        self.ROWS=ROWS; self.COLS=COLS
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
                if inb(nr,nc, self.ROWS, self.COLS) and not self.blocked[nr][nc]:
                    m=min(m, self.g[nr][nc]+1)
            self.rhs[r][c]=m
        if self.g[r][c]!=self.rhs[r][c]:
            self._insert(s, self._key(s))

    def _neighbors(self,s):
        r,c=s
        for dr,dc in NEI4:
            nr,nc=r+dr,c+dc
            if inb(nr,nc, self.ROWS, self.COLS) and not self.blocked[nr][nc]:
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
                if inb(nr,nc, self.ROWS, self.COLS) and not self.blocked[nr][nc] and self.g[nr][nc]<bestv:
                    bestv=self.g[nr][nc]; best=(nr,nc)
            if best is None or best in visited: return []
            cur=best
        path.append(self.goal); return path

# ---------- 시각화 ----------
def rc_to_cellrect(r,c, CELL, MARGIN):
    x=c*(CELL+MARGIN)+MARGIN; y=r*(CELL+MARGIN)+MARGIN
    return x,y,CELL,CELL

def rc_center(r,c, CELL, MARGIN):
    x=c*(CELL+MARGIN)+MARGIN + CELL//2
    y=r*(CELL+MARGIN)+MARGIN + CELL//2
    return x,y

def draw_all(screen, blocked, path, goalA, goalB, start, agent_pos, active_goal_name, mode, ROWS, COLS, CELL, MARGIN, BG, GRID, WALL, START, GOAL_A, GOAL_B, PATH, AGENT, TEXT, W, H, font):
    screen.fill(BG)
    # 격자/장애물
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, GRID, rc_to_cellrect(r,c, CELL, MARGIN))
            if blocked[r][c]:
                pygame.draw.rect(screen, WALL, rc_to_cellrect(r,c, CELL, MARGIN))
    # 경로 시각화
    for r,c in path:
        x,y,_,_ = rc_to_cellrect(r,c, CELL, MARGIN)
        pygame.draw.rect(screen, PATH, (x+4,y+4,CELL-8,CELL-8), border_radius=4)
    # 목표/시작
    for g,col in [(goalA,GOAL_A),(goalB,GOAL_B)]:
        x,y,_,_=rc_to_cellrect(*g, CELL, MARGIN)
        pygame.draw.rect(screen,col,(x+2,y+2,CELL-4,CELL-4),border_radius=4)
    x,y,_,_=rc_to_cellrect(*start, CELL, MARGIN)
    pygame.draw.rect(screen,START,(x+2,y+2,CELL-4,CELL-4),border_radius=4)
    # 에이전트(격자 중심에 원)
    cx,cy=rc_center(*agent_pos, CELL, MARGIN)
    pygame.draw.circle(screen, AGENT, (cx,cy), CELL//2-3)

    # 상태바
    bar=pygame.Rect(0,H,W,40); pygame.draw.rect(screen,(250,250,250),bar)
    msg=f"[1]Start [2]GoalA [3]GoalB [4]Obstacle | [SPACE] Plan  [R] Reset  [C] Clear | Active Goal: {active_goal_name or '-'}"
    screen.blit(font.render(msg,True,TEXT),(10,H+10))
    mode_msg={1:"Place START",2:"Place GOAL A",3:"Place GOAL B",4:"Draw Obstacles"}[mode]
    screen.blit(font.render(f"Mode: {mode_msg}",True,TEXT),(10,H+22))
    pygame.display.flip()

def cell_at_pos(px,py, H, CELL, MARGIN, ROWS, COLS):
    if py>H: return None
    c=px//(CELL+MARGIN); r=py//(CELL+MARGIN)
    if not inb(r,c, ROWS, COLS): return None
    return (r,c)

def choose_goal_quick(blocked, start, goalA, goalB, ROWS, COLS):
    lenA = astar_len(blocked, start, goalA, ROWS, COLS)
    lenB = astar_len(blocked, start, goalB, ROWS, COLS)
    if lenA <= lenB: return ("A", goalA)
    else: return ("B", goalB)
