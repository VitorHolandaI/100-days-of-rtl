#!/usr/bin/env bash
# Simula um item com o iverilog e desenha a onda.
# Uso: ferramentas/rodar.sh dias/dia-001/wire
# A pasta tem o design e um tb_*.sv que grava "onda.vcd" ($dumpfile).
set -euo pipefail

pasta="${1:?uso: ferramentas/rodar.sh <pasta do item>}"
[ -d "$pasta" ] || { echo "pasta não existe: '$pasta'" >&2; exit 2; }
raiz="$(cd "$(dirname "$0")/.." && pwd)"
cd "$pasta"

shopt -s nullglob
fontes=(*.sv *.v)
tbs=(tb_*.sv tb_*.v)
[ ${#fontes[@]} -gt 0 ] || { echo "nenhum .sv ou .v em '$pasta'" >&2; exit 2; }
[ ${#tbs[@]} -eq 1 ] || { echo "esperado 1 tb_*.sv em '$pasta', achei ${#tbs[@]}" >&2; exit 2; }

mkdir -p build
iverilog -g2012 -Wall -s "$(basename "${tbs[0]%.*}")" -o build/sim "${fontes[@]}"
# o tb termina com $finish; falha de checagem sai com $fatal, que vira código != 0
vvp -n build/sim | tee build/saida.txt
if grep -q "FALHOU" build/saida.txt; then
  echo "o tb imprimiu FALHOU em '$pasta'" >&2
  exit 1
fi
[ -f onda.vcd ] || { echo "o tb não gravou onda.vcd em '$pasta'" >&2; exit 1; }
python3 "$raiz/ferramentas/vcd2svg.py" onda.vcd onda.svg
echo "ok: $pasta/onda.svg"
