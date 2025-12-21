from snake.rl.agent_dqn import Agent
from snake.rl.helper import plot
def train(game):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
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

            print('Game', agent.n_games, 'Score', score, 'Record', record)
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

        game.handle_events()
        game.draw("Player")
        game.clock.tick(game.speed)
