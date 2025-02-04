#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')


    #First try to find a good neutral planet to spread to
    closeSpread = Sequence(name='close spread')
    neutralPlanetCheck = Check(isCloseNeutralAvail)
    captureNeutralAction = Action(spreadToBestNeutralPlanet)
    closeSpread.child_nodes = [neutralPlanetCheck, captureNeutralAction]

    #If we cant find any then try to attack
    attackEnemy = Sequence(name='Attack Strategy')
    attackEnemyAction = Action(attackCloseEnemy)
    attackEnemy.child_nodes = [attackEnemyAction]

    # defensive_plan = Sequence(name='Defensive Strategy')
    # under_attack_check = Check(is_under_attack)
    # reinforce_action = Action(reinforce_weakest_planet)
    # defensive_plan.child_nodes = [under_attack_check, reinforce_action]

    destroy_enemy = Sequence(name='Finisher Strategy')
    last_enemy_check = Check(is_final_enemy_base)
    kill_action = Action(finish_enemy)
    destroy_enemy.child_nodes = [last_enemy_check, kill_action]

    root.child_nodes = [closeSpread, attackEnemy, destroy_enemy,]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
