import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = dict()

    # per crawl(), corpus will not include link to itself or duplicates
    # load probability distribution with chance of randomly selecting a page
    for link in corpus:
        distribution[link] = (1 - damping_factor) / len(corpus)

    # add odds surfer choose a link on the page
    for link in corpus[page]:
        # add % chance they choose a link on page
        distribution[link] += damping_factor / len(corpus[page])

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # create dict to be returned
    pagerank = dict()
    for page in corpus.keys():
        pagerank[page] = 0

    # sample page n times and record in pagerank
    for i in range(n):
        if i == 0:
            # first sample: choose a page a random
            page = random.choice(list(corpus.keys()))

        # for every sample, record the choice
        pagerank[page] += 1/n
        distribution = transition_model(corpus, page, damping_factor)

        # select next page based on probability distribution from transition_model
        page = random.choices(list(distribution.keys()), weights=list(distribution.values()))[0]

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # start with equal ranks
    pagerank, check = dict(), dict()

    for page in corpus.keys():
        pagerank[page] = 1 / len(corpus.keys())
        check[page] = False

    while True:
        # iterate through corpus until convergence
        for p in corpus.keys():
            # iterate through all pages I that link to current page p
            # so will need list, based on corpus, of all the pages that have a link to p in corpus.values()
            incoming = []
            for k, v in corpus.items():
                if p in v:
                    incoming.append(k)

            sum = 0
            # then while iterating through those, recursively call iterate_pagerank again
            # this isn't recursion ... it's just calling the static pagerank of i ...
            for i in incoming:
                sum += (pagerank[i] / len(corpus[i]))

            pr = ((1 - damping_factor) / len(corpus.keys())) + (damping_factor * sum)

            # when the pagerank changes < .001, we have reached convergence and should return a dict rather than a value
            if abs(pagerank[p] - pr) < .001:
                check[p] = True
            pagerank[p] = pr

            # return only when all converge
            if False not in check.values():
                return pagerank


if __name__ == "__main__":
    main()
