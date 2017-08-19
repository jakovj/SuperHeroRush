import pygame
import game

class HighScores(object):
    maxHs = 5
    letters = {pygame.K_a:'a',pygame.K_b:'b',pygame.K_c:'c',pygame.K_d:'d',pygame.K_e:'e',pygame.K_f:'f',pygame.K_g:'g',pygame.K_h:'h',pygame.K_i:'i',pygame.K_j:'j',pygame.K_k:'k'
               ,pygame.K_l:'l',pygame.K_m:'m',pygame.K_n:'n',pygame.K_o:'o',pygame.K_p:'p',pygame.K_q:'q',pygame.K_r:'r',pygame.K_s:'s',pygame.K_t:'t',pygame.K_u:'u',pygame.K_v:'v'
               ,pygame.K_w:'w',pygame.K_x:'x',pygame.K_y:'y',pygame.K_z:'z'}
    def __init__(self, game):
        self.game = game
        self.name = 'high_scores.txt'
        self.file = open(self.name,'r')
        self.lowestScore = 0
        self.list = []
        for line in self.file:
            if line != '\n':
                temp = line.split("_")
                self.list.append([temp[0],temp[1]])
        self.close()

    def update(self, score):
        for i in range(len(self.list)):
            if int(self.list[i][0]) < score:
                name = self.enterPlayerName()
                self.list.insert(i,[score,name + '\n'])
                self.list.pop()
                break

        print(self.list)

        self.file = open(self.name, 'w')
        for score in self.list:
            self.file.write(str(score[0]) + "_" + score[1])

    def enterPlayerName(self):
        name = '___'
        self.game.display.fill(tuple(self.game.background))
        line = 'Enter your name :' + name
        msgFont = pygame.font.SysFont('Console', 40)
        msgSurface = msgFont.render(line, False, game.Game.black)
        self.game.display.blit(msgSurface, (100, 100))
        pygame.display.update()

        print("ENTER")
        i = 0
        s = list(name)
        while True:

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:

                    s[i] = HighScores.letters[event.key]
                    i = i + 1

            line = 'Enter your name :' + "".join(s)
            msgFont = pygame.font.SysFont('Console', 40)
            msgSurface = msgFont.render(line, False, game.Game.black)
            self.game.display.blit(msgSurface, (100, 100))
            pygame.display.update()
            pygame.time.wait(500)

            if i == 3:
                return "".join(s)




    def close(self):
        self.file.close()
