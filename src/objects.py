import random
import pygame


class GameObject(pygame.sprite.Sprite):
    '''
    All sprites should inherit from this class.
    '''
    def __init__(self, game, name):
        '''
        Sets the sprite image and rect Surface.
        '''
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.game = game

        self.image = pygame.image.load(name + '.png')

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()

    # basic movement
    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def setCoordinates(self, x, y):
        self.rect.x = x
        self.rect.y = y



class Hero(GameObject):
    '''
    Class which defines hero behavior in the game.
    '''

    maxAttacks = 3

    def __init__(self, game, name):
        '''
        :param game: Game object.
        :param name: Name is expected to be the string before .png extension in name of the matching sprite.
                     Example : sprite name is 'spiderman.png' -> name is 'spiderman'
        '''
        GameObject.__init__(self, game, name)
        rect = self.image.get_rect()
        self.width = rect.width
        self.height = rect.height

        # automatically positions heroes to be in line
        # on the bottom of the window
        self.setCoordinates(len(self.game.heroes) * (self.width + 45) + 40, self.game.height - self.height)


        # hero starts with maximum attacks
        self.num = Hero.maxAttacks

    def update(self, dx, dy):
        if self.rect.x + dx >= 0 and self.rect.x + dx + self.width < self.game.width:
            self.rect.x += dx
        if self.rect.y + dy >= 0 and self.rect.y + dy < self.game.height: # maybe unnecessary
            self.rect.y += dy

    def attack(self):
        if self.num > 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
            sound = pygame.mixer.Sound('attack.ogg')
            self.game.attackSoundCh.play(sound)
            self.game.attacks.add(Attack(self.game))
            self.game.attacksLeft.remove(Attack(self.game))
            self.num -= 1


    def regainAttack(self):
        if self.num < Hero.maxAttacks:
            self.game.attacksLeft.add(Attack(self.game))
            self.num += 1

    def drawAttacksLeft(self):
        for i in range(self.num):
            self.game.display.blit(pygame.image.load('attack.png'), (650 + i * Attack.width, self.game.height - Attack.height))

class Rock(GameObject):
    '''
    Class which defines obstacles and their positioning in the game, as well as, the explosion effect on
    colliding with the attack.
    '''
    width = 40 # real size is 50x50 px
    height = 40

    puffImages = [pygame.image.load('puf.png'), pygame.image.load('puf1.png'), pygame.image.load('puf2.png')]
    puffTime = 15 # time in ms, for which single puff image will be displayed

    def __init__(self,game):
        GameObject.__init__(self, game, 'rock')

        # random positioning in front of the hero
        self.setCoordinates(random.randrange(Rock.width, self.game.width - Rock.width), self.game.hero.rect.y - random.randrange(self.game.height / 2, 2 * self.game.height))



    def puff(self):
        sound = pygame.mixer.Sound('puff.ogg')
        self.game.hitSoundCh.play(sound)
        for puff in Rock.puffImages:
            self.game.display.blit(puff, (self.rect.x, self.rect.y))
            pygame.display.update()
            pygame.time.wait(Rock.puffTime)

class Energy(GameObject):
    width = 40 # the real size
    height = 40

    energyImages = [pygame.image.load('energy.png'), pygame.image.load('energy1.png'), pygame.image.load('energy2.png')]
    energyTime = 15  # time in ms, for which single energy image will be displayed

    def __init__(self,game):
        GameObject.__init__(self, game, 'energy')

        # random positioning in front of the hero
        self.setCoordinates(random.randrange(Rock.width, self.game.width - Rock.width), self.game.hero.rect.y - random.randrange(self.game.height / 2, 2 * self.game.height))
    def collect(self):
        sound = pygame.mixer.Sound('energy.ogg')
        self.game.energySoundCh.play(sound)
        for img in Energy.energyImages:
            self.game.display.blit(img, (self.rect.x, self.rect.y))
            pygame.display.update()
            pygame.time.wait(Energy.energyTime)



class Attack(GameObject):
    '''
    Class which defines attack sprite movement, it's actually different then any other object in the game.
    Attacks go up :)
    '''
    width = 30
    height = 30

    def __init__(self,game):
        GameObject.__init__(self, game, 'attack')
        self.hero = game.hero
        if self.hero != None:
            self.setCoordinates(self.hero.rect.x, self.hero.rect.y)

class Music(GameObject):
    '''
    Music ON/OFF button.
    '''

    width = 40
    height = 40

    def __init__(self, game):
        if pygame.mixer.music.get_busy():
            name = 'musicON'
        else:
            name = 'musicOFF'
        GameObject.__init__(self, game, name)
        self.setCoordinates(self.game.width - Music.width - 20, 20)

    def change(self):
        if self.name == 'musicON':
            self.name = 'musicOFF'
            pygame.mixer.music.stop()
        else:
            self.name = 'musicON'
            pygame.mixer.music.play()
        self.image = pygame.image.load(self.name + '.png')  # must update display image on every change

class Message(object):
    def __init__(self, game, msg, x, y, font, size, color):
        '''
        :param msg: Message to be written.
        :param color: Font color.
        :param x: Top left x coordinate.
        :param y: Top left y coordinate.
        :param font: Font style.
        :param size: Font size.
        '''
        self.game = game
        self.msg = msg
        self.x = x
        self.y = y
        self.color = color
        self.font = font
        self.size = size

    def displayMessage(self):
        msgFont = pygame.font.SysFont(self.font, self.size)
        msgSurface = msgFont.render(self.msg, False, self.color)
        self.game.display.blit(msgSurface, (self.x, self.y))
        pygame.display.update()
    def update(self, msg):
        self.msg = msg
