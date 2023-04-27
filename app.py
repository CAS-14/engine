import pygame
import os
import random
import time

# tutorial used: https://dr0id.bitbucket.io/legacy/pygame_tutorials.html
# this game is (c) 2023 by weirdcease

DIRECTIONS = ["n", "s", "e", "w", "ne", "nw", "se", "sw"]

def load_image(filename):
    return pygame.image.load(os.path.join("assets", filename))


class App:
    def __init__(self):
        self.run_dir = os.path.dirname(__file__)
        os.chdir(self.run_dir)

        self.speed = 60

        self.size = self.width, self.height = 960, 720

        self.move_step = 10

    def main(self):
        pygame.init()

        logo = load_image("catsmirk.png")
        pygame.display.set_icon(logo)
        pygame.display.set_caption("minimal program")
     
        self.screen = pygame.display.set_mode(self.size)
        
        self.sprites = []
        
        for i in range(200):
            x = random.randint(100, self.width-100)
            y = random.randint(100, self.height-100)
            vel_x = random.randint(-10, 10)
            vel_y = random.randint(-10, 10)

            projectile = Projectile(self, "catsmirk.png", pos=(x, y), velocity=(vel_x, vel_y), bounce=True)

            self.sprites.append(projectile)
        
        self.running = True

        # GAME LOOP
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # game logic below here
            self.action()

    def scn_cats(self):
        self.screen.fill((64, 0, 0))

        for sprite in self.sprites:
            if isinstance(sprite, Projectile):
                sprite.step()

            sprite.blit()

        pygame.display.flip()

        time.sleep(1 / self.speed)


class Sprite:
    def  __init__(self, app: App, image_file: str, *, pos: tuple = (1, 1)):
        self.app = app
        self.x, self.y = pos

        self.image = load_image(image_file)

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

    def blit(self):
        self.app.screen.blit(self.image, (self.x, self.y))


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
