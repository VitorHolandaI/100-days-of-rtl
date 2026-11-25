#!/usr/bin/env bash
# Roda todo item que já tem tb (usado pelo CI). Sai com erro se algum falhar.
set -euo pipefail
raiz="$(cd "$(dirname "$0")/.." && pwd)"
falhas=0
while IFS= read -r tb; do
  "$raiz/ferramentas/rodar.sh" "$(dirname "$tb")" || falhas=$((falhas + 1))
done < <(find "$raiz/dias" -name 'tb_*.sv' -o -name 'tb_*.v' | sort)
echo "itens com falha: $falhas"
[ "$falhas" -eq 0 ]
