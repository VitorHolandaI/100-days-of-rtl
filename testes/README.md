# testes

Testes dos scripts de `../ferramentas/`, com o `unittest` da stdlib. Rode da
raiz com `python3 -m unittest discover -s testes`.

- `test_vcd2svg.py`: leitura do VCD (escopo, largura, mudanças, fio repetido),
  o rótulo em hexa e o SVG.
- `test_plano.py`: o plano tem 100 dias, cada item aparece uma vez, o HDLBits
  tem link, a ULA cai antes do prazo e o README do dia sai com a checklist.
