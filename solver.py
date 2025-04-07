import sys
from collections import defaultdict, deque, namedtuple
import heapq
import re

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
                elif node == "empty":
                    node_types[node] = EMPTY
                else:
                    node_types[node] = ANIMAL
                    animals.add(node)

    return graph, node_types, animals, houses, start_node

def get_corresponding_house(animal):
    return f"{animal}_house"

def get_corresponding_animal(house):
    return house.replace("_house", "")

def heuristic(remaining_animals, remaining_fuel):
    # Heuristic: number of remaining animals to deliver, weighted
    return len(remaining_animals) * 10 - remaining_fuel

def a_star(graph, node_types, start_node, fuel_limit):
    heap = []
    visited = {}
    initial_state = State(
        priority=0,
        location=start_node,
        cargo=frozenset(),
        delivered=frozenset(),
        fuel=fuel_limit,
        path=[f"Start at {start_node}"]
    )
    heapq.heappush(heap, initial_state)
    best_path = []
    max_delivered = 0

    while heap:
        state = heapq.heappop(heap)
        key = (state.location, state.cargo, state.delivered)

        # Skip worse states
        if key in visited and visited[key] >= state.fuel:
            continue
        visited[key] = state.fuel

        if len(state.delivered) > max_delivered:
            max_delivered = len(state.delivered)
            best_path = state.path

        if state.fuel == 0:
            continue

        for neighbor in graph[state.location]:
            next_fuel = state.fuel - 1
            next_path = list(state.path)
            next_path.append(f"Step {len(next_path)} : Go to {neighbor}")
            next_cargo = set(state.cargo)
            next_delivered = set(state.delivered)

            if node_types[neighbor] == ANIMAL and neighbor not in state.cargo and neighbor not in state.delivered:
                if len(state.cargo) < CAPACITY:
                    next_cargo.add(neighbor)
                    next_path.append(f"Step {len(next_path)} : Pick up the {neighbor}")
                else:
                    next_path.append(f"Step {len(next_path)} : Visit the {neighbor} (car full)")
            elif node_types[neighbor] == HOUSE:
                animal = get_corresponding_animal(neighbor)
                if animal in next_cargo:
                    next_cargo.remove(animal)
                    next_delivered.add(animal)
                    next_path.append(f"Step {len(next_path)} : Drop off the {animal}")
                else:
                    next_path.append(f"Step {len(next_path)} : Visit the {neighbor}")
            elif node_types[neighbor] == EMPTY:
                next_path.append(f"Step {len(next_path)} : Visit the {neighbor}")

            remaining_animals = set(graph.keys()) - next_delivered
            h = heuristic(set(graph.keys()) - next_delivered, next_fuel)

            new_state = State(
                priority=len(next_path) + h,
                location=neighbor,
                cargo=frozenset(next_cargo),
                delivered=frozenset(next_delivered),
                fuel=next_fuel,
                path=next_path
            )

            heapq.heappush(heap, new_state)

    return best_path

def main():
    if len(sys.argv) < 3:
        print("Usage: python pet_detective_solver.py <graph_file.txt> <fuel_limit>")
        sys.exit(1)

    file_path = sys.argv[1]
    fuel_limit = int(sys.argv[2])

    graph, node_types, animals, houses, start_node = parse_input(file_path)
    best_path = a_star(graph, node_types, start_node, fuel_limit)

    print("\nOptimal Sequence:")
    for step in best_path:
        print(step)

if __name__ == "__main__":
    main()
