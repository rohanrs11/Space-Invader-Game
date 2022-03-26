import pygame
import os
import time
import random
from os import path

pygame.font.init()

"""the pygame functions/syntax were obtained from https://www.pygame.org/docs/"""
"""Parts of this code are taken from https://www.youtube.com/watch?v=Q-__8Xw9KTM and modified to fit our game. 
We have also each written two unique functions that were not from this source. """

#Set the screen size and title of the screen
width, height = 1000, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Shooter Tutorial")


#Different enemy space ships
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#The players ship
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "player_ship.png"))

#The different lasers being shot by both enemies and the player
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (width, height))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, speed):
        self.y += speed

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    """Abstract base class for space invader ships. 
    
    Attributes:
        pos_x (int): the ships current x position
        pos_y (int): the ships current y position
        health (int): health of ship is set to 1000
    """

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        """draws the player ship"""
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, speed, obj):
        """This meathod will check to see if the lasers are 
        on or off screen and will also see if the laser hit 
        the player ship.  If the ship is hit, health will be lost 
            Args:
                speed: the speed in which the players move
                obj: the enemies on the board"""
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        """ this will create an auto cool down so 
        that you can not constantly spam any of the button"""
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        """Find the width of the ship """
        return self.ship_img.get_width()

    def get_height(self):
        """Finds the length/height of the ship """
        return self.ship_img.get_height()


class Player(Ship):
    """This is the player class that will take the attributes from the ship Class.  
    This class will have all the functions a player ship can do """
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        #initializes score and a counter to 0
        self.counter = 0
        self.score = 0



    def move_lasers(self, speed, objs):
        """This will allow for the player ship to attack enemies.
        Args:
            speed(int): the speed at which the attacks are moving
            obj(enemies): the enemies on the board
            """
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        # every time the enemies are removed, your score will increase by 1
                        self.score += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            

    def draw(self, window):
        """This allows for a health bar to be drawn on the player ship 
        Args:
            window(window): the screen in which the game will be played on.
        """
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window): 
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
    
    def scoreboard(self, game_score): 
        """This creates a scoreboard that logs the top 10 point scorers and 
        removes scores once they are beat.  We will read and write to a file to 
        save these top scores
            Args:
                game_score(int): the score of the game you just played
        """
        high_scores = []
        try:
            f = open("high_score.txt", "r")
            for score in f:
                high_scores.append(int(score))
            f.close
        except:
            high_scores = []

        in_top_10 = False
        for i in range(len(high_scores)):
            if game_score > high_scores[i]:
                in_top_10 = True
                high_scores.insert(i, game_score)
                if len(high_scores) > 10:
                    high_scores.pop(10)
                break
        if not in_top_10 and len(high_scores) < 10:
            high_scores.append(game_score)
            in_top_10 = True

        if in_top_10:
            f = open("high_score.txt", "w")
            for score in high_scores:
                f.write(str(score) + "\n")
            f.close

        return self.score



class Enemy(Ship):
    """This is the enemy class that will take the attributes from the ship Class.  
    This class will have all the functions an enemy ship can do """
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    #This meathod was created entirely by Rohan
    def move_zigzag(self, speed): 
        """this will show how the enemy ships are able to 
        move down (zigzag pattern instead of normally going straight downwards.)
        Args:
            speed(int): how fast the enemy is able to move
        """
        self.y += speed
        self.x += random.randrange(-10, 10)
        if self.x < 0:
            self.x = 0
        if self.x > width:
            self.x = width
    
    def shoot(self): 
        """This will show how enemy ships are able to attack """
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    """This will show when 2 objects collide """
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 120
    level = 1
    lives = 10

    
    main_font = pygame.font.SysFont("arial", 20)
    lost_font = pygame.font.SysFont("arial", 20)

    enemies = []
    wave_length = 3
    enemy_speed = 1

    player_speed = 5
    laser_speed = 5

    player = Player(500, 500)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window(score, lives , level):
        window.blit(background, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))

        window.blit(lives_label, (10, 10))
        window.blit(level_label, (width - level_label.get_width() - 10, 10))
        window.blit(score_label, (10, 50))


        for enemy in enemies:
            enemy.draw(window)

        player.draw(window)

        if lost:
            lost_label = lost_font.render("You Lost, Better Luck Next Time", 1, (255,255,255))
            window.blit(lost_label, (width/2 - lost_label.get_width()/2, 350))
            

        pygame.display.update()
    
    

    while run:
        clock.tick(FPS)
        redraw_window(player.score, lives, level)
        
        
        if lives <= 0 or player.health <= 0:
            lost = True
            if lost_count == 0:
                player.scoreboard(player.score)
            lost_count += 1
        # when you lose, the message "you lost better luck next time" will appear for 3 seconds then repromt the main menu

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_speed > 0: # left
            player.x -= player_speed
        if keys[pygame.K_d] and player.x + player_speed + player.get_width() < width: # right
            player.x += player_speed
        if keys[pygame.K_w] and player.y - player_speed > 0: # up
            player.y -= player_speed
        if keys[pygame.K_s] and player.y + player_speed + player.get_height() + 15 < height: # down
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move_zigzag(enemy_speed)
            enemy.move_lasers(laser_speed, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)
            

        player.move_lasers(-laser_speed, enemies)


#this is the startup screen when you start the game
def main_menu():
    title_font = pygame.font.SysFont("arial", 70)
    run = True
    while run:
        window.blit(background, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        window.blit(title_label, (width/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

if __name__ == "__main__":
    main_menu()

#a = 'hello'
#b = 'good bye'
#print(f"abc {a} efg {b}")