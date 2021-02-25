import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        # P(t | g2)
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        # P(t | g1)
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        # P(t | g0)
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # # compute unconditional probability of showing trait, using given distributions
    # # per conditioning P(trait) = P(trait | gX)*P(gX) where gX represents num genes
    # PROBS['trait']['unconditional'] = {True: 0, False: 0}
    # for gene in PROBS['gene']:
    #     PROBS['trait']['unconditional'][True] += PROBS['gene'][gene] * PROBS['trait'][gene][True]
    #     PROBS['trait']['unconditional'][False] += PROBS['gene'][gene] * PROBS['trait'][gene][False]
    #
    # # use marginalization to determine P(g | t) = P(g, t) / P(t) and P(g, t) = P(g)*P(t | g)
    # # so P(g | t) = P(g)*P(t | g) / P(t)
    # PROBS['gene']['conditional'] = {
    #     0: {'trait': 0, 'no_trait': 0},
    #     1: {'trait': 0, 'no_trait': 0},
    #     2: {'trait': 0, 'no_trait': 0},
    # }
    #
    # for gene in PROBS['gene']:
    #
    #     # necessary because i added 'conditional' to gene
    #     if type(gene) is not int:
    #         break
    #     PROBS['gene']['conditional'][gene]['trait'] = (PROBS['gene'][gene] * PROBS['trait'][gene][True]) / PROBS['trait']['unconditional'][True]
    #     PROBS['gene']['conditional'][gene]['no_trait'] = (PROBS['gene'][gene] * PROBS['trait'][gene][False]) / PROBS['trait']['unconditional'][False]
    #
    # # TODO ... that was a lot of setup, i should move that out of this function
    # # yea that's bc this is not the way to do this...


    # they are all sets so, to infer the no_gene and no_trait, can use set subtraction / difference()
    # i could probably do if person not in have_trait but w/e
    no_genes = set(people) - one_gene - two_genes
    no_trait = set(people) - have_trait
    odds = 1
    # loop thru available people and compute joint probability of situation
    for person in people:

        if person in no_genes:

            if people[person]['mother'] is not None and people[person]['father'] is not None:
                odds *= PROBS['gene'][0]
            else:
                # child
                # TODO - this is where i am having some conceptual trouble
                # if child and testing for 0 genes, what info do we know / can we pull about parents at this point?
                # parents could be one of 9 genetic combinations, is that just a loop? a superset?

            if person in have_trait:
                odds *= PROBS['trait'][0][True]
            else:
                odds *= PROBS['trait'][0][False]

            # UNLESS it is child then gene is dependent on parents and we cannot use the given unconditional
            # P(t | g) does not need to change


        if person in one_gene:
            odds *= PROBS['gene'][1]
            if person in have_trait:
                odds *= PROBS['trait'][1][True]
            else:
                odds *= PROBS['trait'][1][False]

        if person in two_genes:
            odds *= PROBS['gene'][2]
            if person in have_trait:
                odds *= PROBS['trait'][2][True]
            else:
                odds *= PROBS['trait'][2][False]

    return odds


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # TODO
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    main()
