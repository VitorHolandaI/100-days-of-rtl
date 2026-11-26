# 100 Days of RTL

Cem dias seguidos escrevendo RTL em SystemVerilog, no espírito do #100DaysOfCode.
Todo dia tem design, testbench e a onda da simulação, tudo aberto.

Os exercícios vêm de três lugares:

- os 244 problemas do [HDLBits](https://www.hdlbits.com/);
- 78 blocos e 3 problemas maiores (cronômetro, semáforo e um RISC-V uniciclo)
  que montei para estudar Verilog;
- as atividades de Lógica Digital e o trabalho final de Arquitetura ASIC e FPGA
  (uma ULA de 8 bits) da especialização em microeletrônica que estou fazendo (CI Inovador, UFSM).

A ordem é por assunto, do fio sozinho até predição de desvio: vetores, módulos,
aritmética, mux e decodificadores, flip-flops, contadores, máquinas de estado,
UART, memórias e FIFO, CDC, pipelines e RISC-V. A ULA vem cedo porque tem prazo
(09/12). O dia a dia está em [PLANO.md](PLANO.md).

## Regras

1. Um dia, um commit (ou mais) com o que foi feito. Dia sem RTL não conta.
2. Cada item tem testbench que confere a saída e imprime `PASSOU` ou `FALHOU`.
3. Cada item tem a onda em `onda.svg`, que aparece no README do dia.
4. Problema do HDLBits só conta depois de passar no site também.

## Como rodar

Precisa de [Icarus Verilog](https://github.com/steveicarus/iverilog) (12 ou mais
novo) e Python 3.11+. Não há dependência de Python.

```bash
python3 ferramentas/plano.py dia 1          # cria dias/dia-001/ com uma pasta por item
cp modelos/tb_modelo.sv dias/dia-001/first-steps-wire/tb_wire.sv
# escreva o design e o tb, depois:
ferramentas/rodar.sh dias/dia-001/first-steps-wire
```

O `rodar.sh` compila com `iverilog -g2012`, roda, para com erro se o tb imprimir
`FALHOU` e transforma `onda.vcd` em `onda.svg`. O CI do GitHub roda todos os
itens a cada push (`ferramentas/rodar_todos.sh`).

## Progresso

| Dia | Data | Tema | Feito |
|---|---|---|---|
| [001](dias/dia-001) | 2026-11-26 | Primeiros passos | |

## Pastas

- `dias/`: um diretório por dia, com o README do dia e uma pasta por item.
- `ferramentas/`: os scripts (plano, simulação e desenho da onda).
- `modelos/`: o modelo de testbench.
- `testes/`: os testes dos scripts em Python.
- `plano.json`: os 100 dias, com os itens de cada um. O `PLANO.md` sai dele.

Licença MIT.
