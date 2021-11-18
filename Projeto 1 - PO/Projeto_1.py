'''
Projeto: Transformação do PFM em PFCM
Autores: Joison Oliveira, Laura Campos, Wendson Carlos
Linguagem: Python
Biblioteca: Pulp 
 
NOTE: Será exibido a resolução do PFM e em seguida a resolução do PFM
transformado em PFCM. Isso servirá para comparar os valores dado pelo solver.
'''
from pulp import *

#Criação da estrutura do grafo

class Grafo:
    
    def __init__(self, vertices):
        self.vertices = vertices
        self.grafo = [[0]*self.vertices for i in range(self.vertices)]
        
    def add_aresta(self, u, v):  #adiciona as arestas dos vertices U e V
        self.grafo[u-1][v-1] = 1 #os vertices iniciam em 0. Para grafo multiplo +=
        
    def exibir(self):
        for i in range(self.vertices): #percorre até n-1
            print(self.grafo[i])
    
    def existe_aresta(self, u, v):
        if self.grafo[u-1][v-1] == 1:
            return 1
        else:
            return 0
            
class Capacidade:
    
    def __init__(self, vertices):
        self.vertices = vertices
        self.grafo = [[0]*self.vertices for i in range(self.vertices)]
        
    def add_aresta(self, u, v, peso):  #adiciona as arestas dos vertices U e V
        self.grafo[u-1][v-1] = peso #os vertices iniciam em 0. Para grafo multiplo +=
        
    def exibir(self):
        for i in range(self.vertices): #percorre até n-1
            print(self.grafo[i])            

    def get_peso(self, u, v):
        return self.grafo[u-1][v-1]
    
    
class Custos:
    
    def __init__(self, vertices):
        self.vertices = vertices
        self.grafo = [[0]*self.vertices for i in range(self.vertices)]
        
    def add_aresta(self, u, v, custo):  #adiciona as arestas dos vertices U e V
        self.grafo[u-1][v-1] = custo #os vertices iniciam em 0. Para grafo multiplo +=
        
    def exibir(self):
        for i in range(self.vertices): #percorre até n-1
            print(self.grafo[i])    
            
    def get_custo(self, u, v):
        return self.grafo[u-1][v-1]

        
#Leitura de arquivo

file = open("instance1.txt","r")

instancia = []

for line in file:
    instancia.append(line.rstrip())
    
nVertice = int(instancia[0])
nEdge =  int(instancia[1])
vOrigem = int(instancia[2])
vEscoadouro = int(instancia[3])
tArcos = instancia[4:]

arcos = []
for i in tArcos:
    arcos.append(i.split())

#Informações do problema 

fluxo = Grafo(int(nVertice)) #Ler do arquivo
fluxoCap = Capacidade(int(nVertice))

i = 0
j = 1 

while i < len(arcos):
    if(j == 2):
        j = 1
    if(j < 2):
        u = int(arcos[i][j - 1])
        v = int(arcos[i][j])
    fluxo.add_aresta(u,v)
    i+=1
    j+=1

 
i = 0
j = 2

while i < len(arcos):
    if(j == 3):
        j = 2
    if(j < 3):
        u = int(arcos[i][j-2])
        v = int(arcos[i][j-1])
        c = int(arcos[i][j])
    fluxoCap.add_aresta(u,v,c)
    i+=1
    j+=1


#Preencher a lista de nos fazer um for

no_origem = int(vOrigem) # Ler do arquivo
no_escoadouro = int(vEscoadouro) # Ler do arquivo

n_arcos = int(nEdge) # Ler do arquivo


#Definição dos dados do problema

vList = []
k = 1

while k < (nVertice + 1):
    vList.append(k)
    k+=1
        
#Varivaeis de decisão
var = {}
i = 0
j = 0
for i in vList:
    for j in vList:
        if fluxo.existe_aresta(i, j):
            var[(i,j)]= LpVariable(name = f'x{i}{j}', lowBound=0)
        else:
            continue
        
    var.update(var)
    
##############################################################################
#                                                                            #
#                MODELO DO PROBLEMA DO FLUXO MÁXIMO                          #
#                                                                            #
##############################################################################

#Criação do modelo
model = LpProblem("PFM", LpMaximize)

lista_fo = []

for x in var.keys():
    if x[0]==no_origem:
        lista_fo.append(var[x])
        

model += lpSum(lista_fo)


#Restrições do problema

lista_origem = []
lista_destino = []

for no in vList:
    for x in var.keys():
        if no == x[0]:
            lista_origem.append(var[x])
        elif no == x[1]:
            lista_destino.append(var[x])
        else:
            continue
    if no == no_escoadouro  or no == no_origem:
        None
    else:
        model += lpSum(lista_origem) - lpSum(lista_destino) == 0
        
    lista_origem = []
    lista_destino = []

for x in var.keys():
    model += var[x] <= fluxoCap.get_peso(x[0], x[1])

print('\n')
print("Resolução do PFM:")
print('\n')

print(model)


#Solucionar  

status = model.solve()
print(LpStatus[status])
print(value(model.objective))

for x in var.values():
    print(f'{x} =  {value(x)}')
    
         
##############################################################################
#                                                                            #
#                MODELO DO PROBLEMA DO FLUXO DE CUSTO MÍNIMO                 #
#                                                                            #
##############################################################################

model2 = LpProblem("PFCM", LpMinimize)

var[(no_escoadouro, no_origem)] = LpVariable(name = f'x{no_escoadouro}{no_origem}', lowBound=0, upBound=1000)
var.update(var)

for no in vList:
    for x in var.keys():
        if no == x[0]:
            lista_origem.append(var[x])
        elif no == x[1]:
            lista_destino.append(var[x])
        else:
            continue
        
    model2 += lpSum(lista_origem) - lpSum(lista_destino) == 0
        
    lista_origem = []
    lista_destino = []

for x in var.keys():
    if x != (no_escoadouro, no_origem):
        model2 += var[x] <= fluxoCap.get_peso(x[0], x[1])


M = 10000

custo = Custos(nVertice)
custo.add_aresta(no_origem, no_escoadouro, M)

F = 10000

for no in vList:
    if no == no_origem:
        for x in var.keys():
            if no == x[0]:
                lista_destino.append(var[x])
            else:
                continue
    if no == no_escoadouro:
        for x in var.keys():
            if no == x[1]:
                lista_origem.append(var[x])
            else:
                continue
    
lista_mult = []  

for x in var.keys():
    if x[0]==no_escoadouro:
        teste = var[x]
        lista_mult.append(-var[x])
        
model2 += lpSum(lista_mult) 

print('\n')
print("Resolução do PFM transformado em PFCM:")
print('\n')

print(model2)  

status = model2.solve()
print(LpStatus[status])
print(value(model2.objective))

for x in var.values():
    print(f'{x} =  {value(x)}')