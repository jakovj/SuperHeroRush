import objects
import pygame, os
import random
import high_scores

#todo:

# work on high score .txt encryption
# add super attack

os.environ['SDL_VIDEO_CENTERED'] = '1' # center the window

class Game(object):
    defaultWidth = 800
    defaultHeight = 800

    pygame.font.init()

    fps = 30
    maxObstacles = 10
    maxEnergy = 3

    energyValue = 200
    obstacleValue = 100

    # color initialization
    red = (255,0,0)
    white = (255,255,255)
    black = (0,0,0)
    skyBlue = (126,203,242)
    lightGray = (201,201,201)

    icon = pygame.image.load('icon.png')

    def __init__(self, width = defaultWidth, height = defaultHeight):
        self.running = True
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.hero = None
        self.score = 0

        self.initMessages()

        # music channels, more than 1 channel needed because of the sounds overlaping
        self.hitSoundCh = pygame.mixer.Channel(1)
        self.hitSoundCh.set_volume(0.3)
        self.attackSoundCh = pygame.mixer.Channel(2)
        self.attackSoundCh.set_volume(0.3)
        self.energySoundCh = pygame.mixer.Channel(3)
        self.energySoundCh.set_volume(0.3)
        self.deathSoundCh = pygame.mixer.Channel(4)
        self.deathSoundCh.set_volume(0.3)

        self.highScore = high_scores.HighScores(self)



        self.background = [126, 203, 242]

        # pygame.sprite.Group(s), logic groups of game items
        self.heroes = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.energy = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()
        self.attacksLeft = pygame.sprite.Group()
        self.musicButton = pygame.sprite.GroupSingle()  # contains only 1 sprite, only it's image changes
        self.musicButton.add(objects.Music(self))
        for i in range(objects.Hero.maxAttacks):
            attack = objects.Attack(self)
            attack.setCoordinates(600 + i * objects.Attack.width, self.height - objects.Attack.height)
            self.attacksLeft.add(attack)


        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('SuperHero Rush')    # setting the game caption
        pygame.display.set_icon(Game.icon)              # setting the game icon



    def startScreen(self):
        '''
        When clicked on Surface it opens appropriate window or starts new game.
        '''
        self.__init__()
        self.heroList()

        self.redrawItems()

        for msg in self.startScreenMsgs:
            msg.displayMessage()


        # choosing hero logic ...
        while self.hero == None:

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.hero = self.chooseHero() # returns None if clicked anywhere else
                    if self.hero == None:
                        self.changeMusicState()
                        self.controls()
                        self.author()
                        self.highScores()
                if event.type == pygame.QUIT:
                    return False
        # when finally chosen it is the only item on screen
        if self.running:
            self.heroes.empty()
            self.heroes.add(self.hero)
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
            return self.run()



    def run(self):
        '''
        Standard run function.
        It ends only if X(in the top-right corner,quit) is pressed or if hero hits an obstacle.
        '''



        # game loop
        while self.running:
            self.handleEvents()
            self.createRocks()
            self.createEnergy()
            self.redrawItems()

            self.collectEnergy()
            self.destroyObstacles()
            if self.heroDeath():
                self.running = False

            self.clock.tick(Game.fps)
            self.moveEverythingDown()

        self.deadMsg.displayMessage()
        self.Hero = None


        sound = pygame.mixer.Sound('death.ogg')
        self.deathSoundCh.play(sound)
        pygame.time.wait(1000)
        self.highScore.update(self.score)

        self.highScore.close()

        return True


    def handleEvents(self):
        '''
        Function which processes all the events.
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    self.hero.update(-40,0)
                elif event.key == pygame.K_RIGHT:
                    self.hero.update(40,0)
                elif event.key == pygame.K_UP:
                    self.hero.attack()
            elif event.type == pygame.USEREVENT + 1:
                self.hero.regainAttack()



    def redrawItems(self):
        '''
        Function which redraws all items on screen
        and removes all items which are not on the screen (due to their movement) from a list
        '''

        self.changeBackgroundColor()

        self.display.fill(tuple(self.background))


        self.removeUnvisibleItems(self.obstacles)
        self.removeUnvisibleItems(self.attacks)
        self.removeUnvisibleItems(self.energy)


        self.obstacles.draw(self.display)
        self.energy.draw(self.display)
        self.attacks.draw(self.display)
        if self.hero != None and self.hero != 1:
            self.hero.drawAttacksLeft()

        self.heroes.draw(self.display)


        if self.hero != None and self.hero != 1:
            # display score only when game is active
            self.scoreMsg.update('Score:' + str(self.score))
            self.scoreMsg.displayMessage()
        else:
            # music state (ON/OFF) can only be changed before starting a game
            self.musicButton.draw(self.display)

        pygame.display.update()

    def removeUnvisibleItems(self, group):
        for item in group.sprites():
            if item.rect.y > self.height or (item.rect.y + item.height < 0 and isinstance(item,objects.Attack)):
                group.remove(item)


    def moveEverythingDown(self):
        '''
        Function which does movement stuff
        and tries to make it look like hero is moving.
        '''

        self.attacks.update(0,-10)
        self.obstacles.update(0,10)
        self.energy.update(0,5)

        if self.hero.rect.y  > self.height / 2:
            self.hero.update(0, -5)
        else:
            # when hero comes up close to the top of the window
            # hero starts to go down slowly
            for i in range(5):
                self.hero.update(0, 1)
            self.redrawItems()



    def createRocks(self):
        '''
        Function which creates obstacles if there is less then maxObstacles.
        '''
        collision = True
        if len(self.obstacles.sprites()) < Game.maxObstacles:
            while collision:
                rockSprite = objects.Rock(self)
                if len(pygame.sprite.spritecollide(rockSprite, self.obstacles, False)) == 0 and len(pygame.sprite.spritecollide(rockSprite, self.energy, False)) == 0:
                    self.obstacles.add(rockSprite)
                    collision = False

    def createEnergy(self):
        collision = True
        if len(self.energy.sprites()) < Game.maxEnergy:
            while collision:
                energySprite = objects.Energy(self)
                if len(pygame.sprite.spritecollide(energySprite, self.obstacles, False)) == 0 and len(pygame.sprite.spritecollide(energySprite, self.energy, False)) == 0:
                    self.energy.add(energySprite)
                    collision = False


    def chooseHero(self):
        '''
        Function which returns clicked Hero or None if not clicked on any hero.
        '''
        xy = pygame.mouse.get_pos()
        x = xy[0]
        y = xy[1]
        hero = None
        for item in self.heroes.sprites():
            if x >= item.rect.x and x <= item.rect.x + item.height and y >= item.rect.y and y <= item.rect.y + item.width:
                hero = item
        return hero

    def heroList(self):
        '''
        Function which initializes playable heroes.
        '''
        self.heroes.add(objects.Hero(self, 'spiderman'))
        self.heroes.add(objects.Hero(self, 'hulk'))
        self.heroes.add(objects.Hero(self, 'wolverine'))
        self.heroes.add(objects.Hero(self, 'thor'))
        self.heroes.add(objects.Hero(self, 'captain_america'))
        self.heroes.add(objects.Hero(self, 'iron_man'))
        self.heroes.add(objects.Hero(self, 'venom'))

    def destroyObstacles(self):
        '''
        When obstacle is hit by an attack it's being destroyed by this funtion.
        Also puff effect is implemented.
        '''
        attacks = self.attacks.sprites()
        for i in range(len(self.attacks)):
            collidingList = pygame.sprite.spritecollide(attacks[i], self.obstacles, True)
            if len(collidingList) != 0:
                # puff effect on first obstacle hit
                collidingList[0].puff()
                self.score += Game.obstacleValue

                self.attacks.remove(attacks[i])

    def collectEnergy(self):

        collidingList = pygame.sprite.spritecollide(self.hero, self.energy, True)
        if len(collidingList) != 0:
            self.score += Game.energyValue
            collidingList[0].collect()
            self.energy.remove(collidingList[0])

    def heroDeath(self):
        collidingList = pygame.sprite.spritecollide(self.hero, self.obstacles, True)
        if len(collidingList) != 0:
            collidingList[0].puff()
            return True
        return False

    def changeBackgroundColor(self):
        '''
        Function which changes background color and makes it look lake a gradient.
        It changes all shades, one at the time, but gently.
        '''
        i = random.randrange(0,3)
        color = self.background[i]
        color += random.randrange(-2,2)
        if color > 90 and color < 230:
            self.background[i] = color

    def changeMusicState(self):
        xy = pygame.mouse.get_pos()
        x = xy[0]
        y = xy[1]
        for item in self.musicButton.sprites():
            if x >= item.rect.x and x <= item.rect.x + item.height and y >= item.rect.y and y <= item.rect.y + item.width:
                item.change()
                self.display.fill(tuple(self.background), pygame.Rect(item.rect.x, item.rect.y, objects.Music.width, objects.Music.height)) # fills the button with background color
                self.musicButton.draw(self.display)     # and then draws the new one
                pygame.display.update()

    def controls(self):
        xy = pygame.mouse.get_pos()
        x = xy[0]
        y = xy[1]

        if x >= self.controlsMsg.x and x <= self.controlsMsg.x + len(self.controlsMsg.msg)*self.controlsMsg.size and y >= self.controlsMsg.y and y <= self.controlsMsg.y + self.controlsMsg.size:
            self.display.fill(tuple(self.background))
            self.controlsMsg.displayMessage()
            linesForDisplay = ['left/right arrows for movement', 'up arrow to shoot', 'S for super attack']

            for line in linesForDisplay:
                msgFont = pygame.font.SysFont('Console', 30)
                msgSurface = msgFont.render(line, False, Game.black)
                self.display.blit(msgSurface, (self.controlsMsg.x - 100, self.controlsMsg.size + 50 + self.controlsMsg.y + linesForDisplay.index(line)*(self.controlsMsg.size + 10)))

            pygame.display.update()
            pygame.time.wait(3000)
            self.controlsMsg.update('Controls')
            self.redrawItems()

            for msg in self.startScreenMsgs:
                msg.displayMessage()


    def highScores(self):
        xy = pygame.mouse.get_pos()
        x = xy[0]
        y = xy[1]

        if x >= self.highScoresMsg.x and x <= self.highScoresMsg.x + len(self.highScoresMsg.msg) * self.highScoresMsg.size and y >= self.highScoresMsg.y and y <= self.highScoresMsg.y + self.highScoresMsg.size:
            self.display.fill(tuple(self.background))
            self.highScoresMsg.displayMessage()
            txt = ''

            for i in range(high_scores.HighScores.maxHs):
                print(i)
                score = self.highScore.list[i]
                name = list(score[1])
                name.pop()
                line = str(i + 1) + ". " + "".join(name) + " " + str(score[0])
                msgFont = pygame.font.SysFont('Console', 30)
                msgSurface = msgFont.render(line, False, Game.black)
                self.display.blit(msgSurface, (self.highScoresMsg.x, self.highScoresMsg.size + 50 + self.highScoresMsg.y + self.highScoresMsg.size + i*30))
            print(txt)


            pygame.display.update()
            pygame.time.wait(4000)
            self.controlsMsg.update('Controls')
            self.redrawItems()

            for msg in self.startScreenMsgs:
                msg.displayMessage()

    def author(self):
        xy = pygame.mouse.get_pos()
        x = xy[0]
        y = xy[1]

        if x >= self.authorMsg.x and x <= self.authorMsg.x + len(self.authorMsg.msg)*self.authorMsg.size and y >= self.authorMsg.y and y <= self.authorMsg.y + self.authorMsg.size:
            self.display.fill(tuple(self.background))
            self.authorMsg.displayMessage()
            line = 'Jakov Jezdić'
            msgFont = pygame.font.SysFont('Console', 60)
            msgSurface = msgFont.render(line, False, Game.black)
            self.display.blit(msgSurface, (self.controlsMsg.x, self.controlsMsg.size + 50 + self.controlsMsg.y + self.controlsMsg.size + 10))

            line = '2017.'
            msgFont = pygame.font.SysFont('Console', 40)
            msgSurface = msgFont.render(line, False, Game.black)
            self.display.blit(msgSurface, (self.controlsMsg.x, self.controlsMsg.size + 50 + self.controlsMsg.y + self.controlsMsg.size + 100))

            pygame.display.update()
            pygame.time.wait(2000)
            self.controlsMsg.update('Controls')
            self.redrawItems()

            for msg in self.startScreenMsgs:
                msg.displayMessage()


    def initMessages(self):
        # StartScreen messages :

        self.highScoresMsg = objects.Message(self, 'High Scores', self.width / 2 - 175, self.height / 2 - 150, 'Console', 50, Game.black)
        self.controlsMsg = objects.Message(self, 'Controls', self.width / 2 - 175, self.height / 2 - 100, 'Console', 50, Game.black)
        self.authorMsg = objects.Message(self, 'Author', self.width / 2 - 175, self.height / 2 - 50, 'Console', 50, Game.black)
        self.clickMsg = objects.Message(self, 'click on a hero to start game', self.width / 2 - 175, self.height / 2 + 20, 'Console', 15, Game.red)
        self.scoreMsg = objects.Message(self, 'Score:' + str(self.score), 0, 0, 'Console', 60, Game.black)
        self.deadMsg = objects.Message(self, 'You\'re dead :(', self.width / 2 - 300, self.height / 2 - 150, 'Console', 60, Game.black)
        self.startScreenMsgs = [self.highScoresMsg, self.controlsMsg, self.authorMsg, self.clickMsg]
