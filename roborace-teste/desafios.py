"""Desafios educativos, créditos e compra de benefícios (sem interface).

ESTRATÉGIA DO BANCO DE PERGUNTAS: a cada rodada sai uma pergunta de uma fila
embaralhada, sem repetir até esgotar o banco; ao esgotar, o banco é embaralhado
de novo e a sequência recomeça.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

import regras


@dataclass(frozen=True)
class Pergunta:
    enunciado: str
    alternativas: tuple[str, str, str]
    correta: int          # índice (0, 1 ou 2) da alternativa correta
    explicacao: str


BANCO_PERGUNTAS = [
    Pergunta("Em Python, o que faz a linha `posicao = 0`?",
             ("Compara posicao com 0",
              "Cria a variável posicao e atribui o valor 0 a ela",
              "Declara uma constante que nunca pode mudar"), 1,
             "O sinal = é o operador de atribuição: guarda o valor 0 na variável. "
             "Para comparar usa-se ==."),
    Pergunta("Depois de `x = 5` e `x = x + 2`, qual é o valor de x?",
             ("52", "7", "5"), 1,
             "Primeiro calcula-se x + 2 com o valor atual (5), dando 7; depois o "
             "resultado é atribuído de volta a x."),
    Pergunta("Qual é o tipo do valor devolvido por `random.randint(1, 3)`?",
             ("float", "int", "str"), 1,
             "randint devolve um número inteiro (int) entre 1 e 3, incluindo os dois limites."),
    Pergunta("Qual é o resultado de `type(\"30\")`?",
             ("<class 'int'>", "<class 'float'>", "<class 'str'>"), 2,
             "Aspas criam texto (str), mesmo que o conteúdo sejam dígitos. "
             "Para virar número é preciso converter com int(\"30\")."),
    Pergunta("Quanto vale `7 // 2` em Python?",
             ("3.5", "4", "3"), 2,
             "// é a divisão inteira: descarta a parte decimal do quociente (3.5 vira 3)."),
    Pergunta("Qual é o resultado de `10 % 3`?",
             ("1", "3", "0.33"), 0,
             "% devolve o resto da divisão: 10 = 3 × 3 + 1."),
    Pergunta("Quando o bloco de `if posicao >= 30:` é executado?",
             ("Somente quando posicao é exatamente 30",
              "Quando posicao é 30 ou maior",
              "Somente quando posicao é menor que 30"), 1,
             ">= significa maior ou igual; por isso a posição 31 também alcança a chegada."),
    Pergunta("Quantas vezes o laço `while not fim:` se repete?",
             ("Exatamente uma vez",
              "Enquanto a variável fim for True",
              "Enquanto a variável fim for False"), 2,
             "`not fim` é verdadeiro enquanto fim for False. O laço termina quando algo "
             "muda fim para True — ideal quando não se sabe quantas rodadas haverá."),
    Pergunta("Quais valores a variável i assume em `for i in range(3):`?",
             ("0, 1, 2", "1, 2, 3", "0, 1, 2, 3"), 0,
             "range(3) gera 3 valores começando em 0 e parando antes do 3."),
    Pergunta("O que faz `random.seed(42)` antes de sortear números?",
             ("Faz o gerador sempre devolver 42",
              "Fixa o ponto de partida da sequência pseudoaleatória, tornando-a reproduzível",
              "Desliga a aleatoriedade do programa"), 1,
             "Com a mesma semente, a mesma sequência de sorteios se repete. "
             "Isso permite reproduzir simulações e testes."),
    Pergunta("Dada `robos = [\"Azul\", \"Vermelho\", \"Verde\"]`, quanto é `robos[1]`?",
             ("Azul", "Vermelho", "Verde"), 1,
             "Os índices de uma lista começam em 0: [0] Azul, [1] Vermelho, [2] Verde."),
    Pergunta("Se `pos = {\"Azul\": 4}`, qual é `pos[\"Azul\"]` depois de `pos[\"Azul\"] += 3`?",
             ("7", "43", "4"), 0,
             "Em um dicionário, pos[\"Azul\"] += 3 lê o valor 4, soma 3 e guarda 7 na mesma chave."),
    Pergunta("O que `avancar(4, 3)` devolve se `def avancar(p, m): return p + m`?",
             ("4", "7", "None"), 1,
             "return entrega o resultado da expressão ao código que chamou a função: 4 + 3 = 7. "
             "Sem return, a função devolveria None."),
    Pergunta("Em uma simulação, por que guardar posições, rodada e créditos em um estado?",
             ("Para que cada rodada continue a partir dos valores atuais, deixados pela anterior",
              "Para que o computador sorteie números maiores",
              "Porque o Python proíbe usar valores sem salvá-los em arquivo"), 0,
             "O estado é a memória da simulação: cada rodada lê os valores atuais, "
             "os atualiza e passa o resultado para a próxima."),
]


def validar_banco(banco) -> list[str]:
    """Devolve a lista de problemas encontrados (vazia se o banco é válido)."""
    erros = []
    if len(banco) < 12:
        erros.append(f"O banco tem {len(banco)} perguntas; são necessárias pelo menos 12.")
    for i, p in enumerate(banco, start=1):
        if len(p.alternativas) != 3:
            erros.append(f"Pergunta {i}: precisa de exatamente 3 alternativas.")
        if p.correta not in range(len(p.alternativas)):
            erros.append(f"Pergunta {i}: índice da resposta correta inválido.")
        if not p.explicacao.strip():
            erros.append(f"Pergunta {i}: falta a explicação.")
    return erros


class Desafios:
    """Estado de créditos, acertos, pergunta da rodada e benefício equipado."""

    def __init__(self, rng: random.Random, banco=None):
        self.banco = list(banco if banco is not None else BANCO_PERGUNTAS)
        self.rng = rng
        self._fila: list[int] = []
        self.creditos = 0
        self.acertos = 0
        self.beneficio: str | None = None      # equipado para a próxima rodada
        self.pergunta: Pergunta | None = None
        # --- dados da rodada em preparação (alimentam o relatório) ---
        self.respondida = False
        self.resultado = "não respondido"      # "acerto" | "erro" | "não respondido"
        self.saldo_inicial = 0
        self.ganhos = 0
        self.gastos = 0

    def preparar_rodada(self) -> None:
        """Abre a preparação de uma rodada: registra o saldo inicial e sorteia a pergunta."""
        self.saldo_inicial = self.creditos
        self.ganhos = 0
        self.gastos = 0
        self.respondida = False
        self.resultado = "não respondido"
        if not self._fila:                      # banco esgotado (ou primeira vez): reembaralha
            self._fila = list(range(len(self.banco)))
            self.rng.shuffle(self._fila)
        self.pergunta = self.banco[self._fila.pop()]

    def responder(self, indice: int) -> tuple[bool, str]:
        """Registra a resposta (uma por rodada). Devolve (acertou, explicação)."""
        if self.pergunta is None:
            raise RuntimeError("Não há desafio disponível.")
        if self.respondida:
            raise RuntimeError("O desafio desta rodada já foi respondido.")
        if indice not in range(len(self.pergunta.alternativas)):
            raise ValueError("Alternativa inválida.")
        self.respondida = True
        acertou = indice == self.pergunta.correta
        if acertou:
            self.creditos += regras.CREDITOS_POR_ACERTO
            self.ganhos += regras.CREDITOS_POR_ACERTO
            self.acertos += 1
            self.resultado = "acerto"
        else:
            self.resultado = "erro"             # erro não tira créditos nem muda posição
        return acertou, self.pergunta.explicacao

    def comprar(self, nome: str) -> int:
        """Compra um benefício para a próxima rodada. Devolve o custo descontado."""
        if nome not in regras.BENEFICIOS:
            raise ValueError(f"Benefício desconhecido: {nome}.")
        if self.beneficio is not None:
            raise ValueError(f"Já há um benefício equipado ({self.beneficio}). "
                             "Só é possível um por rodada.")
        custo = regras.BENEFICIOS[nome]
        if self.creditos < custo:
            raise ValueError(f"Saldo insuficiente: {nome} custa {custo} crédito(s) "
                             f"e você tem {self.creditos}.")
        self.creditos -= custo                  # desconto imediato
        self.gastos += custo
        self.beneficio = nome
        return custo

    def consumir_beneficio(self) -> str | None:
        """Entrega o benefício equipado à corrida e o consome."""
        nome, self.beneficio = self.beneficio, None
        return nome
