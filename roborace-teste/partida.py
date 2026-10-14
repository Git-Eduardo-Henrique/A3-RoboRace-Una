"""Partida = corrida + desafios/créditos + relatórios, estatísticas e exportações.

É a única camada que a interface usa; assim as regras não ficam duplicadas.
"""
from __future__ import annotations

import csv
import random
from dataclasses import dataclass, field

import regras
from corrida import Corrida, RegistroRobo
from desafios import Desafios


@dataclass
class Relatorio:
    rodada: int
    jogador: str
    resultado_desafio: str
    creditos_recebidos: int
    registros: list[RegistroRobo]
    beneficio: str | None
    custo: int
    efeito: str
    saldo_inicial: int
    ganhos: int
    gastos: int
    saldo_final: int
    chegaram: list[tuple[str, int]] = field(default_factory=list)

    def _evento_texto(self, r: RegistroRobo) -> str:
        if r.evento_sorteado != r.evento_aplicado:
            texto = f"{r.evento_sorteado} → {r.evento_aplicado} (Escudo)"
        else:
            texto = r.evento_sorteado
        if r.bonus_extra:
            texto += f" + Turbo comprado (+{r.bonus_extra})"
        return texto

    def beneficio_do_registro(self, r: RegistroRobo) -> str:
        """Texto do benefício aplicado a esse robô (usado no CSV)."""
        if r.bonus_extra:
            return f"Turbo (+{r.bonus_extra})"
        if r.escudo == "bloqueou":
            return f"Escudo (bloqueou {r.evento_sorteado})"
        if r.escudo == "sem_necessidade":
            return "Escudo (sem necessidade)"
        return "nenhum"

    def texto(self) -> str:
        linhas = [f"RELATÓRIO DA RODADA {self.rodada:02d}",
                  f"Desafio: {self.resultado_desafio}. Crédito recebido: +{self.creditos_recebidos}."]
        for r in self.registros:
            nome = r.robo + (" (você)" if r.robo == self.jogador else "")
            linhas.append(f"{nome}: {self._evento_texto(r)} — posição "
                          f"{r.pos_anterior} → {r.pos_atual} ({r.variacao:+d}).")
        if self.beneficio:
            linhas.append(f"Destino: {self.custo} crédito(s) usados em {self.beneficio} "
                          f"para o robô {self.jogador}.")
            linhas.append(f"Efeito do benefício: {self.efeito}")
            if self.beneficio == "Escudo":
                meu = next(r for r in self.registros if r.robo == self.jogador)
                if meu.escudo == "bloqueou":
                    linhas.append(f"Escudo: bloqueou um obstáculo ({meu.evento_sorteado}).")
                else:
                    linhas.append("Escudo: consumido sem necessidade (nenhum obstáculo).")
        else:
            linhas.append("Destino: nenhum benefício usado nesta rodada.")
        linhas.append(f"Saldo: {self.saldo_inicial} inicial + {self.ganhos} ganhos − "
                      f"{self.gastos} gastos = {self.saldo_final} crédito(s) guardados.")
        linhas.append("Créditos não utilizados ficam guardados para as próximas rodadas.")
        if self.chegaram:
            lista = ", ".join(f"{n} ({p})" for n, p in self.chegaram)
            tipo = "Empate na chegada" if len(self.chegaram) > 1 else "Chegada"
            linhas.append(f"{tipo}: {lista}.")
        return "\n".join(linhas)


class Partida:
    def __init__(self, jogador: str, semente: int | None = None, banco=None,
                 robos=regras.ROBOS_PADRAO):
        # Corrida valida a escolha do jogador (robô inválido -> ValueError).
        self.semente = semente if semente is not None else random.SystemRandom().randrange(1_000_000)
        self.corrida = Corrida(random.Random(self.semente), robos, jogador)
        # Gerador separado para perguntas: responder/comprar não altera o sorteio da pista.
        self.desafios = Desafios(random.Random(f"{self.semente}-perguntas"), banco)
        self.iniciada = False
        self.relatorios: list[Relatorio] = []

    # --- consultas ---------------------------------------------------------
    @property
    def jogador(self) -> str:
        return self.corrida.jogador

    @property
    def finalizada(self) -> bool:
        return self.corrida.finalizada

    def resumo_final(self) -> str:
        if not self.finalizada:
            return "Corrida em andamento."
        rotulo = {"vitória": "VITÓRIA", "derrota": "DERROTA", "empate": "EMPATE"}[
            self.corrida.resultado_jogador()]
        chegaram = ", ".join(f"{n} ({self.corrida.posicoes[n]})" for n in self.corrida.vencedores)
        return f"{rotulo} do seu robô ({self.jogador}). Chegaram: {chegaram}."

    # --- ações do jogador --------------------------------------------------
    def iniciar(self) -> None:
        """Largada: a partir daqui o jogador recebe o desafio da rodada 1."""
        if self.iniciada:
            raise RuntimeError("A corrida já foi iniciada.")
        self.iniciada = True
        self.desafios.preparar_rodada()

    def _exigir_em_andamento(self) -> None:
        if not self.iniciada:
            raise RuntimeError("Inicie a corrida primeiro.")
        if self.finalizada:
            raise RuntimeError("A corrida terminou: novas ações estão bloqueadas.")

    def responder(self, indice: int) -> tuple[bool, str]:
        self._exigir_em_andamento()
        return self.desafios.responder(indice)

    def comprar(self, nome: str) -> int:
        self._exigir_em_andamento()
        return self.desafios.comprar(nome)

    def avancar(self) -> Relatorio:
        self._exigir_em_andamento()
        d = self.desafios
        beneficio = d.consumir_beneficio()
        registros = self.corrida.jogar_rodada(beneficio)
        meu = next(r for r in registros if r.robo == self.jogador)

        custo = regras.BENEFICIOS[beneficio] if beneficio else 0
        rel = Relatorio(
            rodada=self.corrida.rodada, jogador=self.jogador,
            resultado_desafio=d.resultado, creditos_recebidos=d.ganhos,
            registros=registros, beneficio=beneficio, custo=custo,
            efeito=self._descrever_efeito(beneficio, meu),
            saldo_inicial=d.saldo_inicial, ganhos=d.ganhos, gastos=d.gastos,
            saldo_final=d.creditos,
            chegaram=[(n, self.corrida.posicoes[n]) for n in self.corrida.vencedores],
        )
        # Prestação de contas: confere a conta antes de guardar o relatório.
        assert rel.saldo_inicial + rel.ganhos - rel.gastos == rel.saldo_final
        assert rel.gastos == rel.custo
        self.relatorios.append(rel)
        if not self.finalizada:
            d.preparar_rodada()                 # desafio da próxima rodada
        return rel

    @staticmethod
    def _descrever_efeito(beneficio: str | None, meu: RegistroRobo) -> str:
        if beneficio == "Turbo":
            if meu.evento_aplicado == "Pane":
                return f"+{meu.bonus_extra} posições extras, mesmo com a pane (sem movimento básico)."
            return (f"+{meu.bonus_extra} posições extras, além do evento {meu.evento_aplicado} "
                    f"(movimento básico de {meu.basico}).")
        if beneficio == "Escudo":
            if meu.escudo == "bloqueou":
                return (f"{meu.evento_sorteado} virou movimento normal "
                        f"(movimento básico de {meu.basico}).")
            return "nenhum obstáculo ocorreu; o Escudo foi consumido sem alterar o movimento."
        return ""


# --- Estatísticas de várias partidas (desafio 09) ---------------------------
class Estatisticas:
    def __init__(self):
        self.zerar()

    def zerar(self) -> None:
        self.concluidas = self.vitorias = self.derrotas = self.empates = 0
        self.total_rodadas = 0

    def registrar(self, partida: Partida) -> None:
        resultado = partida.corrida.resultado_jogador()
        if resultado is None:
            return
        self.concluidas += 1
        self.total_rodadas += partida.corrida.rodada
        if resultado == "vitória":
            self.vitorias += 1
        elif resultado == "derrota":
            self.derrotas += 1
        else:
            self.empates += 1

    @property
    def media_rodadas(self) -> float:
        return self.total_rodadas / self.concluidas if self.concluidas else 0.0


# --- Exportações (desafios 07 e 08) -----------------------------------------
def exportar_txt(partida: Partida, caminho: str) -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("ROBORACE — HISTÓRICO DA PARTIDA\n")
        f.write(f"Jogador: robô {partida.jogador}\n")
        f.write(f"Semente: {partida.semente}\n")
        f.write(f"Resultado final: {partida.resumo_final()}\n")
        f.write("=" * 60 + "\n\n")
        for rel in partida.relatorios:
            f.write(rel.texto() + "\n\n" + "-" * 60 + "\n\n")


COLUNAS_CSV = ["rodada", "robo", "evento_sorteado", "evento_aplicado", "movimento_basico",
               "posicao_anterior", "posicao_atual", "variacao", "beneficio_aplicado"]


def exportar_csv(partida: Partida, caminho: str) -> None:
    # utf-8-sig e ';' para o Excel em português abrir as colunas corretamente.
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(COLUNAS_CSV)
        for rel in partida.relatorios:
            for r in rel.registros:
                aplicado = rel.beneficio_do_registro(r) if r.robo == partida.jogador else "nenhum"
                w.writerow([rel.rodada, r.robo, r.evento_sorteado, r.evento_aplicado, r.basico,
                            r.pos_anterior, r.pos_atual, r.variacao, aplicado])
