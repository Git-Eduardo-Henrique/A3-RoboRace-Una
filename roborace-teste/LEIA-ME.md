# RoboRace — Relatório de desenvolvimento

Jogo em Python (Tkinter/ttk) em que o jogador escolhe um robô, corre contra dois adversários
controlados pelo computador e responde a desafios de programação para ganhar créditos e
comprar benefícios (Turbo e Escudo).

## Como executar

- **Python:** 3.10 ou superior (desenvolvido e testado com 3.12).
- **Dependências:** nenhuma além da biblioteca padrão. O Tkinter já vem com o Python no Windows e
  no macOS; no Linux, instale com `sudo apt install python3-tk`.
- **Sem internet:** tudo funciona localmente.

```
python main.py          # abre o jogo
python testes.py        # roda os 25 testes automáticos das regras
python simulacao.py     # 100, 1.000 e 10.000 corridas (semente 42) -> resultados_simulacao.txt
```

Como jogar: escolha o robô → **Iniciar corrida** (ou Enter) → (opcional) **Responder desafio** →
(opcional) comprar Turbo/Escudo → **Avançar rodada** (ou Enter). Repita até alguém chegar à posição 30.

## Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `regras.py` | Todos os valores das regras (meta, probabilidades, custos). Única fonte da verdade. |
| `corrida.py` | Lógica da corrida: robôs, rodadas, eventos, chegada, empate. Sem créditos, sem interface. |
| `desafios.py` | Banco de 14 perguntas, créditos, resposta única por rodada, compra e consumo de benefícios. |
| `partida.py` | Junta corrida + desafios, gera os relatórios, estatísticas e exportações TXT/CSV. |
| `interface.py` | Interface gráfica. Não contém regras: só chama `Partida`. |
| `main.py` | Ponto de entrada. |
| `testes.py` | 25 testes automáticos (`unittest`). |
| `simulacao.py` | Séries de corridas automáticas sem benefícios. |
| `resultados_simulacao.txt` | Saída da última execução das simulações. |

Para incluir um novo robô, basta acrescentar o nome em `ROBOS_PADRAO` (`regras.py`); a lógica usa
dicionários e listas e não precisa ser reescrita (a interface só precisa de uma cor em `COR_ROBO`,
opcional).

## Ordem de aplicação das regras (por robô, em cada rodada)

1. Sorteia-se **um** evento (Normal 50%, Pane 10%, Turbo 15%, Super Turbo 5%, Óleo 10%, Buraco 10%).
2. Se for o robô do jogador **com Escudo**: pane, óleo ou buraco viram "Normal". O Escudo é
   consumido mesmo que não haja obstáculo.
3. Se o evento aplicado **não** é pane, sorteia-se o movimento básico (1 a 3). A pane não sorteia
   o básico; se o Escudo converter a pane, o básico é sorteado.
4. Aplica-se o efeito do evento e a posição é limitada a no mínimo 0.
5. Se for o robô do jogador **com Turbo comprado**: soma +3 *depois* dos efeitos do evento
   (inclusive após pane).
6. Só depois de processar **todos** os robôs verifica-se a chegada (posição ≥ 30).
   Vários robôs na mesma rodada = **empate**, mesmo com posições diferentes.

**Justificativas:** o Escudo vem antes porque transforma o evento; o Turbo vem depois porque a
regra pede "depois dos efeitos do evento"; o piso em zero vale ao final do evento (e, por isso, o
Turbo comprado soma sobre uma posição já corrigida); a chegada é checada por último para que
todos tenham a oportunidade de se mover e para que benefícios possam provocar chegada ou empate.
O evento **Turbo** (sorteado, +3 ao básico) é diferente do benefício **Turbo** (comprado por
2 créditos, +3 posições extras só para o jogador).

## Desafios e créditos

- Banco de 14 perguntas (variáveis, atribuição, tipos, operadores, decisões, repetições,
  aleatoriedade, coleções, funções e estado), cada uma com 3 alternativas, 1 correta e explicação.
- **Estratégia do banco:** fila embaralhada, sem repetir até esgotar; ao esgotar, embaralha de novo.
- Uma resposta por rodada; acerto = +1 crédito; erro não tira crédito nem altera a posição;
  responder é opcional; o diálogo é modal (a corrida não avança com ele aberto).
- Um benefício equipado por rodada; compra desconta o custo na hora; é consumido na rodada seguinte
  à compra (ao avançar).

## Desafios de implementação escolhidos (5 de 15)

| Nº | Título | Por que escolhemos | Onde está |
|---|---|---|---|
| 05 | Ajuste do tamanho do texto | Acessibilidade em telas pequenas | `App.aplicar_tamanho` (lista "Texto:" no topo) |
| 07 | Exportação do histórico em texto | Reaproveita os relatórios já gerados | `partida.exportar_txt` (aba Histórico) |
| 08 | Exportação de dados em CSV | Permite analisar a partida em planilha | `partida.exportar_csv` (aba Histórico) |
| 09 | Estatísticas de várias partidas | Mostra uso de estado que persiste entre partidas | `partida.Estatisticas` (aba Estatísticas) |
| 12 | Modo de execução reproduzível | Facilita testes e comparação de partidas | campo "Semente" + `Partida(semente=...)` |

> **A preencher pela equipe:** para cada desafio, registrar um teste com resultado esperado e
> obtido e anexar uma captura de tela ou arquivo (o CSV/TXT exportados servem para 07 e 08).

## Simulações automáticas (sem benefícios, semente 42)

| Corridas | Azul | Vermelho | Verde | Empates | Média de rodadas |
|---|---|---|---|---|---|
| 100 | 36 | 22 | 33 | 9 (9,0%) | 11,59 |
| 1.000 | 307 | 280 | 293 | 120 (12,0%) | 11,63 |
| 10.000 (extra) | 2.875 | 3.028 | 2.973 | 1.124 (11,2%) | 11,75 |

**Análise (rascunho para a equipe revisar):**
- Os três robôs têm exatamente as mesmas regras, então esperamos chances iguais (~29–30% de vitória
  exclusiva cada). Com 100 corridas a diferença (22 a 36) é só ruído; com 10.000 as frequências
  ficam próximas, mas ainda variam entre execuções. Por isso **não** concluímos que o jogo é
  "equilibrado" a partir de uma única execução.
- Os empates (cerca de 11–12%) são frequentes porque a chegada é por rodada e o Super Turbo (+6) e o
  Turbo (+3) fazem saltos grandes perto da meta.
- Média ≈ 11,7 rodadas: o ganho esperado por rodada é cerca de 2,1 posições
  (Normal 1,0 + Turbo 0,75 + Super Turbo 0,4 + Óleo ~0,03 − Buraco ~0,1 + Pane 0).
- Essas estatísticas **não** representam as chances do jogador real, pois ele pode ganhar créditos
  e usar Turbo/Escudo, vantagem que a máquina não tem.

## Nota sobre os testes

Os 25 testes cobrem escolha inválida, cada evento e seus limites, recuo perto de zero, chegada
exata e acima de 30, empate com rodada completa, acerto/erro/resposta repetida, compra com saldo
insuficiente, limite de um benefício, Turbo em pane e somado a evento positivo, Escudo contra cada
obstáculo e sem obstáculo, chegada provocada por benefício, saldo consistente, reprodutibilidade
por semente, bloqueio após a chegada e exportações. Os testes de **interface** (redimensionamento,
foco, capturas de tela) devem ser feitos e documentados manualmente pela equipe.
