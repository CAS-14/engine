import pygame
import engine
import random

OBSTACLE_COUNT = 5

class ObstacleTest(engine.App):
    def __init__(self):
        super().__init__(title = "obstacle test")

class Start(engine.Scene):
    def __init__(self, game):
        super().__init__(game, "test")

    def ready(self):
        self.player = engine.Sprite(self.app, image="catsmirk.png", pos=(self.app.width//2, self.app.height//3))
        self.blits.append(self.player)

        team = engine.Team(self.app, "collision", [self.player])

        for _ in range(OBSTACLE_COUNT):
            obs_size = (random.randint(self.app.width//30, self.app.width//3), random.randint(self.app.height//100, self.app.height//10))
            obs_pos = (random.randint(1, self.app.width-obs_size[0]-1), random.randint(1, self.app.height-obs_size[1]-1))
            obs = engine.Obstacle(self.app, color=(200, 0, 0), size=obs_size, pos=obs_pos)
            self.blits.append(obs)
            team.add_member(obs)

    def loop(self, key: int):
        self.app.screen.fill((0, 15, 64))
        keys = pygame.key.get_pressed()

        engine.KEYS_move(keys, self.player, 10)
        
        self.player.restrict()

        engine.AUTO_blit(self.blits)

test = ObstacleTest()
sc1 = Start(test)
test.first_scene = sc1

if __name__ == "__main__":
    test.run()