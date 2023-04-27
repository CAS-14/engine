import pygame
import os
import random
import time

# tutorial used: https://dr0id.bitbucket.io/legacy/pygame_tutorials.html
# this game is (c) 2023 by weirdcease

DIRECTIONS = ["n", "s", "e", "w", "ne", "nw", "se", "sw"]

def asset(filename):
    return os.path.join("assets", filename)

def load_image(filename):
    return pygame.image.load(asset(filename))


class App:
    def __init__(self):
        self.run_dir = os.path.dirname(__file__)
        os.chdir(self.run_dir)

        self.width = 960
        self.height = 720
        self.size = self.width, self.height

        self.speed = 60
        self.move_step = 10

    def check_events(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key:
                        return event.key

    def main(self):
        pygame.init()

        self.logo = load_image("catsmirk.png")
        pygame.display.set_icon(self.logo)
        pygame.display.set_caption("minimal program")
     
        self.font = pygame.font.Font(asset("alagard.ttf"), 14)

        self.text_welcome = Text(self, content="Welcome", pos=(50, 50))
        self.text_newgame = Text(self, content="New Game", pos=(50, 50))
        self.text_options = Text(self, content="Options", pos=(50, 50))

        self.screen = pygame.display.set_mode(self.size)
        
        self.sprites = []
        
        for i in range(200):
            x = random.randint(100, self.width-100)
            y = random.randint(100, self.height-100)
            vel_x = random.randint(-10, 10)
            vel_y = random.randint(-10, 10)

            projectile = Projectile(self, image="catsmirk.png", pos=(x, y), velocity=(vel_x, vel_y), bounce=True)

            self.sprites.append(projectile)
        
        self.loop = self.scn_menu

        self.running = True

        # GAME LOOP
        while self.running:
            key = self.check_events()

            self.loop(key)

            pygame.display.flip()

            time.sleep(1 / self.speed)

    def scn_menu(self, key):
        self.screen.fill((64, 0, 0))
        self.screen.fill((128, 0, 0), rect=(200, 70, 50, self.height-120))

        self.text_welcome.blit()

    def scn_cats(self):
        self.screen.fill((64, 0, 0))

        for sprite in self.sprites:
            if isinstance(sprite, Projectile):
                sprite.step()

            sprite.blit()
        

class Positional:
    def __init__(self, app: App, *, pos: tuple = (1, 1)):
        self.app = app
        self.x, self.y = pos

    def blit(self):
        self.app.screen.blit(self.object, (self.x, self.y))


class Text(Positional):
    def __init__(self, *args, content: str, color: tuple = None, background: tuple = None, font: pygame.font.Font = None, **kwargs):
        super().__init__(*args, **kwargs)

        if not color:
            color = (30, 10, 100)

        if font:
            self.font = font
        else:
            self.font = self.app.font

        self.object = self.font.render(content, True, color, background)


class Sprite(Positional):
    def  __init__(self, *args, image: str, **kwargs):
        super().__init__(*args, **kwargs)

        self.object = self.image = load_image(image)

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.size = self.width, self.height

        self.max_x = self.app.width - self.width
        self.max_y = self.app.height - self.height

    def restrict(self):
        if self.x < 0:
            self.x = 0
        elif self.x > self.max_x:
            self.x = self.max_x

        if self.y < 0:
            self.y = 0
        elif self.y > self.max_y:
            self.y = self.max_y


class Projectile(Sprite):
    def __init__(self, *args, velocity: tuple, bounce: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        self.vel_x, self.vel_y = velocity
        self.vel_x_start, self.vel_y_start = self.vel_x, self.vel_y
        self.bounce = bounce

    def step(self):
        self.x += self.vel_x
        self.y += self.vel_y

        if self.bounce:
            self.restrict()

            if self.x == 0:
                self.vel_x = abs(self.vel_x)
            elif self.x == self.max_x:
                self.vel_x = -abs(self.vel_x)

            if self.y == 0:
                self.vel_y = abs(self.vel_y)
            elif self.y == self.max_y:
                self.vel_y = -abs(self.vel_y)

        else:
            if self.x > self.max_x+5 or self.x < -self.width-5 or self.y > self.max_y+5 or self.y < -self.height-5:
                del self

        
if __name__=="__main__":
    app = App()
    app.main()
