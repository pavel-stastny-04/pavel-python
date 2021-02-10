import pyglet
import math
from pyglet import gl
import random

TITLE = 'Asteroids'
HEIGHT = 600 #px  ! this is automatically set from actual window height !
WIDTH = 800 #px  ! this is automatically set from actual window width !
OBJECTSCNT = 10 #number of objects in the game
SPEEDUP_ACCELERATION = 10 #px/s^2 for ship
SPEEDDOWN_ACCELERATION = 8 #px/s^2 for ship
ROTATING_ACCELERATION = 2 #rad/s^2 for ship
LASER_SPEED = 100 #speed if laser object in px/s
LASER_LIFETIME = math.sqrt(HEIGHT + WIDTH) // 6 #lifetime of laser in s
HP = 3

batch = pyglet.graphics.Batch()
pressed_keys = set()
gameover = False
gametime = 0.0 #time in the game in s
lasercnt = 0 #number of used lasers
winer = False
timeprint = True
ingame_objects = OBJECTSCNT
score = 0 #player's score
win = False
indestructible = 0

class SpaceObject:
    def __init__(self, scale, position_x, position_y, speed):
        clear_image = pyglet.image.load('clear.png')
        self.radius = 0
        self.rotation = 0
        self.rotation_speed = 0
        self.sprite = pyglet.sprite.Sprite(clear_image, batch=batch)
        self.x = 0
        self.y = 0
        self.sprite.x = 0
        self.sprite.y = 0
        self.speed = 0
    
    def tick(self, td):
        #print('ok')
        self.rotation += self.rotation_speed * td
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.sprite.y += math.sin(self.rotation) * self.speed * td
        self.sprite.x += math.cos(self.rotation) * self.speed * td

        if self.sprite.y + self.radius > HEIGHT - HEIGHT // 6 and self.sprite.x < WIDTH // 4 and self.sprite.y + self.radius < HEIGHT - HEIGHT // 8:
            self.sprite.y = 0

        elif self.sprite.x - self.radius < WIDTH // 4 and self.sprite.y > HEIGHT - HEIGHT // 6 and self.sprite.x - self.radius > WIDTH // 8:
            self.sprite.x = WIDTH

        elif self.sprite.y < 0 and self.sprite.x < WIDTH // 4:
            self.sprite.y = HEIGHT - (HEIGHT // 6) - self.radius

        elif self.sprite.x > WIDTH and self.sprite.y > HEIGHT - HEIGHT // 6:
            self.sprite.x = (WIDTH // 4) + self.radius

        elif self.sprite.x < 0:
            self.sprite.x = WIDTH

        elif self.sprite.x > WIDTH:
            self.sprite.x = 0

        elif self.sprite.y < 0:
            self.sprite.y = HEIGHT

        elif self.sprite.y > HEIGHT:
            self.sprite.y = 0

        if 'R' in pressed_keys:
            self.__init__(scale=0, position_x='none', position_y='none', speed=0)
            reset()

    def position(self):
        for k in objects:
            if k.sprite.x > self.sprite.x and k.sprite.y > self.sprite.y:
                if self.radius + k.radius >= math.sqrt((k.sprite.x - self.sprite.x) ** 2 + (k.sprite.y - self.sprite.y) ** 2):
                    self.colision(k)

            if self.sprite.x > k.sprite.x and self.sprite.y > k.sprite.y:
                if self.radius + k.radius >= math.sqrt((self.sprite.x - k.sprite.x) ** 2 + (self.sprite.y - k.sprite.y) ** 2):
                    self.colision(k)

            if self.sprite.x > k.sprite.x and self.sprite.y < k.sprite.y:
                if self.radius + k.radius >= math.sqrt((self.sprite.x - k.sprite.x) ** 2 + (k.sprite.y - self.sprite.y) ** 2):
                   self.colision(k)

            if self.sprite.x < k.sprite.x and self.sprite.y > k.sprite.y:
                if self.radius + k.radius >= math.sqrt((k.sprite.x - self.sprite.x) ** 2 + (self.sprite.y - k.sprite.y) ** 2):
                    self.colision(k)

    def colision(self, spaceobject):
        #print(spaceobject)
        object_speed = spaceobject.speed
        object_rotation = spaceobject.rotation
        self_speed = self.speed
        self_rotation = self.rotation

        spaceobject.speed = self_speed
        spaceobject.rotation = self_rotation
        self.speed = object_speed
        self.rotation = object_rotation

        if str(type(spaceobject)) == "<class '__main__.Spaceship'>":
            spaceobject.colision(self)

        
    def delete(self):
        self.sprite.delete()
        objects.remove(self)


class Spaceship(SpaceObject):
    
    def __init__(self, scale, position_x, position_y, speed):
        ship_image = pyglet.image.load('ship.png')
        ship_image.anchor_x = ship_image.width // 2  #set ship x anchor to middle
        ship_image.anchor_y = ship_image.height // 2  #set ship y anchor to middle
        global batch
        global HEIGHT
        global WIDTH
        self.radius = 13 #radius in pixels
        self.x = WIDTH // 2 #center of screen, ship start position x
        self.y = HEIGHT // 2 #center of screen, ship start position y
        self.x_speed = 0 #startup x speed
        self.y_speed = 0 #startup y speed
        self.speed = 0
        self.rotation_speed = 0  #rad/s
        self.rotation = math.pi / 2 #radians, startup rotation
        self.sprite = pyglet.sprite.Sprite(ship_image, batch=batch) #ship sprite
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.shoottime = 0.3 #in s

    def keyboard(self, td):
        if 'UP' in pressed_keys and self.speed < 80:
            self.speed += td * SPEEDUP_ACCELERATION

        if 'DOWN' in pressed_keys and self.speed > -80:
            self.speed -= td * SPEEDUP_ACCELERATION

        if 'RIGHT' in pressed_keys and self.rotation_speed < 20:
            self.rotation_speed -= ROTATING_ACCELERATION * td

        if 'LEFT' in pressed_keys and self.rotation_speed > -20:
            self.rotation_speed += ROTATING_ACCELERATION * td
        
        if 'UP' not in pressed_keys and 'DOWN' not in pressed_keys:
            if self.speed > 0:
                self.speed -= td * SPEEDDOWN_ACCELERATION

        if 'DOWN' not in pressed_keys and 'UP' not in pressed_keys:
            if self.speed < 0:
                self.speed += td * SPEEDDOWN_ACCELERATION

        if 'RIGHT' not in pressed_keys:
            if self.rotation_speed < 0:
                self.rotation_speed += ROTATING_ACCELERATION * td
                if self.rotation_speed >= 0.02:
                    self.rotation_speed = 0

        if 'LEFT' not in pressed_keys:
            if self.rotation_speed > 0:
                self.rotation_speed -= ROTATING_ACCELERATION * td
                if self.rotation_speed <= -0.02:
                    self.rotation_speed = 0
        
        if 'R' in pressed_keys:
            reset()

        if 'SPACE' in pressed_keys:
            self.shoot()

        if 'D' in pressed_keys:
            global gameover
            self.delete()
            gameover = True
            #print('You were in the game for', math.floor(gametime), 'seconds.')

    def tick(self, td):
        global gametime
        global indestructible
        super().tick(td)
        self.keyboard(td)
        gametime += td
        self.shoottime -= td
        indestructible -= td

    def colision(self, spaceobject):
        global gameover
        global lasercnt
        global HP
        global indestructible
        if str(type(spaceobject)) != "<class '__main__.Ship_Laser'>":
            super().colision(spaceobject)
        if str(type(spaceobject)) == "<class '__main__.Asteroid'>":
            if indestructible <= 0:
                HP -= 1
                self.sprite.x = WIDTH // 2
                self.sprite.y = HEIGHT // 2
                self.speed = 0
                self.rotation_speed = 0
                self.sprite.rotation = 90 - math.degrees(math.pi // 2)
                indestructible = 6
                #print(HP)
                if HP <= 0:
                    self.delete()
                    gameover = True
                    #print('You were in the game for', math.floor(gametime), 'seconds.')
                pressed_keys.clear()

    def shoot(self):
        if self.shoottime <= 0:
            self.shoottime = 0.3
            #print('ok')
            varname2 = 'laser' + str(lasercnt)
            locals()[varname2] = Ship_Laser(ship=self)
            objects.append(locals()[varname2])
        
class Asteroid(SpaceObject):
    def __init__(self, scale, position_x, position_y, speed):
        global HEIGHT
        global WIDTH
        self.scale = scale
        self.speed = speed
        asteroid_image = pyglet.image.load('clear.png')
        imgrand = random.randrange(0, 4)
        if scale == 0:
            if imgrand == 0:
                asteroid_image = pyglet.image.load('asteroid01.png')
                self.scale = 1
                self.radius = 25 #radius in pixels

            if imgrand == 1:
                asteroid_image = pyglet.image.load('asteroid02.png')
                self.scale = 2
                self.radius = 12 #radius in pixels

            if imgrand == 2:
                asteroid_image = pyglet.image.load('asteroid03.png')
                self.scale = 3
                self.radius = 8 #radius in pixels

            if imgrand == 3:
                asteroid_image = pyglet.image.load('asteroid04.png')
                self.scale = 4
                self.radius = 6 #radius in pixels
        
        else:
            if self.scale == 2:
                asteroid_image = pyglet.image.load('asteroid02.png')
                self.radius = 12 #radius in pixels

            if self.scale == 3:
                asteroid_image = pyglet.image.load('asteroid03.png')
                self.radius = 8 #radius in pixels

            if self.scale == 4:
                asteroid_image = pyglet.image.load('asteroid04.png')
                self.radius = 6 #radius in pixels

        asteroid_image.anchor_x = asteroid_image.width // 2
        asteroid_image.anchor_y = asteroid_image.height // 2
        global HEIGHT
        global WIDTH
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(0, 0.1)
        self.anchor_rotation = 0
        self.anchor_rotation_speed = random.uniform(2, 3)
        self.sprite = pyglet.sprite.Sprite(asteroid_image, batch=batch)
        if position_x == 'none' and position_y == 'none':
            pos = random.randrange(0, 4)
            if pos == 0:
                self.sprite.x = random.randrange(0, WIDTH)
                self.sprite.y = HEIGHT
            
            elif pos == 1:
                self.sprite.x = random.randrange(0, WIDTH)
                self.sprite.y = 0
            
            elif pos == 2:
                self.sprite.y = random.randrange(0, HEIGHT)
                self.sprite.x = WIDTH
            
            elif pos == 3:
                self.sprite.y = random.randrange(0, HEIGHT)
                self.sprite.x = 0

        else:
            self.sprite.x = position_x
            self.sprite.y = position_y
            

        self.sprite.rotation = 90 - math.degrees(self.anchor_rotation)
        if self.speed == 0:
            self.speed = random.uniform(10, 30)

    def tick(self, td):
        super().tick(td)
        self.anchor_rotation += self.anchor_rotation_speed * td
        self.sprite.rotation = 90 - math.degrees(self.anchor_rotation)

    def colision (self, spaceobject):
        if str(type(spaceobject)) != "<class '__main__.Ship_Laser'>":
            super().colision(spaceobject)
        
        #else:
         #   spaceobject.delete()

    def delete(self):
        global score
        global ingame_objects
        global objects
        if self.scale == 1:
            score += 1
            varname3 = 'asteroid' + str(ingame_objects + 1)
            locals()[varname3] = Asteroid(scale=2, position_x=self.sprite.x + 15, position_y=self.sprite.y, speed=self.speed + 2)
            objects.append(locals()[varname3])
            varname4 = 'asteroid' + str(ingame_objects + 2)
            locals()[varname4] = Asteroid(scale=2, position_x=self.sprite.x - 15, position_y=self.sprite.y, speed=self.speed + 2)
            objects.append(locals()[varname4])
            ingame_objects += 2
        if self.scale == 2:
            score += 2
            varname3 = 'asteroid' + str(ingame_objects + 1)
            locals()[varname3] = Asteroid(scale=3, position_x=self.sprite.x + 10, position_y=self.sprite.y, speed=self.speed + 2)
            objects.append(locals()[varname3])
            varname4 = 'asteroid' + str(ingame_objects + 2)
            locals()[varname4] = Asteroid(scale=3, position_x=self.sprite.x - 10, position_y=self.sprite.y, speed=self.speed + 2)
            objects.append(locals()[varname4])
            ingame_objects += 2
        if self.scale == 3:
            score += 5
            varname3 = 'asteroid' + str(ingame_objects + 1)
            locals()[varname3] = Asteroid(scale=4, position_x=self.sprite.x + 7, position_y=self.sprite.y, speed=self.speed + 2)
            objects.append(locals()[varname3])
            varname4 = 'asteroid' + str(ingame_objects + 2)
            locals()[varname4] = Asteroid(scale=4, position_x=self.sprite.x - 7, position_y=self.sprite.y, speed=self.speed + 2)
            objects.append(locals()[varname4])
            ingame_objects += 2
        if self.scale == 4:
            score += 10
        
        super().delete()
        #print(score)


class Ship_Laser(SpaceObject):
    def __init__(self, ship):
        laser_image = pyglet.image.load('laser.png')
        laser_image.anchor_x = laser_image.width // 2
        laser_image.anchor_y = laser_image.height // 2
        self.rotation = ship.rotation
        self.rotation_speed = 0
        self.speed = LASER_SPEED + ship.speed
        self.radius = 2 #radius in px
        self.sprite = pyglet.sprite.Sprite(laser_image, batch=batch)
        self.sprite.x = ship.sprite.x
        self.sprite.y = ship.sprite.y
        self.lifetime = LASER_LIFETIME
        self.force = 1

    def tick(self, td):
        super().tick(td)
        self.lifetime -= td
        if self.lifetime <= 0:
            self.delete()

    def colision(self, spaceobject):
        if str(type(spaceobject)) == "<class '__main__.Asteroid'>" and self.force > 0:
            spaceobject.delete()
            self.lifetime = 0
            self.force = 0


game = pyglet.window.Window(caption=TITLE)
game_icon = pyglet.image.load('ship.png')
game.set_icon(game_icon)
game.clear()
HEIGHT = game.height
WIDTH = game.width

objects = []
hp = []

def initialization(objectsCnt):
    global objects
    global winer
    global batch
    winer = False
    objects.clear()
    for i in range(0, objectsCnt + 1):
        if i == 0:
            ship = Spaceship(scale=0, position_x='none', position_y='none', speed=0)
            objects.insert(0, ship)
        else:
            varname = 'asteroid' + str(i)
            locals()[varname] = Asteroid(scale=0, position_x='none', position_y='none', speed=0)
            objects.append(locals()[varname])
            
initialization(OBJECTSCNT)

def draw_ship():
    global gameover
    global gametime
    global pressed_keys
    global winer
    global timeprint
    global win
    global fullscreen
    global WIDTH
    global HEIGHT
    global hp
    global indestructible
    HEIGHT = game.height
    WIDTH = game.width
    if not win:
        game.clear()
    batch.draw()
    for l in hp:
        l.draw()
    rectangle_draw(0, HEIGHT - HEIGHT // 6, WIDTH / 4, HEIGHT - HEIGHT // 6 + 5)
    rectangle_draw(WIDTH / 4, HEIGHT - HEIGHT // 6, WIDTH / 4 - 5, HEIGHT)
    score_text = pyglet.text.Label('SCORE: ' + str(score), font_size= HEIGHT // 30, font_name= 'Liberation Mono', x= WIDTH // 100, y= HEIGHT - HEIGHT // 20)
    score_text.draw()

    indestructible_text = pyglet.text.Label('Indestructible for ' + str(math.floor(indestructible)) + ' s.', font_size= HEIGHT // 30, font_name= 'Liberation Mono', x= WIDTH // 3, y= HEIGHT - HEIGHT // 20)
    if indestructible >= 0:
        indestructible_text.draw()

    if 'F11' in pressed_keys and game.fullscreen == False:
        game.set_fullscreen(True)
        fullscreen = False
    
    if 'F12' in pressed_keys and game.fullscreen == True:
        game.set_fullscreen(False)

    if gameover:
        objects.clear()
        game.clear()
        gameover_text = pyglet.text.Label('GAME OVER', font_size= HEIGHT // 10, font_name= 'Liberation Mono', x= WIDTH // 4, y= HEIGHT // 2)
        score_text2 = pyglet.text.Label('Your score is ' + str(score), font_size= HEIGHT // 50, font_name= 'Liberation Mono', x= WIDTH // 4, y= HEIGHT // 4)
        gametime_text = pyglet.text.Label('You were in the game for ' + str(math.floor(gametime)) + ' seconds', font_size= HEIGHT // 50, font_name= 'Liberation Mono', x= WIDTH // 4, y= HEIGHT // 4 + HEIGHT//10)
        gameover_text.draw()
        score_text2.draw()
        gametime_text.draw()

    if asteroidcheck() and not gameover and not 'R' in pressed_keys:
        winer = False
        win = True
        if timeprint:
            #print('You were in the game for', math.floor(gametime), 'seconds.')
            timeprint = False
        objects.clear()
        game.clear()
        win_text = pyglet.text.Label('YOU WIN!', font_size= HEIGHT // 10, font_name= 'Liberation Mono', x= WIDTH // 4, y= HEIGHT // 2)
        score_text2 = pyglet.text.Label('Your score is ' + str(score), font_size= HEIGHT // 50, font_name= 'Liberation Mono', x= WIDTH // 4, y= HEIGHT // 4)
        gametime_text = pyglet.text.Label('You were in the game for ' + str(math.floor(gametime)) + ' seconds', font_size= HEIGHT // 50, font_name= 'Liberation Mono', x= WIDTH // 4, y= HEIGHT // 4 + HEIGHT//10)
        win_text.draw()
        score_text2.draw()
        gametime_text.draw()
        pressed_keys.clear()

    if 'R' in pressed_keys:
        reset()
        game.clear()

    hp.clear()

    for k in range(1, HP + 1):
        varname5 = 'hpcnter'
        locals()[varname5] = pyglet.sprite.Sprite(pyglet.image.load('ship.png'), x= WIDTH // 1000 + k * 25, y= HEIGHT - HEIGHT // 6.5)
        hp.append(locals()[varname5])

    
 

def clocktick(td):
    for j in objects:
        j.tick(td)
        j.position() 

def press_key(character, modificator):
    if character == pyglet.window.key.UP:
        pressed_keys.add('UP')
    
    if character == pyglet.window.key.DOWN:
        pressed_keys.add('DOWN')

    if character == pyglet.window.key.RIGHT:
        pressed_keys.add('RIGHT')
    
    if character == pyglet.window.key.LEFT:
        pressed_keys.add('LEFT')
    
    if character == pyglet.window.key.R:
        pressed_keys.add('R')

    if character == pyglet.window.key.D:
        pressed_keys.add('D')

    if character == pyglet.window.key.SPACE:
        pressed_keys.add('SPACE')

    if character == pyglet.window.key.F11:
        pressed_keys.add('F11')

    if character == pyglet.window.key.F12:
        pressed_keys.add('F12')

def release_key(character, modificator):
    if character == pyglet.window.key.UP:
        pressed_keys.discard('UP')
    
    if character == pyglet.window.key.DOWN:
        pressed_keys.discard('DOWN')

    if character == pyglet.window.key.RIGHT:
        pressed_keys.discard('RIGHT')

    if character == pyglet.window.key.D:
        pressed_keys.discard('D')
    
    if character == pyglet.window.key.LEFT:
        pressed_keys.discard('LEFT')

    if character == pyglet.window.key.R:
        pressed_keys.discard('R')
    
    if character == pyglet.window.key.SPACE:
        pressed_keys.discard('SPACE')

    if character == pyglet.window.key.F11:
        pressed_keys.discard('F11')

    if character == pyglet.window.key.F12:
        pressed_keys.discard('F12')

def reset():
    global OBJECTSCNT
    global gameover
    global gametime
    global winer
    global timeprint
    global win
    global score
    global HP
    HP = 3
    gameover = False
    winer = False
    gametime = 0.0
    timeprint = True
    win = False
    score = 0
    initialization(OBJECTSCNT)

def asteroidcheck():
    global winer
    global objects
    if not winer:
        ast = 0
        for l in objects:
            if str(type(l)) == "<class '__main__.Asteroid'>":
                ast += 1

        if ast == 0:
            return True

def rectangle_draw(x1, y1, x2, y2):
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(int(x1), int(y1))
    gl.glVertex2f(int(x1), int(y2))
    gl.glVertex2f(int(x2), int(y2))
    gl.glVertex2f(int(x2), int(y1))
    gl.glEnd()



game.push_handlers(on_draw=draw_ship, on_key_press=press_key, on_key_release=release_key)

pyglet.clock.schedule(clocktick)

pyglet.app.run()
