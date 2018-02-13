from enum import Enum


class Owner(Enum):
    ME = 0
    ENEMY = 1


class UnitType(Enum):
    light_armor = 'l'
    heavy_armor = 'h'


class TowerType(Enum):
    cannon_tower = 'c'
    archer_tower = 'a'


class World:
    INITIAL_HEALTH = None
    MAX_TURNS_IN_GAME = None
    INITIAL_MONEY = None
    INITIAL_BEANS_COUNT = None
    INITIAL_STORMS_COUNT = None
    STORM_RANGE = None
    _DEBUGGING_MODE = False
    _LOG_FILE_POINTER = None

    def __init__(self, queue):
        self.queue = queue
        self.map = [None, None]
        self.players = [None, None]
        self.current_turn = 0

        self.dead_units_in_this_turn = []
        self.passed_units_in_this_turn = []
        self.destroyed_towers_in_this_turn = []
        self.beans_in_this_turn = []
        self.storms_in_this_turn = []

        self._units = []
        self._towers = []

    def _handle_init_message(self, msg):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write(str(msg))
            World._LOG_FILE_POINTER.write('\n')
        msg = msg['args'][0]
        self.map = [Map(msg['map']), Map(msg['map'])]
        for path in msg['paths']:
            path_cells0 = []
            path_cells1 = []
            for loc in path['cells']:
                path_cells0.append(self.map[0].get_cell_loc(loc))
                path_cells1.append(self.map[1].get_cell_loc(loc))
            self.map[0].paths.append(Path(path_cells0))
            self.map[1].paths.append(Path(path_cells1))
        params = msg['params']
        self.players = [Player(int(params[1]), 0, int(params[0]), int(params[3]), int(params[4])),
                        Player(int(params[1]), 0, int(params[0]), int(params[3]), int(params[4]))]

        World.INITIAL_HEALTH = int(params[0])
        World.INITIAL_MONEY = int(params[1])
        World.MAX_TURNS_IN_GAME = int(params[2])
        World.INITIAL_BEANS_COUNT = int(params[3])
        World.INITIAL_STORMS_COUNT = int(params[4])
        World.STORM_RANGE = int(params[5])

        LightUnit.INITIAL_PRICE = int(params[6][0][0])
        LightUnit.PRICE_INCREASE = int(params[6][0][1])
        LightUnit.INITIAL_HEALTH = int(params[6][0][2])
        LightUnit.HEALTH_COEFF = float(params[6][0][3])
        LightUnit.INITIAL_BOUNTY = int(params[6][0][4])
        LightUnit.BOUNTY_INCREASE = int(params[6][0][5])
        LightUnit.MOVE_SPEED = int(params[6][0][6])
        LightUnit.DAMAGE = int(params[6][0][7])
        LightUnit.VISION_RANGE = int(params[6][0][8])
        LightUnit.LEVEL_UP_THRESHOLD = int(params[6][0][9])
        LightUnit.ADDED_INCOME = int(params[6][0][10])

        HeavyUnit.INITIAL_PRICE = int(params[6][1][0])
        HeavyUnit.PRICE_INCREASE = int(params[6][1][1])
        HeavyUnit.INITIAL_HEALTH = int(params[6][1][2])
        HeavyUnit.HEALTH_COEFF = float(params[6][1][3])
        HeavyUnit.INITIAL_BOUNTY = int(params[6][1][4])
        HeavyUnit.BOUNTY_INCREASE = int(params[6][1][5])
        HeavyUnit.MOVE_SPEED = int(params[6][1][6])
        HeavyUnit.DAMAGE = int(params[6][1][7])
        HeavyUnit.VISION_RANGE = int(params[6][1][8])
        HeavyUnit.LEVEL_UP_THRESHOLD = int(params[6][1][9])
        HeavyUnit.ADDED_INCOME = int(params[6][1][10])

        ArcherTower.INITIAL_PRICE = int(params[7][0][0])
        ArcherTower.INITIAL_LEVEL_UP_PRICE = int(params[7][0][1])
        ArcherTower.PRICE_COEFF = float(params[7][0][2])
        ArcherTower.INITIAL_DAMAGE = int(params[7][0][3])
        ArcherTower.DAMAGE_COEFF = float(params[7][0][4])
        ArcherTower.ATTACK_SPEED = int(params[7][0][5])
        ArcherTower.ATTACK_RANGE = int(params[7][0][6])
        ArcherTower.ATTACK_RANGE_SUM = float(params[7][0][7])

        CannonTower.INITIAL_PRICE = int(params[7][1][0])
        CannonTower.INITIAL_LEVEL_UP_PRICE = int(params[7][1][1])
        CannonTower.PRICE_COEFF = float(params[7][1][2])
        CannonTower.INITIAL_DAMAGE = int(params[7][1][3])
        CannonTower.DAMAGE_COEFF = float(params[7][1][4])
        CannonTower.ATTACK_SPEED = int(params[7][1][5])
        CannonTower.ATTACK_RANGE = int(params[7][1][6])
        CannonTower.ATTACK_RANGE_SUM = float(params[7][1][7])

    def _handle_turn_message(self, msg):
        self.current_turn += 1
        msg = msg['args'][0]
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write(str(msg))
            World._LOG_FILE_POINTER.write('\n')
        self.dead_units_in_this_turn = []
        self.passed_units_in_this_turn = []
        self.destroyed_towers_in_this_turn = []
        self.beans_in_this_turn = []
        self.storms_in_this_turn = []

        for bean in msg['events']['beans']:
            if bean[0] == 0:   #FIXME not sure about index
                self.beans_in_this_turn.append(BeanEvent(bean[1], Owner.ENEMY))
                self.map[Owner.ME.value].get_cells_grid()[int(bean[1]['x'])][int(bean[1]['y'])] = \
                    BlockCell(int(bean[1]['x']), int(bean[1]['y']))
            if bean[0] == 1:
                self.beans_in_this_turn.append(BeanEvent(bean[1], Owner.ME))
                self.map[Owner.ENEMY.value].get_cells_grid()[int(bean[1]['x'])][int(bean[1]['y'])] = \
                    BlockCell(int(bean[1]['x']), int(bean[1]['y']))

        for storm in msg['events']['storms']:
            if storm[0] == 0:
                self.storms_in_this_turn.append(StormEvent(storm[1], Owner.ME))
            if storm[0] == 1:
                self.storms_in_this_turn.append(StormEvent(storm[1], Owner.ENEMY))

        for dead in msg['events']['deadunits']:
            self.dead_units_in_this_turn.append(self._units[dead[1]])

        for passed in msg['events']['endofpath']:
            self.passed_units_in_this_turn.append(self._units[passed[1]])

        for destroyed in msg['events']['destroyedtowers']:
            self.destroyed_towers_in_this_turn.append(self._towers[destroyed[1]])

        self.map[0].clear()
        self.map[1].clear()
        self._units = {}
        self._towers = {}
        my_units = msg['myunits']
        for unit in my_units:
            new_unit = None
            if unit[1] == UnitType.light_armor.value:
                new_unit = LightUnit(unit, Owner.ME,
                                     self.map[Owner.ENEMY.value].paths[int(unit[6])])
            if unit[1] == UnitType.heavy_armor.value:
                new_unit = HeavyUnit(unit, Owner.ME,
                                     self.map[Owner.ENEMY.value].paths[int(unit[6])])
            self.map[Owner.ENEMY.value].get_cell_loc(unit[4]).add_unit(new_unit)
            self.map[Owner.ENEMY.value].get_units().append(new_unit)
            self._units[unit[0]] = new_unit

        enemy_units = msg['enemyunits']
        for unit in enemy_units:
            new_unit = None
            if unit[1] == UnitType.light_armor.value:
                new_unit = LightUnit(unit, Owner.ENEMY, None)
            if unit[1] == UnitType.heavy_armor.value:
                new_unit = HeavyUnit(unit, Owner.ENEMY, None)
            self.map[Owner.ME.value].get_cell_loc(unit[3]).add_unit(new_unit)
            self.map[Owner.ME.value].get_units().append(new_unit)
            self._units[unit[0]] = new_unit

        my_towers = msg['mytowers']
        for tower in my_towers:
            new_tower = None
            if tower[1] == TowerType.archer_tower.value:
                new_tower = ArcherTower(
                    tower, Owner.ME)
            elif tower[1] == TowerType.cannon_tower.value:
                new_tower = CannonTower(
                    tower, Owner.ME)
            self.map[Owner.ME.value].get_cell_loc(tower[3]).add_tower(new_tower)
            self.map[Owner.ME.value].get_towers().append(new_tower)
            self._towers[tower[0]] = new_tower

        enemy_towers = msg['enemytowers']
        for tower in enemy_towers:
            new_tower = None
            if tower[1] == TowerType.archer_tower.value:
                new_tower = ArcherTower(
                    tower, Owner.ENEMY)
            elif tower[1] == TowerType.cannon_tower.value:
                new_tower = CannonTower(
                    tower, Owner.ENEMY)
            self.map[Owner.ENEMY.value].get_cell_loc(tower[3]).add_tower(new_tower)
            self.map[Owner.ENEMY.value].get_towers().append(new_tower)
            self._towers[tower[0]] = new_tower

        my_player = msg['players'][0]
        self.players[Owner.ME.value] = Player(int(my_player[1]), int(my_player[2]), int(my_player[0]),
                                              int(my_player[3]),
                                              int(my_player[4]))

        enemy_player = msg['players'][1]
        self.players[Owner.ENEMY.value] = Player(0, 0, int(enemy_player[0]), int(enemy_player[1]), int(enemy_player[2]))

        if World._DEBUGGING_MODE:
            self._print_log()

    def get_current_turn(self):
        return self.current_turn

    def get_beans_in_this_turn(self):
        return self.beans_in_this_turn

    def get_storms_in_this_turn(self):
        return self.storms_in_this_turn

    def get_dead_units_in_this_turn(self):
        return self.dead_units_in_this_turn

    def get_destroyed_towers_in_this_turn(self):
        return self.destroyed_towers_in_this_turn

    def get_passed_units_in_this_turn(self):
        return self.passed_units_in_this_turn

    def get_my_units(self):
        return self.map[Owner.ENEMY.value].get_units()

    def get_enemy_units(self):
        return self.map[Owner.ME.value].get_units()

    def get_my_towers(self):
        return self.map[Owner.ME.value].get_towers()

    def get_visible_enemy_towers(self):
        return self.map[Owner.ENEMY.value].get_towers()

    def get_maps(self):
        return self.map

    def get_my_map(self):
        return self.map[Owner.ME.value]

    def get_enemy_map(self):
        return self.map[Owner.ENEMY.value]

    def get_defence_map(self):
        return self.get_my_map()

    def get_attack_map(self):
        return self.get_enemy_map()

    def get_enemy_information(self):
        return self.players[Owner.ENEMY.value]

    def get_my_information(self):
        return self.players[Owner.ME.value]

    def create_light_unit(self, path_index):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write('cu, ' + str([UnitType.light_armor.value, path_index]))
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(Event('cu', [UnitType.light_armor.value, path_index]))

    def create_heavy_unit(self, path_index):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write('cu' + str([UnitType.heavy_armor.value, path_index]))
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(Event('cu', [UnitType.heavy_armor.value, path_index]))

    def create_cannon_tower(self, level, x, y):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write('ct, ' + str([TowerType.cannon_tower.value, level, x, y]))
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(Event('ct', [TowerType.cannon_tower.value, level, x, y]))

    def create_archer_tower(self, level, x, y):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write('ct, ' + str([TowerType.archer_tower.value, level, x, y]))
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(Event('ct', [TowerType.archer_tower.value, level, x, y]))

    def upgrade_tower(self, tower):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write('ut, ' + str([tower.get_id()]))
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(Event('ut', [tower.get_id()]))

    def create_storm(self, x, y):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write('s, ' + str([x, y]))
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(Event('s', [x, y]))

    def plant_bean(self, x, y):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write('s, ' + str([x, y]))
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(Event('b', [x, y]))

    def _get_end_message(self):
        return Event('end', [self.get_current_turn()])

    def end_turn(self, end_message):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write(end_message.type)
            World._LOG_FILE_POINTER.write('\n')
        self.queue.put(end_message)

    def is_tower_constructable(self, x, y):
        cell = self.get_defence_map().get_cell(x, y)
        if type(cell) in [RoadCell, BlockCell]:
            return False
        for tower in self.get_my_towers():
            if abs(tower.get_location().get_x() - cell.get_location().get_x()) == 0 \
                    and abs(tower.get_location().get_y() - cell.get_location().get_y()) == 1:
                return False
            if abs(tower.get_location().get_x() - cell.get_location().get_x()) == 1 \
                    and abs(tower.get_location().get_y() - cell.get_location().get_y()) == 0:
                return False
            if abs(tower.get_location().get_x() - cell.get_location().get_x()) == 0 \
                    and abs(tower.get_location().get_y() - cell.get_location().get_y()) == 0:
                return False
        return True

    def get_attack_map_paths(self):
        return self.get_enemy_map().get_paths()

    def get_defence_map_paths(self):
        return self.get_my_map().get_paths()

    def _print_log(self):
        if World._LOG_FILE_POINTER is None:
            World._LOG_FILE_POINTER = open("client.log", 'w')
        World._LOG_FILE_POINTER.write("turn number " + str(self.get_current_turn()) + ' : ')
        World._LOG_FILE_POINTER.write('\n')
        l = []
        for m in self.get_my_units():
            l += [str(m.get_id())]
        World._LOG_FILE_POINTER.write(str(l))
        World._LOG_FILE_POINTER.write('\n')
        l = []
        for m in self.get_enemy_units():
            l += [str(m.get_id())]
        World._LOG_FILE_POINTER.write(str(l))
        World._LOG_FILE_POINTER.write('\n')
        l = []
        for m in self.get_my_towers():
            l += [str(m.get_id())]
        World._LOG_FILE_POINTER.write(str(l))
        World._LOG_FILE_POINTER.write('\n')
        l = []
        for m in self.get_visible_enemy_towers():
            l += [str(m.get_id())]
        World._LOG_FILE_POINTER.write(str(l))
        World._LOG_FILE_POINTER.write('\n')

        World._LOG_FILE_POINTER.write(str(self.get_visible_enemy_towers()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_my_towers()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_my_units()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_enemy_units()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_passed_units_in_this_turn()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_destroyed_towers_in_this_turn()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_dead_units_in_this_turn()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_beans_in_this_turn()))
        World._LOG_FILE_POINTER.write('\n')
        World._LOG_FILE_POINTER.write(str(self.get_storms_in_this_turn()))
        World._LOG_FILE_POINTER.write('\n')


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_loc(self):
        return {'x': self.x, 'y': self.y}

    def __eq__(self, other):
        if self.x == other.get_x() and self.y == other.get_y():
            return True
        return False

    def __str__(self):
        return str(self.get_loc())


class Player:
    def __init__(self, money, income, strength, beans_left, storms_left):
        self.money = money
        self.strength = strength
        self.income = income
        self.beans_left = beans_left
        self.storms_left = storms_left

    def get_money(self):
        return self.money

    def get_strength(self):
        return self.strength

    def get_income(self):
        return self.income

    def get_beans_left(self):
        return self.beans_left

    def get_storms_left(self):
        return self.storms_left


class Map:
    def __init__(self, msg):
        self.width = int(msg['size'][0])
        self.height = int(msg['size'][1])
        self.cells = []
        self.paths = []
        self.units = []
        self.towers = []
        for i in range(self.width):
            self.cells.append([])
            for j in range(self.height):
                self.cells[i].append(None)

        for i in range(self.width):
            for j in range(self.height):
                if msg['cells'][j][i] == 'g':
                    self.cells[i][j] = GrassCell(i, j)
                elif msg['cells'][j][i] == 'r':
                    self.cells[i][j] = RoadCell(i, j)
                else:
                    self.cells[i][j] = BlockCell(i, j)

    def get_paths(self):
        return self.paths

    def get_units(self):
        return self.units

    def get_towers(self):
        return self.towers

    def get_cells_grid(self):
        return self.cells

    def get_cells_list(self):
        cells_list = []
        for row in range(len(self.cells)):
            cells_list += self.cells[row]
        return cells_list

    def get_cell_loc(self, loc):
        return self.get_cell(int(loc['x']), int(loc['y']))

    def get_cell(self, x, y):
        return self.cells[x][y]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def clear(self):
        self.units = []
        self.towers = []
        for cell in self.get_cells_list():
            cell.clear()


class Cell:
    def __init__(self, x, y):
        self.location = Point(x, y)

    def get_location(self):
        return self.location

    def clear(self):
        pass


class RoadCell(Cell):
    def __init__(self, x, y):
        Cell.__init__(self, x, y)
        self.units = []

    def get_units(self):
        return self.units

    def add_unit(self, unit):
        self.units.append(unit)

    def clear(self):
        self.units = []


class GrassCell(Cell):
    def __init__(self, x, y):
        Cell.__init__(self, x, y)
        self.towers = []

    def get_towers(self):
        return self.towers

    def add_tower(self, tower):
        self.towers.append(tower)

    def clear(self):
        self.towers = []


class BlockCell(Cell):
    def __init__(self, x, y):
        Cell.__init__(self, x, y)


class Path:
    def __init__(self, cells):
        self.road = []
        for cell in cells:
            self.road.append(cell)

    def get_road(self):
        return self.road


class Entity:
    def __init__(self, location, owner, id):
        self.id = id
        self.location = Point(int(location['x']), int(location['y']))
        self.owner = owner

    def get_owner(self):
        return self.owner

    def get_location(self):
        return self.location

    def get_id(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        st = 'Entity:\n\n'
        st += str(self.id)
        st += '\n'
        st += str(self.location)
        st += '\n'
        st += str(self.owner)
        st += '\n\n\n'
        return st


class Unit(Entity):
    def __init__(self, params, owner, path):
        if len(params) > 4:
            Entity.__init__(self, params[4], owner, int(params[0]))
        else:
            Entity.__init__(self, params[3], owner, int(params[0]))
        self.remtick = None
        self.health = None
        self.level = int(params[2])
        self.path = path
        if len(params) > 4:
            self.remtick = int(params[5])
            self.health = int(params[3])

    def get_health(self):
        return self.health

    def get_move_speed(self):
        pass

    def get_damage(self):
        pass

    def get_level(self):
        return self.level

    def get_price(self, level=None):
        pass

    def get_vision_range(self):
        pass

    def get_bounty(self, level=None):
        pass

    def get_path(self):
        return self.path

    def get_added_income(self):
        pass


class HeavyUnit(Unit):
    INITIAL_PRICE = None
    PRICE_INCREASE = None

    INITIAL_HEALTH = None
    HEALTH_COEFF = None

    INITIAL_BOUNTY = None
    BOUNTY_INCREASE = None

    MOVE_SPEED = None
    DAMAGE = None
    VISION_RANGE = None
    LEVEL_UP_THRESHOLD = None

    ADDED_INCOME = None

    def __init__(self, params, owner, path):
        Unit.__init__(self, params, owner, path)

    def get_move_speed(self):
        return HeavyUnit.MOVE_SPEED

    def get_damage(self):
        return HeavyUnit.DAMAGE

    def get_price(self, level=None):
        if level is None:
            level = self.level
        return HeavyUnit.PRICE_INCREASE * (level - 1) + HeavyUnit.INITIAL_PRICE

    def get_bounty(self, level=None):
        if level is None:
            level = self.level
        return HeavyUnit.INITIAL_BOUNTY + HeavyUnit.BOUNTY_INCREASE * (level - 1)

    def get_added_income(self):
        return HeavyUnit.ADDED_INCOME

    def get_vision_range(self):
        return HeavyUnit.VISION_RANGE


class LightUnit(Unit):
    INITIAL_PRICE = None
    PRICE_INCREASE = None

    INITIAL_HEALTH = None
    HEALTH_COEFF = None

    INITIAL_BOUNTY = None
    BOUNTY_INCREASE = None

    MOVE_SPEED = None
    DAMAGE = None
    VISION_RANGE = None
    LEVEL_UP_THRESHOLD = None

    ADDED_INCOME = None

    def __init__(self, params, owner, path):
        Unit.__init__(self, params, owner, path)

    def get_move_speed(self):
        return LightUnit.MOVE_SPEED

    def get_damage(self):
        return LightUnit.DAMAGE

    def get_price(self, level=None):
        if level is None:
            level = self.level
        return LightUnit.PRICE_INCREASE * (level - 1) + LightUnit.INITIAL_PRICE

    def get_bounty(self, level=None):
        if level is None:
            level = self.level
        return LightUnit.INITIAL_BOUNTY + LightUnit.BOUNTY_INCREASE * (level - 1)

    def get_added_income(self):
        return LightUnit.ADDED_INCOME

    def get_vision_range(self):
        return LightUnit.VISION_RANGE


class Tower(Entity):
    def __init__(self, params, owner):
        Entity.__init__(self, params[3], owner, int(params[0]))
        self.level = int(params[2])

    def get_damage(self, lvl=None):
        pass

    def get_price(self, lvl=None):
        pass

    def get_attack_range(self, lvl=None):
        pass

    def get_attack_speed(self):
        pass

    def get_level(self):
        return self.level


class CannonTower(Tower):
    INITIAL_PRICE = None
    INITIAL_LEVEL_UP_PRICE = None
    PRICE_COEFF = None

    INITIAL_DAMAGE = None
    DAMAGE_COEFF = None

    ATTACK_SPEED = None
    ATTACK_RANGE = None
    ATTACK_RANGE_SUM = None

    def __init__(self, params, owner):
        Tower.__init__(self, params, owner)

    def get_damage(self, lvl=None):
        if lvl is None:
            lvl = self.level
        return int(CannonTower.INITIAL_DAMAGE * CannonTower.DAMAGE_COEFF ** (lvl - 1))

    def get_price(self, lvl=None):
        if lvl is None:
            lvl = self.level
        if lvl == 1:
            return CannonTower.INITIAL_PRICE
        return int(CannonTower.INITIAL_PRICE +
                   CannonTower.INITIAL_LEVEL_UP_PRICE * CannonTower.PRICE_COEFF ** (lvl - 2))

    def get_attack_range(self, lvl=None):
        return CannonTower.ATTACK_RANGE

    def get_attack_speed(self):
        return CannonTower.ATTACK_SPEED


class ArcherTower(Tower):
    INITIAL_PRICE = None
    INITIAL_LEVEL_UP_PRICE = None
    PRICE_COEFF = None

    INITIAL_DAMAGE = None
    DAMAGE_COEFF = None

    ATTACK_SPEED = None
    ATTACK_RANGE = None
    ATTACK_RANGE_SUM = None

    def __init__(self, params, owner):
        Tower.__init__(self, params, owner)

    def get_damage(self, lvl=None):
        if lvl is None:
            lvl = self.level
        return int(ArcherTower.INITIAL_DAMAGE * ArcherTower.DAMAGE_COEFF ** (lvl - 1))

    def get_price(self, lvl=None):
        if lvl is None:
            lvl = self.level
        if lvl == 1:
            return ArcherTower.INITIAL_PRICE
        return int(ArcherTower.INITIAL_PRICE +
                   ArcherTower.INITIAL_LEVEL_UP_PRICE * ArcherTower.PRICE_COEFF ** (lvl - 2))

    def get_attack_range(self, lvl=None):
        if lvl is None:
            lvl = self.level
        return int(ArcherTower.ATTACK_RANGE)

    def get_attack_speed(self):
        return ArcherTower.ATTACK_SPEED


class GameEvent:
    def __init__(self, location, owner):
        self.location = Point(int(location['x']), int(location['y']))
        self.owner = owner

    def get_owner(self):
        return self.owner

    def get_location(self):
        return self.location

    def __str__(self):
        st = 'ServerEVENT:\n'
        st += str(self.location)
        st += '\n'
        st += str(self.owner)
        st += '\n\n\n'
        return st


class StormEvent(GameEvent):
    def __init__(self, location, owner):
        GameEvent.__init__(self, location, owner)


class BeanEvent(GameEvent):
    def __init__(self, location, owner):
        GameEvent.__init__(self, location, owner)


class Event:
    EVENT = "event"

    def __init__(self, type, args):
        self.type = type
        self.args = args

    def add_arg(self, arg):
        self.args.append(arg)


class ServerConstants:
    KEY_ARGS = "args"
    KEY_NAME = "name"
    KEY_TYPE = "type"

    CONFIG_KEY_IP = "ip"
    CONFIG_KEY_PORT = "port"
    CONFIG_KEY_TOKEN = "token"

    MESSAGE_TYPE_EVENT = "event"
    MESSAGE_TYPE_INIT = "init"
    MESSAGE_TYPE_SHUTDOWN = "shutdown"
    MESSAGE_TYPE_TURN = "turn"

    CHANGE_TYPE_ADD = "a"
    CHANGE_TYPE_DEL = "d"
    CHANGE_TYPE_MOV = "m"
    CHANGE_TYPE_ALT = "c"
