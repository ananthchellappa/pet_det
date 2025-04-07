import sys
from collections import defaultdict, namedtuple
import heapq
import re
import time

# Constants
CAPACITY = 4

# Node types
ANIMAL = "animal"
HOUSE = "house"
EMPTY = "empty"

# State representation
State = namedtuple("State", ["priority", "location", "cargo", "delivered", "fuel", "path"])

def parse_input(file_path):
    graph = defaultdict(set)
    node_types = defaultdict(lambda: EMPTY)
    animals = set()
    houses = set()
    start_node = None

    with open(file_path) as f:
        for line in f:
            if not line.strip():
                continue
            a, b = [x.strip() for x in line.strip().split("<-->")]
            graph[a].add(b)
            graph[b].add(a)

            for node in (a, b):
                if node.startswith("car"):
                    start_node = node
                elif node.endswith("_house"):
                    node_types[node] = HOUSE
                    houses.add(node)
                elif re.match(r"empty\d*", node):
                    node_types[node] = EMPTY
                else:
                    node_types[node] = ANIMAL
                    animals.add(node)

    return graph, node_types, animals, houses, start_node

def get_corresponding_house(animal):
    return f"{animal}_house"

def get_corresponding_animal(house):
    return house.replace("_house", "")

def precompute_shortest_paths(graph):
    shortest_paths = {}
    for start in graph:
        dist = {start: 0}
        queue = [(start, 0)]
        while queue:
            current, d = queue.pop(0)
            for neighbor in graph[current]:
                if neighbor not in dist:
                    dist[neighbor] = d + 1
                    queue.append((neighbor, d + 1))
        shortest_paths[start] = dist
    return shortest_paths

def heuristic(state, animals, houses, shortest_paths):
    est = 0
    for pet in state.cargo:
        house = get_corresponding_house(pet)
        est += shortest_paths[state.location].get(house, 100)
    for pet in animals - state.cargo - state.delivered:
        est += shortest_paths[state.location].get(pet, 100)
    return est

def a_star(graph, node_types, animals, houses, start_node, fuel_limit, debug=False):
    shortest_paths = precompute_shortest_paths(graph)
    heap = []
    visited = {}
    initial_state = State(
        priority=0,
        location=start_node,
        cargo=frozenset(),
        delivered=frozenset(),
        fuel=fuel_limit,
        path=[f"Start at {start_node} (fuel: {fuel_limit}, cargo: [], pending: {sorted(animals)})"]
    )
    heapq.heappush(heap, initial_state)
    best_path = []
    max_delivered = 0
    full_solution_path = None
    steps = 0

    while heap:
        state = heapq.heappop(heap)
        steps += 1
        if debug and steps % 1000 == 0:
            print(f"[DEBUG] Steps: {steps}, Queue size: {len(heap)}, Delivered: {len(state.delivered)}")

        key = (state.location, state.cargo, state.delivered)
        if key in visited and visited[key] >= state.fuel:
            continue
        visited[key] = state.fuel

        if len(state.delivered) > max_delivered:
            max_delivered = len(state.delivered)
            best_path = state.path

        if len(state.delivered) == len(animals):
            full_solution_path = state.path
            break

        if state.fuel == 0:
            continue

        for neighbor in graph[state.location]:
            next_fuel = state.fuel - 1
            next_cargo = set(state.cargo)
            next_delivered = set(state.delivered)
            remaining_animals = animals - next_cargo - next_delivered
            pending_text = f", pending: {sorted(remaining_animals)}" if len(remaining_animals) < 4 else ""
            next_path = list(state.path)
            next_path.append(f"Step {len(next_path)} : Go to {neighbor} (fuel: {next_fuel}, cargo: {sorted(state.cargo)}{pending_text})")

            if node_types[neighbor] == ANIMAL and neighbor not in state.cargo and neighbor not in state.delivered:
                if len(state.cargo) < CAPACITY:
                    next_cargo.add(neighbor)
                    pending_text = f", pending: {sorted(animals - next_cargo - next_delivered)}" if len(animals - next_cargo - next_delivered) < 4 else ""
                    next_path.append(f"Step {len(next_path)} : Pick up the {neighbor} (fuel: {next_fuel}, cargo: {sorted(next_cargo)}{pending_text})")
                else:
                    next_path.append(f"Step {len(next_path)} : Visit the {neighbor} (car full) (fuel: {next_fuel}, cargo: {sorted(next_cargo)}{pending_text})")
            elif node_types[neighbor] == HOUSE:
                animal = get_corresponding_animal(neighbor)
                if animal in next_cargo:
                    next_cargo.remove(animal)
                    next_delivered.add(animal)
                    pending_text = f", pending: {sorted(animals - next_cargo - next_delivered)}" if len(animals - next_cargo - next_delivered) < 4 else ""
                    next_path.append(f"Step {len(next_path)} : Drop off the {animal} (fuel: {next_fuel}, cargo: {sorted(next_cargo)}{pending_text})")
                else:
                    next_path.append(f"Step {len(next_path)} : Visit the {neighbor} (fuel: {next_fuel}, cargo: {sorted(next_cargo)}{pending_text})")
            elif node_types[neighbor] == EMPTY:
                next_path.append(f"Step {len(next_path)} : Visit the {neighbor} (fuel: {next_fuel}, cargo: {sorted(next_cargo)}{pending_text})")

            h = heuristic(state, animals, houses, shortest_paths)
            new_state = State(
                priority=len(next_path) + h,
                location=neighbor,
                cargo=frozenset(next_cargo),
                delivered=frozenset(next_delivered),
                fuel=next_fuel,
                path=next_path
            )

            heapq.heappush(heap, new_state)

    return full_solution_path if full_solution_path else best_path, full_solution_path is not None

def main():
    if len(sys.argv) < 3:
        print("Usage: python pet_detective_solver.py <graph_file.txt> <fuel_limit> [DEBUG]")
        sys.exit(1)

    file_path = sys.argv[1]
    fuel_limit = int(sys.argv[2])
    debug = (len(sys.argv) > 3 and sys.argv[3] == "DEBUG")

    start_time = time.time()
    graph, node_types, animals, houses, start_node = parse_input(file_path)
    best_path, full_delivered = a_star(graph, node_types, animals, houses, start_node, fuel_limit, debug)
    elapsed = time.time() - start_time

    print("\nOptimal Sequence:")
    for step in best_path:
        print(step)

    if full_delivered:
        print("\n✅ Full delivery successful!")
    else:
        print("\n⚠️ Only partial delivery possible with given fuel.")

    print(f"Elapsed time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
