from enum import Enum
import random

class Ship_type(Enum):
    INTERCEPTOR = 1
    CRUISER = 2
    DREADNOUGHT = 3
    STARBASE = 4
    
class Ship_part_names(Enum):
    ELECTRON_COMPUTER = 1
    HULL = 2
    ION_CANNON = 3
    NUCLEAR_DRIVE = 4
    NUCLEAR_SOURCE = 5
    
    
    
# Need a data structure to represent ship configurations
ship_types = {Ship_type.INTERCEPTOR: 
              {"slots":4, "base_initiative":2, 
               "installed_parts": [Ship_part_names.ION_CANNON, Ship_part_names.NUCLEAR_DRIVE, Ship_part_names.NUCLEAR_SOURCE, None]}
             }

# Need a data structure to represent the various tech tiles 
ship_parts = {
    Ship_part_names.ELECTRON_COMPUTER: {"type": "computer", "targeting": 1, "cost":0},
    Ship_part_names.HULL: {"type":"hull", "armor":1, "cost":0},
    Ship_part_names.ION_CANNON: {"type": "weapon", "damage": 1, "cost": 1},
    Ship_part_names.NUCLEAR_DRIVE: {"type": "drive", "initiative": 2, "cost": 1},
    Ship_part_names.NUCLEAR_SOURCE: {"type": "source", "power": 3}
}
# Need to be able to simulate the rolling of die, assigning of damage per
# round

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
        self.update_hp()
        self.update_targeting()

        
    def add_part(self, part_name, part_position):
        #TODO - Check if we have enough power to mount this part, if not, throw an error
        
        
        #TODO - Check if adding this part removes our last drive and we're not a starbase - if so, throw an error
        
        self.ship_parts[part_position] = part_name
        self.update_init()
        self.update_hp()
        
    def remove_part(self, part_position):
        #Removing a part resets the part to its default configuration - may not need this
        self.ship_parts[part_position] = ship_types[self.ship_type]["installed_parts"][part_position]
        self.update_init()
        
    def get_avail_power(self) -> int:
        power = 0
        for part in self.ship_parts:
            if ship_parts[part]["type"] == 'source':
                power += ship_parts[part]['power']
            else:
                power -= ship_parts[part]['cost']
        return power
          
        
    def fire_missiles(self) -> list[int]:
        pass
    
    
    def fire_weapons(self) -> list[int]:
        dmg_stack = []
        
        for part in self.ship_parts:
            if part is None:
                continue
            elif 'damage' in ship_parts[part]:
                atk_roll = random.randint(1,6)
                if atk_roll + self._targeting >= 6:
                    print(f"ship {self} rolls a {atk_roll} for a hit and adds {ship_parts[part]['damage']} to the damage stack!")
                    dmg_stack.append(ship_parts[part]['damage'])
                
        return dmg_stack
            
    
        
    def update_init(self) -> int:
        self._initiative = ship_types[self.ship_type]["base_initiative"]
        for part in self.ship_parts:
            if part is None:
                continue
            elif 'initiative' in ship_parts[part]:
                self._initiative += ship_parts[part]['initiative']
                
        return self._initiative
    
    def update_hp(self) -> int:
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
        
    def __lt__(self, other):
        print(f'sorting: self._initiatve: {self._initiative}, other._init: { other._initiative}')
        if other._initiative == self._initiative:
            #ties go to the defender
            return self.is_attacker
        elif other._initiative > self._initiative:
            return True
        return False
    
    def __str__(self):
        #return(f"P-{self.player_num}/T-{self.ship_type}/Atk:{self.is_attacker}, parts: {self.ship_parts}")
        return(f"P-{self.player_num}/T-{self.ship_type}/Atk:{self.is_attacker}/HP:{self._hp}")
        

class Battle_sim:
    
    def __init__(self, player_1_ships: list[Ship], player_2_ships: list[Ship]):
        self.player_1_ships = player_1_ships
        self.player_2_ships = player_2_ships
        
        #Determine initiative order
        self.sorted_ships = sorted(player_1_ships + player_2_ships, reverse=True)
        
        #for ship in self.sorted_ships:
        #    print(ship)

    def ppships(self, player_num):
        output_str = f'Player_{player_num} ships: '
        for ship in eval(f"self.player_{player_num}_ships"):
            output_str += str(ship)
        return output_str
      
    def do_battle(self):
        
        #In init order roll attack die, assign damage based on AI model. 
        #If a ship is destroyed, remove it from the list (potentially before it fires)
        #Loop until all ships on one side or the other are defeated
        round = 1

        print(f'*** Start of battle ***\n {self.ppships(1)}\nvs\n{self.ppships(2)}\n *** ***')
        
        #First fire missiles in initiative order
        #print('Begin Missiles')
        for ship in self.sorted_ships:
            pass
            #TODO IMPLEMENT
            
            
        #print('Missiles Complete!')
        
        
        for i in range(1,100): #Assume no combat will take more than 100 rounds for now
            print(f'\n\nRound {i} begin...')
            #Second fire all other weapons in initiative order
            for ship in self.sorted_ships:
                print(ship)
                dmg = ship.fire_weapons()
                print(dmg)
                if dmg:
                    self.assign_dmg(ship, dmg)
                
            #If both sides have living ships continue, otherwise end
            #print(f'p1 ship count: {len(self.player_1_ships)} ... p2 ship count: {len(self.player_2_ships)}')
            if len(self.player_1_ships) >= 1 and len(self.player_2_ships) >= 1:
                round +=1
            else:
                print('Combat complete..?')
                break

        print(f'*** End of battle ***\n{self.ppships(1)}\nvs\n{self.ppships(2)}\n *** ***')
                
            
            
    def assign_dmg(self, firing_ship, dmg_stacks: list[int] ):
        #TODO - all damage is damage at a certain shield level so there's another dimension to this...
          
        #For now, all ships use the Ancients strat which is destroy the largest ship possible
        #If no ships can be destroyed damage the largest ship possible
        print(f"firing ship: {firing_ship}, dmg_stacks: {dmg_stacks}")
        
        for ship in sorted(eval(f"self.player_{firing_ship.player_num % 2 + 1}_ships"), key=lambda x : x.ship_type, reverse=True):
            print(f"largest ship is: {ship} ?")
            #If we can destroy this ship, do so, deleting it and using the bare minimium of damage stacks
            if sum([int(i) for i in dmg_stacks]) >= ship._hp:
                #efficiently kill this ship so that no damage is wasted
                #TODO - antimatter cannon splitter not supported yet
                temp_stack = 0
                for stack in dmg_stacks.copy():
                    if stack + temp_stack == ship._hp:
                        #efficient damage, pop stack, delete this ship, and continue
                        print(f"destroying ship: {ship}, with new stack {stack} and temp_stack {temp_stack}")
                        dmg_stacks.remove(stack)
                        eval(f"self.player_{firing_ship.player_num % 2 + 1}_ships").remove(ship)
                        break
                    elif stack + temp_stack < ship._hp:
                        #add this stack to temp_stack
                        print(f'stack {stack} + temp_stack {temp_stack} < ship._hp {ship._hp}')
                        temp_stack+=stack
                        dmg_stacks.remove(stack)
                        
                    else:
                        # Wasted damage
                        # TODO - reallocate, for now just burn this one
                        print(f"destroying ship: {ship}, with new stack {stack} and temp_stack {temp_stack}")
                        dmg_stacks.remove(stack)
                        eval(f"self.player_{firing_ship.player_num % 2 + 1}_ships").remove(ship)
                        break
               #Any stack damage left will be applied to the next surviving ship
            else: #All damage available can't destroy this ship so try the next one
                continue
                
        #If we fall through check to see if any damage is left, if so just throw it on the largest ship
        if len(dmg_stacks) > 0:
            print(f'leftover dmg_stacks: {dmg_stacks}')
            sorted(eval(f"self.player_{firing_ship.player_num % 2 + 1}_ships"), 
                   key=lambda x : x.ship_type, reverse=True)[0]._hp -= sum([int(i) for i in dmg_stacks])
                
        

# Need to be able to run monte carlo sim of two ships and output 
# probabilities of winning/losing

def main():
    test_ship = Ship(Ship_type.INTERCEPTOR, 1, is_attacker = False)
    #print(test_ship)
    test_ship_2 = Ship(Ship_type.INTERCEPTOR, 2)


    test_ship_2.add_part(Ship_part_names.NUCLEAR_DRIVE, 3)
    #print(test_ship_2)



    battle_sim = Battle_sim([test_ship], [test_ship_2])

    battle_sim.do_battle()


if __name__ == "__main__":
    main()