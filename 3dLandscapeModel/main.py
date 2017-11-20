from OpenGL.GL import *

import cameraandlighting
import configjson as config
import model
import pygame
import hud
from input import InputHandler
from scripting_aggregator import ScriptHolder
from user import User

pygame.init()

pygame.display.set_mode(config.window_info.window_size,
                        pygame.OPENGL | pygame.DOUBLEBUF | (
                            pygame.FULLSCREEN if config.window_info.full_screen else 0) | pygame.HWSURFACE)

# I honestly have no clue why I did this. Oh well
pygame.display.set_caption('Model Magic OOOooOOooOOoo Spooky!', "I ain't typing the same thing here! HAHA!")

camera = cameraandlighting.CameraAndLighting()
camera.setup()

model_data = model.StaticModelData()
model_data.setup()  # Everybody do the setup shake!

# I seriously thing something is wrong with me, putting in all these random comments and strings and stuff.
# Oh well

clock = pygame.time.Clock()

pygame.mouse.set_pos(config.window_info.window_size[0] / 2, config.window_info.window_size[1] / 2)

user = User(model.geom_data["spawn"], camera, model_data)

input_handler = InputHandler(user)

hud = hud.HUD(model_data)

scripter = ScriptHolder(model_data, user)
scripter.load("script.txt")

while True:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    user.update_camera()
    camera.apply()
    model_data.draw()
    model_data.setup_price_labels(user)
    hud.apply(user)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise
        input_handler.dispatch(event)
    input_handler.game_loop()
    if input_handler.dx_move != 0 or input_handler.dz_move != 0:
        scripter.player_moves()
    user.physics_tick(input_handler.dx_move, input_handler.dz_move)
    pygame.display.flip()
    clock.tick(60)
