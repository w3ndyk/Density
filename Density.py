import pygame
import os
import sys
import time
import random
import math

# constants
wn_w = 1200
wn_h = 670
fps = 60

ship_w = ship_h = 13
pill_w = 7
pill_h = 25
pill_count = 0

BLACK = (0, 0, 0)
GRAY = (248, 248, 248)
WHITE = (255, 255, 255)

RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (39, 39, 202)

YELLOW = (245, 245, 0)
ORANGE = (255, 140, 0)
VIOLET = (148, 0, 211)

PINK = (255, 0, 222)

# classes
class Game:
    def __init__(self, caption, screen_w, screen_h):
        self.caption = pygame.display.set_caption(str(caption))
        self.screen = pygame.display.set_mode((screen_w, screen_h), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.intro = self.call = self.play = self.outro = True

        self.title = Text(175, "Density", WHITE, 600, 285)
        self.click = Text(75, "-- Click here to start --", WHITE, 600, 435)
        self.winner = Text(175, "winner", WHITE, 600, 285)
        self.again = Text(75, "-- Click here to play again --", WHITE, 600, 435)

    def blink(self, image, rect):
        # blinking text
        if (pygame.time.get_ticks() % 1000) < 500:
            self.screen.blit(image, rect)

    def announce(self, ship_g, vl, hl):
        t1 = Text(150, "First one to 15000...", BLACK, 600, 335)
        t2 = Text(150, "WINS!", BLACK, 600, 335)
        num = [t1, t2]
        for x in num:
            self.screen.fill(WHITE)
            ship_g.draw(self.screen)
            self.screen.blit(vl, (wn_w / 2, wn_h / 15))
            self.screen.blit(hl, (0, wn_h / 15))

            self.screen.blit(x.image, x.rect)

            self.clock.tick(fps)
            pygame.display.flip()
            time.sleep(1.75)

        time.sleep(1.5)
        self.call = False


class Text:
    def __init__(self, size, text, color, x, y):
        self.font = pygame.font.Font(None, int(size))
        self.image = self.font.render(str(text), 1, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class GameText(pygame.sprite.Sprite):
    def __init__(self, player, size, color, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.color = color
        self.font = pygame.font.Font(None, int(size))
        self.image = self.font.render('0', 1, self.color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y

    def update(self, l_density, r_density):
        if self.player == 'left':
            if l_density <= 0:
                text = "Density: 0"
            else:
                text = "Density: " + str(l_density - 169)

        if self.player == 'right':
            if r_density <= 0:
                text = "Density: 0"
            else:
                text = "Density: " + str(r_density - 169)

        self.image = self.font.render(str(text), 1, self.color)


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.speed = 5
        self.density = ship_w * ship_h
        self.image = pygame.Surface((math.sqrt(ship_w), math.sqrt(ship_h))).convert()
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def grow(self):
        self.rect.width = self.rect.height = math.sqrt(self.density)
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

    def update(self, pill_group, game):
        # ship movement
        key = pygame.key.get_pressed()
        if self.player == 'left':
            if key[pygame.K_w]:
                self.rect.y -= self.speed
            if key[pygame.K_s]:
                self.rect.y += self.speed
            if key[pygame.K_a]:
                self.rect.x -= self.speed
            if key[pygame.K_d]:
                self.rect.x += self.speed
        if self.player == 'right':
            if key[pygame.K_UP]:
                self.rect.y -= self.speed
            if key[pygame.K_DOWN]:
                self.rect.y += self.speed
            if key[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if key[pygame.K_RIGHT]:
                self.rect.x += self.speed

        # boundaries
        if self.rect.y < wn_h/15:
            self.rect.y = wn_h/15
        if self.rect.y > wn_h - self.rect.height:
            self.rect.y = wn_h - self.rect.height

        if self.player == 'left':
            if self.rect.x < 0:
                self.rect.x = wn_w/2 - self.rect.width
            if self.rect.x > wn_w/2 - self.rect.width:
                self.rect.x = 0
        if self.player == 'right':
            if self.rect.x > wn_w - self.rect.width:
                self.rect.x = wn_w/2
            if self.rect.x < wn_w/2:
                self.rect.x = wn_w - self.rect.width

        # eating pills
        collisions = pygame.sprite.spritecollide(self, pill_group, True)
        for key in collisions:
            # red, green, blue, black -- +density
            if key.density < 5:
                self.density += key.density * 50
            # yellow -- slows down
            elif key.density == 5:
                self.speed = 2
            # orange -- -density
            elif key.density == 6:
                self.density -= 50
            # violet -- makes ships similar color to screen
            elif key.density == 7:
                self.image.fill(GRAY)
            # pink -- +density, remedy (resets speed and color)
            elif key.density == 8:
                self.image.fill(BLACK)
                self.speed = 5
                self.density += 25

        # grow ship
        self.grow()


class Pill(pygame.sprite.Sprite):
    def __init__(self, xval, density):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 3
        self.image = pygame.Surface((pill_w, pill_h)).convert()
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(xval, wn_h/15)
        self.density = density
        self.image.fill(self.set_color())

    def set_color(self):
        if self.density == 1:
            return RED
        elif self.density == 2:
            return GREEN
        elif self.density == 3:
            return BLUE
        elif self.density == 4:
            return BLACK

        elif self.density == 5:
            return YELLOW
        elif self.density == 6:
            return ORANGE
        elif self.density == 7:
            return VIOLET

        elif self.density == 8:
            return PINK

    def update(self):
        # speed
        if self.density == 1:
            self.rect.y += 3
        elif self.density == 2:
            self.rect.y += 5
        elif self.density == 3:
            self.rect.y += 7
        elif self.density == 4:
            self.rect.y += 9

        elif self.density == 5:
            self.rect.y += 4
        elif self.density == 6:
            self.rect.y += 4
        elif self.density == 7:
            self.rect.y += 4

        elif self.density == 8:
            self.rect.y += 2

        # off screen
        if self.rect.y > wn_h:
            self.kill()


def gen_random(x1, x2):
    xval_density = []
    for i in range(3000):
        xval_density.append((random.randrange(x1, x2), int(random.choice('1111111111111111222223334555666777778888'))))
    return xval_density


def main():
    # initialize variables
    global wn_w, wn_h, fps, ship_w, ship_h, pill_w, pill_h, pill_count, \
        BLACK, GRAY, WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, VIOLET, PINK

    while True:
        # objects
        game = Game("Density", wn_w, wn_h)

        l_xval_density = gen_random(0, (wn_w / 2) - pill_w)
        r_xval_density = gen_random(wn_w / 2, (wn_w - pill_w))
        max_pill_count = len(l_xval_density)
        loop_counter = 0

        l_ship = Ship((wn_w/4) - (ship_w/2), wn_h - (ship_h*4), 'left')
        r_ship = Ship((wn_w/4)*3 - (ship_w/2), wn_h - (ship_h*4), 'right')

        v_line = pygame.Surface((1, wn_h))
        h_line = pygame.Surface((wn_w, 1))

        l_score = GameText('left', 40, BLACK, wn_w/5, 10)
        r_score = GameText('right', 40, BLACK, wn_w*0.7, 10)

        # groups
        ship_group = pygame.sprite.Group()
        ship_group.add(l_ship, r_ship)

        pill_group = pygame.sprite.Group()

        score_group = pygame.sprite.Group()
        score_group.add(l_score, r_score)

        # intro loop
        while game.intro:
            # checks if window exit button is pressed or if screen is clicked
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                    game.screen.blit(game.click.image, game.click.rect)
                    pygame.display.flip()
                    game.intro = False
                    time.sleep(1)

            # blit images
            game.screen.fill(BLACK)
            game.screen.blit(game.title.image, game.title.rect)
            # blinking text
            game.blink(game.click.image, game.click.rect)

            # limits frames per iteration of while loop
            game.clock.tick(fps)
            # writes to main surface
            pygame.display.flip()

        # game loop
        while game.play:
            for event in pygame.event.get():
                # window exit button
                if event.type == pygame.QUIT:
                    sys.exit()
                # keyboard
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # announcement
            while game.call:
                ship_group.update(pill_group, game)
                game.announce(ship_group, v_line, h_line)

            # update groups
            ship_group.update(pill_group, game)
            pill_group.update()
            score_group.update(l_ship.density, r_ship.density)

            # adding pills
            if pill_count < max_pill_count and loop_counter % 5 == 0:
                l_pill = Pill(l_xval_density[pill_count][0], l_xval_density[pill_count][1])
                r_pill = Pill(r_xval_density[pill_count][0], r_xval_density[pill_count][1])
                pill_group.add(l_pill, r_pill)
                pill_count += 1

            # score
            if l_ship.density >= 15000:
                game.winner = Text(175, "Left Player wins!", WHITE, 600, 285)
                if l_ship.density < 45000:
                    l_ship.density += 50
                    r_ship.density -= 5
                    if r_ship.density <= 0:
                        r_ship.density = 0
                        r_ship.rect.width = 0
                        r_ship.rect.height = 0
                        pygame.time.delay(1000)
                        game.play = False
                else:
                    pygame.time.delay(1000)
                    game.play = False

            elif r_ship.density >= 15000:
                game.winner = Text(175, "Right Player wins!", WHITE, 600, 285)
                if r_ship.density < 45000:
                    r_ship.density += 50
                    l_ship.density -= 5
                    if l_ship.density <= 0:
                        l_ship.density = 0
                        l_ship.rect.width = 0
                        l_ship.rect.height = 0
                        pygame.time.delay(1000)
                        game.play = False
                else:
                    pygame.time.delay(1000)
                    game.play = False

            # print groups
            game.screen.fill(WHITE)

            ship_group.draw(game.screen)
            pill_group.draw(game.screen)

            game.screen.blit(v_line, (wn_w/2, wn_h/15))
            game.screen.blit(h_line, (0, wn_h/15))

            score_group.draw(game.screen)

            # limits frames per iteration of while loop
            loop_counter += 1
            game.clock.tick(fps)
            # writes to main surface
            pygame.display.flip()

        # outro loop
        while game.outro:
            # checks if window exit button is pressed or if screen is clicked
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                    game.screen.blit(game.again.image, game.again.rect)
                    pygame.display.flip()
                    game.outro = False
                    time.sleep(1)

            # blit images
            game.screen.fill(BLACK)
            game.screen.blit(game.winner.image, game.winner.rect)
            # blinking
            game.blink(game.again.image, game.again.rect)

            # limits frames per iteration of while loop
            game.clock.tick(fps)
            # writes to main surface
            pygame.display.flip()


if __name__ == "__main__":
    # force static position of screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # runs imported module
    pygame.init()

    main()