
import random

from Model import *
import time


class AI:
    def simple_turn(self, world):
        print('turn number ' + str(world.get_current_turn()) + ':')
        r = random.Random()
        world.create_unit(r.choice(world.get_enemy_map().get_paths()), r.choice([UnitType.heavy_armor, UnitType.light_armor]))
        world.create_storm(r.choice(r.choice(world.get_enemy_map().get_cells())))
        world.create_tower(r.choice([TowerType.archer_tower, TowerType.cannon_tower]), 1,  r.choice(r.choice(world.get_my_map().get_cells())))
        if len(world.get_my_towers()) > 0:
            world.upgrade_tower(r.choice(world.get_my_towers()))
        world.plant_bean(r.choice(r.choice(world.get_enemy_map().get_cells())))

    def complex_turn(self, world):
        print('turn number ' + str(world.get_current_turn()) + ':')
        r = random.Random()
        world.create_unit(r.choice(world.get_enemy_map().get_paths()), r.choice([UnitType.heavy_armor, UnitType.light_armor]))
        world.create_storm(r.choice(r.choice(world.get_enemy_map().get_cells())))
        world.create_tower(r.choice([TowerType.archer_tower, TowerType.cannon_tower]), 1,  r.choice(r.choice(world.get_my_map().get_cells())))
        if len(world.get_my_towers()) > 0:
            world.upgrade_tower(r.choice(world.get_my_towers()))
        world.plant_bean(r.choice(r.choice(world.get_enemy_map().get_cells())))