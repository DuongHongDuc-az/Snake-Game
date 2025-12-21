import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size) # Two hidden layers for better calculating
        self.stream1 = nn.Linear(hidden_size, 1) # Evaluate current state
        self.stream2 = nn.Linear(hidden_size, output_size) # Evaluate the advantage of each action

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        val = self.stream1(x)
        act = self.stream2(x)
        if act.dim() == 1:
            q_values = val + (act - act.mean())
        else:
            q_values = val + (act - act.mean(dim=1, keepdim=True))
        return q_values

    def save(self, file_name = 'model.pth'):
        model_folder_path = os.path.dirname(__file__)
        model_path = os.path.join(model_folder_path)
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    def load(self, file_name='model.pth'):
        model_folder_path = os.path.dirname(__file__)
        file_path = os.path.join(model_folder_path, file_name)
        if os.path.exists(file_path):
            saved_state = torch.load(file_path)
            self.load_state_dict(saved_state)
            return True
        else:
            return False

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss() #Loss function

    def train_step(self, state, action, reward, next_state, game_over):
        state = torch.tensor(np.array(state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            next_state = torch.unsqueeze(next_state, 0)
            game_over = (game_over, )

        # Bellman Equation -> Loss function
        pred = self.model(state)
        target = pred.clone()
        for idx in range(len(game_over)):
            Q_new = reward[idx]
            if not game_over[idx]:
                state_tensor = next_state[idx].unsqueeze(0)
                with torch.no_grad():
                    Q_next = torch.max(self.model(state_tensor))
                Q_new = reward[idx] + self.gamma * Q_next
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()