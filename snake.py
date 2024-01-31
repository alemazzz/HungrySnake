import numpy as np
import random, pygame

class Color:
    def __init__(self):
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        
class Snake:
    def __init__(self):
        
        self.scale = 1
        self.padding = 100 * self.scale
        self.game_width, self.game_height = 600 * self.scale, 600 * self.scale
        
        self.snake_size = 30 * self.scale
        self.food_size = 30 * self.scale
        
        self.screen_width, self.screen_height = self.game_width, self.game_height + self.padding
        self.board = np.zeros((self.game_height // self.snake_size, self.game_width // self.snake_size))
        
        self.dir = 'right'
        self.x, self.y = (self.game_width // 2, self.game_height // 2)
        self.c, self.r = self.coords_to_index(self.x, self.y)
        
        self.food_r, self.food_c = self.generate_food()
        self.board[self.food_r][self.food_c] = 2
        self.board[self.r][self.c] = 1
        
        self.c_change = 1
        self.r_change = 0
        
        self.color = Color()
        self.score = 0
        self.game_over = False
        
        self.pygame = pygame
        self.pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
    
    def available_actions(self):
        return [0, 1, 2, 3]
    
    def get_state(self):
        state = []
        
        state.append(int(self.dir == 'left'))
        state.append(int(self.dir == 'right'))
        state.append(int(self.dir == 'up'))
        state.append(int(self.dir == 'down'))
        state.append(int(self.c > self.food_c)) # LEFT
        state.append(int(self.c < self.food_c)) # RIGHT
        state.append(int(self.r < self.food_r)) # DOWN
        state.append(int(self.r > self.food_r)) # UP
        state.append(self.is_unsafe(self.r, self.c-1))
        state.append(self.is_unsafe(self.r, self.c+1))
        state.append(self.is_unsafe(self.r-1, self.c))
        state.append(self.is_unsafe(self.r+1, self.c))
        
        return state
    
    def coords_to_index(self, x, y):
        c = int(x / self.snake_size)
        r = int(y / self.snake_size) 
        
        return c, r
    
    def index_to_coords(self, r, c):
        x = c * self.snake_size
        y = r * self.snake_size
        
        return x, y
    
    def is_unsafe(self, r, c):
        if self.valid_index(r, c):
            if self.board[r][c] == 1:
                return 1
            return 0
        else:
            return 0
    
    def valid_index(self, r, c):
        return 0 <= r < len(self.board) and 0 <= c < len(self.board[0])
    
    def generate_food(self):
        food_c = int(round(random.randrange(0, self.game_width - self.food_size) / self.food_size))
        food_r = int(round(random.randrange(0, self.game_height - self.food_size) / self.food_size))
        
        if self.board[food_r][food_c] == 1:
            food_r, food_c = self.generate_food()
        
        return food_r, food_c
    
    def draw_snake(self):
        r, c = self.r, self.c
        x, y = self.index_to_coords(r, c)
        
        pygame.draw.rect(self.screen, self.color.blue, [x, y, self.snake_size, self.snake_size])
        
    def print_score(self):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(f'Score: {self.score}', True, self.color.white)
        self.screen.blit(text, (self.padding/2, self.screen_height-self.padding/2))
        
    def take_action(self, action='None'):
        
        if action == 'None':
            action = random.choice(['right', 'left', 'up', 'down'])
        else:
            action = ['right', 'left', 'up', 'down'][action]
        
        self.last_dir = self.dir
        
        if action == "left":
            self.c_change = -1
            self.r_change = 0
            self.dir = "left"
        elif action == "right":
            self.c_change = 1
            self.r_change = 0
            self.dir = "right"
        elif action == "up":
            self.r_change = -1
            self.c_change = 0
            self.dir = "up"
        elif action == "down":
            self.r_change = 1
            self.c_change = 0
            self.dir = "down"
            
        if self.c >= (self.game_width // self.snake_size) or self.r >= (self.game_height // self.snake_size) or self.c < 0 or self.r < 0:
            self.game_over = True
            
        if self.valid_index(self.r, self.c):    
            self.board[self.r][self.c] = 0
        
        self.c += self.c_change
        self.r += self.r_change
        
        food_x, food_y = self.index_to_coords(self.food_r, self.food_c)
        pygame.draw.rect(self.screen, self.color.red, [food_x, food_y, self.food_size, self.food_size])
        
        if self.valid_index(self.r, self.c):
            self.board[self.r][self.c] = 1
        
        self.draw_snake()
        
        self.screen.fill(self.color.black)
        
        self.draw_snake()
        
        self.print_score()
        
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                x, y = self.index_to_coords(row, col)
                pygame.draw.rect(self.screen, self.color.white, [x, y, (self.snake_size*self.scale), (self.snake_size*self.scale)], 1)
        
        food_x, food_y = self.index_to_coords(self.food_r, self.food_c)
        pygame.draw.rect(self.screen, self.color.red, [food_x, food_y, self.food_size, self.food_size])
        
        pygame.display.update()
        
        if self.c == self.food_c and self.r == self.food_r:
            self.food_r, self.food_c = self.generate_food()
            self.board[self.food_r][self.food_c] = 0
            self.score += 1
        
    def reset(self):
        self.score = 0
        self.dir = 'right'
        self.x, self.y = (self.game_width // 2, self.game_height // 2)
        self.c, self.r = self.coords_to_index(self.x, self.y)
        self.food_r, self.food_c = self.generate_food()
        self.c_change = 1
        self.r_change = 0
        self.game_over = False