# ferramentas

Os scripts que fazem o repo funcionar. Nenhum precisa de pacote fora da stdlib.

- `plano.py`: lê o `../plano.json`. `md` reescreve o `../PLANO.md`; `dia N`
  cria `../dias/dia-NNN/` com o README do dia (checklist e um espaço para a
  onda de cada item) e uma pasta vazia por item.
- `rodar.sh <pasta>`: compila o design e o `tb_*.sv` da pasta com o iverilog,
  roda, falha se o tb imprimir `FALHOU` e chama o `vcd2svg.py` para gerar o
  `onda.svg`. Os arquivos de compilação vão para `build/`, fora do git.
- `rodar_todos.sh`: chama o `rodar.sh` em toda pasta que tem `tb_*`. É o que o
  CI (`../.github/workflows/simular.yml`) roda.
- `vcd2svg.py`: lê o VCD e desenha os sinais. Um bit vira onda quadrada, um
  vetor vira barramento com o valor em hexa, x aparece em vermelho e z em
  cinza. O mesmo fio visto no tb e no DUT aparece uma vez só. `--so clk,q`
  limita aos sinais pedidos.
