from src import robos
from random import randint

class Jogo:
    def __init__(self):
        self.rodada = 0

    def iniciarRodada(self, jogador, robo1, robo2):
        self.rodada += 1

        if self.rodada == 1:
            jogador.posicao = 0
            robo1.posicao = 0
            robo2.posicao = 0
        else:
            novo_movimento1 = self.sortearMovimento()
            novo_movimento2 = self.sortearMovimento()
            novo_movimento3 = self.sortearMovimento()
            jogador.posicao += novo_movimento1
            robo1.posicao += novo_movimento2
            robo2.posicao += novo_movimento3

        self.mostrarPosicao(jogador)
        self.mostrarPosicao(robo1)
        self.mostrarPosicao(robo2)

    def sortearMovimento(self): # sorteia o próxima movimento
        chance = randint(0, 100)

        if chance <= 50: # MOVIMENTO BÁSICO ( 1 A 3 )
            movimento = randint(1, 3)
        elif chance > 50 and chance <= 65: # TURBO ( MOVIMENTO BÁSICO + 3 DE BONUS )
            movimento = randint(1, 3) + 3
        elif chance > 65 and chance <= 75: # PANE ( SEM MOVIMENTO )
            movimento = 0
        elif chance > 75 and chance <= 85: # OLEO ( MOVIMENTO BÁSICO - 2 / MINIMO 0)
            movimento = randint(1, 3) - 2
            if movimento < 0:
                movimento = 0
        elif chance > 85 and chance <= 95: # BURACO ( MOVIMENTO BÁSICO - 3 / SEMPRE 0)
            movimento = -3
        elif chance > 95: # SUPER TURBO ( MOVIMENTO BÁSICO + 6 DE BONUS )
            movimento = randint(1, 3) + 6

        return movimento

    def mostrarPosicao(self, jogador): # mostra a pista e posição do robo nela
        pista = []

        for casa in range(0, 30):
            if casa == jogador.posicao:
                if jogador.cor == "azul":
                    pista.append("\033[44m🤖\033[m")
                elif jogador.cor == "vermelho":
                    pista.append("\033[41m🤖\033[m")
                elif jogador.cor == "verde":
                    pista.append("\033[42m🤖\033[m")
            else:
                pista.append("-")

        print("".join(pista))