'''
Mission Critical:
	-Remove ability to spawn enemies
Mission Less-Critical:
	-Main menu
	-Comment all the things
	-Music and sound effects
	-Scoring system
	-Remove awkward transitions and teleports
'''

#---------------------------------------- Imports ----------------------------------------#
import pygame
import sys
import math
import random
import time

#======================================== Constants ========================================#
resX = 1440															# Horizontal resolution
resY = 900															# Vertical resolution
bulletVel = 60														# Bullet velocity
playerVel = 40														# Player movement speed
initialEnemyVel = 10												# Initial enemy velocity
enemyVel = initialEnemyVel											# Ensures that enemyVel has a value to begin with
alphaMod = 0.5														# Increment by which the background cycles its alpha values
lowerAlpha = 30														# Lower bound of the background alpha cycle
higherAlpha = 60													# Upper bound of the background alpha cycle
initialSpawnChance = 5												# Initial chance of an enemy appearing each second (out of 100)
lColors = ["red", "orange", "yellow", "green", "teal", "blue"]		# A list of colors used for determining what color bullet to fire

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~ Screen ~~~~~~~~~~~~~~~~~~~~#
class Screen(object):
	#~~~ Screen Init ~~~#
	def __init__(self, file):
		'''Initialize the Screen object, which is intended for images that are dimensioned to fit the entire screen.'''
		self.alpha = lowerAlpha
		self.alphaMod = alphaMod

		self.file = file
		
		self.surf = pygame.image.load(self.file).convert()
		self.surf = pygame.transform.scale(self.surf, (resX, resY))
		self.rect = self.surf.get_rect()
		self.surf.set_alpha(self.alpha)

	#~~~ Update ~~~#
	def update(self, screenRect):
		'''Movement of screens is currently not supported.'''
		pass

	#~~~ Cycle ~~~#
	def cycle(self):
		'''Cycle the transparency of a screen between two constants (lowerAlpha and higherAlpha) by an increment of alphaMod'''
		if self.alpha >= higherAlpha:
			self.alphaMod = -alphaMod
		elif self.alpha <= lowerAlpha:
			self.alphaMod = alphaMod
		
		self.alpha += self.alphaMod
		self.surf.set_alpha(self.alpha)
	
	#~~~ Fade In ~~~#
	def fadeIn(self, end, jump):
		'''Increase the alpha of the screen until max.'''
		if self.surf.get_alpha() < end:
			self.alpha += jump
			self.surf.set_alpha(self.alpha)
			
	#~~~ Fade Out ~~~#
	def fadeOut(self, end, jump):
		'''Decrease the alpha of the screen until min.'''
		if self.surf.get_alpha() > 0:
			self.alpha -= jump
			self.surf.set_alpha(self.alpha)
			
	#~~~ Draw ~~~#
	def draw(self, screen):
		'''Blit the Screen (class) to the screen (thing the player views)'''
		screen.blit(self.surf, self.rect)
#~~~~~~~~~~~~~~~~~~~~ Bullet ~~~~~~~~~~~~~~~~~~~~#
class Bullet(object):
	#~~~ Init ~~~#
	def __init__(self, x0, y0, playerDirection):
		'''Initialize the Bullet object, which is fired by the Player with the intention of destroying Enemies. Determines the color of bullets, and which direction they should be fired.'''
		posMod = 40

		if playerDirection == "Left":
			x0 += posMod
			index = random.randint(3, 5)
		else:
			x0 -= posMod
			index = random.randint(0, 2)

		image = "bullet_%s.png" %(lColors[index])

		self.surf = pygame.image.load(image).convert_alpha()
		self.surf.set_alpha(100)
		self.rect = self.surf.get_rect()
		
		self.rect.center = (x0, y0)
		if playerDirection == "Left":
			self.vel = bulletVel
		elif playerDirection == "Right":
			self.vel = -bulletVel

	#~~~ Update ~~~#
	def update(self, screenRect):
		'''Update the position of the bullet.'''
		self.rect.move_ip(-self.vel, 0)	

	#~~~ Draw ~~~#
	def draw(self, screen):
		'''Blit the bullet to the screen'''
		screen.blit(self.surf, self.rect)
		
	#~~~ Erase ~~~#
	def erase(self, screen, bg):
		'''Remove the bullet from the screen. Currently unused, since bullets are managed by a list.'''
		screen.blit(bg, self.rect)
		
	#~~~ Collide ~~~#
	def collide(self, bullet, enemy, enemies):
		'''Determine if the given bullet is colliding with the given enemy.'''
		if bullet.rect.colliderect(enemy.rect):
			enemies.remove(enemy)
#~~~~~~~~~~~~~~~~~~~~ Player ~~~~~~~~~~~~~~~~~~~~#
class Player(object):
	#~~~ Init ~~~#
	def __init__(self):
		'''Initialize the Player object, which always begins facing to the left.'''
		self.surf = pygame.image.load("player_left.png").convert_alpha()
		self.rect = self.surf.get_rect()
		self.rect.center = (resX / 2 - 60, resY / 2)
		self.moving = [False, False]					#Up, down
		self.currentDirection = "Left"
		self.vel = playerVel
		self.surf.set_alpha(255)
	
	#~~~ Update ~~~#
	def update(self, screenRect):
		'''Update the location of the Player, based upon the truth of the list called "moving"'''
		if self.moving[0]:
			future = self.rect.move(0, -self.vel)
			if future.top < 0:
				self.rect.top = 0
			else:
				self.rect = future
		elif self.moving[1]:
			future = self.rect.move(0, self.vel)
			if future.bottom > resY:
				self.rect.bottom = resY
			else:
				self.rect = future

	#~~~ Swap ~~~#		
	def swap(self, screenRect):
		'''Switch which side of the screen the Player is facing.'''
		if self.currentDirection == "Left":
			self.rect.center = (resX / 2 + 60, self.rect.centery)
			self.surf = pygame.image.load("player_right.png").convert_alpha()
			self.currentDirection = "Right"
		elif self.currentDirection == "Right":
			self.rect.center = (resX / 2 - 60, self.rect.centery)
			self.surf = pygame.image.load("player_left.png").convert_alpha()
			self.currentDirection = "Left"
	
	#~~~ Draw ~~~#
	def draw(self, screen):
		'''Blit the Player to the screen'''
		screen.blit(self.surf, self.rect)
#~~~~~~~~~~~~~~~~~~~~ Enemy ~~~~~~~~~~~~~~~~~~~~#
class Enemy(object):
	#~~~ Init ~~~#
	def __init__(self):
		'''Initialize the Enemy object, with a random vertical location and random side.'''
		spawnVal = random.randint(0, 1)
		
		if spawnVal == 0:
			self.spawnSide = "Left"
			x0 = -100
			self.vel = enemyVel
			num = random.randint(5, 8)
		else:
			self.spawnSide = "Right"
			x0 = resX + 100
			self.vel = -enemyVel
			num = random.randint(1, 4)
		y0 = random.randint(50, resY - 50)
		index = random.randint(0, 5)
		image = "enemy_%d.png" %(num)

		self.surf = pygame.image.load(image).convert_alpha()
		self.rect = self.surf.get_rect()
		self.rect.center = (x0, y0)

	#~~~ Update ~~~#
	def update(self, screenRect):
		'''Update the location of the enemy, which moves at a constant velocity.'''
		self.rect.move_ip(self.vel, 0)	

	#~~~ Draw ~~~#
	def draw(self, screen):
		'''Blit the enemy to the screen.'''
		screen.blit(self.surf, self.rect)

	#~~~ Erase ~~~#
	def erase(self, screen, bg):
		''''Erase the Enemy from the screen. Currently unused, since enemies are managed by a list.'''
		screen.blit(bg, self.rect)
#~~~~~~~~~~~~~~~~~~~~ Screen ~~~~~~~~~~~~~~~~~~~~#
class Meter(object):
	#~~~ Meter Init ~~~#
	def __init__(self, file):
		'''Initialize the Meter object, which displays the player's progress towards losing.'''
		self.alpha = lowerAlpha
		self.alphaMod = alphaMod

		self.file = file
		
		self.surf = pygame.image.load(self.file).convert()
		self.rect = self.surf.get_rect()
		self.rect.center = (resX / 2, resY * 1.5)
		self.surf.set_alpha(120)
	
	#~~~ Update ~~~#
	def update(self, screenRect):
		'''Update the location of the meter.'''
		self.rect.move_ip(0, -10)	
		
	#~~~ Cycle ~~~#
	def cycle(self):
		'''Cycle the transparency of a meter between two constants (lowerAlpha and higherAlpha) by an increment of alphaMod'''
		if self.alpha >= 40:
			self.alphaMod = -alphaMod
		elif self.alpha <= 20:
			self.alphaMod = alphaMod
		
		self.alpha += self.alphaMod
		self.surf.set_alpha(self.alpha)
	
	#~~~ Fade In ~~~#
	def fadeIn(self, end, jump):
		'''Increase the alpha of the meter until max.'''
		if self.surf.get_alpha() < end:
			self.alpha += jump
			self.surf.set_alpha(self.alpha)
			
	#~~~ Fade Out ~~~#
	def fadeOut(self, end, jump):
		'''Decrease the alpha of the meter until min.'''
		if self.surf.get_alpha() > 0:
			self.alpha -= jump
			self.surf.set_alpha(self.alpha)
			
	#~~~ Draw ~~~#
	def draw(self, screen):
		'''Blit the Meter to the screen'''
		screen.blit(self.surf, self.rect)
		
#---------------------------------------- Functions ----------------------------------------#
#--- Collide Lists ---#
def collideLists(list1, list2):
	'''Iterate through two lists of objects, and determine if any of the objects in the first list have collided with objects in the second list.'''
	for i in list1:
		for j in list2:
			if i.rect.colliderect(j.rect):
				#list1.remove(i)
				list2.remove(j)
		
#//////////////////////////////////////// Higher Level Classes ////////////////////////////////////////#
#//////////////////// Intro ////////////////////#
class Intro(object):
	#/// Init ///#
	def __init__(self):
		'''Initialize the Intro object, which is used to display static screens.'''
		# Pygame initialization
		pygame.init()
		self.screen = pygame.display.set_mode((resX, resY), pygame.FULLSCREEN)
		self.clock = pygame.time.Clock()
		self.startTime = time.time()
		self.timeAtStarting = -1
		
		# Initialize gameState, which determines whether to show intros, game, etc.
		print "-------------------------------------------------------------------------------"
		print "Initializing gameState as 'intro'."
		self.gameState = "intro"
		
		# Prepare objects related to the intro screens
		self.bg = Screen("screen_background.png")
		self.bg.surf.set_alpha(30)

		self.helix = Screen("screen_helix.png")
		self.helix.surf.set_alpha(0)

		self.up = Screen("screen_up.png")
		self.up.surf.set_alpha(0)

	#/// Intro Process Events ///#
	def intro_processEvents(self):
		'''Only allows users to quit at this time.'''
		
		self.elapsedTime = time.time() - self.startTime
		
		# Check keyboard input
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					sys.exit()
				if event.key == pygame.K_SPACE:
					print "Changing gameState to 'starting'."
					self.gameState = "starting"
					self.timeAtStarting = time.time()
					
		# Check mouse clicks
		if pygame.mouse.get_pressed()[0]:
			print pygame.mouse.get_pos()
					
	#/// Intro Update  ///#
	def intro_update(self):
		'''Used to fade screens in and out.'''
		
		if self.elapsedTime <= 2:
			self.helix.fadeIn(255, 10)
		elif self.elapsedTime > 2 and self.elapsedTime <= 4: 
			self.helix.fadeOut(0, 10)
		elif self.elapsedTime > 4 and self.elapsedTime <= 6:
			self.up.fadeIn(230, 5)	
		elif self.gameState == "starting":
			self.up.fadeOut(0, 10)
		
	#/// Intro Draw ///#
	def intro_draw(self):
		'''Blank the screen and draw objects.'''
		self.screen.fill((0, 0, 0))
		self.helix.draw(self.screen)
		self.up.draw(self.screen)
		self.bg.draw(self.screen)
		
	#/// Intro Exit ///#
	def intro_exit(self):
		timeSinceStarting = time.time() - self.timeAtStarting
		if timeSinceStarting > 2 and self.timeAtStarting != -1:
			print "Changing gameState to 'game'."
			self.gameState = "game"
			self.gameStartTime = time.time()
			pygame.mouse.set_visible(False)
					
#//////////////////// Game ////////////////////#
class Game(object):
	#/// Init ///#
	def __init__(self):
		'''Initialize the Game object, which is updated and drawn during the actual game, but not during intro screens and menus.'''
		# Prepare class objects
		self.meter = Meter("meter.png")
		self.bullets = []
		self.player = Player()
		self.enemies = []
		self.gameOver = Screen("screen_gameOver.png")
		self.gameOver.surf.set_alpha(0)
		self.gameIsOver = False
		
		self.nEscaped = 0
				
	#/// Process Events ///#
	def processEvents(self):
		'''Search for keyboard input and respond accordingly.'''
		for event in pygame.event.get():
		
			if event.type == pygame.KEYDOWN:
				# Exit the game
				if event.key == pygame.K_ESCAPE:
					sys.exit()
				# Create a bullet
				if event.key == pygame.K_SPACE:
					if len(self.bullets) < 2:
						self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.centery, self.player.currentDirection))
				# Begin moving the player up
				if event.key == pygame.K_UP:
					self.player.moving[0] = True
				# Begin moving the player down
				if event.key == pygame.K_DOWN:
					self.player.moving[1] = True
				# Switch which side of the screen the player is on
				if event.key == pygame.K_LSHIFT:
					self.player.swap(i.screen.get_rect())
				# Spawn an enemy
				if event.key == pygame.K_e:
					self.enemies.append(Enemy())
					
			if event.type == pygame.KEYUP:
				# Stop moving the player up
				if event.key == pygame.K_UP:
					self.player.moving[0] = False
				# Stop moving the player down
				if event.key == pygame.K_DOWN:
					self.player.moving[1] = False
					
	#/// Update ///#
	def update(self):
		'''Run the update functions of all objects: update movement and transparency, check for collisions.'''
		elapsedTime = time.time() - i.gameStartTime
		
		if not gameIsOver:
		
		i.bg.cycle()										# Cycle background alpha
		self.meter.cycle()
		
		self.player.update(i.screen.get_rect())				# Move player
		
		# Update Bullets
		for item in self.bullets:
			item.update(i.screen.get_rect())					# Move bullet
			if item.rect.right < 0 or item.rect.left > resX:	# If bullet is offscreen...
				self.bullets.remove(item)						# Delete the bullet
		
		# Update enemy difficulty
		spawnChance = initialSpawnChance + elapsedTime / 5
		enemyVel = initialEnemyVel + elapsedTime / 2
		num = random.randint(0, 100)
		if num < spawnChance:
			self.enemies.append(Enemy())
		
		# Update enemy position and note if enemies have escaped
		for item in self.enemies:
			item.update(i.screen.get_rect())
			if (item.rect.right < 0 and item.spawnSide == "Right") or item.rect.left > resX and item.spawnSide == "Left":
				self.enemies.remove(item)								# Delete the enemy
				
				if self.nEscaped < 20:
					self.nEscaped += 1
								
				print "%.2f: Enemy %d escaped." %(elapsedTime, self.nEscaped)
			
		# Check if any bullet is colliding with any enemy
		collideLists(self.bullets, self.enemies)
		
		if self.meter.rect.top > resY - 45 * self.nEscaped:
			self.meter.update(i.screen.get_rect())
			if self.nEscaped >= 20:
				gameIsOver = True
		
	#/// Draw ///#
	def draw(self):
		'''Blank the screen and draw all objects.'''
		i.screen.fill((0, 0, 0))								# Fill the screen with blackness
		i.bg.draw(i.screen)									# Draw the background
		self.player.draw(i.screen)								# Draw the player
		for item in self.bullets:								# Loop through all bullets
			item.draw(i.screen)
		for item in self.enemies:								# Loop through all enemies
			item.draw(i.screen)
		self.meter.draw(i.screen)
		self.gameOver.draw(i.screen)

#'''''''''''''''''''''''''''''''''''''''' Master Render Loop ''''''''''''''''''''''''''''''''''''''''#
i = Intro()
g = Game()

while True:
	i.clock.tick(30)				# Set the clock speed
	
	if i.gameState == "intro" or i.gameState == "starting":
		i.intro_processEvents()
		i.intro_update()
		i.intro_draw()
		i.intro_exit()
	elif i.gameState == "game":
		g.processEvents()
		g.update()
		g.draw()
		
	pygame.display.flip()			# Flip the display