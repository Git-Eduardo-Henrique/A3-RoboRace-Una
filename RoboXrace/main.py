from random import randint
from src import menus

def gerar_pista(pista = []): # gere uma lista aleatoria de posições para a pista
    for casa in range(0, 30):
        chance = randint(0, 100)

        if chance <= 50:
            pista.append(0) 
        elif chance <= 80 and chance > 70:
            pista.append(4) 
        elif chance <= 90 and chance > 80:
            pista.append(5) 
        elif chance <= 100 and chance > 90:
            pista.append(6) 

    return pista

pista_robo_az = []
pista_robo_verm = []
pista_robo_verd = []

jogador = menus.menuEscolhaRobo()
menus.menuEmJogo(jogador=jogador)
