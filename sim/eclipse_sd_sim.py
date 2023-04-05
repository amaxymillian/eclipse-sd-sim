import random, os
import json, jsonpickle
import pandas as pd
from enum import IntEnum
from copy import deepcopy

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

class Ship_type(IntEnum):
    TERRAN_INTERCEPTOR = 1
    TERRAN_CRUISER = 2
    TERRAN_DREADNOUGHT = 3
    TERRAN_STARBASE = 4
    ERIDANI_INTERCEPTOR = 5
    ERIDANI_CRUISER = 6
    ERIDANI_DREADNOUGHT = 7
    ERIDANI_STARBASE = 8
    ORION_INTERCEPTOR = 9
    ORION_CRUISER = 10
    ORION_DREADNOUGHT = 11
    ORION_STARBASE = 12
    PLANTA_INTERCEPTOR = 13
    PLANTA_CRUISER = 14
    PLANTA_DREADNOUGHT = 15
    PLANTA_STARBASE = 16
    
class Ship_part_names(IntEnum):
    ABSORPTION_SHIELD = 1
    ANTIMATTER_CANNON = 2
    CONIFOLD_FIELD = 3
    ELECTRON_COMPUTER = 4
    FLUX_MISSILE = 5
    FUSION_DRIVE = 6
    FUSION_SOURCE = 7
    GAUSS_SHIELD = 8
    GLUON_COMPUTER = 9
    HULL = 10
    IMPROVED_HULL = 11
    ION_CANNON = 12
    NUCLEAR_DRIVE = 13
    NUCLEAR_SOURCE = 14
    PHASE_SHIELD = 15
    PLASMA_CANNON = 16
    PLASMA_MISSILE = 17
    POSITRON_COMPUTER = 18
    RIFT_CANNON = 19
    SENTIENT_HULL = 20
    SOLITON_CANNON = 21
    TACHYON_DRIVE = 22
    TACHYON_SOURCE = 23
    TRANSITION_DRIVE = 24
    ZEROPOINT_SOURCE = 25
    
    
    
# Need a data structure to represent ship configurations
ship_types = {
    Ship_type.TERRAN_INTERCEPTOR: 
    {"slots":4, "base_initiative":2, 
    "installed_parts": [Ship_part_names.ION_CANNON, Ship_part_names.NUCLEAR_DRIVE, Ship_part_names.NUCLEAR_SOURCE, None]},
    
    Ship_type.TERRAN_CRUISER: 
    {"slots":6, "base_initiative":1, 
    "installed_parts": [Ship_part_names.ION_CANNON, Ship_part_names.NUCLEAR_DRIVE, Ship_part_names.NUCLEAR_SOURCE,
    Ship_part_names.ELECTRON_COMPUTER, Ship_part_names.HULL, None]},
    
    Ship_type.TERRAN_DREADNOUGHT: 
    {"slots":8, "base_initiative":0, 
    "installed_parts": [Ship_part_names.ION_CANNON, Ship_part_names.ION_CANNON, Ship_part_names.NUCLEAR_DRIVE, Ship_part_names.NUCLEAR_SOURCE,
    Ship_part_names.ELECTRON_COMPUTER, Ship_part_names.HULL, Ship_part_names.HULL, None]},

    Ship_type.TERRAN_STARBASE: 
    {"slots":5, "base_initiative":4, 
    "installed_parts": [Ship_part_names.ION_CANNON, Ship_part_names.ELECTRON_COMPUTER, Ship_part_names.HULL, Ship_part_names.HULL, None]}

    }

# Need a data structure to represent the various tech tiles 
ship_parts = {
    Ship_part_names.ABSORPTION_SHIELD: {"type": "shield", "shielding": -1, "power": 4},
    Ship_part_names.ANTIMATTER_CANNON: {"type": "cannon", "damage": 4, "power": -4},
    Ship_part_names.CONIFOLD_FIELD: {"type":"hull", "armor":3, "power": -2},
    Ship_part_names.ELECTRON_COMPUTER: {"type": "computer", "targeting": 1, "power": 0},
    Ship_part_names.FLUX_MISSILE: {"type": "missile", "damage": 1, "times_fired": 2, "power": 0}, 
    Ship_part_names.FUSION_DRIVE: {"type": "drive", "initiative": 2, "power": -2},
    Ship_part_names.FUSION_SOURCE: {"type": "source", "power": 6},
    Ship_part_names.GAUSS_SHIELD: {"type": "shield", "shielding": -1, "power": 0},
    Ship_part_names.GLUON_COMPUTER: {"type": "computer", "targeting": 3, "power":-2},
    Ship_part_names.HULL: {"type":"hull", "armor":1, "power":0},
    Ship_part_names.IMPROVED_HULL: {"type":"hull", "armor":2, "power":0},
    Ship_part_names.ION_CANNON: {"type": "cannon", "damage": 1, "power": -1},
    Ship_part_names.NUCLEAR_DRIVE: {"type": "drive", "initiative": 1, "power": -1},
    Ship_part_names.NUCLEAR_SOURCE: {"type": "source", "power": 3},
    Ship_part_names.PHASE_SHIELD: {"type": "shield", "shielding": -2, "power": -1},
    Ship_part_names.PLASMA_CANNON: {"type": "cannon", "damage": 2, "power": -2},
    Ship_part_names.PLASMA_MISSILE: {"type": "missile", "damage": 2, "times_fired": 2, "power": -1}, 
    Ship_part_names.POSITRON_COMPUTER: {"type": "computer", "targeting": 2, "power": -1},
    Ship_part_names.RIFT_CANNON: {"type": "cannon", "damage": "RIFT_DAMAGE", "power": -2},
    Ship_part_names.SENTIENT_HULL: {"type":"hull", "armor":1, "targeting": 1, "power":0},
    Ship_part_names.SOLITON_CANNON: {"type": "cannon", "damage": 3, "power": -3},
    Ship_part_names.TACHYON_DRIVE: {"type": "drive", "initiative": 3, "power": -3},
    Ship_part_names.TACHYON_SOURCE: {"type": "source", "power": 9},
    Ship_part_names.TRANSITION_DRIVE: {"type": "drive", "initiative": 0, "power": 0},
    Ship_part_names.ZEROPOINT_SOURCE: {"type": "source", "power": 12}
}


# TODO: Create a 'Ship_Class' class to store the ship_parts so that instances of 'Ship' are really about particular
# ship damage tracking?

class Ship:

    def __init__(self, Ship_type, player_num, is_attacker = True, ship_parts: list[str] = None):
        self.ship_type = Ship_type
        self.player_num = player_num
        self.is_attacker = is_attacker
        if ship_parts:
            self.ship_parts = ship_parts.copy()
        else: 
            #Install default parts
            self.ship_parts = ship_types[Ship_type]["installed_parts"].copy()
        
        self.update_init()
        self.recalc_hp()
        self.update_targeting()
        self.update_shielding()

        
    def add_part(self, part_name, part_position):
        #TODO - Check if we have enough power to mount this part, if not, throw an error
        
        
        #TODO - Check if adding this part removes our last drive and we're not a starbase - if so, throw an error
        
        self.ship_parts[part_position] = part_name
        self.update_init()
        self.recalc_hp()
        
    def remove_part(self, part_position):
        #Removing a part resets the part to its default configuration - may not need this
        self.ship_parts[part_position] = ship_types[self.ship_type]["installed_parts"][part_position]
        self.update_init()

    def get_hp(self) -> int:
        return self._hp

    def set_hp(self, new_hp):
        self._hp = new_hp
        
    def get_avail_power(self) -> int:
        power = 0
        for part in self.ship_parts:
            if ship_parts[part]["type"] == 'source':
                power += ship_parts[part]['power']
            else:
                power -= ship_parts[part]['cost']
        return power
          
        
    def fire_missiles(self) -> list[int]:
        #TODO firing missiles should really just be their own battle sim that happens only once as 'Round 0'...?
        pass
    
    
    def fire_weapons(self) -> list[tuple[int, int]]:
        '''
        Returns a list of tuples representing the potential damage for each weapon and its roll.  Actual hits require knowing the shielding of the enemy.
        '''
        dmg_stack = []
        
        for part in self.ship_parts:
            if part is None:
                continue
            elif 'damage' in ship_parts[part]:
                atk_roll = random.randint(1,6)
                if ship_parts[part]['damage'] == 'RIFT_DAMAGE':
                    # Rift cannons work very differently: 1: deal 1 dmg to a ship with a rift weapon equipped,
                    # 2 or 3 is a miss, 4 is one guaranteed damage to the target, 5 is two gauranteed damage, 
                    # 6 is 3 damage to the target and 1 to a rift equipped ship

                    #Gauranteed target damage can be treated as rolling a nat 6 for that damage amount
                    if atk_roll == 1:
                        #Special self damage
                        dmg_stack.append((-999, 1))
                        logger.debug(f"ship {self} rolls a {atk_roll} on a rift cannon and adds 1 friendly fire damage to the damage stack!")
                    elif atk_roll == 2 or atk_roll == 3:
                        #miss
                        continue
                    elif atk_roll == 4:
                        dmg_stack.append((6, 1))
                        logger.debug(f"ship {self} rolls a {atk_roll} on a rift cannon and adds 1 rift damage to the damage stack!")
                    elif atk_roll == 5:
                        dmg_stack.append((6, 2))
                        logger.debug(f"ship {self} rolls a {atk_roll} on a rift cannon and adds 2 rift damage to the damage stack!")
                    else: #A 6
                        dmg_stack.append((6, 3))

                        #Special self damage
                        dmg_stack.append((-999, 1))
                        logger.debug(f"ship {self} rolls a {atk_roll} on a rift cannon and adds 3 rift damage and 1 friendly fire damage to the damage stack!")
                else:    
                    if atk_roll == 1:
                        #1 is always a miss
                        continue
                    else:
                        logger.debug(f"ship {self} rolls a {atk_roll} and adds that roll with {ship_parts[part]['damage']} to the damage stack!")
                        dmg_stack.append((atk_roll, ship_parts[part]['damage']))
                
        return dmg_stack
            
    
        
    def update_init(self) -> int:
        self._initiative = ship_types[self.ship_type]["base_initiative"]
        for part in self.ship_parts:
            if part is None:
                continue
            elif 'initiative' in ship_parts[part]:
                self._initiative += ship_parts[part]['initiative']
                
        return self._initiative
    
    def recalc_hp(self) -> int:
        #Recalc HP of this ship which is 1 + any installed part with hull add ons
        self._hp = 1
        
        for part in self.ship_parts:
            if part is None:
                continue
            elif 'armor' in ship_parts[part]:
                self._hp += ship_parts[part]['armor']
                
        return self._hp
    
    def update_targeting(self) -> int:
        #Recalc targeting of this ship which is 0 + any installed part with targetting add ons
        self._targeting = 0
        
        for part in self.ship_parts:
            if part is None:
                continue
            elif 'targeting' in ship_parts[part]:
                self._targeting += ship_parts[part]['targeting']
                
        return self._targeting

    def get_initiative(self, defender_weighted: bool = False) -> int:
        """Returns the current initiatve value for this ship.

        Args:
            defender_weighted (bool, optional): If specified, multiply initiative by 2 and add player_num-1 
            to make sure there are no initiative ties. This works because initiative is comparative and absolute
            value doesn't matter.  Defaults to False.

            Consider the following example:
            Attacker has 3 ships with initiative 2, 2, and 4.  
            Defender has 2 ships with initiative 1, 2, and 3.

            Attack order should be A4, D3, D2, (A2, A2), D1.

            Using the above algorith we transform the initiatves as follows:
            Attacker: 4, 4, 8
            Defender: 3, 5, 7

            Attacker order can now be reverse sorted and works as expected: 8, 7, 5, (4, 4), 3

        Returns:
            int: A number greater than zero representing the current initiatve value for this ship.
        """
        if defender_weighted:
            return self._initiative * 2 + self.player_num - 1
        else:
            return self._initiative
        
    
    def get_targeting(self):
        return self._targeting

    def update_shielding(self) -> int:
        #Recalc shield of this ship which is 0 + any installed part with targetting add ons
        self._shielding = 0
        
        for part in self.ship_parts:
            if part is None:
                continue
            elif 'shielding' in ship_parts[part]:
                self._shielding += ship_parts[part]['shielding']
                
        return self._shielding


    def get_shielding(self) -> int:
        return self._shielding

        
    def __lt__(self, other):
        logger.debug(f'sorting: self._initiatve: {self._initiative}, other._init: { other._initiative}')
        if other._initiative == self._initiative:
            #ties go to the defender
            return self.is_attacker
        elif other._initiative > self._initiative:
            return True
        return False
    
    def __str__(self):
        #return(f"P-{self.player_num}/T-{self.ship_type}/Atk:{self.is_attacker}, parts: {self.ship_parts}")
        #return(f"P-{self.player_num}/T-{self.ship_type}/Atk:{self.is_attacker}/HP:{self._hp}")
        return(f"P{self.player_num}/T{self.ship_type}/HP{self._hp}")
        

class Battle_sim:
    
    def __init__(self, player_1_ships: list[Ship], player_2_ships: list[Ship]):
        self.player_1_ships = player_1_ships
        self.player_2_ships = player_2_ships
        
        # Determine initiative order by creating lists for each distinct group of ships that fire at a single moment.
        # Note, opposing ships can never fire at the same time in Eclipse as defenders win all initiative ties.
        self.sorted_ships = sorted(player_1_ships + player_2_ships, reverse=True)
        self.create_ship_init_dict()

        #Init results dataframe
        self._df = pd.DataFrame(columns=['Result', 'Winning Player', 'Surviving Intr', 'Surviving Crus', 'Surviving Dred', 'Surviving Strb', 'Raw Count', 'Percentage'])                                         
        
        self._df = self._df.set_index('Result')

    def create_ship_init_dict(self):
        self.ships_init_dict = {}
        for ship in self.sorted_ships:
            weighted_init = ship.get_initiative(defender_weighted=True)
            if weighted_init in self.ships_init_dict:
                self.ships_init_dict[weighted_init].append(ship)
            else:
                self.ships_init_dict[weighted_init] = [ship]

    def ppships(self, player_num):
        output_str = f'P{player_num} s: '
        for ship in eval(f"self.player_{player_num}_ships"):
            output_str += str(ship)
        return output_str
    
    def get_surviving_count(self, player_num =1):
        i = 0
        for ship in [s for s in self.sorted_ships if s.player_num == player_num]:
            if ship.get_hp() > 0:
                i+=1
        return i

    #TODO - type hint for return should include | None when this is upgraded to python 3.10+
    def get_dmg(self, ship_dmg_stacks: dict[Ship, list[tuple[int, int]]], target_ship: Ship ) ->  dict[Ship, list[tuple[int, int]]]:
        """Given a dictionary of ships with lists of tuples representing the attack rolls they've made for this round, determine 
        how many of those stacks can hit the specified target ship.

        Args:
            ship_dmg_stacks (dict[Ship, list[tuple[int, int]]]): A dict with Ship instances as keys and values as lists of the tuples
            (roll, damage).
            target_ship (Ship): The ship potentially being fired on.

        Returns:
            dict[Ship, list[tuple[int, int]]]: Only damage stacks that can hit the targetted ship are returned.
        """        
        target_dmg_stacks = {}
        for ship in ship_dmg_stacks.keys():
            for roll, damage in ship_dmg_stacks[ship]:
                if roll == 6 or ship.get_targeting() + roll - target_ship.get_shielding() >= 6:
                    # This is a hit
                    if ship in target_dmg_stacks:
                        target_dmg_stacks[ship].append((roll, damage))
                    else:
                        target_dmg_stacks[ship] = [(roll, damage)]

        return target_dmg_stacks
        
    # TODO - type hints in 3.10 allow Ship | None format - refactor when upgrading python
    def get_largest_targetable_ship(self, firing_ship: Ship, roll) -> Ship:
        ships_to_check = self.get_player_ships(firing_ship.player_num, get_other_player=True)
        # With default reverse sort, this should always go from largest ship to smallest
        for ship in ships_to_check:
            if ship.get_hp() <= 0:
                #skip dead ships
                continue
            elif firing_ship.get_targeting() + roll - ship.get_shielding() >= 6:
                return ship
        return None


    def get_player_ships(self, player_num: int, get_other_player: bool = False, sort_reverse: bool = True) -> list[Ship]:
        """Get a list of ships owned by the indicated player number or the list of ships owned by the 'other' player in the battle.

        Args:
            player_num (int): The player number whose ships are desired
            get_other_player (bool, optional): If set to False returns the other player's ships.  E.g., returns player 2's ships 
                                                if player 1 is indicated with the first parameter. Defaults to False.
            sort_reverse (bool, optional): If set to false return ships in ascending initiative order, otherwise Descending. Defaults to True.

        Returns:
            list[Ship]: A list of Ship objects representing the requested player's ships.
        """
        if get_other_player:
            return sorted(eval(f"self.player_{player_num % 2 + 1}_ships"), key=lambda x : x.ship_type, reverse=sort_reverse)
        else:
            return sorted(eval(f"self.player_{player_num}_ships"), key=lambda x : x.ship_type, reverse=sort_reverse)
        
    
    #TODO upgrade to Python 3.10 and support return list[Ship] | None
    def get_surviving_ships(self, ship_type_filter: Ship_type = None) -> list[Ship]:
        """Returns all ships for both players with HP > 0

        Args:
            ship_type_filter (Ship_type, optional): If specified, only return surviving ships of this type, e.g., Interceptor. Defaults to None.

        Returns:
            list[Ship]: Returns a list of Ship objects with HP > 0
        """
        ship_list = []
        for ship in self.sorted_ships:
            if ship.get_hp() > 0:
                if ship_type_filter is None or ship.ship_type == ship_type_filter:
                    ship_list.append(ship)
        return ship_list
    
    def reset_ship_health_counts(self, surviving_ships: list[Ship]) -> list[Ship]:
        """For the provided dataframe, iterate over ships in surviving ships column and reset their HPs to full.

        Args:
            surviving_ships (list[Ship]): A list of ships that need health counts reset.

        Returns:
            list[Ship]: The updated list of ships.
        """
        for ship in surviving_ships:
            ship.recalc_hp()

        return surviving_ships
    

    def get_flattened_df(self) -> pd.DataFrame:
        """Given that our internal dataframe stores all distinct outcomes (e.g., a surviving ship with 1 hp is distinct 
        from one with 2 hp) this method removes HP as a distinguishing characteristic and flattens the df accordingly.

        Returns:
            pd.DataFrame: A Dataframe where each row corresponds a battle outcome with a distinct number of surviving ships
        """
        logger.debug(f'Dataframe before flattening: \n{self._df}')
        '''
        flattened_df = self._df['Surviving Ships'].map(lambda x: self.reset_ship_health_counts(x))
        flattened_df.name = 'Surviving Ships'

        self._df.update(flattened_df)

        self._df = self._df.groupby(['Surviving Ships']).size().reset_index(name='count')
        '''
        #flattened_df = self._df.groupby(self._df[['Surviving Intr', 'Surviving Crus', 'Surviving Dred', 'Surviving Strb']].map(tuple)).apply(lambda x : x)
        raise NotImplementedError
        flattened_df = pd.DataFrame()
        logger.debug(f'Dataframe after flattening: \n{self._df}')
        return flattened_df
    

    def save_fleet(self, player_num: int, filepath: str) -> None:
        # Nothing fancy here just if branch instead of an eval
        with open(filepath, 'w') as f:
            if player_num == 1:
                json.dump(jsonpickle.encode(self.player_1_ships), f, indent=4)
            else:
                json.dump(jsonpickle.encode(self.player_2_ships), f, indent=4)

    def load_fleet(self, player_num: int, filepath: str) -> None:
        with open(filepath, 'r') as f:
            if player_num == 1:
                self.player_1_ships = jsonpickle.decode(json.load(f))
            else:
                self.player_2_ships = jsonpickle.decode(json.load(f))


    def print_battle_stats(self):
        """Print the winner and their surviving ships
        """
        print(f"\n***BATTLE RESULTS ***\n\n{self._df}")

        filter_df = self._df
        filter_df[['Surviving Intr', 'Surviving Crus', 'Surviving Dred', 'Surviving Strb']] = filter_df[['Surviving Intr', 'Surviving Crus', 'Surviving Dred', 'Surviving Strb']].applymap(lambda x: len(x))
        filter_df = filter_df.groupby([ 'Winning Player', 'Surviving Intr', 'Surviving Crus', 'Surviving Dred', 'Surviving Strb']).sum()
        
        filter_df['Percentage'] = (filter_df['Raw Count'] / filter_df['Raw Count'].sum()) * 100
        
        print(f"\nDistinct Outcome Percentages:\n{filter_df}")



    def process_rift_stacks(self, firing_ship: Ship, dmg_stacks: list[tuple[int,int]]) -> None:
        """Process any rift damage in the dmg_stacks.
         
           The rules for self inflicted rift damage are:
        Rift damage to your own Ships must be assigned to Ships that have Rift weapons.  If possible, 
        the damage is assigned so that your ships with Rift weapons are destroyed from largest to smallest.
        If none of your Ships with Rift weapons can be destroyed, the damage is assigned to inflict as much
        damage to them as possible, from largest to smallest.

        Args:
            firing_ship (Ship): The f
            dmg_stacks (List[tuple): _description_
        """
        raise NotImplementedError


      
    def do_battle(self, sim_count = 1):
        
        #In init order roll attack die, assign damage based on AI model. 
        #If a ship is destroyed, remove it from the list (potentially before it fires)
        #Loop until all ships on one side or the other are defeated.
        #Run the sim for sim_count times and return a probability distribution of the outcomes encountered

        # Create backups of the ships to reset after each loop... there's probably a better way to do this
        player_1_ships_orig = deepcopy(self.player_1_ships)
        player_2_ships_orig = deepcopy(self.player_2_ships)

        for battle in range(sim_count):
            round = 1

            logger.info(f'*** Start of battle {battle} ***\n {self.ppships(1)}\nvs\n{self.ppships(2)}\n *** ***')
            
            #First fire missiles in initiative order
            #print('Begin Missiles')
            for ship in self.sorted_ships:
                pass
                #TODO IMPLEMENT
                
                
            #print('Missiles Complete!')
            
            # Round loop
            for i in range(1,100): #Assume no combat will take more than 100 rounds for now
                logger.debug(f'\n\nRound {i} begin...')
                # Second fire all other weapons in initiative order; damage will be assigned and resolved in the order highest to lowest, defender wins all ties.
                # Player 2 is always the defender
                for init in sorted(self.ships_init_dict.keys(), reverse=True):
                    self.process_one_init_group(self.ships_init_dict[init])
                    
                #If both sides have living ships continue, otherwise end
                #print(f'p1 ship count: {len(self.player_1_ships)} ... p2 ship count: {len(self.player_2_ships)}')
                #if len(self.player_1_ships) >= 1 and len(self.player_2_ships) >= 1:
                if self.get_surviving_count(player_num=1) >= 1 and self.get_surviving_count(player_num=2) >=1 :
                    round +=1
                else:
                    logger.debug('Combat complete..?')
                    break

            logger.info(f'*** End of battle {battle} ***\n{self.ppships(1)}\nvs\n{self.ppships(2)}\n *** ***')

            # TODO - Return a dataframe representing the outcome?
            result_arr = f"|{self.ppships(1)} <-> {self.ppships(2)}|"
            # print(f"self._df.loc['Result':]: {self._df.loc['Result':]}")
            if '|P1 s:  <-> P2 s: |' in result_arr:
                #This means all ships destroyed one another - an error condition that cannot occur AFAIK - 
                # defender wins initiative ties so there is now way for ordinance to pass each other in space
                raise RuntimeError
                
            if result_arr in self._df.index:
                self._df.loc[result_arr, 'Raw Count'] += 1
            else:
                new_row = pd.DataFrame([{'Result': result_arr,  'Winning Player': self.get_surviving_ships()[0].player_num, 
                                         'Surviving Intr': self.get_surviving_ships(Ship_type.TERRAN_INTERCEPTOR), 
                                         'Surviving Crus': self.get_surviving_ships(Ship_type.TERRAN_CRUISER),
                                         'Surviving Dred': self.get_surviving_ships(Ship_type.TERRAN_DREADNOUGHT),
                                         'Surviving Strb': self.get_surviving_ships(Ship_type.TERRAN_STARBASE),
                                         'Raw Count': 1, 'Percentage': 0}])
                new_row = new_row.set_index('Result')
                self._df = pd.concat([self._df, new_row])
                # self._df = self._df.set_index('Result')

            # Reset this object for another iteration
            self.player_1_ships = deepcopy(player_1_ships_orig)
            self.player_2_ships = deepcopy(player_2_ships_orig)

            self.sorted_ships = sorted(self.player_1_ships + self.player_2_ships, reverse=True)
            self.create_ship_init_dict()


        # With all simulated battles complete, calculate percentage distribution of the various unique outcomes
        self._df['Percentage'] = (self._df['Raw Count'] / self._df['Raw Count'].sum()) * 100
        return self._df
    

    def process_one_init_group(self, ships: list[Ship]):
        """For ships that share the same initiative, process the damage that they might deal to the other player's ships.

        Args:
            ships (list[Ship]): A list of ships with the same initiative value.
        """
        ship_dmg_stacks = {}
        for ship in ships:
            #is this ship already destroyed? 
            if ship.get_hp() == 0:
                continue
                #self.sorted_ships.remove(ship)
            logger.debug(ship)
            dmg = ship.fire_weapons()
            if dmg:
                logger.debug(dmg)
                ship_dmg_stacks[ship] = dmg

        # Since these ships all fire 'at once' the damage stack should be assigned simultaneously not one at a time
        if ship_dmg_stacks:
            self.assign_dmg(ship_dmg_stacks)

            
    #def assign_dmg(self, firing_ships: list[Ship], dmg_stacks: list[tuple[int, int]] ):
    def assign_dmg(self, ship_dmg_stacks: dict[Ship, list[tuple[int, int]]] ):
        """For now, all ships use the Ancients strat which is destroy the largest ship possible
        
        ToDo - Add support for smarter strategies, e.g., prefententially destroying ships that haven't fired yet.
               Running a monte carlo within the monte carlo to identify statistically optimal dmg allocation??

        Args:
            ship_dmg_stacks (dict[Ship, list[tuple[int, int]]]): The stack of potential damage from the ships firing
            on this particular initiative block.  (e.g., all shots fired from ships with initiative 4.)

        Raises:
            AttributeError: If damage is allocated to a ship that is already dead an AttributeError is raised.
        """        
       
        
        logger.debug(f"ship_dmg_stacks: {ship_dmg_stacks}")

    
        firing_player_num = list(ship_dmg_stacks.keys())[0].player_num
        for target_ship in self.get_player_ships(firing_player_num, get_other_player=True):
            logger.debug(f"largest ship is: {target_ship} ?")
            if target_ship._hp == 0:
                logger.debug(f"ship {target_ship} has already been destroyed, skipping...")
                continue

            #Create a damage stack only of damage that can hit this ship
            target_ship_dmg_stacks = self.get_dmg(ship_dmg_stacks, target_ship)

            if not target_ship_dmg_stacks:
                #If there are no stacks that can hit this ship, go to the next one
                continue

            #If we can destroy this ship, do so, deleting it and using the bare minimium of damage stacks
            
            # Todo - make this a badass nested list comprehension
            potential_dmg = 0
            for ship, dmg_list in target_ship_dmg_stacks.items():
                potential_dmg += sum([int(i[1]) for i in dmg_list])
            # potential_dmg = sum([int(i[1]) for i in target_ship_dmg_stacks.values()])
            logger.debug(f"Total damage that could hit ship {target_ship} is: {potential_dmg}")
            if potential_dmg >= target_ship._hp:
                #efficiently kill this ship so that no damage is wasted
                #TODO - antimatter cannon splitter not supported yet
                temp_stack = 0
                #for roll, dmg in target_ship_dmg_stacks.copy():
                for firing_ship, dmg_stack_list in target_ship_dmg_stacks.copy().items():
                    for (roll, dmg) in dmg_stack_list:
                        if dmg + temp_stack == target_ship._hp:
                            #efficient damage, pop stack, delete this ship, and continue
                            logger.debug(f"destroying ship: {target_ship}, with new stack {(roll, dmg)} and temp_stack {temp_stack}")
                            
                            ship_dmg_stacks[firing_ship].remove((roll, dmg))
                            target_ship_dmg_stacks[firing_ship].remove((roll, dmg))
                            #This doesn't work as the destroyed ship may not have been calculated to fire - we need to mark it destroyed and so exclude it from being
                            # able to fire!
                            #eval(f"self.player_{firing_ship.player_num % 2 + 1}_ships").remove(ship)
                            target_ship.set_hp(0)
                            break
                        elif dmg + temp_stack < target_ship._hp:
                            #add this stack to temp_stack
                            logger.debug(f'stack {dmg} + temp_stack {temp_stack} < ship._hp {target_ship._hp}')
                            temp_stack+=dmg
                            ship_dmg_stacks[firing_ship].remove((roll, dmg))
                            target_ship_dmg_stacks[firing_ship].remove((roll, dmg))
                            
                        else:
                            # Wasted damage
                            # TODO - reallocate, for now just burn this one
                            logger.debug(f"destroying ship: {target_ship}, with new stack {dmg} and temp_stack {temp_stack}")
                            ship_dmg_stacks[firing_ship].remove((roll, dmg))
                            target_ship_dmg_stacks[firing_ship].remove((roll, dmg))
                            self.get_player_ships(firing_player_num, get_other_player=True).remove(target_ship)
                            target_ship.set_hp(0)
                            break
               #Any stack damage left will be applied to the next surviving ship
            else: #All damage available can't destroy this ship so try the next one
                continue

                  
        #If we fall through check to see if any damage is left, if so just throw it on the largest ship
        # We only assign leftover damage if there is leftover damage AND there are no surviving ships left to hit.  (e.g., if we overkilled the last ship)
        for firing_ship, dmg_stack_list in target_ship_dmg_stacks.items():
            for (roll, dmg) in dmg_stack_list:
                largest_hit_ship = self.get_largest_targetable_ship(firing_ship, roll)
                if largest_hit_ship:
                    logger.debug(f'Applying leftover dmg stack ({roll}, {dmg}) to ship {largest_hit_ship}')
                    largest_hit_ship.set_hp(largest_hit_ship.get_hp() - dmg)
                    if largest_hit_ship.get_hp() <= 0:
                        raise AttributeError(f"Error: dmg of {dmg} for ship {largest_hit_ship} exceeded its available HP, so ship should already be dead!")

                
        

# Need to be able to run monte carlo sim of two ships and output 
# probabilities of winning/losing

def main():
    test_ship = Ship(Ship_type.TERRAN_INTERCEPTOR, 1, is_attacker = False)
    test_ship_b = Ship(Ship_type.TERRAN_INTERCEPTOR, 1, is_attacker = False)
    #print(test_ship)
    test_ship_2 = Ship(Ship_type.TERRAN_DREADNOUGHT, 2)


    test_ship_2.add_part(Ship_part_names.NUCLEAR_DRIVE, 3)
    #print(test_ship_2)



    battle_sim = Battle_sim([test_ship, test_ship_b], [test_ship_2])

    battle_sim.do_battle(sim_count=1000)
    battle_sim.print_battle_stats()
    #battle_sim.get_flattened_df()
    pass


if __name__ == "__main__":
    main()