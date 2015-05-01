# This project implements the Grounded Discussion Game.

As the user you can play against other humans, a single automated opponent, a
single automated proponent, or let them fight each other!

## File manifest

/gregory_myers
 |- argument.py
 |- game.py
 +- generator/
       |- digraph_gen.rb   run with "ruby digraph_gen.rb" to generate test graphs.
 |- graphs/                generated graphs from digraph_gen are placed here.
 |- labelling.py
 |- main.py                main file, run with "python3 main.py". See user manual.
 |- main_test.py           "python3 -m unittest discover -p '\''*_test.py'\''" (retired tests)
 |- player.py
 |- results/               results from runner.rb processing graphs/ placed here.
 |- runner.rb              run with "ruby runner.rb" to run all files in graphs/ and record output to results/

## Installation

1) Install Python3.4 and Ruby (preferrably 2.1 but 1.9 should work, but untested)
2) Run
3) That's it! No dependencies! No PIPs! No Gems! No Easy_Install! No VENV!
