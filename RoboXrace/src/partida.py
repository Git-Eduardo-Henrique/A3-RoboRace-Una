from src import menus
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

            novo_movimento1 = [0, "inicio"]
            novo_movimento2 = [0, "inicio"]
            novo_movimento3 = [0, "inicio"]
        else:
            novo_movimento1 = self.sortearMovimento()
            novo_movimento2 = self.sortearMovimento()
            novo_movimento3 = self.sortearMovimento()
            jogador.posicao += novo_movimento1[0]
            robo1.posicao += novo_movimento2[0]
            robo2.posicao += novo_movimento3[0]

        msg1 = self.mostrarPosicao(jogador, novo_movimento1[0], novo_movimento1[1])
        msg2 = self.mostrarPosicao(robo1, novo_movimento2[0], novo_movimento2[1])
        msg3 = self.mostrarPosicao(robo2, novo_movimento3[0], novo_movimento3[1])

        menus.linha()
        print(msg1)
        print(msg2)
        print(msg3)

    def sortearMovimento(self): # sorteia o próxima movimento
        chance = randint(0, 100)
        tipo = ""

        if chance <= 50: # MOVIMENTO BÁSICO ( 1 A 3 )
            movimento = randint(1, 3)
            tipo = "basico"
        elif chance > 50 and chance <= 65: # TURBO ( MOVIMENTO BÁSICO + 3 DE BONUS )
            movimento = randint(1, 3) + 3
            tipo = "turbo"
        elif chance > 65 and chance <= 75: # PANE ( SEM MOVIMENTO )
            movimento = 0
            tipo = "pane"
        elif chance > 75 and chance <= 85: # OLEO ( MOVIMENTO BÁSICO - 2 / MINIMO 0)
            movimento = randint(1, 3) - 2
            if movimento < 0:
                movimento = 0
            tipo = "oleo"
        elif chance > 85 and chance <= 95: # BURACO ( MOVIMENTO BÁSICO - 3 / SEMPRE 0)
            movimento = -3
            tipo = "buraco"
        elif chance > 95: # SUPER TURBO ( MOVIMENTO BÁSICO + 6 DE BONUS )
            movimento = randint(1, 3) + 6
            tipo = "superturbo"

        return [movimento, tipo]

    def mostrarPosicao(self, jogador, movimento, tipo): # mostra a pista e posição do robo nela
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

        if tipo == "inicio":
            return f"Partida iniciada!! robo {jogador.cor} inicia na posição {movimento}"
        elif tipo == "basico":
            return f"robo {jogador.cor} movimentou {movimento} posições"
        elif tipo == "turbo":
            return f"robo {jogador.cor} ativou o turbo!! e movimentou {movimento} posições"
        elif tipo == "pane":
            return f"robo {jogador.cor} sofreu pane na pista.. {movimento} movimentos"
        elif tipo == "oleo":
            return f"robo {jogador.cor} encontrou oleo na pista.. movimentou apenas {movimento} posições"
        elif tipo == "buraco":
            return f"robo {jogador.cor} encontrou um buraco na pista.. {movimento} posições"
        elif tipo == "superturbo":
            return f"robo {jogador.cor} ativou o SUPER TURBO!!!! e movimentou {movimento} posições"
        