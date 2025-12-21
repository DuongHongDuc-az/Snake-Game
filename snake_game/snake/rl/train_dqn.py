from snake.rl.agent_dqn import Agent
def train(game):
    record = 0
    agent = Agent()
    while game.running:
        #get old state
        state_old = agent.get_state(game)

        #get move
        final_move = agent.get_action(state_old)

        reward, game_over, score = game.get_move(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
            if agent.n_games % 20 == 0:
                agent.model.save()

            # print('Game', agent.n_games, 'Score', score, 'Record', record)

        game.handle_events()
        game.draw("Player")
        game.clock.tick(game.speed)

def play(game):
    agent = Agent()
    while game.running:
        state = agent.get_state(game)
        move = agent.get_action(state)
        reward, game_over, score = game.get_move(move)
        if game_over:
            game.running = False
        game.handle_events()
        game.draw("Player")
        game.clock.tick(game.speed)