"""Valores e regras do RoboRace em um único lugar.

Nenhum outro arquivo repete esses números: se o professor mudar uma regra
(ex.: meta de 40 posições), basta alterar aqui.
"""

# --- Pista e participantes -------------------------------------------------
META = 30                                   # posição de chegada
ROBOS_PADRAO = ("Azul", "Vermelho", "Verde")  # incluir um nome aqui cria um novo robô

# --- Movimento básico (sorteio inclusivo) ----------------------------------
MOVIMENTO_MIN = 1
MOVIMENTO_MAX = 3

# --- Eventos: nome -> probabilidade em % (a soma deve ser 100) -------------
EVENTOS = {
    "Normal": 50,
    "Pane": 10,
    "Turbo": 15,
    "Super Turbo": 5,
    "Óleo": 10,
    "Buraco": 10,
}
BONUS_TURBO_EVENTO = 3      # evento Turbo: +3 ao movimento básico
BONUS_SUPER_TURBO = 6       # evento Super Turbo: +6 ao movimento básico
REDUCAO_OLEO = 2            # evento Óleo: -2 no movimento básico (mínimo 0)
RECUO_BURACO = 3            # evento Buraco: avança o básico e depois recua 3
OBSTACULOS = ("Pane", "Óleo", "Buraco")  # eventos que o Escudo converte em Normal

# --- Créditos e benefícios comprados (valem só para o jogador) -------------
CREDITOS_POR_ACERTO = 1
BENEFICIOS = {"Turbo": 2, "Escudo": 1}   # nome -> custo em créditos
BONUS_TURBO_COMPRADO = 3                 # benefício Turbo: +3 após o evento

assert sum(EVENTOS.values()) == 100, "As probabilidades dos eventos devem somar 100%"
