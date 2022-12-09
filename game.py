from asyncio.windows_events import NULL
import pygame
import random
import os
import time
import neat
import pickle
from math import sqrt

pygame.font.init()

WIN_WIDTH = 700
WIN_HEIGHT = 550
STAT_FONT = pygame.font.SysFont("", 40)

SHIP_IMG = pygame.image.load(os.path.join("imgs", "ship.png"))
ALIEN_SHIP_IMGS = [pygame.image.load(os.path.join("imgs", "alien_ship1.png")), pygame.image.load(os.path.join("imgs", "alien_ship2.png")), pygame.image.load(os.path.join("imgs", "alien_ship_death.png"))]
BULLET_IMG = pygame.image.load(os.path.join("imgs", "bullet.png"))
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png"))
BLACK_BG_IMG = pygame.image.load(os.path.join("imgs", "black_bg.png"))

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

alien_ships = []
ship_bullets = []
alien_ship_bullets = []

class Bullet:
    WIDTH = 10
    HEIGHT = 10
    IMG = BULLET_IMG
    SPEED = 20
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    
    def move(self, direction):
        
        d = self.y + direction*self.SPEED
        if d < -10:
            self.destroy()
        elif d > 550:
            self.destroy()
        else:
            self.y = d
        
    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))
        
    def collide_ship(self, ship):
        ship_mask = ship.get_mask()
        bullet_mask = pygame.mask.from_surface(self.IMG)
        offset = (self.x - round(ship.x), round(self.y) - ship.y)
        
        overlap_point = ship_mask.overlap(bullet_mask, offset)
        
        if overlap_point: 
            return True
        
        return False
    
    def collide_alien_ship(self, alien_ship):
        alien_ship_mask = alien_ship.get_mask()
        bullet_mask = pygame.mask.from_surface(self.IMG)
        offset = (round(self.x) - alien_ship.x, round(self.y) - round(alien_ship.y))
        
        overlap_point = alien_ship_mask.overlap(bullet_mask, offset)
        
        if overlap_point: 
            return True
        
        return False
    
    def destroy(self):
        ok = 0
        for ship_bullet in ship_bullets:
            if self == ship_bullet:
                ship_bullets.remove(self)
                ok = 1
                break
            
        if not ok:
            for alien_ship_bullet in alien_ship_bullets:
                if self == alien_ship_bullet:
                    alien_ship_bullets.remove(self)
                    break

class Ship:
    WIDTH = 50
    HEIGHT = 50
    IMG = SHIP_IMG
    UNITS = 10
    
    def __init__(self, x):
        self.x = x
        self.y = 470
    
    def move_left(self):
        d = self.x - self.UNITS
        
        if d < 0:
            d = 0
        
        self.x = d
    
    def move_right(self):
        d = self.x + self.UNITS
        
        if d + self.WIDTH >= 700:
            d = 700 - self.WIDTH
        
        self.x = d
        
    def shoot(self):
        bullet = Bullet(self.x + 20, self.y - 10)
        return bullet
    
    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))
        
    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)
        
class AlienShip:
    WIDTH = 50
    HEIGHT = 50
    IMGS = ALIEN_SHIP_IMGS
    SPEED = 2
    ANIMATION_TIME = 10
    
    def __init__(self, x, index, spawn_point_index):
        self.img_count = 0
        self.img = self.IMGS[0]
        self.x = x
        self.y = -50
        self.index = index
        self.spawn_point_index = spawn_point_index
        self.shooted = False
        self.spawn_cooldown = 80
    
    def shoot(self):
        bullet = Bullet(self.x + 20, self.y + self.HEIGHT + 10)
        return bullet
    
    def move(self):
        d = self.y + self.SPEED
        if d > 600:
            self.destroy()
            return True
        else:
            self.y = d
            return False
    
    def draw(self, win):
        self.img_count += 1
        
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*2 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
            
        win.blit(self.img, (self.x, self.y))
        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
    def collide_ship(self, ship):
        ship_mask = ship.get_mask()
        alien_ship_mask = self.get_mask()
        offset = (self.x - round(ship.x), round(self.y) - ship.y)
        
        overlap_point = alien_ship_mask.overlap(ship_mask, offset)
        
        if overlap_point:
            return True
        
        return False
    
    @staticmethod
    def spawn_point_index_used(spawn_point_index):
        for alien_ship in alien_ships:
            if alien_ship.spawn_point_index == spawn_point_index or spawn_point_index == alien_ship.spawn_point_index - 1 or spawn_point_index == alien_ship.spawn_point_index + 1:
                return True
        
        return False
    
    @staticmethod
    def spawn(index):
        #spawn_points = [40, 140, 240, 340, 440, 540, 640]
        spawn_points = [10, 80, 150, 220, 290, 360, 430, 500, 570, 640]
        spawn_point_index = random.randrange(10)
        
        while AlienShip.spawn_point_index_used(spawn_point_index):
            spawn_point_index = random.randrange(10)
        
        spawn_point = spawn_points[spawn_point_index]
        
        new_alien_ship = AlienShip(spawn_point, index, spawn_point_index)
        
        alien_ships.insert(index, new_alien_ship)
        
    def destroy(self):
        index = self.index
        
        alien_ships.pop(self.index)
        
        AlienShip.spawn(index)
                
class Bg:
    SPEED = 25
    HEIGHT = BG_IMG.get_height()
    IMG = BG_IMG
    
    def __init__(self):
        self.x = 0
        self.y1 = 0
        self.y2 = self.HEIGHT
    
    def move(self):
        self.y1 = self.y1 + self.SPEED
        self.y2 = self.y2 + self.SPEED
        
        if self.y1 > WIN_HEIGHT:
            self.y1 = self.y2 - self.HEIGHT
            
        if self.y2 > WIN_HEIGHT:
            self.y2 = self.y1 - self.HEIGHT
    
    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y1))
        win.blit(self.IMG, (self.x, self.y2))
       
def draw_window(win, bg, ship, score, the_x, the_y):
    bg.draw(win)
    ship.draw(win)
    for ship_bullet in ship_bullets:
        ship_bullet.draw(win)
    for alien_ship in alien_ships:
        alien_ship.draw(win)
    for alien_ship_bullet in alien_ship_bullets:
        alien_ship_bullet.draw(win)
        
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    try:
        pygame.draw.line(win, (255,0,0), (ship.x + 25, ship.y), (the_x + 25, the_y + 45), 3)
    except:
        pass
    
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))
    
    pygame.display.update()

def get_min_diff_x_alienship(x_ship, y_ship):
    min_x_diff = 10000
    his_y_diff = 10000
    the_x = 0
    the_y = 0
    for alien_ship in alien_ships:
        if abs(alien_ship.x - x_ship + 20) < abs(min_x_diff) and alien_ship.y > 50:
            min_x_diff = alien_ship.x - x_ship + 20
            the_x = alien_ship.x
            his_y_diff = alien_ship.y - y_ship
            the_y = alien_ship.y
    
    return min_x_diff, his_y_diff, the_x, the_y

def get_min_dist_bullet(ship_x, ship_y):
    min_dist = 10000
    for alien_ship_bullet in alien_ship_bullets:
        if sqrt((alien_ship_bullet.x - ship_x)**2 + (alien_ship_bullet.y - ship_y)**2) < min_dist:
            min_dist = sqrt((alien_ship_bullet.x - ship_x)**2 + (alien_ship_bullet.y - ship_y)**2)
    
    return min_dist
            
  
def eval_genomes(genomes, config):   
    win = WIN
    clock = pygame.time.Clock()
    #quited = False
    bg = Bg()
    nets = []
    ships = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        ships.append(Ship(WIN_WIDTH/2 - 25))
        ge.append(genome)
    
    for i, ship in enumerate(ships):
        score = 0
        AlienShip.spawn(0)
        AlienShip.spawn(1)
        AlienShip.spawn(2)
        
        shoot_ship_time = 51
        SHOOT_SHIP_COOLDOWN = 50
        
        alien_ships_allowed_to_pass = 15
        
        is_still = False
        last_ship_x = WIN_WIDTH/2 - 25 - 1
        
        run = True
        while run:
            clock.tick(300)
            shoot_ship_time += 1
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    #quited = True
                    pygame.quit()
                
            
            bg.move()
            
                        
            min_x_diff_alien_ship, y_diff, the_x, the_y = get_min_diff_x_alienship(ship.x, ship.y)
            
            
            output = nets[i].activate((min_x_diff_alien_ship, y_diff, ship.x + 20))
            
            if last_ship_x == ship.x:
                is_still = True
            last_ship_x = ship.x
            
            if output[0] > 0.5:
                ship.move_left()
                if not is_still:
                    ge[i].fitness += 0.01
            if output[1] > 0.5:
                ship.move_right()
                if not is_still:
                    ge[i].fitness += 0.01
            if is_still:
                ge[i].fitness -= 0.02
            if output[2] > 0.5:
                if not shoot_ship_time <= SHOOT_SHIP_COOLDOWN:
                    new_bullet = ship.shoot()
                    ship_bullets.append(new_bullet)
                    for alien_ship in alien_ships:
                        if ship.x + 20 >= alien_ship.x and alien_ship.x + 40 <= ship.x + 20:
                            ge[i].fitness += 0.2
                    shoot_ship_time = 0
            
            for ship_bullet in ship_bullets:
                ship_bullet.move(-1)
                for alien_ship in alien_ships:
                    if ship_bullet.collide_alien_ship(alien_ship):
                        score += 1
                        ge[i].fitness += 1
                        alien_ship.destroy()
                        ship_bullet.destroy()
                
            
            for alien_ship in alien_ships:
                if alien_ship.spawn_cooldown > 0:
                    alien_ship.spawn_cooldown -= 1
                else:
                    if alien_ship.move():
                        ge[i].fitness -= 0.05
                        alien_ships_allowed_to_pass -= 1
                        if alien_ships_allowed_to_pass == 0:
                            ge[i].fitness -= 0.3
                            run = False
                            alien_ships.clear()
                            alien_ship_bullets.clear()
                            ship_bullets.clear()
                            break
                        
                    if alien_ship.collide_ship(ship):
                        ge[i].fitness -= 0.3
                        run = False
                        alien_ships.clear()
                        alien_ship_bullets.clear()
                        ship_bullets.clear()
                        break
                
            draw_window(win, bg, ship, score, the_x, the_y)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-8')
    #p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))
    
    winner = p.run(eval_genomes, 50)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)