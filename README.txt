Write your own engines using MCTS.

Example:
python reversi.py -a greedy -b random
python reversi.py -a greedy -b random -t 30 -v
python reversi.py -a human -b greedy -t 30

python reversi.py -a MCTS4 -b greedy

python reversi.py -a simple2 -b MCTS4
python reversi.py -a MCTS4 -b MCTS5 -v
python reversi.py -a MCTS4 -b random

python reversi.py -a greedy -b MCTS2

for ((i=0; i<=100; i++)) do python reversi.py -a greedy -b random; done

for ((i=0; i<=20; i++)) do python reversi.py -a MCTS -b MCTS4; done

python reversi.py -a MCTS -b MCTS4



python reversi.py -a myPlayer -b random


python reversi.py -a simple2 -b m12


ÐòÁÐ»¯