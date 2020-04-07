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
        print(f"path: {path}")
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1}({path[i][1]}) and {person2}({path[i + 1][1]}) starred in {movie}({path[i + 1][0]})")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    frontier = QueueFrontier()
    initial_state = Node(source, None, None)

    frontier.add(initial_state)
    explored = {}

    while True:
        if len(frontier.frontier) == 0:
            print("DEBUG: Frontier empty...")
            return None
        suspect = frontier.frontier[0]
        print(f"DEBUG: exploring {suspect.state}...")
        # get every co-star for the current node
        neighbors = neighbors_for_person(suspect.state)
        print(f"DEBUG: neighbors: {neighbors}")
        if len(neighbors) == 0:
            print("DEBUG: No neighbors...")
            return None

        for movie_id, person_id in neighbors:
            # do not re-explore an actors neighbors
            print(f"DEBUG: now scanning {movie_id, person_id}...")
            # if person_id in explored:
            #     print(f"DEBUG: {person_id} explored, ignoring...")
            #     break

            if person_id == target:
                # target MAY appear multiple times in this set, depending on the movie...
                path = [(movie_id, target)]
                    if suspect.parent == None:
                        while True:
                        break
                    # path.append(movie_id that ties together source and next actor, next_actor_id)
                    path.append((suspect.action, suspect.state))
                    print(f"DEBUG: added to path {suspect.action, suspect.state}")
                    # overwrite suspect with the next parent up the chain for the loop
                    suspect = explored[suspect.parent]
                path.reverse()
                return path

            # if not target & not in frontier, add to the frontier
            # ([person, movies set], movie linking person to parent, parent)
            if not frontier.contains_state(person_id):
                print(f"DEBUG: {person_id} not in frontier, adding...")
                frontier.add(Node(person_id, suspect.state, movie_id))

        # pop suspect
        print(f"DEBUG: popping {suspect.state}")
        explored[suspect.state] = frontier.remove()
        print(f"DEBUG: explored {len(explored)} states")


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
        for actor_id in movies[movie_id]["stars"]:
            if actor_id != person_id:
                neighbors.add((movie_id, actor_id))
    return neighbors


if __name__ == "__main__":
    main()
