from __future__ import absolute_import
from engines import Engine
from copy import deepcopy
import time
from math import sqrt, log
from reversi import winner
import random


CONFIDENCE = 0.4
cal_time = 5

class node:
    def __init__(self, action, parent, color, board=None):
        self.parent = parent 
        self.action = action
        self.children = []
        
        self.N = 0
        self.W = 0  
        if board is None:
            self.board = self._greedy_trans(parent.board, color)
        else:
            self.board = board

        self.remain_move = self.board.get_legal_moves(color)

    def _greedy_trans(self, board, color):
        newboard = deepcopy(board)
        newboard.execute_move(self.action, color)
        color *= -1
        moves = newboard.get_legal_moves(color)
        if not moves:
            return newboard
        move = max(moves, key=lambda move: self._get_greedy_cost(newboard, color, move))
        newboard.execute_move(move, color)
        return newboard

    def _get_greedy_cost(self, board, color, move):
        newboard = deepcopy(board)
        newboard.execute_move(move, color)
        num_pieces_op = len(newboard.get_squares(color*-1))
        num_pieces_me = len(newboard.get_squares(color))
        return num_pieces_me - num_pieces_op



class MCTSEngine(Engine):
    def get_move(self, board, color, move_num=None, time_remaining=None, time_opponent=None):
        self.color = color
        if time_remaining > 200 or time_remaining is None:
            time = 10
        else:
            time = time_remaining / 2
        return self.UCT_search(board, time)

    def UCT_search(self, board, cal_time):
        root = node(None, None, self.color, board)
        begin = time.time()
        count = 0
        while time.time() - begin < cal_time:
            vl = self.tree_policy(root)
            reward = self.default_policy(vl, self.color)
            self.backup(vl, reward)
            count += 1
        print ("MCTS cacluted " + str(count) + " times")
        for x in range(len(root.children)):
        	print("MCTS " + str(root.children[x].N) + " " + str(root.children[x].W) )
        return self.best_child(root).action

    def best_child(self, v):
        return max(v.children, key=lambda child: child.W/child.N+CONFIDENCE*sqrt(log(v.N)/child.N))

    def backup(self, v, win):
        while v is not None:
            v.N += 1
            v.W += win
            v = v.parent

    def expand(self, v):
        move = random.choice(v.remain_move)
        v.remain_move.remove(move)
        new_child = node(move, v, self.color)
        v.children.append(new_child)
        return new_child

    def default_policy(self, v, color):
        board = deepcopy(v.board)
        temp_color = color
        while not is_terminal(board, temp_color):
            board.execute_move(random.choice(board.get_legal_moves(temp_color)), temp_color)
            temp_color *= -1
        if winner(board)[0] == color:
            return 1
        else:
            return 0

    def tree_policy(self, v):
        while not is_terminal(v.board, self.color):
            if v.remain_move:
                return self.expand(v)
            else:
                v = self.best_child(v)
        return v


def is_terminal(b, color):
    moves = b.get_legal_moves(color)
    if moves:
        return False
    else:
        return True

        

engine = MCTSEngine

