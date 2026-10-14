"""Testes automáticos das regras (rode com: python testes.py)."""
import csv
import os
import tempfile
import unittest

import regras
from corrida import Corrida, deslocamento_do_evento
from desafios import BANCO_PERGUNTAS, Desafios, validar_banco
from partida import Estatisticas, Partida, exportar_csv, exportar_txt


class RngRoteirizado:
    """Gerador falso: devolve eventos e movimentos básicos previamente escolhidos."""

    def __init__(self, eventos, basicos=()):
        self.eventos = list(eventos)
        self.basicos = list(basicos)

    def choices(self, population, weights=None, k=1):
        return [self.eventos.pop(0)]

    def randint(self, a, b):
        return self.basicos.pop(0)

    def shuffle(self, lista):
        pass


def corrida_roteirizada(eventos, basicos, jogador="Azul"):
    return Corrida(RngRoteirizado(eventos, basicos), jogador=jogador)


class TestEventos(unittest.TestCase):
    def test_efeito_de_cada_evento(self):
        self.assertEqual(deslocamento_do_evento("Normal", 2), 2)
        self.assertEqual(deslocamento_do_evento("Pane", 0), 0)
        self.assertEqual(deslocamento_do_evento("Turbo", 2), 5)
        self.assertEqual(deslocamento_do_evento("Super Turbo", 2), 8)
        self.assertEqual(deslocamento_do_evento("Óleo", 3), 1)
        self.assertEqual(deslocamento_do_evento("Óleo", 1), 0)      # mínimo zero
        self.assertEqual(deslocamento_do_evento("Buraco", 3), 0)

    def test_pane_nao_sorteia_movimento_basico(self):
        # só 2 movimentos disponíveis: se a pane sorteasse um, o teste falharia
        c = corrida_roteirizada(["Pane", "Normal", "Normal"], [1, 1])
        c.jogar_rodada()
        self.assertEqual(c.posicoes, {"Azul": 0, "Vermelho": 1, "Verde": 1})

    def test_buraco_perto_de_zero_nunca_fica_negativo(self):
        c = corrida_roteirizada(["Buraco"] * 3, [1, 1, 1])
        c.jogar_rodada()
        self.assertTrue(all(p == 0 for p in c.posicoes.values()))

    def test_buraco_avanca_e_recua(self):
        c = corrida_roteirizada(["Normal"] * 3 + ["Buraco"] * 3, [3, 3, 3, 2, 2, 2])
        c.jogar_rodada()
        c.jogar_rodada()                         # 3 + 2 - 3 = 2
        self.assertEqual(c.posicoes["Azul"], 2)

    def test_chegada_exata_e_acima_de_30(self):
        c = corrida_roteirizada(["Normal"] * 3, [1, 1, 1])
        c.posicoes.update({"Azul": 29, "Vermelho": 28, "Verde": 0})
        c.jogar_rodada()
        self.assertTrue(c.finalizada)
        self.assertEqual(c.vencedores, ["Azul"])
        c = corrida_roteirizada(["Super Turbo", "Normal", "Normal"], [3, 1, 1])
        c.posicoes["Azul"] = 25
        c.jogar_rodada()                         # 25 + 3 + 6 = 34
        self.assertEqual(c.posicoes["Azul"], 34)
        self.assertEqual(c.resultado_jogador(), "vitória")


class TestEmpateEResultado(unittest.TestCase):
    def test_empate_com_posicoes_diferentes_e_rodada_completa(self):
        c = corrida_roteirizada(["Normal", "Turbo", "Normal"], [1, 1, 1])
        c.posicoes.update({"Azul": 29, "Vermelho": 29, "Verde": 5})
        c.jogar_rodada()                         # Azul 30, Vermelho 33
        self.assertEqual(c.vencedores, ["Azul", "Vermelho"])
        self.assertEqual(c.resultado_jogador(), "empate")
        self.assertEqual(c.posicoes["Verde"], 6)  # o terceiro robô também foi processado

    def test_derrota(self):
        c = corrida_roteirizada(["Normal", "Normal", "Normal"], [1, 3, 1], jogador="Azul")
        c.posicoes.update({"Azul": 10, "Vermelho": 28, "Verde": 10})
        c.jogar_rodada()
        self.assertEqual(c.resultado_jogador(), "derrota")

    def test_escolha_invalida(self):
        with self.assertRaises(ValueError):
            Corrida(RngRoteirizado([]), jogador="Amarelo")
        with self.assertRaises(ValueError):
            Partida("")

    def test_sem_rodada_apos_o_fim(self):
        c = corrida_roteirizada(["Normal"] * 3, [1, 1, 1])
        c.posicoes["Azul"] = 29
        c.jogar_rodada()
        with self.assertRaises(RuntimeError):
            c.jogar_rodada()


class TestBeneficios(unittest.TestCase):
    def test_turbo_comprado_em_pane(self):
        c = corrida_roteirizada(["Pane", "Normal", "Normal"], [1, 1])
        c.jogar_rodada("Turbo")
        self.assertEqual(c.posicoes["Azul"], 3)

    def test_turbo_comprado_soma_a_evento_positivo(self):
        c = corrida_roteirizada(["Turbo", "Normal", "Normal"], [2, 1, 1])
        c.jogar_rodada("Turbo")                  # 2 + 3 (evento) + 3 (benefício)
        self.assertEqual(c.posicoes["Azul"], 8)

    def test_turbo_vale_so_para_o_jogador(self):
        c = corrida_roteirizada(["Normal"] * 3, [1, 1, 1])
        c.jogar_rodada("Turbo")
        self.assertEqual(c.posicoes, {"Azul": 4, "Vermelho": 1, "Verde": 1})

    def test_escudo_contra_cada_obstaculo(self):
        for obstaculo in regras.OBSTACULOS:
            c = corrida_roteirizada([obstaculo, "Normal", "Normal"], [2, 1, 1])
            reg = c.jogar_rodada("Escudo")[0]
            self.assertEqual((reg.evento_sorteado, reg.evento_aplicado, reg.escudo),
                             (obstaculo, "Normal", "bloqueou"))
            self.assertEqual(c.posicoes["Azul"], 2)   # pane convertida também sorteia o básico

    def test_escudo_preserva_evento_positivo_e_e_consumido(self):
        c = corrida_roteirizada(["Turbo", "Normal", "Normal"], [1, 1, 1])
        reg = c.jogar_rodada("Escudo")[0]
        self.assertEqual(reg.evento_aplicado, "Turbo")
        self.assertEqual(reg.escudo, "sem_necessidade")
        self.assertEqual(c.posicoes["Azul"], 4)

    def test_escudo_nao_protege_maquina(self):
        c = corrida_roteirizada(["Normal", "Pane", "Normal"], [1, 1])
        reg = c.jogar_rodada("Escudo")[1]
        self.assertEqual(reg.evento_aplicado, "Pane")

    def test_beneficio_pode_provocar_chegada(self):
        c = corrida_roteirizada(["Normal"] * 3, [1, 1, 1])
        c.posicoes["Azul"] = 26
        c.jogar_rodada("Turbo")                  # 26 + 1 + 3 = 30
        self.assertEqual(c.resultado_jogador(), "vitória")


class TestDesafiosECreditos(unittest.TestCase):
    def novo(self):
        d = Desafios(RngRoteirizado([]))
        d.preparar_rodada()
        return d

    def test_banco_valido(self):
        self.assertGreaterEqual(len(BANCO_PERGUNTAS), 12)
        self.assertEqual(validar_banco(BANCO_PERGUNTAS), [])
        self.assertTrue(validar_banco(BANCO_PERGUNTAS[:5]))

    def test_acerto_erro_e_resposta_repetida(self):
        d = self.novo()
        certa = d.pergunta.correta
        acertou, explicacao = d.responder(certa)
        self.assertTrue(acertou)
        self.assertTrue(explicacao)
        self.assertEqual((d.creditos, d.acertos), (1, 1))
        with self.assertRaises(RuntimeError):
            d.responder(certa)                   # segunda resposta na mesma rodada
        self.assertEqual(d.creditos, 1)
        d.preparar_rodada()
        d.responder((d.pergunta.correta + 1) % 3)   # erro: não tira crédito
        self.assertEqual((d.creditos, d.resultado), (1, "erro"))

    def test_compra_saldo_insuficiente_desconto_e_limite(self):
        d = self.novo()
        with self.assertRaises(ValueError):
            d.comprar("Turbo")                   # saldo 0
        d.creditos = 3
        self.assertEqual(d.comprar("Turbo"), 2)
        self.assertEqual(d.creditos, 1)          # descontou na hora
        with self.assertRaises(ValueError):
            d.comprar("Escudo")                  # já há benefício equipado
        self.assertEqual(d.creditos, 1)

    def test_fila_reinicia_ao_esgotar_o_banco(self):
        d = Desafios(RngRoteirizado([]))
        for _ in range(len(BANCO_PERGUNTAS) * 2 + 1):
            d.preparar_rodada()
            self.assertIsNotNone(d.pergunta)


class TestPartidaERelatorios(unittest.TestCase):
    def test_saldo_consistente_em_partida_completa(self):
        p = Partida("Verde", semente=7)
        p.iniciar()
        while not p.finalizada:
            if p.desafios.creditos and p.desafios.beneficio is None:
                p.comprar("Escudo")
            p.responder(p.desafios.pergunta.correta)
            rel = p.avancar()
            self.assertEqual(rel.saldo_inicial + rel.ganhos - rel.gastos, rel.saldo_final)
        self.assertEqual(len(p.relatorios), p.corrida.rodada)
        with self.assertRaises(RuntimeError):
            p.avancar()                          # bloqueado após a chegada
        with self.assertRaises(RuntimeError):
            p.comprar("Turbo")

    def test_mesma_semente_mesmo_resultado(self):
        def jogar():
            p = Partida("Azul", semente=123)
            p.iniciar()
            while not p.finalizada:
                p.avancar()
            return [r.texto() for r in p.relatorios]
        self.assertEqual(jogar(), jogar())

    def test_relatorio_mostra_destino_e_saldo(self):
        p = Partida("Azul", semente=1)
        p.iniciar()
        p.desafios.creditos = 2
        p.desafios.saldo_inicial = 2
        p.comprar("Turbo")
        texto = p.avancar().texto()
        self.assertIn("RELATÓRIO DA RODADA 01", texto)
        self.assertIn("2 crédito(s) usados em Turbo para o robô Azul", texto)
        self.assertIn("Saldo: 2 inicial + 0 ganhos − 2 gastos = 0", texto)

    def test_estatisticas(self):
        e = Estatisticas()
        p = Partida("Azul", semente=5)
        p.iniciar()
        while not p.finalizada:
            p.avancar()
        e.registrar(p)
        self.assertEqual(e.concluidas, 1)
        self.assertEqual(e.vitorias + e.derrotas + e.empates, 1)
        e.zerar()
        self.assertEqual((e.concluidas, e.media_rodadas), (0, 0.0))

    def test_exportacoes(self):
        p = Partida("Azul", semente=9)
        p.iniciar()
        while not p.finalizada:
            p.avancar()
        with tempfile.TemporaryDirectory() as pasta:
            txt, csv_ = os.path.join(pasta, "h.txt"), os.path.join(pasta, "d.csv")
            exportar_txt(p, txt)
            exportar_csv(p, csv_)
            conteudo = open(txt, encoding="utf-8").read()
            self.assertEqual(conteudo.count("RELATÓRIO DA RODADA"), len(p.relatorios))
            self.assertIn("Jogador: robô Azul", conteudo)
            linhas = list(csv.reader(open(csv_, encoding="utf-8-sig"), delimiter=";"))
            self.assertEqual(linhas[0][0], "rodada")
            self.assertEqual(len(linhas) - 1, 3 * len(p.relatorios))


if __name__ == "__main__":
    unittest.main(verbosity=2)
