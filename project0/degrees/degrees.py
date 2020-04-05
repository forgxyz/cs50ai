import csv
import sys
from time import sleep # for debugging. remove later

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                # The names dictionary is a way to look up a person by their name:
                # it maps names to a set of corresponding ids
                #(because it’s possible that multiple actors have the same name).
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    frontier = QueueFrontier()
    # source and target are person_ids
    # get {source: {movie_set}}
    initial_state = Node([source, people[source]['movies']], None, None)
    frontier.add(initial_state)

    # list of people_ids that have been explored
    explored_ids = {}
    # list for return value
    path = []

    # loop: check each movie in movie_set
    while True:
        print(f"DEBUG: Searching the frontier... node: {frontier.frontier[0].state, frontier.frontier[0].parent, frontier.frontier[0].action}")
        if len(frontier.frontier) == 0:
            # last item removed from frontier, nothing left to explore so there is no solution
            return None

        for movie_id in frontier.frontier[0].state[1]:
            if target in movies[movie_id]['stars']:
                while True:
                    if frontier.frontier[0].parent == None or frontier.frontier[0].parent == source:
                        break
                    print(f"DEBUG: Adding node to path... node: {frontier.frontier[0].state, frontier.frontier[0].parent, frontier.frontier[0].action}")
                    path.append((frontier.frontier[0].action, frontier.frontier[0].parent))
                    frontier.frontier[0] = explored_ids[frontier.frontier[0].parent]
                path.reverse()
                path = path + [(movie_id, target)]
                return path

            for actor_id in movies[movie_id]['stars']:
                if actor_id not in explored_ids.keys() and actor_id != source:
                    frontier.add(Node([actor_id, people[actor_id]['movies']], frontier.frontier[0].state[0], movie_id))
                    print(f"DEBUG: Adding to the frontier... node: {frontier.frontier[-1].state, frontier.frontier[-1].parent, frontier.frontier[-1].action}")

            # for each movie, get {movie: {stars_set}}
                # goal check: if target in stars_set end
                # else add {movie: stars_set} to frontier
        # movie list exhausted, move to next and track the explored node
        try:
            explored_ids[frontier.frontier[0].state[0]] = frontier.remove()
        except IndexError:
            raise Exception(f"{source} has not starred in any movies in this dataset.")

    # path = [(person_id, movie_id), ...]
    # work backwards, up the chain, tracing my way back from the target to the source
    # this current node has: [actor, movies], parent_actor_id, parent_movie_id
    # so, i can take one step back but I'm deleting the nodes so the previous parent data is destroyed
    # explored_ids needs to be nodes, not just actor_ids
    return False


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
