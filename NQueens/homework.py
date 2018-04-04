from __future__ import print_function
import numpy as np
from collections import deque
import time
import random
import math
import threading

class SA:
    def __init__(self,P,N,start_time):
        self.P=P
        self.N=N
        self.Z=np.zeros((N,N),dtype=np.int32)
        self.current_state = []
        self.next_state = []
        self.best_solution=[]
        self.conflicts_best = 0
        self.solution_found =False
        self.temperature = 0
        self.threadinglock = threading.Condition()
        self.start_time = start_time
        self.holes_p =False

    def SAMaster(self):
        t = threading.Thread(name='thread1', target=self.SimulatedAnnealing)
        t2 = threading.Thread(name='thread2', target=self.SAmethod2)
        t.start()
        t2.start()
        res = t.join()
        res1=t2.join()
        if self.solution_found==False:
            fout = open("output.txt", 'w')
            fout.write('FAIL')
            fout.close()

    def read_input_SA(self,Z,f):
        i = 0
        j = 0
        count =0
        delimiter = [' ', '/n', '/r']
        while (i < self.N):
            j = 0
            while (j < self.N):
                val = f.read(1)
                if val in delimiter:
                    continue
                if val == '\n':
                    continue
                no = int(val) - int(0)
                if no >= 0 and no < 3:
                    Z[i][j] = no
                    if no ==0:
                        count=count+1

                j = j + 1
            i = i + 1
        if count<self.P:
            print('here')
            fout = open("output.txt", 'w')
            fout.write('FAIL')
            fout.close()
            self.holes_p = True

        elif count== self.P:
            state=[]
            self.holes_p = True
            for i in range(0,self.N):
                for j in range(0,self.N):
                    if self.Z[i][j]==0:
                        state.append((i,j))
            conflicts = self.conflicts(state)
            if conflicts ==0:
                self.write_solution(state)
                writeResult(self.Z)
            else:
                fout = open("output.txt", 'w')
                fout.write('FAIL')
                fout.close()


    def SAmethod2(self):

        current_state = self.generate_initial_state()
        current_conflict = self.conflicts(current_state)
        max_iteration = 2000000
        for iteration in range(2, max_iteration):
            if time.time() - self.start_time > 260 or self.solution_found==True:
                break
            temperature = 1.0/math.log(iteration)
            next_state = self.generate_next_state(current_state)
            next_conflict = self.conflicts(next_state)
            if next_conflict==0:
                self.threadinglock.acquire()
                self.solution_found=True
                self.conflicts_best =next_state[:]
                self.write_solution(next_state)
                writeResult(self.Z)
                self.threadinglock.release
                return True

            deltaE = next_conflict - current_conflict
            if deltaE < 0 or self.accept(deltaE, temperature):
                current_state = next_state[:]
                current_conflict = next_conflict
                #print('method 2 next_conflict %d'%(next_conflict))
        return False

    def print_solution(self,state):
        temp_board = np.copy(self.Z)
        for k in state:
            temp_board[k[0]][k[1]] =1
        print (np.matrix(temp_board))

    def generate_next_state(self,current_state):
        next_state=[] #check once
        queen_no=random.randint(0,self.P -1)
        #print ('position to be changed',queen_no,current_state[queen_no])
        flag = False
        coord_old = current_state[queen_no]
        while flag == False:
            new_x = random.randint(0,self.N-1) #(current_state[queen_no][0] +random.randint(-1,1))%self.N #random.randint(0,self.N-1)
            new_y = random.randint(0,self.N-1)#(current_state[queen_no][1] +random.randint(-1,1))%self.N #random.randint(0,self.N-1)
            coord_new =(new_x,new_y)
            if coord_new not in current_state and self.Z[new_x][new_y]==0:
                flag = True
                next_state=[k for k in current_state]
                next_state[queen_no]=coord_new
        return next_state

    def generate_initial_state(self):
        i=0
        current_state=[]
        while i<self.P :
            x = random.randint(0,self.N-1)
            y = random.randint(0,self.N-1)
            if self.Z[x][y] ==0 and (x,y) not in self.current_state:
                current_state.append((x,y))
                i=i+1
        #print (len(current_state))
        return current_state

    def conflicts(self,state):
        count =0
        for i in range(0,self.P):
           for j in range(i+1,self.P):
               coord_current = state[i]
               coord_comp = state[j]

               if coord_current[0]==coord_comp[0]:
                   max_c = max(coord_current[1],coord_comp[1])
                   min_c = min(coord_current[1],coord_comp[1])

                   tree=False
                   for k in range(min_c,max_c):
                       if self.Z[coord_current[0]][k] == 2:
                           tree=True
                           break
                   if tree== False :
                       count=count +1

               if coord_current[1]== coord_comp[1]:
                   max_c = max(coord_current[0], coord_comp[0])
                   min_c = min(coord_current[0], coord_comp[0])

                   tree = False
                   for k in range(min_c, max_c):
                       if self.Z[k][coord_current[1]] == 2:
                           tree = True
                           break
                   if tree == False:
                       count = count + 1

               if (coord_current[0]-coord_current[1])== (coord_comp[0]-coord_comp[1]):
                   val =0
                   if coord_current[0]<coord_comp[0]:
                       val =1
                   else:
                      val =-1

                   k =coord_current[0]
                   l =coord_current[1]
                   tree=False
                   while k!=coord_comp[0] :
                       k =k + val
                       l =l + val
                       if self.Z[k][l]==2:
                           tree= True
                           break
                   if tree==False:
                       count =count+1
               if( coord_current[0]+coord_current[1]) ==(coord_comp[0]+coord_comp[1]):
                   val =0
                   if coord_current[0]<coord_comp[0]:
                       val =1
                   else:
                      val =-1
                   k = coord_current[0]
                   l =coord_current[1]
                   tree=False
                   while k!=coord_comp[0]:
                        k =k+val
                        l =l-val
                        if self.Z[k][l]==2:
                            tree =True
                            break
                   if tree==False:
                       count=count+1

        return count

    def write_solution(self,state):
        #print('len of sol %d'%(len(state)))
        for k in state:
            self.Z[k[0]][k[1]] =1
            #print(k)

    def SimulatedAnnealing(self):
        temperature = self.P*10
        cooling_factor = 0.99
        current_state = self.generate_initial_state()
        current_conflict = self.conflicts(current_state)
        stabilizing_temp =35
        #print('method1')
        if current_conflict == 0:
            self.write_solution(current_state)
            writeResult(self.Z)
            return
        while temperature > 0.001 and (time.time()-self.start_time)< 260 and self.solution_found==False :
            for energy in range(int(stabilizing_temp)):
                next_state =self.generate_next_state(current_state)
                next_conflict = self.conflicts(next_state)
                if next_conflict == 0:
                    self.threadinglock.acquire()
                    #print('lock acquired')
                    self.solution_found = True
                    self.conflicts_best = next_state[:]
                    self.write_solution(self.next_state)
                    writeResult(self.Z)
                    self.threadinglock.release()
                    return True
                deltaE = next_conflict -current_conflict
                if deltaE<0 or self.accept(deltaE,temperature):
                    self.current_state=self.next_state[:]
                    current_conflict=next_conflict
                    #print('method 1 %d'%(next_conflict))
            temperature = temperature*cooling_factor
            stabilizing_temp =stabilizing_temp *1.005

        return False


    def accept(self,deltaE, temperature):
        val1 =-float(deltaE)/temperature
        val = math.exp(val1)
        #print(val,val1)
        if val>random.uniform(0,1):
            return True
        else:
            return False






class DFS:
    def __init__(self, N,P):
        self.P =P
        self.N =N
        self.Z =np.zeros((N,N),dtype=np.int32)


    def depthSearch(self):
        row=0
        col=0

        if self.dfssolver(row,col,self.P) :
            writeResult(self.Z)
            return True
        else :
            fout = open("output.txt", 'w')
            fout.write('FAIL')
            fout.close()
            #print('FAIL')
            return False


    def validChild(self,row,col):
        i =row
        j=col
        while j>=0:
            if self.Z[row][j] ==2:
                break
            if self.Z[row][j]==1:
                return False
            j=j-1

        i=row
        j=col


        while i >=0 and j>=0:
            if self.Z[i][j] ==2:
                break
            if self.Z[i][j]==1:
                return False
            i =i-1
            j=j-1

        i=row
        j=col

        flag=True
        while i<self.N and j>=0 :
            if self.Z[i][j]==2:
                break
            if self.Z[i][j]==1:
                return False
            i =i+1
            j=j-1
        return True






    def dfssolver(self,row,col,P):
        if P==0:
            return True
        if P>0 and col >= self.N:
            return False
        for i in range(row,self.N):
            if self.Z[i][col] ==2:
                continue
            if self.validChild(i,col):
                self.Z[i][col]=1
                P = P-1
                #print(np.matrix(self.Z))
                j=i+1
                while j<self.N:
                    if self.Z[j][col] ==2:
                        j=j+1
                        break
                    j =j+1
                if j< self.N:
                    if self.dfssolver(j,col,P):
                        return True
                if self.dfssolver(0,col+1,P):
                    return True

                self.Z[i][col]= 0
                P = P +1

        if self.dfssolver(0,col+1,P):
            return True
        return False

class Struct:
    def __init__(self,P,l):
        self.P=P
        self.l=[x for x in l]


class Solver:
    def __init__(self,N, P):
        self.N=N
        self.P=P
        self.Z =np.zeros((N,N),dtype=np.int32)
        self.Q = deque()
        self.flag_sol= False
        self.solution_state = None

    def checkifvalid(self,state,row,col):
        temp_board = np.copy(self.Z)
        for k in state.l:
            temp_board[k[0]][k[1]] =1
        #print(np.matrix(temp_board))
        i=col
        while i>=0:
            if temp_board[row][i] ==1:
                return False
            if temp_board[row][i] ==2:
                break;
            i=i-1


        i = row
        j = col

        while i>=0 and j>=0:
            if temp_board[i][j]==1:
                return False
            if temp_board[i][j]==2:
                break;
            i=i-1
            j=j-1

        i =row
        j=col

        while i<N and j >=0:
            if temp_board[i][j]==1:
                return False
            if temp_board[i][j]==2:
                break;
            i =i +1
            j =j-1
        return True





    def find_children(self,state):
        k =len(state.l)
        k =k-1
        current_row = state.l[k][0]
        current_col = state.l[k][1]
        no_sol =0
        #print(' finding children of (%d,%d)'%(current_row,current_col))
        i =current_row +1
        while(i<self.N):
            if self.Z[i][current_col]==2:
                break
            i=i+1
        i=i+1

        if i<self.N:
            while(i<self.N):
                if self.Z[i][current_col]==0:
                    no_sol =no_sol +1
                    if self.checkifvalid(state,i,current_col):
                        child_state=Struct(state.P-1,state.l)
                        child_state.l.append((i,current_col))
                        if child_state.P==0:
                            self.flag_sol = True
                            self.solution_state=child_state

                        self.Q.append(child_state)
                i=i+1
        current_col =current_col + 1
        while(current_col<N and no_sol <=(2*self.N)):
            for j in range(0, N):
                if self.Z[j][current_col] == 0:
                    no_sol =no_sol+1
                    #print("checking for ", j, current_col+1,state.P-1)
                    if self.checkifvalid(state, j, current_col):
                        #print(' inserted in queue ', j, current_col)
                        child_state = Struct( state.P - 1, state.l)
                        child_state.l.append((j, current_col ))
                        if child_state.P == 0:
                            self.flag_sol = True
                            self.solution_state = child_state
                        self.Q.append(child_state)
            current_col =current_col +1




    def print_solution(self, state):
        for k in state.l:
            self.Z[k[0]][k[1]] =1
        print(np.matrix(self.Z))


    def BFS(self):
        col =0
        no_sol =0
        while(col<self.N and no_sol<2*self.N):
            for i in range(self.N):
                if self.Z[i][col]==2:
                    continue
                l =[]
                l.append((i,col))
                state =Struct(P-1,l)
                self.Q.append(state)
                no_sol = no_sol+1
            col = col+1
        while(len(self.Q)!=0 and self.flag_sol == False):
            current_state= self.Q.popleft()
            self.find_children(current_state)

        if self.flag_sol == False:
            fout = open("output.txt", 'w')
            fout.write('FAIL \r\n')
            fout.close()
        else :
            for k in self.solution_state.l:
                self.Z[k[0]][k[1]] = 1
            writeResult(self.Z)


def read_input(Z,f,N):
    i = 0
    j = 0

    delimiter = [' ', '/n','/r']
    while (i < N):
        j = 0
        while (j < N):
            val = f.read(1)
            if val in delimiter:
                continue
            if val == '\n':
                continue
            no = int(val) - int(0)
            if no >= 0 and no < 3:
                Z[i][j] = no
            j = j + 1
        i = i + 1
    #print('input is \n')
    #print(np.matrix(Z))

def writeResult(Z):
    f = open('output.txt', 'w')
    N = len(Z)
    f.write('OK\n')
    str1 = ''.join(str(Z[i][j]) if j!=(N-1) else str(Z[i][j]) + '\n' for i in range(N) for j in range(N))
    str1=str1 +'\r\n'
    f.write(str1)
    f.close()
    #print(str1)
    return




if __name__ == "__main__":
    time_start = time.time()
    with open("input.txt",'r') as f:
        line =f.readline()
        method=line.rstrip('\n ')
        line=f.readline()
        Nval=line.rstrip()
        N =(int)(Nval)
        line=f.readline()
        Pval=line.rstrip()
        P=int(Pval)

        method_lower = method.lower()
        if method_lower == 'bfs':
            s =Solver(N,P)
            read_input(s.Z,f,N)
            s.BFS()
        elif method_lower=='dfs':
            dfs_solver = DFS(N,P)
            read_input(dfs_solver.Z,f,N)
            dfs_solver.depthSearch()
        else :
            simul = SA(P, N,time_start)
            simul.read_input_SA(simul.Z,f)
            if simul.holes_p ==False:
                simul.SAMaster()
    f.close()
