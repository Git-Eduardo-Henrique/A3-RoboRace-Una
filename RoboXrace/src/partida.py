from src import menus
from random import randint

class Jogo:
    def __init__(self):
        self.rodada = -1

    def iniciarRodada(self, jogador, robo1, robo2, rec_turbo=False, rec_escudo=False):
        self.rodada += 1

        if self.rodada == 0:
            jogador.posicao = 0
            robo1.posicao = 0
            robo2.posicao = 0

            novo_movimento1 = [0, "inicio"]
            novo_movimento2 = [0, "inicio"]
            novo_movimento3 = [0, "inicio"]
        else:
            if rec_turbo:
                novo_movimento1 = self.sortearMovimento(robo=jogador)
                novo_movimento1[0] += 3
            elif rec_escudo:
                novo_movimento1 = self.sortearMovimento(robo=jogador)
            else:
                novo_movimento1 = self.sortearMovimento(robo=jogador)

            novo_movimento2 = self.sortearMovimento(robo=robo1)
            novo_movimento3 = self.sortearMovimento(robo=robo2)

        msg1 = self.gerarPista(jogador, novo_movimento1[0], novo_movimento1[1])
        msg2 = self.gerarPista(robo1, novo_movimento2[0], novo_movimento2[1])
        msg3 = self.gerarPista(robo2, novo_movimento3[0], novo_movimento3[1])

        menus.linha()
        print(f"RODADA: {self.rodada}")
        print(msg1)
        print(msg2)
        print(msg3)

        if jogador.posicao > 30:
            menus.fimDeJogo(cor_jogador=jogador.cor, rodada=self.rodada, cor_vencedor=jogador.cor)
            return False
        elif robo1.posicao > 30:
            menus.fimDeJogo(cor_jogador=jogador.cor, rodada=self.rodada, cor_vencedor=robo1.cor)
            return False
        elif robo2.posicao > 30:
            menus.fimDeJogo(cor_jogador=jogador.cor, rodada=self.rodada, cor_vencedor=robo2.cor)
            return False
        
        return True

    def sortearMovimento(self, robo): # sorteia o próxima movimento
        chance = randint(0, 100)
        tipo = ""

        if chance <= 50: # MOVIMENTO BÁSICO ( 1 A 3 )
            movimento = randint(1, 3)
            robo.posicao += movimento
            tipo = "basico"
        elif chance > 50 and chance <= 65: # TURBO ( MOVIMENTO BÁSICO + 3 DE BONUS )
            movimento = randint(1, 3) + 3
            robo.posicao += movimento
            tipo = "turbo"
        elif chance > 65 and chance <= 75: # PANE ( SEM MOVIMENTO )
            movimento = 0
            tipo = "pane"
        elif chance > 75 and chance <= 85: # OLEO ( MOVIMENTO BÁSICO - 2 / MINIMO 0)
            movimento = randint(1, 3) - 2
            if movimento < 0:
                movimento = 0

            robo.posicao += movimento
            tipo = "oleo"
        elif chance > 85 and chance <= 95: # BURACO ( MOVIMENTO BÁSICO - 3 / SEMPRE 0)
            if (robo.posicao - 3) <= 0:
                movimento = "ao final da pista"
                robo.posicao = 0
            else:
                movimento = -3
                robo.posicao += movimento
            tipo = "buraco"
        elif chance > 95: # SUPER TURBO ( MOVIMENTO BÁSICO + 6 DE BONUS )
            movimento = randint(1, 3) + 6
            robo.posicao += movimento
            tipo = "superturbo"

        return [movimento, tipo]

    def gerarPista(self, jogador, movimento, tipo): # mostra a pista e posição do robo nela
        pista = []

        if jogador.cor == "vermelho":
            num_cor_robo = 1
            cor_robo = "\033[41m🤖\033[m"
        elif jogador.cor == "verde":
            num_cor_robo = 2
            cor_robo = "\033[42m🤖\033[m"
        else:
            num_cor_robo = 4
            cor_robo = "\033[44m🤖\033[m"

        for casa in range(0, 31):
            if casa == jogador.posicao:
                pista.append(cor_robo)
            elif casa == 30:
                pista.append("=")
            else:
                pista.append(str(casa)) 
                    

        self.mostrarPista(pista=pista)

        if tipo == "inicio":
            return f"Partida iniciada!! robo {menus.adicionarCor(jogador.cor, num_cor_robo)} inicia na posição {menus.adicionarCor(movimento, num_cor_robo)}"
        elif tipo == "basico":
            return f"robo {menus.adicionarCor(jogador.cor, num_cor_robo)} movimentou {menus.adicionarCor(movimento, num_cor_robo)} posições"
        elif tipo == "turbo":
            return f"robo {menus.adicionarCor(jogador.cor, num_cor_robo)} ativou o {menus.adicionarCor("turbo!!", num_cor_robo)} e movimentou {menus.adicionarCor(movimento, num_cor_robo)} posições"
        elif tipo == "pane":
            return f"robo {menus.adicionarCor(jogador.cor, num_cor_robo)} sofreu {menus.adicionarCor("pane na pista", num_cor_robo)}.. {menus.adicionarCor(movimento, num_cor_robo)} movimentos"
        elif tipo == "oleo":
            return f"robo {menus.adicionarCor(jogador.cor, num_cor_robo)} encontrou {menus.adicionarCor("oleo na pista", num_cor_robo)}.. movimentou apenas {menus.adicionarCor(movimento, num_cor_robo)} posições"
        elif tipo == "buraco":
            return f"robo {menus.adicionarCor(jogador.cor, num_cor_robo)} encontrou um {menus.adicionarCor("buraco na pista", num_cor_robo)}.. voltou {menus.adicionarCor(movimento, num_cor_robo)}"
        elif tipo == "superturbo":
            return f"robo {menus.adicionarCor(jogador.cor, num_cor_robo)} ativou o {menus.adicionarCor("SUPER TURBO!!!!", num_cor_robo)} e movimentou {menus.adicionarCor(movimento, num_cor_robo)} posições"

    def mostrarPista(self, pista):
        for casa in pista:
            print(casa, end=" ")

        print()

    def recompensa(self, jogador, robo1, robo2, tipo):
        if tipo == "compra_turbo" and jogador.creditos >= 2:
            jogador.creditos -= 2
            self.iniciarRodada(jogador, robo1, robo2, True, False)
        elif tipo == "escudo" and jogador.creditos >= 1:
            jogador.creditos -= 1
            self.iniciarRodada(jogador, robo1, robo2, False, True)
        else:
            self.iniciarRodada(jogador, robo1, robo2)
            print("Créditos insuficiente!! rodada normal")
            


if __name__ == "__main__":
    print("modulo Partida iniciado! para iniciar o jogo execute o arquivo MAIN.PY")