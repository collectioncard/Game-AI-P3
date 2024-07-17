

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def if_no_neutral_planet_available(state):
    return len(state.not_my_planets()) == len(state.enemy_planets())

def doesNeutralExist(state):
    return any(state.neutral_planets())

def isCloseNeutralAvail(state):
    for neutral_planet in state.neutral_planets():
        for my_planet in state.my_planets():
            if state.distance(my_planet.ID, neutral_planet.ID) < 500:
                return True
    return False

def isUnderAttack(state):
    return any(fleet.destination_planet in [planet.ID for planet in state.my_planets()] for fleet in state.enemy_fleets())

def is_final_enemy_base(state):
    return (len(state.neutral_planets()) == 0) and (len(state.enemy_planets()) < 2)

def is_under_attack(state):
    return any(fleet.destination_planet in [planet.ID for planet in state.my_planets()] for fleet in state.enemy_fleets())