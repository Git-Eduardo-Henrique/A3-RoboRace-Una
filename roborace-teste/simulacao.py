"""Simulações automáticas SEM benefícios educativos (100 e 1.000 corridas).

Uso:  python simulacao.py            (usa a semente fixa abaixo)
      python simulacao.py 123        (outra semente)
Salva o resultado em resultados_simulacao.txt.
"""
import random
import sys
from collections import Counter

import regras
from corrida import Corrida

SEMENTE_PADRAO = 42
SERIES = (100, 1000, 10000)   # 100 e 1.000 são os pedidos; 10.000 é extra, só para comparação


def simular(n: int, semente: int) -> dict:
    rng = random.Random(semente)
    vitorias_exclusivas = Counter()
    empates = 0
    soma_rodadas = 0
    for _ in range(n):
        corrida = Corrida(rng)                  # sem jogador => sem benefícios
        while not corrida.finalizada:
            corrida.jogar_rodada()
        soma_rodadas += corrida.rodada
        if len(corrida.vencedores) == 1:
            vitorias_exclusivas[corrida.vencedores[0]] += 1
        else:
            empates += 1
    return {"n": n, "semente": semente, "vitorias": vitorias_exclusivas,
            "empates": empates, "media_rodadas": soma_rodadas / n}


def formatar(res: dict) -> str:
    n = res["n"]
    linhas = [f"Série de {n} corridas (semente {res['semente']}, sem benefícios)"]
    for robo in regras.ROBOS_PADRAO:
        v = res["vitorias"][robo]
        linhas.append(f"  Vitórias exclusivas de {robo}: {v} ({100 * v / n:.1f}%)")
    linhas.append(f"  Empates: {res['empates']} ({100 * res['empates'] / n:.1f}%)")
    linhas.append(f"  Média de rodadas: {res['media_rodadas']:.2f}")
    return "\n".join(linhas)


if __name__ == "__main__":
    semente = int(sys.argv[1]) if len(sys.argv) > 1 else SEMENTE_PADRAO
    blocos = [formatar(simular(n, semente)) for n in SERIES]
    texto = "\n\n".join(blocos)
    print(texto)
    with open("resultados_simulacao.txt", "w", encoding="utf-8") as f:
        f.write(texto + "\n")
