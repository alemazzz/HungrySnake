import numpy as np
import random
from snake import Snake
import sys
import pickle

class SnakeAI:
    
    def __init__(self):
        self.env = Snake()
        self.alpha = 0.5
        self.epsilon = 0
        self.table = dict()
    

    def get_q_value(self, state, action):
        for couple in self.table:
            if couple == (tuple(state), action):
                return self.table[couple]
        return 0
    
    def update_q_value(self, state, action, old_q, reward, future_rewards):
        self.table[(tuple(state), action)] = old_q + self.alpha * (reward + future_rewards - old_q)
    
    def future_rewards(self, state):
        max_q = float('-inf')

        for action in self.env.available_actions():
            max_q = self.get_q_value(state, action) if self.get_q_value(state, action) > max_q else max_q
        
        return 0 if max_q == float('-inf') else max_q
    
    def update(self, state, action, new_state, reward):
        old = self.get_q_value(state, action)
        future_rewards = self.future_rewards(new_state)
        self.update_q_value(state, action, old, reward, future_rewards)
    
    def choose_action(self, state, epsilon=True):
        max_q = float('-inf')
        
        if epsilon and random.random() < self.epsilon:
            return random.choice(self.env.available_actions())
        else:
            for action in self.env.available_actions():
                if self.get_q_value(state, action) > max_q:
                    max_q = self.get_q_value(state, action)
                    best_action = action
            return best_action 
    
    
def main(p, epochs=300):
    ai = SnakeAI()
    
    if p in ['Play', 'play', 'p']:
        play(ai, epochs)
    elif p in ['Evaluate', 'evaluate', 'e']:
        evaluate(ai, epochs)
    elif p in ['Train', 'train', 't']:
        for i in range(int(epochs)):
            print(f"Playing training game {i + 1}")
            
            while ai.env.game_over == False:
                
                ai.env.clock.tick(120)
                
                for event in ai.env.pygame.event.get():
                    if event.type == ai.env.pygame.QUIT:
                        ai.env.pygame.quit()
                
                state = ai.env.get_state()
                action = ai.choose_action(state)
                
                last_score = ai.env.score
                
                ai.env.take_action(action)
                new_state = ai.env.get_state()
                new_score = ai.env.score
                
                if new_score > last_score: # snake eat an apple
                    ai.update(state, action, new_state, +1)
                
                directions = {'right': 0, 'left': 1, 'up': 2, 'down': 3} # available directions
                dict_dir = {1: new_state[4], 0: new_state[5], 3: new_state[6], 2: new_state[7]} # map the directions to the food pos to set the rewards
                
                if dict_dir[directions[ai.env.dir]] == 0: # Nessun cibo in questa direzione -> punishment
                    ai.update(state, action, new_state, -0.1)  
                else: # Cibo per questa direzione
                    ai.update(state, action, new_state, +0.05)     
                        
                if ai.env.game_over == True: # Morte
                    ai.update(state, action, new_state, -10)
                    
                if ai.env.game_over == True: # Game over: reset the snake score, positions.
                    print(f'Last state: {state}\nScore: {ai.env.score}')
                    ai.env.reset()
                    break
                
                if ai.env.score >= 200: # snake is intelligent
                    print(f'Last state: {state}\nScore: {ai.env.score}')
                    ai.env.reset()
                    break
        
        # Save the model to a file:
        with open(f"./models/trained_{epochs}.pkl","wb") as f:
            pickle.dump(ai.table, f)

def play(ai, epochs):
    with open(f'./models/trained_{epochs}.pkl', 'rb') as f:
        ai.table = pickle.load(f)
        
    while ai.env.game_over == False:
        
        ai.env.clock.tick(5)
        
        for event in ai.env.pygame.event.get():
            if event.type == ai.env.pygame.QUIT:
                ai.env.pygame.quit()
        
        state = ai.env.get_state()
        action = ai.choose_action(state)
        last_score = ai.env.score
        
        ai.env.take_action(action)
        
        if ai.env.game_over:
            print(f'Score: {last_score}')
            
def evaluate(ai, epochs):
    scores = list()
    with open(f'./models/trained_{epochs}.pkl', 'rb') as f:
        ai.table = pickle.load(f)
    
    for i in range(100):
        while ai.env.game_over == False:
        
            ai.env.clock.tick(240)
            
            for event in ai.env.pygame.event.get():
                if event.type == ai.env.pygame.QUIT:
                    ai.env.pygame.quit()
            
            state = ai.env.get_state()
            action = ai.choose_action(state)
            
            ai.env.take_action(action)
            
            if ai.env.game_over == True:
                scores.append(ai.env.score)
                ai.env.reset()
                break
            
            if ai.env.score >= 200:
                scores.append(ai.env.score)
                ai.env.reset()
                break
            
    total = 0
    for score in scores:
        total += score
        
    print(f'Avarage score: {total/100}')
    
if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        print('Usage: python ai.py Train/Play n_epochs')
        
    