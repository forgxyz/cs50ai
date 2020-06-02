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
    # both methods use this transition model
    # take a page as input
    pages, links = len(corpus.keys()), len(corpus[page])
    rand = (1 - damping_factor) / pages # to be applied to all pages
    inline = (damping_factor / links) if links > 0 else damping_factor
    # probability of next page being a link vs random page
    distribution = {}
    for pg in corpus.keys():
        distribution[pg] = rand
        if pg in corpus[page]:
            distribution[pg] += inline
    # return probability distribution of next page
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # pick an initial page at random
    page = list(corpus)[random.randint(0, len(corpus.keys()) - 1)]
    visits = {pg: 0 for pg in corpus.keys()}
    for i in range(n):
        # keep track of surfer's moves
        visits[page] += 1
        # make next step based on the distribution
        distribution = transition_model(corpus, page, damping_factor)
        population, weights = list(distribution.keys()), list(distribution.values())
        page = random.choices(population, weights=weights)[0]

    # return distribution of what pages we actually went to (their rank)
    check = 0
    for key, value in visits.items():
        visits[key] = value/10000
        check += visits[key]
    print(check == 1)
    return visits


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus.keys())

    # set initial values
    ranks = {pg: 1 / N for pg in corpus.keys()}

    # begin iterative loop
    while True:
        for page in corpus.keys():
            rank = pagerank(page, ranks, corpus, damping_factor, N)
            if rank != True:
                return ranks


def pagerank(page, ranks, corpus, damping_factor, N):
    # randomly choose a page with probability (1 - d)/N
    rando = (1 - damping_factor) / N
    # I is the set of all links i that lead to current page p
    # we determine this if current page is present in any page's corpus.values() list
    I = [pg for pg, links in corpus.items() if page in links]
    # iterate through body of links and sum probabilities in sigma
    sigma = 0
    for i in I:
        probability = ranks[i]
        numLinks = len(corpus[i])
        sigma += (probability/numLinks)
    follow = damping_factor * sigma
    pr = rando + follow
    if abs(pr - ranks[page]) < .001:
        return ranks
    ranks[page] = pr
    return True

    # break only when all pagerank value change by less than .001
    # so, maybe keep a list of False values the length of the pages. When all are flipped to True, it ends


if __name__ == "__main__":
    main()
