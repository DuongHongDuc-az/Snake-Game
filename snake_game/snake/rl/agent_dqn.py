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

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #for randomness
        self.load_completed = False
        self.gamma = 0.95 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11,256,3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        if self.model.load():
            self.load_completed = True
            print('Load completed')
        else:
            print('Load failed')

    def get_state(self, game):
        CELL_SIZE = game.cell_size
        headx, heady = game.snake.body[0]
        foodx, foody = game.food.position
        # MAX_DIST = game.play_width + game.play_height
        # normalized_dist = (abs(foodx - headx) + abs(foody - heady)) / MAX_DIST
        point_l = Point(headx - CELL_SIZE, heady)
        point_r = Point(headx + CELL_SIZE, heady)
        point_u = Point(headx, heady - CELL_SIZE)
        point_d = Point(headx, heady + CELL_SIZE)

        dir_l = game.snake.direction == Direction.LEFT.value
        dir_r = game.snake.direction == Direction.RIGHT.value
        dir_u = game.snake.direction == Direction.UP.value
        dir_d = game.snake.direction == Direction.DOWN.value

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

            foodx < headx, #food left
            foodx > headx, #food right
            foody < heady, #food up
            foody > heady #food down
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
        self.epsilon = 0
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
