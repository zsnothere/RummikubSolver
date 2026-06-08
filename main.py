import pygame

def getOptions(board, hand):
    o = []
    for i in board:
        for ii in i:
            o.append(ii)
    for i in hand:
        o.append(i)
    return o
    
def powerset(l):
    o = [[]]
    for i in l:
        o += [s+[i] for s in o]
    return o

def renderBoard(board, width=900, height=600, tileWidth=25, tileHeight=45, margin=10):
    colors = {
        1: (220, 60, 60),
        2: (60, 120, 220),
        3: (60, 180, 90),
        4: (240, 200, 60),
        0: (180, 180, 180)
    }
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Rummikub Board")
    font = pygame.font.SysFont(None, 28)
    screen.fill((30, 30, 30))
    start = margin
    y = margin
    for i in board:
        x = start
        for ii in i:
            rect = pygame.Rect(x,y,tileWidth,tileHeight)
            pygame.draw.rect(screen, colors[ii[1]], rect, border_radius=6)
            pygame.draw.rect(screen, (20, 20, 20), rect, 2, border_radius=6)
            label = "J" if ii[0] == 0 else str(ii[0])
            text = font.render(label, True, (20, 20, 20))
            textRect = text.get_rect(center=rect.center)
            screen.blit(text, textRect)
            x += tileWidth
        y += tileHeight+15
        if y > height-tileHeight-margin:
            y = margin
            start += 500
        pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

class config:
    def __init__(self, board, options):
        self.board = board
        self.options = sorted(options, key=lambda x: x[0])
        self.branches = []
    def copy(self):
        return config([i.copy() for i in self.board], self.options.copy())
    def validRun(self, run):
        colors = []
        a, b = True, True
        for i in range(len(run)):
            if a and (run[i][0] == run[0][0] or run[i][0]==0) and len(run)<5:
                if (run[i][1] in colors) and run[0][1]!=0: a = False
                else: colors.append(run[i][1])
            else: a = False
            A = (run[i][0] == run[i-1][0]+1) # not a joker
            B = run[0][0] == 0 and i == 1 # joker at the start
            C = i>1 and (run[i-2][0] == run[i][0]-2 and run[i-1][0] == 0) # joker in the middle
            D = run[i][0]==0 # joker at the end (not implemented yet)
            if i>0 and b and (A or B or C or D):
                if ((run[-1][1] not in [run[i][1], 0]) or (run[(i+1)%len(run)][1] not in [run[i][1], 0])) and run[i][1]!=0: b = False
            elif i>0: b = False
            if not (a or b): return False
        return True
    def isValid(self):
        for i in self.board:
            if not self.validRun(i): return False
        return True
    def tryBranch(self):
        self.branches = []
        if len(self.board)>0:
            for i in range(len(self.board)):
                n = self.copy()
                try:
                    n.board[i].append(self.options[0])
                    n.options.remove(self.options[0])
                    if n.isValid(): self.branches.append(n)
                except IndexError as e:
                    pass
        n = self.copy()
        try:
            n.board.append([self.options[0]])
            n.options.remove(self.options[0])
            if n.isValid(): self.branches.append(n)
        except IndexError as e:
            pass
    def isSolution(self):
        for i in self.board:
            if len(i)<3: return False # This will only run on valid configs, so this is all that needs to be tested.
        return len(self.options)==0
    def signature(self):
        return (
            tuple(tuple(sorted(i)) for i in self.board),
            tuple(sorted(self.options, key=lambda x: (x[0], x[1])))
        )
    def solve(self, seen=None):
        if seen==None:
            seen = set()
        s = self.signature()
        if s in seen: return []
        seen.add(s)
        if self.isSolution():
            return self
        self.tryBranch()
        for i in self.branches:
            o = i.solve(seen=seen)
            if o and o.isSolution(): return o
        return []
    def __repr__(self):
        return str(self.board)

class solver:
    def __init__(self, board, hand, t=False):
        if t:
            o = []
            for i in powerset(hand):
                if config([], getOptions(board, hand)).validRun(i) and sum([ii[0] for ii in i])>29:
                    self.solution = [i]
                    return
            self.solution = "draw"
        else:
            self.solution = False
            self.configs = []
            for i in powerset(hand)[1:]:
                self.configs.append(config(board, i))
    def solve(self):
        if self.solution: return self.solution
        for i in self.configs[::-1]:
            s = i.solve()
            if s!=[] and s.isSolution(): return s
        return "draw"

board = [
    [(1, 1), (2, 1), (3, 1), (4, 1)],
    [(5, 2), (6, 2), (7, 2), (8, 2)],
    [(2, 3), (3, 3), (4, 3), (5, 3)],
    [(9, 4), (10, 4), (11, 4), (12, 4), (13, 4)],
    [(6, 1), (7, 1), (8, 1)],
    [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2)],
    [(9, 1), (9, 2), (9, 3), (0, 0)],
    [(10, 1), (10, 2), (10, 3), (10, 4)],
    [(11, 1), (11, 2), (11, 3)],
    [(12, 1), (12, 2), (12, 3), (12, 4)],
    [(7, 2), (7, 3), (7, 4)],
    [(8, 1), (8, 2), (8, 3)],
    [(13, 1), (12, 1), (11, 1), (0, 0)][::-1],
    [(6, 3), (6, 4), (6, 1)],
    [(3, 4), (4, 4), (5, 4), (6, 4)]
]
hand = [
    (1, 3),
    (4, 4),
    (5, 1),
    (8, 4),
    (9, 2),
    (11, 4),
    (0, 0),
    (2, 1)
]

c = solver(board, hand)
s = c.solve()
print("Solved")
print(s)
if type(s) == config: renderBoard(s.board)