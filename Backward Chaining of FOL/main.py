from __future__ import print_function
import numpy as np



class Predicates:
    def __init__(self):
        self.positive=[]
        self.negative=[]


class Kbase:
    def __init__(self):
        self.pred ={}
        self.kb =[]
        self.resolvents=[]
        self.no_kb =0
        self.found_solution =False
        self.solution =False
        self.v_count =2

    def store_info(self,clause, query_no):
        parts = clause.split('|')
        for part in parts:
            part = part.rstrip(' ')
            part = part.lstrip(' ')
            lpart =part.lstrip('~')
            lpartl= lpart.split('(')
            partl =part.split('(')
            lpart =lpartl[0]
            part =partl[0]

            if self.pred.has_key(lpart):
                if part ==lpart:
                    pl=self.pred.get(part)
                    pl.positive.append(query_no)
                    self.pred[part] =pl
                else:
                    pl = self.pred.get(lpart)
                    pl.negative.append(query_no)
                    self.pred[lpart] = pl
            else:
                self.pred[lpart] = Predicates()
                if part == lpart:
                    pl = self.pred.get(part)
                    pl.positive.append(query_no)
                    self.pred[part] = pl
                else:
                    pl = self.pred.get(lpart)
                    pl.negative.append(query_no)
                    self.pred[lpart] = pl



    def print_kb(self):
        for i in self.pred:
            #print (i, self.pred[i])
            k =self.pred[i]
            print(i,k.positive,k.negative)


    def evaluate_query(self,query):
        query = query.strip('\n')
        part = query.strip('')
        lpart = query.lstrip('~')
        if lpart ==part:
            lpart ='~'+lpart
        val =self.standardize(lpart,len(self.kb))

        self.kb.append(val)
        print(len(self.kb))

        visited = np.zeros(len(self.kb),dtype =np.int8 )
        i =len(self.kb)-1
        #visited[i]=True
        ans =self.backward_chaining(self.kb[i],visited)
        #print(ans,self.solution)
        return ans

    def get_function_name(self,clause):
        clause =clause.strip(' ')
        parts =clause.split('(')

        parts_n =parts[0].lstrip('~')
        if parts_n !=parts[0]:
            parts_n =parts_n.strip(' ')
            parts[0]='~'+parts_n

        return parts[0]


    def backward_chaining(self,query,visited):
        if self.found_solution==True:
            return self.solution



        query_p =query.split('|')
        for part in query_p:
            part =part.strip(' ')
            fn_name =part.lstrip('~')

            if fn_name ==part:
                #positive => look for -ve terms
                fname =self.get_function_name(fn_name)
                if self.pred.has_key(fname):
                    pl = self.pred.get(fname)
                    for cl in pl.negative:
                        if visited[cl] == self.v_count:
                            #print('True -ve',cl)
                            continue
                        visited[cl] +=1
                        #print('before comb', cl, query, self.kb[cl])
                        comb=self.combine_query(cl,query,visited)
                        #print('comb', comb,query,self.kb[cl])
                        if comb[0] == True:
                            result=comb[1]
                            for r in result:
                                if r =='':
                                    self.found_solution =True
                                    self.solution =True
                                    return True

                                self.resolvents.append(self.kb)
                                if self.backward_chaining(r,visited):
                                    return True
                        visited[cl]=visited[cl]-1
            else:
                fname = self.get_function_name(fn_name)
                if self.pred.has_key(fname):
                    pl = self.pred.get(fname)
                    for cl in pl.positive:
                        #print('visited', cl, query, self.kb[cl],visited)
                        if visited[cl] == self.v_count:
                            #print('True +ve', cl)
                            continue
                        visited[cl] +=1
                        #print('before comb',cl, query, self.kb[cl])
                        comb =self.combine_query(cl,query,visited)
                        #print('comb',comb,query,self.kb[cl])
                        if comb[0] == True:
                            result = comb[1]
                            for r in result:
                                if r == '':
                                    self.found_solution = True
                                    self.solution = True
                                    return True

                                self.resolvents.append(self.kb)
                                if self.backward_chaining(r, visited):
                                    return True
                        visited[cl] = visited[cl] - 1


        return False

    def find_functions(self,clause):
        clause=clause.strip(' ')
        parts =clause.split('|')
        fns=[]
        for part in parts:
            val= self.get_function_name(part)
            fns.append(val)
        return fns

    def negated(self,fn):
        fn_n =fn.lstrip('~')
        fn_n =fn_n.strip(' ')
        if fn_n ==fn:
            sol ='~'+fn
            return sol
        return fn_n

    def combine_query(self, clause_no,clause,visited):
        clause1 =self.kb[clause_no]
        #visited[clause_no] =True

        fns1 =self.find_functions(clause1)
        fns2 =self.find_functions(clause)
        result=[]
        for fn in fns2:
            index2 =fns2.index(fn)
            fn_n =self.negated(fns2[index2])
            for i in range(0,len(fns1)):
                if fn_n ==fns1[i]:
                    index1 = i
                    result_c =self.find_substitution(clause1,clause,index1,index2)
                    if result_c[0] ==True:
                        result.append(result_c[1])


        if len(result)==0:
            return (False,'')
        else:
            #print('combined query',result)
            return(True,result)



    def find_substitution(self,clause1,clause2, index1,index2):

        clause1=clause1.strip(' ')
        clause2=clause2.strip(' ')

        parts1 =clause1.split('|')
        parts2 =clause2.split('|')

        result =self.unify(parts1[index1],parts2[index2])
        #print('result',result)
        if result[0]==False:
            return ('False'," ")

        name=' '
        if result[1] ==True:
            name =self.get_function_name(parts1[index1])
            name =name.lstrip('~')
        n_query=''
        cnt =0
        for part in parts1:
           fn_name =self.get_function_name(part)
           fn_name_n =fn_name.lstrip('~')
           if cnt==index1:
               #print('index1',index1)
               cnt=cnt+1
               continue
           cnt=cnt+1
           n_query =n_query+fn_name+'('
           args =self.get_args(part)
           count =0
           for arg in args:
               if result[2].has_key(arg):
                   v =result[2][arg]
                   args[count]=v
               count=count+1
           n_query =n_query +",".join(args) + ")|"

        cnt =0
        #print('parts2',parts2)
        for part in parts2:
           fn_name =self.get_function_name(part)
           fn_name_n =fn_name.lstrip('~')
           if cnt == index2:
               cnt=cnt+1
               continue
           cnt =cnt+1
           n_query =n_query+fn_name+'('
           args =self.get_args(part)
           count =0
           for arg in args:
               if result[2].has_key(arg):
                   v =result[2][arg]
                   args[count]=v
               count=count+1
           n_query =n_query +",".join(args) + ")|"
        n_query=n_query.rstrip('|')

        n_query =self.check_duplicates(n_query)
        if n_query==' ':
            return (False,n_query)
        return(True,n_query)

    def check_duplicates(self,query):
        fns = self.find_functions(query)
        parts =query.split('|')

        remov=[]
        for i in range(0,len(fns)):
            for j in range(i+1,len(fns)):
                if fns[i]==fns[j]:
                    flag =True
                    args1=self.get_args(parts[i])
                    args2=self.get_args(parts[j])
                    for k in range(0,len(args1)):
                        if args1[k]!=args2[k]:
                            flag=False
                            break
                    if flag == True:
                        remov.append(i)
                elif fns[j]== self.negated(fns[i]):
                    flag =True
                    args1 = self.get_args(parts[i])
                    args2 = self.get_args(parts[j])
                    for k in range(0, len(args1)):
                        if args1[k] != args2[k]:
                            flag = False
                            break
                    if flag == True:
                        remov.append(i)
                        remov.append(j)

        if len(remov)==0:
            return query
        else:
            remov.sort(reverse =True)
            for x in remov:
                parts.pop(x)
            if len(parts)==0:
                return ' '
        n_query=''
        n_query=n_query +"|".join(parts)
        return n_query






    def toberemoved(self,part1,part2):
        f_name1=self.get_function_name(part1)
        f_name2=self.get_function_name(part2)
        if f_name1==f_name2:
            return False
        else:
            return True

    def get_args(self,clause):
        clause= clause.strip(' ')
        clause = clause.rstrip('\n')
        clause = clause.strip(')')
        parts  = clause.split('(')
        args   = parts[1].split(',')
        for i in range(0,len(args)):
            args[i]=args[i].strip(' ')
        return args

    def isvar(self,arg):
        arg=arg.strip(' ')
        if arg[0].isupper():
            return False
        return True

    def unify(self,part1,part2):
        part1 =part1.strip(' ')
        part2 =part2.strip(' ')
        arg1 =self.get_args(part1)
        arg2 =self.get_args(part2)
        subs ={}

        if len(arg1)!=len(arg2):
            print('ERROR arg length not matching')
        else:
            for i in range(len(arg1)):
                if self.isvar(arg1[i]) and  self.isvar(arg2[i]):
                    if subs.has_key(arg1[i]):
                        val =arg1[i]
                        if val!=arg2[i]:
                            print('ERROR 1',arg1[i],val)
                    subs[arg1[i]]=arg2[i]
                elif self.isvar(arg1[i]) and (not self.isvar(arg2[i])):
                    if subs.has_key(arg1[i]):
                        val = arg1[i]
                        if val != arg2[i]:
                            print('ERROR 2', arg1[i], val)
                    subs[arg1[i]]=arg2[i]
                elif (not self.isvar(arg1[i])) and self.isvar(arg2[i]):
                    if subs.has_key(arg2[i]):
                        val = arg1[i]
                        if val != arg1[i]:
                            print('ERROR 3', arg1[i], val)
                    subs[arg2[i]]=arg1[i]
                else:
                    if arg1[i]!=arg2[i]:
                        return (False,False,subs)

        #print(len(subs))

        return (True,self.toberemoved(part1,part2),subs)



    '''
    def standardize(clause, i):
        l = []
        args = get_args(clause).split(",")
        for v in args:
            if is_variable(v):
                l.append(v + str(i))
            else:
                l.append(v)
        clause = get_op(clause) + "(" + ",".join(l) + ")"
        return clause
    '''


    def standardize(self,query,i):
        parts = query.split('|')
        new_query=''
        for part in parts:
            fn_name =self.get_function_name(part)
            new_query=new_query+ fn_name+'('
            args =  self.get_args(part)
            #print(args)
            for arg in args:
                if self.isvar(arg):
                    arg=arg+ str(i)
                new_query =new_query+arg+','
            new_query =new_query.rstrip(',')
            #print('0.5',new_query)
            new_query=new_query+')'+'|'
            #print('1',new_query)

        new_query =new_query.rstrip('|')
        #print(new_query)
        return new_query


    def clear(self):
        self.resolvents[:] =[]
        self.kb.pop()
        self.found_solution=False





if __name__=='__main__':

    query =[]
    know_base = Kbase()
    with open("input.txt", 'r') as f:
        line = f.readline()
        Nval = line.rstrip()
        N = (int)(Nval)

        for i in range(0,N):
            line = f.readline()
            val = line.rstrip()
            query.append(val)
        line = f.readline()
        kb_no = line.rstrip()
        know_base.no_kb =(int)(kb_no)
        for i in range(0,know_base.no_kb):
            line = f.readline()
            val = line.strip(' ')
            val =know_base.standardize(val,i)
            know_base.kb.append(val)
            know_base.store_info(val,i)
    #    know_base.print_kb()

    #for i in range(0,know_base.no_kb):
    #    print(know_base.kb[i])
    sol=[]
    for i in range(0,N):
       sol.append(know_base.evaluate_query(query[i]))
       know_base.clear()
    #print('solution')

    fout = open('output.txt', 'w')
    st=''
    for s in sol:
        print(s)
        st =st+ str(s).upper()+'\n'
    fout.write(st)










