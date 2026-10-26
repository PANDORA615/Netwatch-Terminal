"""Original deterministic, solvable alternating row/column puzzle."""
import random


class Puzzle:
    def __init__(self, seed=None):
        rng = random.Random(seed)
        codes = ['1C','55','E9','BD','7A','FF']
        self.grid = [[rng.choice(codes) for _ in range(5)] for _ in range(5)]
        route = [(0, rng.randrange(5))]
        for step in range(1,6):
            r,c = route[-1]
            options = [(x,c) for x in range(5)] if step % 2 else [(r,x) for x in range(5)]
            route.append(rng.choice([p for p in options if p not in route]))
        self.solution = route
        self.target = [self.grid[r][c] for r,c in route[:3]]
        self.moves = []

    def allowed(self, r,c):
        if self.finished or (r,c) in self.moves: return False
        if not self.moves: return r == 0
        row,col = self.moves[-1]
        return c == col if len(self.moves) % 2 else r == row

    @property
    def buffer(self):
        return [self.grid[r][c] for r,c in self.moves]

    @property
    def won(self):
        b = self.buffer
        return any(b[i:i+len(self.target)] == self.target for i in range(len(b)-len(self.target)+1))

    @property
    def finished(self):
        return self.won or len(self.moves) >= 6

    def choose(self,r,c):
        if not self.allowed(r,c): raise ValueError('Invalid move')
        self.moves.append((r,c))
