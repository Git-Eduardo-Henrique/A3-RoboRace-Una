"""Lógica da corrida: robôs, rodadas, eventos, chegada e empate.

Este módulo não conhece perguntas, créditos nem interface. Ele só recebe,
a cada rodada, o benefício (ou None) que vale para o robô do jogador.

ORDEM DE APLICAÇÃO (por robô, em cada rodada) — justificativa no LEIA-ME:
 1. Sorteia-se UM evento.
 2. Se o robô é o do jogador e tem Escudo: pane/óleo/buraco viram "Normal".
 3. Se o evento aplicado NÃO é pane, sorteia-se o movimento básico (1 a 3).
    (Pane não sorteia o básico; se o Escudo converter a pane, o básico é sorteado.)
 4. Aplica-se o efeito do evento e a posição não pode ficar negativa.
 5. Se o robô é o do jogador e tem Turbo comprado: soma +3 depois do evento.
 6. Só depois de processar TODOS os robôs verifica-se a chegada (>= META).
"""
from __future__ import annotations

import random
from dataclasses import dataclass

import regras


def sortear_evento(rng: random.Random) -> str:
    """Sorteia um evento respeitando as probabilidades de regras.EVENTOS."""
    nomes = list(regras.EVENTOS)
    pesos = list(regras.EVENTOS.values())
    return rng.choices(nomes, weights=pesos, k=1)[0]


def deslocamento_do_evento(evento: str, basico: int) -> int:
    """Deslocamento (pode ser negativo) causado pelo evento, antes do piso em zero."""
    if evento == "Normal":
        return basico
    if evento == "Pane":
        return 0
    if evento == "Turbo":
        return basico + regras.BONUS_TURBO_EVENTO
    if evento == "Super Turbo":
        return basico + regras.BONUS_SUPER_TURBO
    if evento == "Óleo":
        return max(0, basico - regras.REDUCAO_OLEO)
    if evento == "Buraco":
        return basico - regras.RECUO_BURACO   # avança o básico e depois recua
    raise ValueError(f"Evento desconhecido: {evento}")


@dataclass
class RegistroRobo:
    """O que aconteceu com um robô em uma rodada (evento e benefício separados)."""
    robo: str
    evento_sorteado: str      # o que o sorteio deu
    evento_aplicado: str      # o que valeu de fato (difere se o Escudo converteu)
    basico: int               # movimento básico sorteado (0 se pane)
    pos_anterior: int
    pos_atual: int
    bonus_extra: int = 0      # posições extras do Turbo comprado
    escudo: str = ""          # "", "bloqueou" ou "sem_necessidade"

    @property
    def variacao(self) -> int:
        return self.pos_atual - self.pos_anterior


class Corrida:
    def __init__(self, rng: random.Random, robos=regras.ROBOS_PADRAO, jogador: str | None = None):
        if jogador is not None and jogador not in robos:
            raise ValueError(f"Robô inválido: {jogador!r}. Escolha entre: {', '.join(robos)}.")
        self.rng = rng
        self.robos = tuple(robos)
        self.jogador = jogador
        self.posicoes = {r: 0 for r in self.robos}
        self.rodada = 0
        self.finalizada = False
        self.vencedores: list[str] = []

    def jogar_rodada(self, beneficio: str | None = None) -> list[RegistroRobo]:
        """Processa todos os robôs e só então verifica a chegada."""
        if self.finalizada:
            raise RuntimeError("A corrida já terminou.")
        self.rodada += 1
        registros = []
        for robo in self.robos:
            anterior = self.posicoes[robo]
            recebe = beneficio is not None and robo == self.jogador

            sorteado = sortear_evento(self.rng)
            aplicado = sorteado
            escudo = ""
            if recebe and beneficio == "Escudo":
                if sorteado in regras.OBSTACULOS:
                    aplicado, escudo = "Normal", "bloqueou"
                else:
                    escudo = "sem_necessidade"   # consumido mesmo sem obstáculo

            basico = 0 if aplicado == "Pane" else self.rng.randint(
                regras.MOVIMENTO_MIN, regras.MOVIMENTO_MAX)

            nova = max(0, anterior + deslocamento_do_evento(aplicado, basico))
            extra = 0
            if recebe and beneficio == "Turbo":
                extra = regras.BONUS_TURBO_COMPRADO   # vale até em pane
                nova += extra

            self.posicoes[robo] = nova
            registros.append(RegistroRobo(robo, sorteado, aplicado, basico,
                                          anterior, nova, extra, escudo))

        # Chegada: somente depois de processar todos (e os benefícios da rodada).
        # Vários robôs na mesma rodada = empate, mesmo com posições diferentes.
        chegaram = [r for r in self.robos if self.posicoes[r] >= regras.META]
        if chegaram:
            self.finalizada = True
            self.vencedores = chegaram
        return registros

    def lideres(self) -> list[str]:
        maior = max(self.posicoes.values())
        return [r for r in self.robos if self.posicoes[r] == maior]

    def resultado_jogador(self) -> str | None:
        """'vitória', 'derrota' ou 'empate' (None se não terminou ou sem jogador)."""
        if not self.finalizada or self.jogador is None:
            return None
        if self.jogador not in self.vencedores:
            return "derrota"
        return "vitória" if len(self.vencedores) == 1 else "empate"
