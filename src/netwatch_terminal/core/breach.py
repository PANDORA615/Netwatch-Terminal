"""Original multi-sequence timed puzzle with a guaranteed solution."""
import random


class Puzzle:
    size=7
    capacity=6
    duration=60.0
    def __init__(self,seed=None):
        rng=random.Random(seed); codes=['1C','55','E9','BD','7A','FF']
        self.grid=[[rng.choice(codes) for _ in range(self.size)] for _ in range(self.size)]
        route=[(0,rng.randrange(self.size))]
        for step in range(1,self.capacity):
            r,c=route[-1]
            options=[(x,c) for x in range(self.size)] if step%2 else [(r,x) for x in range(self.size)]
            route.append(rng.choice([p for p in options if p not in route]))
        self.solution=route; sequence=[self.grid[r][c] for r,c in route]
        self.targets=[sequence[:3],sequence[2:5],sequence[3:6]]
        self.target=self.targets[0]; self.moves=[]; self.expired=False
    @property
    def buffer(self):return [self.grid[r][c] for r,c in self.moves]
    @property
    def completed(self):
        b=self.buffer
        return [any(b[i:i+len(target)]==target for i in range(len(b)-len(target)+1)) for target in self.targets]
    @property
    def won(self):return all(self.completed)
    @property
    def finished(self):return self.won or self.expired or len(self.moves)>=self.capacity
    def allowed(self,r,c):
        if not (0<=r<self.size and 0<=c<self.size) or self.finished or (r,c) in self.moves:return False
        if not self.moves:return r==0
        row,col=self.moves[-1]; return c==col if len(self.moves)%2 else r==row
    def choose(self,r,c):
        if not self.allowed(r,c):raise ValueError('Invalid move')
        self.moves.append((r,c))
    def restart(self):self.moves=[]; self.expired=False
