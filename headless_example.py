#!/usr/bin/env python
# -*- coding: utf-8 -*-

import esper
import time


##################################
#  Define some Components:
##################################
class Velocity:
    def __init__(self, vx=0.0, vy=0.0):
        self.vx = vx
        self.vy = vy


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


################################
#  Define some Processors:
################################
class MovementProcessor(esper.Processor):
    def __init__(self):
        super().__init__()

    def process(self, dt=0.0):
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt
            print("Current Position: {}".format((int(pos.x), int(pos.y))))


##########################################################
# Instantiate everything, and create your main logic loop:
##########################################################
def main():
    # Create a World instance to hold everything:
    world = esper.World()

    # Instantiate a Processor (or more), and add them to the world:
    movement_processor = MovementProcessor()
    world.add_processor(movement_processor)

    # Create entities, and assign Component instances to them:
    player = world.create_entity()
    world.add_component(player, Velocity(vx=0.9, vy=1.2))
    world.add_component(player, Position(x=5, y=5))

    # A dummy main loop:
    try:
        while True:
            # Call world.process() to run all Processors.
            world.process(1.0)
            time.sleep(1)

    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    print("\nHeadless Example. Press Ctrl+C to quit!\n")
    main()
