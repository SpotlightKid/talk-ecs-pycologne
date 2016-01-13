#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyglet
from pyglet.gl import *
from pyglet.window import key

import esper


FPS = 60
RESOLUTION = 720, 480
BGCOLOR = (0, 0, 0, 255)


##################################
#  Define some Components:
##################################
class Velocity:
    def __init__(self, vx=0.0, vy=0.0, accel=200.0):
        self.vx = vx
        self.vy = vy
        self.accel = accel


class Body:
    def __init__(self, x=0, y=0, width=1, height=1):
        self._x = x
        self._y = y
        self.width = width
        self.height = height
        self._dirty = True

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        if val != self._x:
            self._x = val
            self._dirty = True

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        if val != self._y:
            self._y = val
            self._dirty = True


class Renderable:
    def __init__(self, texture):
        self.texture = texture
        self.group = TextureBindGroup(texture)
        self.vertex_list = None


################################
#  Define some Processors:
################################
class MovementProcessor(esper.Processor):
    def __init__(self, minx, miny, maxx, maxy):
        super().__init__()
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, dt=0.0):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, body) in self.world.get_components(Velocity, Body):
            # Update the Renderable Component's position by it's Velocity:
            body.x += vel.vx * dt
            body.y += vel.vy * dt
            # An example of keeping the sprite inside screen boundaries. Basically,
            # adjust the position back inside screen boundaries if it tries to go outside:
            body.x = max(self.minx, body.x)
            body.y = max(self.miny, body.y)
            body.x = min(self.maxx - body.width, body.x)
            body.y = min(self.maxy - body.height, body.y)


class TextureRenderProcessor(esper.Processor):
    def __init__(self, batch):
        super().__init__()
        self.batch = batch

    def process(self, *args):
        # This will iterate over every Entity that has this Component, and
        # add the texture associated with the Renderable Component instance
        # and its vertice_list to the render batch. The batch will then be
        # drawn by the 'on_draw' event handler of teh main window:
        for entity, (rend, body) in self.world.get_components(Renderable, Body):
            self.draw_texture(rend, body)

    def draw_texture(self, rend, body):
        texture = rend.texture

        if rend.vertex_list is None:
            rend.vertex_list = self.batch.add(4, GL_QUADS, rend.group,
                                              'v2f/dynamic', 'c4B',
                                              ('t3f', texture.tex_coords))

        if body._dirty:
            x1 = body.x - texture.anchor_x
            y1 = body.y - texture.anchor_y
            x2 = x1 + body.width
            y2 = y1 + body.height
            rend.vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]
            rend.vertex_list.colors[:] = [255, 255, 255, 255] * 4
            body._dirty = False


############################################
#  Some pyglet helper classes and functions:
############################################
def texture_from_image(image_name):
    """Create a pyglet Texture from an image file"""
    return pyglet.resource.image(image_name).get_texture()


# Code below cobbled together from
# https://pyglet.readthedocs.org/en/latest/programming_guide/graphics.html#hierarchical-state
# and pyglet.sprite.SpriteGroup

class TextureEnableGroup(pyglet.graphics.Group):
    def set_state(self):
        glEnable(GL_TEXTURE_2D)

    def unset_state(self):
        glDisable(GL_TEXTURE_2D)


texture_enable_group = TextureEnableGroup()


class TextureBindGroup(pyglet.graphics.Group):
    def __init__(self, texture):
        super().__init__(parent=texture_enable_group)
        assert texture.target == GL_TEXTURE_2D
        self.texture = texture
        self.blend_src = GL_SRC_ALPHA
        self.blend_dest = GL_ONE_MINUS_SRC_ALPHA

    def set_state(self):
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)

    def unset_state(self):
        glPopAttrib()
        glDisable(self.texture.target)

    def __eq__(self, other):
        return (other.__class__ is self.__class__ and
                self.parent is other.parent and
                self.texture.target == other.texture.target and
                self.texture.id == other.texture.id and
                self.blend_src == other.blend_src and
                self.blend_dest == other.blend_dest)

    def __hash__(self):
        return hash((id(self.parent),
                     self.texture.id, self.texture.target,
                     self.blend_src, self.blend_dest))


################################
#  The main core of the program:
################################
def run(args=None):
    # Initialize the main window stuff
    config = pyglet.gl.Config(double_buffer=True)
    window = pyglet.window.Window(width=RESOLUTION[0], height=RESOLUTION[1],
                                  fullscreen=False, vsync=True, config=config)
    window.set_caption("Esper pyglet Example")
    pyglet.gl.glClearColor(*BGCOLOR)
    # pyglet graphics batch for efficient rendering
    renderbatch = pyglet.graphics.Batch()
    fps_display = pyglet.clock.ClockDisplay()

    # Initialize Esper world, and create a "player" Entity with a few Components.
    world = esper.World()
    player = world.create_entity()
    world.add_component(player, Body(x=100, y=100, width=64, height=64))
    world.add_component(player, Velocity(vx=0, vy=0))
    redsquare = Renderable(texture=texture_from_image("redsquare.png"))
    world.add_component(player, redsquare)

    # Another motionless Entity:
    enemy = world.create_entity()
    world.add_component(enemy, Body(x=400, y=250, width=64, height=64))
    bluesquare = Renderable(texture=texture_from_image("bluesquare.png"))
    world.add_component(enemy, bluesquare)

    # Create some Processor instances, and asign them to be processed.
    render_processor = TextureRenderProcessor(batch=renderbatch)
    movement_processor = MovementProcessor(minx=0, maxx=RESOLUTION[0], miny=0,
                                           maxy=RESOLUTION[1])
    world.add_processor(render_processor)
    world.add_processor(movement_processor)

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol in (key.UP, key.DOWN, key.LEFT, key.RIGHT):
            velocity = world.component_for_entity(player, Velocity)
            if symbol == key.UP:
                velocity.vy = velocity.accel
            elif symbol == key.DOWN:
                velocity.vy = -velocity.accel
            elif symbol == key.LEFT:
                velocity.vx = -velocity.accel
            elif symbol == key.RIGHT:
                velocity.vx = velocity.accel
        elif symbol == key.ESCAPE:
            pyglet.app.exit()
        elif symbol == key.F11:
            window.set_fullscreen()
            movement_processor.maxx, movement_processor.maxy = window.get_size()

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol in (key.UP, key.DOWN):
            world.component_for_entity(player, Velocity).vy = 0.0
        if symbol in (key.LEFT, key.RIGHT):
            world.component_for_entity(player, Velocity).vx = 0.0

    @window.event
    def on_draw():
        # Clear the window:
        window.clear()
        # Draw the batch of Renderables:
        renderbatch.draw()
        fps_display.draw()

    def update(dt):
        # A single call to world.process() will update all Processors:
        world.process(dt)

    pyglet.clock.schedule_interval(update, 1.0 / FPS)
    pyglet.app.run()


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]) or 0)
