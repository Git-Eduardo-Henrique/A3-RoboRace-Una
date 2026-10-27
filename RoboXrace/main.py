from random import randint
# 30 posições
# cada casa deve ter uma aleatóriedade
# irá ter a maior chance de ser casa normal
# allgumas casa irá ter obstacúlos
# outras irão ter possíveis benefícios
# para iniciar será com a tecla

opc_jogador = 0
pista_robo1 = []

print(50 * "=")
print("Escolha seu robo:")
print("1 = \033[34mrobo azul\033[m")
print("2 = \033[31mrobo vermelho\033[m")
print("3 = \033[32mrobo verde\033[m")
print(50 * "=")

while opc_jogador <= 0 or opc_jogador > 3:
    opc_jogador= int(input("sua opcao: "))

print(50 * "=")

if opc_jogador == 1:
    print("você escolheu o \033[34mrobo azul\033[m")
elif opc_jogador == 2:
    print("você escolheu o \033[31mrobo vermelho\033[m")
else:
    print("você escolheu o \033[32mrobo verde\033[m")

for casa1 in range(0, 30):
    chance = randint(0, 100)

    if chance <= 70:
        pista_robo1.append(0) # casa vazia
    elif chance <= 80 and chance > 70:
        pista_robo1.append(4) # oleo na pista
    elif chance <= 90 and chance > 80:
        pista_robo1.append(5) # turbo boost
    elif chance <= 100 and chance > 90:
        pista_robo1.append(6) # acidente na pista
    