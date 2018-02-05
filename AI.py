
import random

from Model import *
import time


class AI:
    def simple_turn(self, world):
        print('turn number ' + str(world.get_current_turn()) + ':')
        r = random.Random()
        if r.choice([0, 1]) == 0:
            world.create_light_unit(r.randint(0, len(world.get_attack_map_paths()) - 1))
        else:
            world.create_heavy_unit(r.randint(0, len(world.get_attack_map_paths()) - 1))

        storm_cell = r.choice(world.get_defence_map().get_cells_list())
        world.create_storm(storm_cell.get_location().get_x(), storm_cell.get_location().get_y())

        bean_cell = r.choice(world.get_defence_map().get_cells_list())
        world.create_storm(bean_cell.get_location().get_x(), bean_cell.get_location().get_y())

        tower_cell = r.choice(world.get_defence_map().get_cells_list())
        if r.choice([0, 1]) == 0:
            world.create_archer_tower(r.randint(1, 3),
                                      tower_cell.get_location().get_x(), tower_cell.get_location().get_y())
        else:
            world.create_cannon_tower(r.randint(1, 3),
                                      tower_cell.get_location().get_x(), tower_cell.get_location().get_y())

        if len(world.get_my_towers()) > 0:
            world.upgrade_tower(r.choice(world.get_my_towers()))

    def complex_turn(self, world):
        print('turn number ' + str(world.get_current_turn()) + ':')
        r = random.Random()
        if r.choice([0, 1]) == 0:
            world.create_light_unit(r.randint(0, len(world.get_attack_map_paths()) - 1))
        else:
            world.create_heavy_unit(r.randint(0, len(world.get_attack_map_paths()) - 1))

        storm_cell = r.choice(world.get_defence_map().get_cells_list())
        world.create_storm(storm_cell.get_location().get_x(), storm_cell.get_location().get_y())

        bean_cell = r.choice(world.get_defence_map().get_cells_list())
        world.create_storm(bean_cell.get_location().get_x(), bean_cell.get_location().get_y())

        tower_cell = r.choice(world.get_defence_map().get_cells_list())
        if r.choice([0, 1]) == 0:
            world.create_archer_tower(r.randint(1, 3),
                                      tower_cell.get_location().get_x(), tower_cell.get_location().get_y())
        else:
            world.create_cannon_tower(r.randint(1, 3),
                                      tower_cell.get_location().get_x(), tower_cell.get_location().get_y())

        if len(world.get_my_towers()) > 0:
            world.upgrade_tower(r.choice(world.get_my_towers()))