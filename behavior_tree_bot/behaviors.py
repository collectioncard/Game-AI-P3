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


#### Stuff from Derek that I didnt use in the current. IDK if we still wanna use it

# Sort by lowest distance to target planet
def distance(source, destination):
    dx = source.x - destination.x
    dy = source.y - destination.y
    return int(ceil(sqrt(dx * dx + dy * dy)))


# Not accounting for distance yet
def spread_to_best_neutral_planet(state):
    #  my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships * (1 + 1/p.growth_rate)))

    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships * (1 + 1 / p.growth_rate))
    target_planets = iter(neutral_planets)

    try:
        while True:
            target_planet = next(target_planets)
            i = 0
            my_empire = state.my_planets()
            my_empire.sort(key=lambda p: p.num_ships * (1 + 1 / p.growth_rate))
            my_top_5 = []
            top_5_ships_available = 0
            while i < 5 and i < len(my_empire):
                my_top_5.append(my_empire[i])
                top_5_ships_available += my_empire[i].num_ships * (
                            1 / 3)  # 1/3 of the number of ships from our closest best 5 planets
                i += 1
            #            logging.info(i)
            my_top_5.sort(key=lambda p: distance(p, target_planet))
            my_planets = iter(my_top_5)
            my_planet = next(my_planets)
            required_ships = target_planet.num_ships + 5
            j = 0
            forces_sent = 0

            while j < 5 and j < len(state.my_planets()):
                if top_5_ships_available > required_ships:
                    while forces_sent != required_ships and my_planet.num_ships * (2 / 3) >= 25:
                        regiment = my_planet.num_ships * (1 / 3)
                        forces_sent += regiment
                        issue_order(state, my_planet.ID, target_planet.ID, regiment)
                        my_planet = next(my_planets)
                j += 1


    except StopIteration:
        return False
