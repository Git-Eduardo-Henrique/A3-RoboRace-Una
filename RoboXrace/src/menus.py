from src import robos, partida

def linha(): # gera linha no terminal para estetica
    print("\033[34m", end="")
    print(30 * "=-=", "\033[m")

def limpar(): # limpa o terminal
    print("\033c", end="")

def adicionarCor(texto = "", cor = 1):
    if cor == 1: # vermelho
        return f"\033[31m{texto}\033[m"
    elif cor == 2: # verde
        return f"\033[32m{texto}\033[m"
    elif cor == 3: # amarelo
        return f"\033[33m{texto}\033[m"
    elif cor == 4: # azul
        return f"\033[34m{texto}\033[m"
    elif cor == 5: # magenta
        return f"\033[35m{texto}\033[m"
    elif cor == 6: # ciano
        return f"\033[36m{texto}\033[m"
    elif cor == 7: # cinza
        return f"\033[37m{texto}\033[m"
    else:
        return "COR INVALIDA! ( APENAS DE 1 A 7 )"

# ==========================================================================

def menuEscolhaRobo():
    opc_jogador = 0

    linha()
    print("Escolha seu robo:")
    print(f"1 = {adicionarCor("Robo azul", 4)}")
    print(f"2 = {adicionarCor("Robo vermelho", 1)}")
    print(f"3 = {adicionarCor("Robo verde", 2)}")
    linha()

    while opc_jogador <= 0 or opc_jogador > 3:
        opc_jogador= int(input(f"Sua opção {adicionarCor("( apenas de 1 a 3 )", 4)}: "))

    limpar()

    return opc_jogador

def menuEmJogo(jogador=1):
    emJogo = True
    jogo = partida.Jogo()

    if jogador == 1:
        print(f"você escolheu o {adicionarCor("Robo azul", 4)}")
        robo_jogador = robos.Robo(cor="azul", posicao=0)
        robo_rival1 = robos.Robo(cor="vermelho", posicao=0)
        robo_rival2 = robos.Robo(cor="verde", posicao=0)
    elif jogador == 2:
        print(f"você escolheu o {adicionarCor("Robo vermelho", 1)}")
        robo_jogador = robos.Robo(cor="vermelho", posicao=0)
        robo_rival1 = robos.Robo(cor="azul", posicao=0)
        robo_rival2 = robos.Robo(cor="verde", posicao=0)
    else:
        print(f"você escolheu o {adicionarCor("Robo verde", 2)}")
        robo_jogador = robos.Robo(cor="verde", posicao=0)
        robo_rival1 = robos.Robo(cor="vermelho", posicao=0)
        robo_rival2 = robos.Robo(cor="azul", posicao=0)

    while emJogo:
        opc = -1 

        linha()

        linha()
        print(f"Jogo em {adicionarCor("andamento!", 4)} Digite uma opção")
        print(f"{adicionarCor("0 - Fechar jogo", 1)}")
        print(f"1 - {adicionarCor("Avançar rodada", 4)}")
        print(f"2 - {adicionarCor("Loja de créditos", 4)}")
        print(f"3 - {adicionarCor("Desafios", 4)}")
        linha()

        while opc < 0 or opc > 3:
                opc = int(input(f"Sua opção {adicionarCor("( apenas de 0 a 3 )", 4)}: "))

        limpar()

        if opc == 0:
            emJogo = False
        elif opc == 1:
            jogo.iniciarRodada(robo_jogador, robo_rival1, robo_rival2)

if __name__ == "__main__":
    print("modulo Menus iniciado! para iniciar o jogo execute o arquivo MAIN.PY")
