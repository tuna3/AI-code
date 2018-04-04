import random
import numpy as np

def generate_board(board,N):
    for i in range(0, N) :
        for j in range(0,N):
            board[i][j] = random.randint(0, 1)


N =15
Z =np.zeros((N,N),dtype =np.int32)
generate_board(Z,N)
f = open('input.txt', 'w')
str2 = str(N)+'\n'+str(N)+'\n'+'123 \n'
f.write(str2)
str1 = ''.join(str(Z[i][j]) if j!=(N-1) else str(Z[i][j]) + '\n' for i in range(N) for j in range(N))
str1=str1 +'\r\n'
f.write(str1)
f.close()
    #print(str1)
