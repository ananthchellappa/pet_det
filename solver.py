import sys
from collections import defaultdict, deque, namedtuple
import re

# Constants
CAPACITY = 4

# Node types
ANIMAL = "animal"
HOUSE = "house"
EMPTY = "empty"

# State representation
State = namedtuple("State", ["location", "cargo", "delivered", "fuel", "path"])

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

def is_house(node):
    return node.endswith("_house")

def get_corresponding_house(animal):
    return f"{animal}_house"

def get_corresponding_animal(house):
    return house.replace("_house", "")

def bfs(graph, node_types, start_node, fuel_limit):
    queue = deque()
    visited = set()
    initial_state = State(
        location=start_node,
        cargo=frozenset(),
        delivered=frozenset(),
        fuel=fuel_limit,
        path=[f"Start at {start_node}"]
    )
    queue.append(initial_state)
    best_path = []
    max_delivered = 0

    while queue:
        state = queue.popleft()

        if (state.location, state.cargo, state.delivered, state.fuel) in visited:
            continue
        visited.add((state.location, state.cargo, state.delivered, state.fuel))

        if len(state.delivered) > max_delivered:
            max_delivered = len(state.delivered)
            best_path = state.path

        if state.fuel == 0:
            continue

        for neighbor in graph[state.location]:
            next_fuel = state.fuel - 1
            next_path = state.path + [f"Step {len(state.path)} : Go to {neighbor}"]
            next_cargo = set(state.cargo)
            next_delivered = set(state.delivered)

            # Pick up logic
            if node_types[neighbor] == ANIMAL and neighbor not in state.cargo and neighbor not in state.delivered:
                if len(state.cargo) < CAPACITY:
                    next_cargo.add(neighbor)
                    next_path.append(f"Step {len(next_path)} : Pick up the {neighbor}")
                else:
                    next_path.append(f"Step {len(next_path)} : Visit the {neighbor} (car full)")

            # Drop off logic
            elif node_types[neighbor] == HOUSE:
                animal = get_corresponding_animal(neighbor)
                if animal in state.cargo:
                    next_cargo.remove(animal)
                    next_delivered.add(animal)
                    next_path.append(f"Step {len(next_path)} : Drop off the {animal}")
                else:
                    next_path.append(f"Step {len(next_path)} : Visit the {neighbor}")

            elif node_types[neighbor] == EMPTY:
                next_path.append(f"Step {len(next_path)} : Visit the {neighbor}")

            new_state = State(
                location=neighbor,
                cargo=frozenset(next_cargo),
                delivered=frozenset(next_delivered),
                fuel=next_fuel,
                path=next_path
            )

            queue.append(new_state)

    return best_path

def main():
    if len(sys.argv) < 3:
        print("Usage: python pet_detective_solver.py <graph_file.txt> <fuel_limit>")
        sys.exit(1)

    file_path = sys.argv[1]
    fuel_limit = int(sys.argv[2])

    graph, node_types, animals, houses, start_node = parse_input(file_path)
    best_path = bfs(graph, node_types, start_node, fuel_limit)

    print("\nOptimal Sequence:")
    for step in best_path:
        print(step)

if __name__ == "__main__":
    main()
