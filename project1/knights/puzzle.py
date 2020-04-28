from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
knowledge0 = And(
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    # A says "I am both a knight and a knave."
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(AKnave, Not(And(AKnight, AKnave))),
)

# Puzzle 1
knowledge1 = And(
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    # A says "We are both knaves."
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave)))
    # B says nothing.
)

# Puzzle 2
knowledge2 = And(
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    # A says "We are the same kind."
    Implication(
        AKnight,
        And(Or(And(AKnight, BKnight), And(AKnave, BKnave)), Not(And(And(AKnight, BKnave), And(AKnave, BKnave))))
    ),
    Implication(
        AKnave,
        Not(And(Or(And(AKnight, BKnight), And(AKnave, BKnave)), Not(And(And(AKnight, BKnave), And(AKnave, BKnave)))))
    ),
    # B says "We are of different kinds."
    Implication(
        BKnight,
        Not(And(Or(And(AKnight, BKnight), And(AKnave, BKnave)), Not(And(And(AKnight, BKnave), And(AKnave, BKnave)))))
    ),
    Implication(
        BKnave,
        And(Or(And(AKnight, BKnight), And(AKnave, BKnave)), Not(And(And(AKnight, BKnave), And(AKnave, BKnave))))
    )
)

# Puzzle 3
knowledge3 = And(
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    And(Or(CKnight, CKnave), Not(And(CKnight, CKnave))),
    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    # Or(AKnight, AKnave),
    # Or(Implication(AKnight, AKnave), Implication(AKnave, AKnight)),
    # B says "A said 'I am a knave'."
    Implication(BKnight, Or(Implication(AKnight, AKnave), Implication(AKnave, AKnight))),
    Implication(BKnave, AKnight),
    # B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, CKnight),
    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, AKnave)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
