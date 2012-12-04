import pygame, sys

class Map(object):
    def __init__(self):
        """initializes the map"""
        self.data = open("map.txt").readlines()
        self.data = [line.rstrip() for line in self.data]
        self.water = pygame.image.load("gfx/water.png").convert()
        self.land = pygame.image.load("gfx/land.png").convert()
        
    def draw(self, screen):
        """draws the map"""
        for i, row in enumerate(self.data):
            for j, column in enumerate(row):
                if column == "l":
                    #draw the land tile
                    screen.blit(self.land, pygame.Rect(j*64, i*64, 64, 64))
                elif column == "w":
                    screen.blit(self.water, pygame.Rect(j*64, i*64, 64, 64))
                    

class Ball(object):
    """this is the enemy ball thing"""
    def __init__(self):
        super(Ball, self).__init__()
        self.img = pygame.image.load("gfx/ball.png").convert_alpha()
        self.rect = self.img.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.vel_x = 3
        self.vel_y = 3
        self.score = 0

    def update(self, screen_rect):
        """updates ball's position"""
        future_rect = self.rect.move(self.vel_x, self.vel_y)
        if future_rect.left < screen_rect.left or future_rect.right > screen_rect.right:
            self.vel_x = -self.vel_x
            self.score += 1
        if future_rect.top < screen_rect.top or future_rect.bottom > screen_rect.bottom:
            self.vel_y = -self.vel_y
            self.score += 1
        self.rect.move_ip(self.vel_x, self.vel_y)

    def draw(self, screen):
        """draws ball to screen"""
        screen.blit(self.img, self.rect)

class Player(object):
    """cute fat little bear"""
    def __init__(self):
        self.image = pygame.image.load("gfx/bear.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.width = 64
        self.rect.height = 143
        self.rect.x = 25
        self.rect.y = 25
        self.xvel = 6
        self.yvel = 6
        self.direction = 0 #0 == right, 1 == left
        self.moving = [False, False, False, False] #up, down, left, right
        self.frame = 0
        
    def update(self, score):
        """updates position of the bear"""
        if self.moving[0] and self.moving[1]:
            return score
        elif self.moving[2] and self.moving[3]:
            return score
        if self.moving[0]:
            future = self.rect.move(0, -self.yvel)
            if future.top < 0:
                self.rect.top = 0
                score += 1
            else:
                self.rect = future
        elif self.moving[1]:
            future = self.rect.move(0, self.yvel)
            if future.bottom > 448:
                self.rect.bottom = 448
                score += 1
            else:
                self.rect = future
        if self.moving[2]:
            self.direction = 1
            future = self.rect.move(-self.xvel, 0)
            if future.left < 0:
                self.rect.left = 0
                score += 1
            else:
                self.rect = future
        elif self.moving[3]:
            self.direction = 0
            future = self.rect.move(self.xvel, 0)
            if future.right > 640:
                self.rect.right = 640
                score += 1
            else:
                self.rect = future
        if self.moving == [False, False, False, False]:
            self.frame = 0
        else:
            self.frame += 1
            if self.frame > 19:
                self.frame = 0
        return score
        
    def draw(self, screen):
        """draws the bear"""
        screen.blit(self.image, self.rect, pygame.Rect(64*(self.frame/5),self.direction*143,64, 143))

class Game(object):
    def __init__(self):
        """initializes the game"""
        pygame.init()
        self.screen = pygame.display.set_mode((640, 448))
        self.clock = pygame.time.Clock()
        self.map = Map()
        self.player = Player()
        self.ball = Ball()
        self.f32 = pygame.font.Font(None, 32)
        self.score = 0
        
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key == pygame.K_UP:
                    self.player.moving[0] = True
                if event.key == pygame.K_DOWN:
                    self.player.moving[1] = True
                if event.key == pygame.K_LEFT:
                    self.player.moving[2] = True
                if event.key == pygame.K_RIGHT:
                    self.player.moving[3] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.player.moving[0] = False
                if event.key == pygame.K_DOWN:
                    self.player.moving[1] = False
                if event.key == pygame.K_LEFT:
                    self.player.moving[2] = False
                if event.key == pygame.K_RIGHT:
                    self.player.moving[3] = False
        
        
    def update(self):
        self.score = self.player.update(self.score)
        self.ball.update(self.screen.get_rect())
        
    def draw(self):
       self.map.draw(self.screen)
       self.ball.draw(self.screen)
       self.player.draw(self.screen)
       scoresurf = self.f32.render("Score = %d"%self.score, 1, (0,0,0))
       scorerect = scoresurf.get_rect()
       scorerect.center = (320, 30)
       self.screen.blit(scoresurf, scorerect)
        
g = Game()
while True:
    g.clock.tick(30)
    g.process_events()
    g.update()
    g.draw()
    pygame.display.flip()