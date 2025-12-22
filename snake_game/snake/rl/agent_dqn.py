import torch
import random
import numpy as np
from enum import Enum
from collections import namedtuple
from collections import deque
from snake.rl.dqn_model import Linear_QNet, QTrainer

class Direction(Enum):
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    UP = "UP"
    DOWN = "DOWN"

Point = namedtuple("Point", ["x", "y"])

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001

def free(game, start, limit=None):
    snake_set = set(tuple(x) for x in game.snake.body)
    vst = set([start])
    q = deque([start])
    BLOCK_SIZE = game.cell_size
    bx, by, bw, bh = game.bounds

    free = 0

    while q:
        p = q.popleft()
        free += 1
        if limit and free >= limit:
            return free
        for dx, dy in ((BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)):
            np = Point(p.x + dx, p.y + dy)
            
            if p.x < bx or p.x >= bx + bw or p.y < by or p.y >= by + bh and np not in snake_set and np not in vst:
                vst.add(np)
                q.append(np)

    return free

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #for randomness
        self.load_completed = False
        self.gamma = 0.95 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(14,128,3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        if self.model.load():
            self.load_completed = True
            print('Load completed')
        else:
            print('Load failed')

    def get_state(self, game):
        BLOCK_SIZE = game.cell_size
        head = Point(game.snake.body[0][0], game.snake.body[0][1])
        foodx, foody = game.food.position
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)

        dir_l = game.snake.direction == Direction.LEFT.value
        dir_r = game.snake.direction == Direction.RIGHT.value
        dir_u = game.snake.direction == Direction.UP.value
        dir_d = game.snake.direction == Direction.DOWN.value

        if dir_r:
            next_front = Point(head.x + BLOCK_SIZE, head.y)
            next_left  = Point(head.x, head.y - BLOCK_SIZE)
            next_right = Point(head.x, head.y + BLOCK_SIZE)
        elif dir_l:
            next_front = Point(head.x - BLOCK_SIZE, head.y)
            next_left  = Point(head.x, head.y + BLOCK_SIZE)
            next_right = Point(head.x, head.y - BLOCK_SIZE)
        elif dir_u:
            next_front = Point(head.x, head.y - BLOCK_SIZE)
            next_left  = Point(head.x - BLOCK_SIZE, head.y)
            next_right = Point(head.x + BLOCK_SIZE, head.y)
        else:  # dir_d
            next_front = Point(head.x, head.y + BLOCK_SIZE)
            next_left  = Point(head.x + BLOCK_SIZE, head.y)
            next_right = Point(head.x - BLOCK_SIZE, head.y)


        safe_front = free(game, next_front, limit=game.snake.length) >= game.snake.length
        safe_left  = free(game, next_left,  limit=game.snake.length) >= game.snake.length
        safe_right = free(game, next_right, limit=game.snake.length) >= game.snake.length

        state = [
            (dir_l and game.is_collision(game.bounds, point_l)) or
            (dir_r and game.is_collision(game.bounds, point_r)) or
            (dir_u and game.is_collision(game.bounds, point_u)) or
            (dir_d and game.is_collision(game.bounds, point_d)),

            (dir_u and game.is_collision(game.bounds, point_r)) or
            (dir_r and game.is_collision(game.bounds, point_d)) or
            (dir_d and game.is_collision(game.bounds, point_l)) or
            (dir_l and game.is_collision(game.bounds, point_u)),

            (dir_l and game.is_collision(game.bounds, point_d)) or
            (dir_r and game.is_collision(game.bounds, point_u)) or
            (dir_u and game.is_collision(game.bounds, point_l)) or
            (dir_d and game.is_collision(game.bounds, point_r)),

            dir_l, dir_r, dir_u, dir_d,

            foodx < head.x, #food left
            foodx > head.x, #food right
            foody < head.y, #food up
            foody > head.y, #food down

            safe_front, safe_left, safe_right
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            minibatch = random.sample(self.memory, BATCH_SIZE)
        else:
            minibatch = self.memory
        states, actions, rewards, next_stages, game_overs = zip(*minibatch)
        self.trainer.train_step(states, actions, rewards, next_stages, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        #The more games we have, the less likely random values will fall below the epsilon, and when epsilon becomes negative, we no longer use random move.
        self.epsilon = 0 # max(0.02, 1 - self.n_games/600)
        final_move = [0, 0, 0]
        if random.random() < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move
