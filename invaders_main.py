from math import ceil
from random import randint, choice
import pygame 
from time import sleep

WIDTH = 1200
HEIGHT = 600

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT), 1, 32)
pygame.display.set_caption('Invaders')

BLACK = (0,0,0)
BLUE = (0,100,200)
WHITE = (255,255,255)
background_image = pygame.image.load('assets/invaders/images/space_background.jpg')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# background sound
pygame.mixer.music.load("assets/invaders/sounds/background.wav")
pygame.mixer.music.play(-1) # the -1 makes the file play in a loop

def checkCollision(sprite1, sprite2):
    rect1, rect2 = sprite1.rect, sprite2.rect
    return rect1.colliderect(rect2)

def checkGroupCollision(group1, group2):
    '''group1 = opposition group
        group2 = player group'''
    for sprite in group1:
        collision = None 
        collision = pygame.sprite.spritecollide(sprite, group2, False, collided = None)
        if collision:
            return True

def checkGroupCollision2(group1, group2):
    '''group1: opposition group
        group2: player group'''
    for sprite in group1:
        for gamer in group2:
            if gamer.hasCollided(sprite.mask):
                return True
        

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        image = pygame.image.load('assets/invaders/images/player.png')
        p_width, p_height = image.get_size()
        self.image = pygame.transform.scale(image, (int(p_width*.75), int(p_height*.75)))
        self.mask = pygame.mask.from_surface(self.image)
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.center = pygame.math.Vector2(WIDTH/2, HEIGHT-50)
        self.sound_fire = pygame.mixer.Sound('assets/invaders/sounds/laser.wav')
        self.sound_gameover_impact = pygame.mixer.Sound('assets/invaders/sounds/gameover_impact.wav')
        self.sound_gameover_voice = pygame.mixer.Sound('assets/invaders/sounds/gameover_voice.wav')
        self.bullets = pygame.sprite.Group()
        self.bullet_limit = 10
        self.speed = 7
        self.score = 0

    def moveLeft(self):
        x = self.rect.center[0]-self.speed
        y = self.rect.center[1]
        if x < 0: 
            x = self.rect.center[0]
        move_to = pygame.math.Vector2(x, y)
        self.rect.center = move_to
    
    def moveRight(self):
        x = self.rect.center[0]+self.speed
        y = self.rect.center[1]
        if x > WIDTH: 
            x = self.rect.center[0]
        move_to = pygame.math.Vector2(x, y)
        self.rect.center = move_to

    def moveUp(self):
        x = self.rect.center[0]
        y = self.rect.center[1]-self.speed
        if y < 0: 
            y = self.rect.center[1]
        move_to = pygame.math.Vector2(x, y)
        self.rect.center = move_to

    def moveDown(self):
        x = self.rect.center[0]
        y = self.rect.center[1]+self.speed
        if y > HEIGHT: 
            y = self.rect.center[1]
        move_to = pygame.math.Vector2(x, y)
        self.rect.center = move_to

    def shoot(self):
        self.bullets.add(Bullet((self.rect.x + self.width/2, self.rect.y - self.height/2)))
        self.sound_fire.play(0, 100)

    # def hasCollided(self, mask): # , x=0, y=0):
    #     pointOfIntersection = mask.overlap(self.mask, (self.rect.x, self.rect.y))
    #     print(pointOfIntersection)
    #     return pointOfIntersection

    def die(self):
        self.sound_gameover_impact.play()
        self.sound_gameover_voice.play()
        self.kill()

    def update(self):
        # mouse_pos = pygame.mouse.get_pos()
        # self.rect.center = mouse_pos
        
        for bullet in self.bullets:
            if bullet.rect.y + bullet.height < 0:
                self.bullets.remove(bullet)
        self.bullets.draw(WIN)
        self.bullets.update()

class Enemy(pygame.sprite.Sprite):
    '''
    If the enemy touches (collides with) the player, the player dies.
    If the enemy's bomb touches the player, he dies.
    '''
    id = 0

    def __init__(self, pos):
        super(Enemy, self).__init__()
        self.image = pygame.image.load('assets/invaders/images/enemy.png')
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos_vec = pygame.math.Vector2(*pos)
        # self.id = id
        self.death_scream = pygame.mixer.Sound('assets/invaders/sounds/explosion.wav')
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 1 #2.5
        self.bombs = pygame.sprite.Group()
        self.bomb_limit = 2
        self.id = Enemy.id
        Enemy.id += 1
        self.attack = False
        self.life_force = 3

    def attackPlayer(self, player_pos):
        # get direction to move in
        player_pos_vec = pygame.math.Vector2(*player_pos)
        try:
            self.direction = (player_pos_vec - self.pos_vec).normalize()
        except ValueError:
            self.direction *= 0
        # start moving towards player at a constant speed 
        self.pos_vec += self.direction * self.speed
        self.rect.center = self.pos_vec

    def dropBomb(self):
        # Number of bombs the enemy can drop before they leave the screen should 
        # increase with level
        if len(self.bombs) <= self.bomb_limit:
            # place bomb initially just under the image of the enemy
            self.pos_vec = pygame.math.Vector2(self.rect.center) + \
                pygame.math.Vector2(0, self.image.get_height()/2)
            self.bombs.add(Bomb(self.pos_vec))

    def die(self):
        self.death_scream.play()
        self.kill()

    def update(self, attacker_id, player_pos):
        if attacker_id == self.id:
            self.attack = True
        if self.attack:
            self.attackPlayer(player_pos)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        image = pygame.image.load('assets/invaders/images/bullet.png')   
        self.width, self.height = image.get_size()
        self.image = pygame.transform.scale(image, (int(self.width*.5), int(self.height*.5)))
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = pygame.math.Vector2(*pos)
        self.speed = 7

    def update(self):
        self.rect.center -= pygame.math.Vector2(0, self.speed)

class Bomb(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('assets/invaders/images/ball.png')   
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = pygame.math.Vector2(*pos)
        self.speed = 3

    def update(self):
        self.rect.center += pygame.math.Vector2(0, self.speed)

class SpaceRock(pygame.sprite.Sprite):
    def __init__(self, pos, scale):
        super().__init__()
        image = pygame.image.load('assets/invaders/images/ufo.png')   
        width, height = image.get_size()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = pygame.math.Vector2(*pos)
        self.speed = 1
        self.death_scream = pygame.mixer.Sound('assets/invaders/sounds/explosion.wav')
        self.life_force = ceil(scale)

    def update(self):
        self.rect.center += pygame.math.Vector2(self.speed, self.speed)

    def die(self):
        self.death_scream.play()
        self.kill()

class Game():

    def __init__(self):

        self.gamer = Player() 
        self.gamer_group = pygame.sprite.GroupSingle()
        self.gamer_group.add(self.gamer)
        self.enemy_group = pygame.sprite.Group()
        self.bomb_group = pygame.sprite.Group()
        self.rock_group = pygame.sprite.Group()
        self.level = 1
        self.game_over = False
        self.all_ids = []
        self.getEnemies()
        self.total_enemies_init = len(self.enemy_group)
        self.attacker_range = list(range(self.total_enemies_init))
        self.level_score = 0
        
    def resetLevel(self, previous_score):
        sleep(2)
        self.gamer = Player() 
        self.gamer.score = previous_score
        self.gamer_group.add(self.gamer)
        self.game_over = False
        self.bomb_group.empty()
        self.enemy_group.empty()
        self.rock_group.empty()
        self.all_ids = []
        self.getEnemies()
        self.total_enemies_init = len(self.enemy_group)
        self.level_score = 0
   
    def nextLevel(self):
        new_score = self.gamer.score + self.level_score
        self.level += 1
        self.resetLevel(new_score)

    def endGameMessage(self):
        font = pygame.font.SysFont('times', 20)
        info_text = 'CONGRATS! YOU WIN!!'
        level_text = font.render(info_text, False, WHITE)
        WIN.blit(level_text, (WIDTH/2, HEIGHT/2))

    def textInfo(self):
        font = pygame.font.SysFont('times', 20)
        level_info = f'LEVEL: {self.level}'
        score_info = f'SCORE: {self.gamer.score + self.level_score}'
        enemy_info = f'ENEMIES: {len(self.enemy_group)}'
        level_text = font.render(level_info, False, WHITE)
        score_text = font.render(score_info, False, WHITE)
        enemy_text = font.render(enemy_info, False, WHITE)
        WIN.blit(level_text, (50, 20))
        WIN.blit(score_text, (50, 45))
        WIN.blit(enemy_text, (50, 70))

    def getLayout(self, level):
        layout = []
        if level < 6:
            while len(layout) < level:
                row1 = ''
                while len(row1) < 14:
                    row1 += '*' * level
                    row1 += ' '
                layout.append(row1)
                row2 = ''
                while len(row2) < 14:
                    row2 += ' ' * ceil(level/2)
                    row2 += '*' 
                layout.append(row2)
        else:
            while len(layout) < 5:
                row1 = ''
                while len(row1) < 14+level:
                    row1 += '*' * level
                layout.append(row1)
                row2 = ''
                while len(row2) < 14+level:
                    row2 += ' ' * ceil(level/9)
                    row2 += '*' 
                layout.append(row2)
        return layout 

    def getEnemies(self):
        '''Use the layout to create and place enemies''' 
        layout = self.getLayout(self.level)
        for i in range(len(layout)):
            for j in range(len(layout[i])):
                if layout[i][j] == '*':
                    enemy = Enemy((100+j*80, (i+1)*50))
                    self.all_ids.append(enemy.id)
                    self.enemy_group.add(enemy)
        self.attacker_range = list(range(len(self.enemy_group)))
        
    def getAttackerID(self):
        '''
            The probability of picking an attacker should depend on the number of 
            enemies. The fewer the enemies, the higher the probability and vice-versa.
            It should be made that the id of every enemy is returned eventually.
        '''
        attacker_id = 1
        num_enemies_left = len(self.enemy_group)
        if num_enemies_left > len(self.attacker_range) - 40:
            attacker_id = randint(0, int(pow(num_enemies_left*.5, 3)*20/(self.level+1)))
        else:
            if self.all_ids:
                attacker_id = choice(self.all_ids)
                self.all_ids.remove(attacker_id)
            else:
                pass
        return attacker_id

    def getSpaceRock(self):
        x = randint(-250, 750)
        y = randint(-100, -10)
        scale = randint(20,35)/10
        freq = int(360/self.level)
        if randint(0,700) % freq == 0:
            self.rock_group.add(SpaceRock((x,y), scale))

    def display(self):
        self.getSpaceRock()
        attacker_id = self.getAttackerID()

        # Add bombs to group
        bomber_id = randint(0, int(len(self.enemy_group)*30*ceil(self.level/100)))
        enemy_ids = []
        for enemy in self.enemy_group:
            enemy_ids.append(enemy.id)
            if enemy.id == bomber_id:
                self.bomb_group.add(Bomb(enemy.pos_vec))

        # Limit attacker id range to the maximum id
        if enemy_ids: # if any enemies still left
            self.attacker_range = list(range(min(enemy_ids)-1, max(enemy_ids)+1))

        # Destroy all bombs that have gone offscreen
        for bomb in self.bomb_group:
            if bomb.rect.y > HEIGHT:
                bomb.kill()

        WIN.fill(BLUE)
        WIN.blit(background_image, (0,0))
        self.enemy_group.draw(WIN)
        self.enemy_group.update(attacker_id, self.gamer.rect.center)
        self.textInfo()
        self.gamer_group.draw(WIN)
        self.gamer_group.update()
        self.bomb_group.draw(WIN)
        self.bomb_group.update()
        self.rock_group.draw(WIN)
        self.rock_group.update()
        pygame.display.flip()

    def raiseScore(self, enemy=True):
        if enemy: # if enemy killed
            self.level_score += 3
        else: # if saucer killed
            self.level_score += 1

    def main(self):
        clock = pygame.time.Clock()

        running = True 
        while running:

            clock.tick(60)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or keys[pygame.K_q]:
                    running = False 

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.gamer.shoot()

            if keys[pygame.K_LEFT]:
                self.gamer.moveLeft()
            if keys[pygame.K_RIGHT]:
                self.gamer.moveRight()        
            if keys[pygame.K_UP]:
                self.gamer.moveUp()        
            if keys[pygame.K_DOWN]:
                self.gamer.moveDown()        
            
            # Enable continuous fire after a certain level
            if self.level > 2:
                self.gamer.bullet_limit = self.level
                if keys[pygame.K_SPACE]:
                    if len(self.gamer.bullets) <= self.gamer.bullet_limit:
                        self.gamer.shoot()

            # Reset level if gamer dies
            if not self.game_over:
                self.display()
            else:
                self.resetLevel(self.gamer.score)

            # Move to next level if player wins
            if len(self.enemy_group) == 0:
                self.nextLevel()
            
            # Handle enemy collision with bullets
            for bullet in self.gamer.bullets:
                for enemy in self.enemy_group:
                    if checkCollision(enemy, bullet):
                        enemy.life_force -= 1
                        if enemy.life_force == 0:
                            enemy.die()
                            self.raiseScore()
                            # print('Enemies left:', len(self.enemy_group))
                        bullet.kill()
            for bullet in self.gamer.bullets:
                for rock in self.rock_group:
                    if checkCollision(rock, bullet):
                        rock.life_force -= 1
                        if rock.life_force == 0:
                            rock.die()
                            self.raiseScore(False)
                        bullet.kill()

            # Handle gamer collision with enemy and bullet and rocks
            if checkGroupCollision(self.enemy_group, self.gamer_group):
                self.game_over = True
                self.gamer.die()
            if checkGroupCollision(self.bomb_group, self.gamer_group):
                self.game_over = True
                self.gamer.die()
            if checkGroupCollision(self.rock_group, self.gamer_group):
                self.game_over = True
                self.gamer.die()
                  

        pygame.quit()
        
game = Game()
game.main()
            