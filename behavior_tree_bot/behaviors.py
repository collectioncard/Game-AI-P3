import sys, logging
from math import ceil, sqrt

sys.path.insert(0, '../')
from planet_wars import issue_order


def attackCloseEnemy(state):
    # Find the strongest planet that we have
    ourStrongestPlanet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    if not ourStrongestPlanet:
        return False

    # Find an enemy planet close to our strongest planet that we can easily take. Sort first by distance and then
    # number of ships if they are the same.
    enemyPlanets = sorted(state.enemy_planets(),
                          key=lambda p: (state.distance(ourStrongestPlanet.ID, p.ID), p.num_ships))

    for planet in enemyPlanets:
        # Calc the travel time to the enemy planet and use that to determine the actual enemy ship number when we get there.
        travelTime = state.distance(ourStrongestPlanet.ID, planet.ID)
        enemyOnArrival = planet.num_ships + (planet.growth_rate * travelTime)
        requiredShips = enemyOnArrival + 1

        # If our strongest planet has more ships than the required ships, send the fleet
        if ourStrongestPlanet.num_ships > requiredShips:
            return issue_order(state, ourStrongestPlanet.ID, planet.ID, requiredShips)

    return False


def spreadToBestNeutralPlanet(state):
    # Find all neutral planets and sort them by their distance to the closest player-owned planet, then by their growth rate.
    neutralPlanets = sorted(
        state.neutral_planets(),
        key=lambda neutralPlanet: (
            min(state.distance(neutralPlanet.ID, myPlanet.ID) for myPlanet in state.my_planets()),
            # Find the smallest distance between our planet and the neutral planet
            -neutralPlanet.growth_rate))  # if we find dupes, sort by growth rate

    for neutralPlanet in neutralPlanets:
        # Dont send more than one fleet
        if any(fleet.destination_planet == neutralPlanet.ID for fleet in state.my_fleets()):
            continue

        # Find the closest player-owned planet to the neutral planet
        closestOwnedPlanet = min(state.my_planets(),
                                 key=lambda ownedPlanet: state.distance(ownedPlanet.ID, neutralPlanet.ID), default=None)

        if closestOwnedPlanet and closestOwnedPlanet.num_ships > neutralPlanet.num_ships:
            # Send it if we can!
            issue_order(state, closestOwnedPlanet.ID, neutralPlanet.ID, neutralPlanet.num_ships + 1)

    return False

def finish_enemy(state):
    """
    Finish enemy when they are left with a single planet
    """
    try:
        enemy_planet = next(iter(state.enemy_planets()), None)

        # (1) If enemy has a planet, then attack with the top 5 strongest planets
        if enemy_planet:
            logging.info(f"Attacking enemy planet {enemy_planet.ID} with top 5 strongest planets")
            strongest_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)[:5]
            for local in strongest_planets:
                # Unconditionally attack the enemy planet
                logging.info(f"Attacking from planet {local.ID} to enemy planet {enemy_planet.ID}")
                if local.num_ships > 1:  # Ensure there is at least one ship left behind
                    if issue_order(state, local.ID, enemy_planet.ID, local.num_ships - 1):
                        return True

            # No suitable planet can attack
            return False

        # (2) If enemy has no planet, check for their fleets, reinforce planets being targeted
        logging.info("No enemy planets found, checking for enemy fleets")
        enemy_fleets = sorted(state.enemy_fleets(), key=lambda f: f.num_ships, reverse=True)
        if enemy_fleets:
            enemy_targets = set(f.destination_planet for f in enemy_fleets)

            for fleet in enemy_fleets:
                target_planet = state.planets[fleet.destination_planet]
                # Check if target will survive
                target_defence = target_planet.num_ships + (target_planet.growth_rate * fleet.turns_remaining)
                if target_defence >= fleet.num_ships:
                    continue

                # Target will fall, so send support
                local_friendlies = sorted(state.my_planets(), key=lambda t: state.distance(target_planet.ID, t.ID))
                # remove target from list
                local_friendlies = local_friendlies[1:]

                for local in local_friendlies:
                    if local.ID not in enemy_targets:
                        logging.info(f"Sending support from planet {local.ID} to planet {target_planet.ID}")
                        if issue_order(state, local.ID, target_planet.ID, local.num_ships - 1):
                            return True

        # No planets will be lost
        return False
    except Exception as e:
        logging.error(f"Error in finish_enemy: {e}")
        return False
    
def reinforce_weakest_planet(state):
    """
    Reinforce the weakest planet by sending half of the ships from the strongest planet.
    """
    try:
        # Find the strongest planet
        strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
        
        # Find the weakest planet
        weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)

        # Check if we have both a strongest and weakest planet
        if strongest_planet and weakest_planet and strongest_planet.num_ships > 1:
            num_ships_to_send = strongest_planet.num_ships // 2  # Send half the ships
            logging.info(f"Reinforcing weakest planet {weakest_planet.ID} from strongest planet {strongest_planet.ID} with {num_ships_to_send} ships")
            return issue_order(state, strongest_planet.ID, weakest_planet.ID, num_ships_to_send)

        return False
    except Exception as e:
        logging.error(f"Error in reinforce_weakest_planet: {e}")
        return False