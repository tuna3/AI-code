from __future__ import print_function
import numpy as np
from collections import deque
import time
from operator import itemgetter



class Fruit_Rage:
    def __init__(self,N ,P , rt):
        self.N =N
        self.P =P
        self.remaining_time =rt
        self.board = np.zeros((N+2,N+2),dtype=np.int32)
        self.depth = 3
        self.no_elements =0
        self.counter =0
        self.start_time = time.clock()
        self.set_flag =True

        for i in range(0,N+2):
            self.board[i][0]   =-1
            self.board[0][i]   =-1
            self.board[N+1][i] =-1
            self.board[i][N+1] =-1


    def gravity(self,covered,board):
        temp_board =np.copy(board)
        for j in range(1, self.N + 1):
            i = self.N + 1
            jump = 0
            while i > 0:
                if covered[i][j] == True:
                    start = i
                    while covered[i][j] == True:
                        i = i - 1
                    # print(' if covered ',i)
                    end = i
                    jump += start - end
                while covered[i][j] == False and i > 0:
                    if jump:
                        temp_board[i + jump][j] = board[i][j]
                    i = i - 1
            for i in range(1, jump + 1):
                temp_board[i][j] = -1

        return temp_board

    def generate_moves_1(self,board):
        visited = np.zeros((self.N + 2, self.N + 2), dtype=bool)
        moves =[]
        for x in range(1,self.N+1):
            for y in range(1,self.N+1):
                if visited[x][y] == False and board[x][y]!=-1 :
                    covered = np.zeros((self.N + 2, self.N + 2), dtype=bool)
                    value = board[x][y]
                    Q = deque()
                    Q.append((x, y))
                    count = 0
                    visited[x][y] = True
                    while len(Q) != 0:
                        count = count + 1
                        parent = Q.popleft()
                        i = parent[0]
                        j = parent[1]
                        covered[i][j] = True
                        if board[i + 1][j] == value and visited[i + 1][j] == False:
                            Q.append((i + 1, j))
                            visited[i + 1][j] = True
                        if board[i - 1][j] == value and visited[i - 1][j] == False:
                            Q.append((i - 1, j))
                            visited[i - 1][j] = True
                        if board[i][j + 1] == value and visited[i][j + 1] == False:
                            Q.append((i, j + 1))
                            visited[i][j + 1] = True
                        if board[i][j - 1] == value and visited[i][j - 1] == False:
                            Q.append((i, j - 1))
                            visited[i][j - 1] = True

                    moves.append((count * count, x, y, covered))
        moves.sort(key=itemgetter(0), reverse=True)
        if len(moves) > 20:
            n_trunc = len(moves) - 20
            del moves[-n_trunc:]
        #print(moves)
        return moves

    def compute_depth(self):
        t =time.clock()-self.start_time
        depth =3
        if self.no_elements <25 :
            if rem_time < 5:
                depth =3
            else:
                depth = 6
        elif self.no_elements <100:
            if rem_time < 5:
                depth =2
            else:
                depth = 4
        elif self.no_elements<225:
            if rem_time<5:
                depth =1
            else : depth =3
        else:
            if rem_time<5:
                depth =1
            else :
                depth =3
        return depth


    def alpha_beta_pruning(self,depth,seed,alpha,beta,parent_score, parent_board):

        best_row =-1
        best_col =-1
        best_board =parent_board
        score =-1
        current_score =-1

        nextMoves = self.generate_moves_1(parent_board)
        if len(nextMoves) ==0 :
            val =self.N*self.N
            if val >300:
                val =300
            if parent_score >0:
                return (parent_score +val,best_row,best_col,best_board,current_score)
            return (parent_score - val, best_row, best_col, best_board, current_score)


        if depth ==0:
            sum = 0
            i = 0
            alpha =1
            for move in nextMoves:
                if i<2:
                    if i % 2 == 0:
                        sum = sum + move[0]*alpha
                    else:
                        sum = sum - move[0]*alpha
                    alpha = alpha * 0.9
                    i = i + 1
            if seed ==True:
                return (parent_score +sum, best_row, best_col, best_board, current_score)
            return (parent_score - sum, best_row, best_col, best_board, current_score)

        if self.set_flag == False:
            depth =self.compute_depth()
            self.set_flag =True



        counter =0
        for move in nextMoves:
            self.counter =self.counter +1
            counter =counter +1
            current_board =self.gravity(move[3],parent_board)

            if seed ==True:
                score = self.alpha_beta_pruning(depth-1,False,alpha,beta,parent_score+move[0],current_board)[0]
                #print(" this move cost True ", move[0], parent_score)
                if score > alpha:
                    #print('score > alpha',score)
                    alpha=score
                    best_row=move[1]
                    best_col=move[2]
                    best_board= np.copy(current_board)
                    current_score =move[0]


            else:
                score = self.alpha_beta_pruning(depth - 1, True, alpha, beta,parent_score-move[0], current_board)[0]

                #print(" this move cost False ", move[0],parent_score)
                if score<beta:
                    beta=score
                    best_row=move[1]
                    best_col=move[2]
                    best_board =np.copy(current_board)
                    current_score =move[0]

            if alpha>=beta:
                break;

        if seed ==True:
            return (alpha,best_row,best_col,best_board,current_score)
        else :
            return (beta,best_row,best_col,best_board,current_score)

    def game(self):
        score = self.alpha_beta_pruning(depth =3,seed =True,alpha=-10000,beta=+10000,parent_score=0,parent_board=self.board)
        print ('result',score[0],score[1],score[2],score[3],score[4])
        f = open('output.txt', 'w')
        str2 = str(N)+'\n'+str(N)+'\n'
        f.write(str2)
        col = str(score[2] - 1)
        col = col + str(score[1]) + '\n'
        f.write(col)
        str1 =''
        for i in range(1, self.N + 1):
            for j in range(1, self.N + 1):
                if score[3][i][j] == -1:
                    val = '*'
                else:
                    val = str(score[3][i][j])
                if j == N:
                    val = val + '\n'
                str1 = str1 + val
        f.write(str1)
        f.close()
        return


if __name__ == "__main__":

    with open("input.txt",'r') as f:
        line=f.readline()
        Nval=line.rstrip()
        N =(int)(Nval)
        line=f.readline()
        Pval=line.rstrip()
        P=int(Pval)
        line=f.readline()
        r_t =line.rstrip()
        rem_time =float(r_t)
        fr=Fruit_Rage(N, P, rem_time)
        print(N,P,rem_time)

        i = 1
        j = 1

        delimiter = [' ', '\n', '\r']
        while (i < N+1):
            j = 1
            while (j < N+1):
                val = f.read(1)
                if val in delimiter:
                    continue
                if val == '*':
                    fr.board[i][j] =-1
                    j =j+1
                    continue
                no = int(val) - int(0)
                if no >= 0 and no <= 9:
                    fr.board[i][j] = no
                    fr.no_elements = fr.no_elements +1
                j = j + 1
            i = i + 1

        fr.game()
        print(fr.counter)

    print (time.clock())

