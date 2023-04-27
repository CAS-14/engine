import pygame
import os
import random
import time

# tutorial used: https://dr0id.bitbucket.io/legacy/pygame_tutorials.html
# this game is (c) 2023 by weirdcease

DIRECTIONS = ["n", "s", "e", "w", "ne", "nw", "se", "sw"]
LIFESQUARE = True

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

        self.texts = []
        self.blits = []

    def check_events(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key:
                        return event.key

    def get_text(self, content: str, color: tuple = None, background: tuple = None, font: pygame.font.Font = None):
        for text in self.texts:
            if text.content == content and ((not color) or text.color == color) and ((not background) or text.background == background) and ((not font) or text.font == font):
                return text
            
        new_text = Text(self, content, color=color, background=background, font=font)
        self.texts.append(new_text)
        return new_text

    def main(self):
        pygame.init()

        self.logo = load_image("catsmirk.png")
        pygame.display.set_icon(self.logo)
        pygame.display.set_caption("minimal program")
     
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.Font(asset("alagard.ttf"), 50)
        
        self.loop = self.main_menu
        
        # set scenes as non-initialized
        self.init_cats = False

        # init stuff
        self.menu_index = 0
        self.initialized = []
        self.times = []

        self.running = True

        # GAME LOOP
        while self.running:
            key = self.check_events()
            if key: print(f"{key} pressed!")

            self.loop(key)

            if LIFESQUARE:
                self.screen.fill(tuple([random.randint(0, 255) for i in range(3)]), rect=(self.width-30, self.height-30, 20, 20))

            pygame.display.flip()

            if len(self.times) > 10:
                self.times.pop(1)
            self.times.append(time.time())
            time.sleep(1 / self.speed)

    def opt_quit(self, key):
        self.running = False

    def main_menu(self, key):
        menu_items = ["New Game", "Options", "Music Room", "Cat Room", "Quit"]
        menu_funcs = [None, None, None, self.scn_cats, self.opt_quit]

        if key == pygame.K_DOWN: 
            self.menu_index += 1
        elif key == pygame.K_UP: 
            self.menu_index -= 1
        elif key == pygame.K_RETURN:
            self.loop = menu_funcs[self.menu_index]
            self.menu_index = 0
        
        if self.menu_index > len(menu_items) - 1: 
            self.menu_index = 0
        elif self.menu_index < 0: 
            self.menu_index = len(menu_items) - 1

        self.screen.fill((64, 0, 0))
        self.screen.fill((128, 0, 0), rect=(50, self.height-120, 200, 70))

        for i in range(len(menu_items)):
            if i == self.menu_index:
                color = (30, 10, 150)
                background = (160, 0, 0)
            else:
                color = (250, 40, 5)
                background = None

            text = self.get_text(menu_items[i], color=color, background=background)
            text.blit((70, 70 + 30 * i))

    def scn_cats(self, key):
        if not self.init_cats:
            for i in range(200):
                x = random.randint(100, self.width-100)
                y = random.randint(100, self.height-100)
                vel_x = random.randint(-10, 10)
                vel_y = random.randint(-10, 10)

                projectile = Projectile(self, image="catsmirk.png", pos=(x, y), velocity=(vel_x, vel_y), bounce=True)
                self.blits.append(projectile)

            self.init_cats = True

        self.screen.fill((64, 0, 0))

        for sprite in self.blits:
            if isinstance(sprite, Projectile):
                sprite.step()

            sprite.blit()
        

class Positional:
    def __init__(self, app: App, *, pos: tuple = (1, 1)):
        self.app = app
        self.x, self.y = pos

    def blit(self, pos: tuple = None):
        if not pos:
            pos = self.x, self.y
        self.app.screen.blit(self.object, pos)


class Text(Positional):
    def __init__(self, app: App, content: str, *, pos: tuple = (1, 1), color: tuple = None, background: tuple = None, font: pygame.font.Font = None, antialias: bool = True):
        super().__init__(app, pos=pos)

        if not color:
            color = (30, 10, 100)

        self.content = content
        self.color = color
        self.background = background

        if font:
            self.font = font
        else:
            self.font = self.app.font

        self.object = self.font.render(self.content, antialias, self.color, self.background)


class Sprite(Positional):
    def  __init__(self, app: App, *, image: str, pos: tuple = (1, 1)):
        super().__init__(app, pos=pos)

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
    def __init__(self, app: App, *, image: str, pos: tuple = (1, 1), velocity: tuple = (0, 0), bounce: bool = False):
        super().__init__(app, image=image, pos=pos)

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
