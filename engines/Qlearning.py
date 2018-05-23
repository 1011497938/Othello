from __future__ import absolute_import
from engines import Engine
from copy import deepcopy
import time
from math import sqrt, log
from reversi import winner
import random

# import pickle
try:
    import cPickle as pickle
except ImportError:
    import pickle

from board import Board

mainColor = -1 #caclue V as -1

S = dict()

sideAngleValue = [
    [100, -5, 10,  5,  5, 10, -5,100],
    [ -5,-45,  1,  1,  1,  1,-45, -5],
    [ 10,  1,  3,  2,  2,  3,  1, 10],
    [  5,  1,  2,  1,  1,  2,  1,  5],
    [  5,  1,  2,  1,  1,  2,  1,  5],
    [ 10,  1,  3,  2,  2,  3,  1, 10],
    [ -5,-45,  1,  1,  1,  1,-45, -5],
    [100, -5, 10,  5,  5, 10, -5,100]
]

learning_rate=0.3
reward_decay=0.9 
e_greedy=0.5

def board_hash(board, color):
    s = ""
    for x in range(4):
        total = 0
        for y in range(8):
            total = total * 3 + board.pieces[2*x][y] + 1
        for y in range(8):
            total = total * 3 + board.pieces[2*x+1][y] + 1
        s += str(total)

    s += str(color + 1)
    return s

def create_and_link_node(action, parentHashValue, color, board):
    hashValue = board_hash(board, color)

    if not hashValue in S:
        S[hashValue] = Node(board, color, hashValue)
        # print("sad")
    # else:
        # print("lucky")

    S[parentHashValue].childrens[hashValue] = action
    S[hashValue].linkToParent(action, parentHashValue)
    # print(S)
    # print(hashValue)
    
    return S[hashValue]

def create_node(color, board):
    hashValue = board_hash(board, color)
    if not hashValue in S:
        S[hashValue] = Node(board, color, hashValue)
        # S[hashValue].exapnd()
    return S[hashValue]

class Node:
    def __init__(self, board, color, boardHashValue):
        self.parents = {}
        
        self.childrens = {}

        self.board = deepcopy(board)
        self.remain_action = self.board.get_legal_moves(color)

        self.hashValue = boardHashValue
        self.color = color #color go now

        # self.important = False
        
        self.V = 0

    def exapnd(self):
        for action in self.remain_action:
            self._append(action)

    def _get_result(self):
        if winner(self.board)[0] == 0:
            return 0
        elif winner(self.board)[0] == mainColor:
            return 1
        else:
            return -1  

    def get_board(self):
        return deepcopy(self.board)

    # need rewrite
    def _get_best_action(self):
        best_children = max(self.childrens.items(), key=lambda child: S[child[0]].V)

        # print("now succeed rate:")
        # print(S[best_children[0]].V)
        # print(len(S))
        # S[best_children[0]].board.my_display()

        return  best_children[1]

    def _get_worst_action(self):
        best_children = min(self.childrens.items(), key=lambda child:  S[child[0]].V)

        # print("now succeed rate:")
        # print(1-S[best_children[0]].V)
        # print(len(S))
        # S[best_children[0]].board.my_display()

        return  best_children[1]

    def _eval_r(self,action):
        board = self.get_board()
        board.execute_move(action, self.color)

        reward = 0
        for x in range(8):
            for y in range(8):
                if board[x][y]==self.color:
                    reward += sideAngleValue[x][y]

        return reward
        

    def _tree_policy(self):
        if self.remain_action:
            if random.random() < e_greedy:
                return max( self.remain_action, key=lambda action: self._eval_r(action))
                # return max( self.remain_action, key=lambda chessPieces: sideAngleValue[chessPieces[0]][chessPieces[1]])
                # return max( self.remain_action, key=lambda chessPieces: sideAngleValue[chessPieces[0]][chessPieces[1]])
            else:
                return random.choice(self.remain_action)
        else:
            return None

    def _simulateOnce(self):
        action = self._tree_policy()
        if action is not None:
            childrenNode = self._append(action)
            childrenNode._simulateOnce()
        else:
            return True
        return False

    def linkToParent(self, action, parentHashValue):
        self.parents[parentHashValue] = action
        if len(self.remain_action)==0 and len(self.childrens)==0:
            self.V = self._get_result()
            # self._end_back_forward(result)
            self._back_forward()
        # else:
        #     self._back_forward()
        # return

    # def _end_back_forward(self, reward):
    #     parents = self.parents
    #     if len(parents) > 0:
    #         for hashValue in parents:

    #             action = S[hashValue].childrens[self.hashValue]
    #             if action in S[hashValue].remain_action:
    #                 S[hashValue].remain_action.remove(action)

    #             S[hashValue].V = reward
    #             S[hashValue]._back_forward()


    # there is something wrong

    def _back_forward(self):
        isTerminal = len(self.remain_action)==0
        parents = self.parents
        if len(parents) > 0:
            for hashValue in parents:

                if isTerminal:
                    action = S[hashValue].childrens[self.hashValue]
                    if action in S[hashValue].remain_action:
                        S[hashValue].remain_action.remove(action)

                if len(S[hashValue].childrens)==1 and len(S[hashValue].remain_action)==0:
                    S[hashValue].V = self.V
                else:
                    predict = S[hashValue].V
                    maxHashValue = max( S[hashValue].childrens.items(), key=lambda child: S[child[0]].V)[0]

                    target = reward_decay * S[maxHashValue].V

                    S[hashValue].V += learning_rate * (target - predict)
                S[hashValue]._back_forward()



    def _append(self, action):
        board = self.get_board()
        board.execute_move(action, self.color)
        return create_and_link_node(action, self.hashValue, self.color*-1, board)

   
def nodeToDict(N):
    D = {}
    D["V"] = N.V
    D["CO"] = N.color
    D["B"] = N.board.pieces
    D["R"] = N.remain_action
    D["H"] = N.hashValue
    D["P"] = N.parents
    D["CH"] = N.childrens

    return D

def dictToS(D):

    hashValue = D["H"]
    board = Board()
    board.pieces = D["B"]


    S[hashValue] = Node(board, D["CO"], hashValue)
    S[hashValue].V = D["V"]
    S[hashValue].remain_action = D["R"]
    S[hashValue].hashValue =  hashValue
    S[hashValue].parents = D["P"]
    S[hashValue].childrens = D["CH"]


class MCTSEngine(Engine):
    def get_move(self, board, color, move_num=None, time_remaining=None, time_opponent=None):
        # player = {-1 : "Black", 1 : "White"}
        # print(player[color] + " go now")
        self.color = color
        if time_remaining > 200 or time_remaining is None:
            time = 55
        else:
            print("time will run off")
            time = time_remaining / 2
        return self.UCT_search(board, time)

    def UCT_search(self, board, cal_time):
        root = create_node(self.color, board)

        begin = time.time()
        count = 0
        while time.time() - begin < cal_time:
            # print("simulateOnce")
            isOver = root._simulateOnce()
            if isOver:
                # print("over")
                break
            count +=  1
        print ("q learning cacluted " + str(count) + " times")
        if mainColor == self.color:
            return root._get_best_action()
        else:
            return root._get_worst_action()


    # def __init__(self):
    #     print("start load")
    #     f = open("./temp9","rb")
    #     p = pickle.load(f)
    #     for key in p:
    #         dictToS(p[key])
    #     f.close()
    #     print("load cache, length:" + str(len(S)))
        
        # f = open("out", "w")
        # for hashValue in S:
        #     s = S[hashValue]
        #     print(s.hashValue, file = f)
        #     print(s.board.toString(), file = f)
        #     print("parents: " + str(s.parents), file = f)
        #     print("childrens: " + str(s.childrens), file = f)
        #     # print("V: " + str(s.V), file = f)
        #     print("remain_action: " + str(s.remain_action), file = f)
        #     print("\n\n", file = f)
        # print("end")
        # f.close()
        # while True:
        #     pass

    # def close(self):
    #     p = {}
    #     for hashValue in S:
    #         p[hashValue] = nodeToDict(S[hashValue])
    #     f = open("./temp12","wb")
    #     pickle.dump(p,f,2)
    #     f.close()
    #     print("write cache, length:" + str(len(p)))

    #     f = open("out", "w")
    #     for hashValue in S:
    #         s = S[hashValue]
    #         print(s.hashValue, file = f)
    #         print(s.board.toString(), file = f)
    #         print("parents: " + str(s.parents), file = f)
    #         print("childrens: " + str(s.childrens), file = f)
    #         print("V: " + str(s.V), file = f)
    #         print("remain_action: " + str(s.remain_action), file = f)
    #         print("\n\n", file = f)
    #     print("end")
    #     f.close()
# 
engine = MCTSEngine