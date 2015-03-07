# Evaluation: Compare sqlite to non-sql
# Evaluate use of labeling vs non labeling
# Evaluate edge cases, wierd ones, loops, unlabelled
# SQLite installed by default?
# looked at sqlalchemy and Django.model but were not good enough
# Include software engineering books
# Testing must include white + black box testing
# reevaluate requirements
# consider my tasks in context of requirements
# design needs architecture diagrams
# link design diagrams + docs with requirements
# Do so in a shareable form. Images from board vs office drawn things.
# scratch pad

# Talk about how python was put on me. Compare + contrast with Ruby.
# Use ruby utilities to generate testing data to rub it in.

# Game knows or throws when it is complete.

from main import *
g = Game.from_file("example_kb_2.txt")
p = Proponent(g)
o = Opponent(g)
p.has_to_be("b")
o.concede("d")
