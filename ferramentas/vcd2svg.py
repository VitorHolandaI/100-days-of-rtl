"""Desenha a onda de um .vcd num .svg, só com a stdlib.

Uso: python3 ferramentas/vcd2svg.py onda.vcd onda.svg [--so clk,conta]
O SVG abre no navegador e aparece no README do dia no GitHub.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

ALTURA_LINHA = 30
LARGURA_NOMES = 170
LARGURA_ONDA = 900
ALTO, BAIXO = 6, 22  # y do nível 1 e do nível 0 dentro da linha


@dataclass
class Sinal:
    nome: str
    largura: int
    mudancas: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class Onda:
    sinais: list[Sinal]
    fim: int
    unidade: str


def _ler_cabecalho(palavras: list[str]) -> tuple[dict[str, list[Sinal]], list[Sinal], str, int]:
    """Lê até $enddefinitions; devolve sinais por código, a ordem, a unidade e onde parou."""
    por_codigo: dict[str, list[Sinal]] = {}
    ordem: list[Sinal] = []
    escopo: list[str] = []
    unidade = ""
    i = 0
    while i < len(palavras) and palavras[i] != "$enddefinitions":
        p = palavras[i]
        if p == "$timescale":
            fim = palavras.index("$end", i)
            unidade = "".join(palavras[i + 1:fim])
            i = fim
        elif p == "$scope":
            escopo.append(palavras[i + 2])
        elif p == "$upscope":
            escopo.pop()
        elif p == "$var":
            largura, codigo, nome = int(palavras[i + 2]), palavras[i + 3], palavras[i + 4]
            # o mesmo código é o mesmo fio visto de outro escopo (tb.clk e tb.dut.clk)
            if codigo not in por_codigo:
                sinal = Sinal(".".join([*escopo, nome]), largura)
                por_codigo[codigo] = [sinal]
                ordem.append(sinal)
        i += 1
    return por_codigo, ordem, unidade, i


def _anotar(sinais: list[Sinal], tempo: int, valor: str) -> None:
    for sinal in sinais:
        if not sinal.mudancas or sinal.mudancas[-1][1] != valor:
            sinal.mudancas.append((tempo, valor))


def ler_vcd(texto: str) -> Onda:
    palavras = texto.split()
    por_codigo, ordem, unidade, i = _ler_cabecalho(palavras)
    if not ordem:
        raise ValueError("VCD sem sinal: nenhum $var antes de $enddefinitions; "
                         "esperado um tb com $dumpfile e $dumpvars")
    tempo = 0
    while i < len(palavras):
        p = palavras[i]
        if p.startswith("#"):
            tempo = int(p[1:])
        elif p[0] in "bBrR" and i + 1 < len(palavras):
            _anotar(por_codigo.get(palavras[i + 1], []), tempo, p[1:].lower())
            i += 1
        elif p[0] in "01xXzZ" and len(p) > 1:
            _anotar(por_codigo.get(p[1:], []), tempo, p[0].lower())
        i += 1
    return Onda(ordem, tempo, unidade)


def rotulo(bits: str, largura: int) -> str:
    """Valor de barramento em hexa; com x ou z em qualquer bit, mostra só x ou z."""
    for especial in "xz":
        if especial in bits:
            return especial
    digitos = max(1, (largura + 3) // 4)
    return format(int(bits, 2), "x").zfill(digitos)


def _x(tempo: int, fim: int) -> float:
    return LARGURA_NOMES + LARGURA_ONDA * tempo / max(fim, 1)


def _trechos(sinal: Sinal, fim: int) -> list[tuple[float, float, str]]:
    pontos = [*sinal.mudancas, (fim, "")]
    return [(_x(t, fim), _x(pontos[k + 1][0], fim), v)
            for k, (t, v) in enumerate(pontos[:-1])]


def _bit(sinal: Sinal, fim: int, y: int) -> list[str]:
    caminho: list[str] = []
    partes: list[str] = []
    for x0, x1, v in _trechos(sinal, fim):
        if v in "xz":
            cor = "#c00" if v == "x" else "#888"
            partes.append(f'<rect x="{x0:.1f}" y="{y + ALTO}" width="{x1 - x0:.1f}" '
                          f'height="{BAIXO - ALTO}" fill="{cor}" opacity="0.25"/>')
            continue
        nivel = y + (ALTO if v == "1" else BAIXO)
        caminho.append(f"M{x0:.1f},{nivel} L{x1:.1f},{nivel}")
        caminho.append(f"M{x0:.1f},{y + ALTO} L{x0:.1f},{y + BAIXO}")
    partes.append(f'<path d="{" ".join(caminho)}" stroke="#063" fill="none"/>')
    return partes


def _barramento(sinal: Sinal, fim: int, y: int) -> list[str]:
    partes: list[str] = []
    meio = y + (ALTO + BAIXO) // 2
    for x0, x1, v in _trechos(sinal, fim):
        texto = rotulo(v, sinal.largura)
        cor = "#c00" if texto == "x" else "#036"
        partes.append(f'<polygon points="{x0 + 3:.1f},{y + ALTO} {x1 - 3:.1f},{y + ALTO} '
                      f'{x1:.1f},{meio} {x1 - 3:.1f},{y + BAIXO} {x0 + 3:.1f},{y + BAIXO} '
                      f'{x0:.1f},{meio}" stroke="{cor}" fill="none"/>')
        if x1 - x0 > 8 * len(texto) + 6:
            partes.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{meio + 4}" '
                          f'text-anchor="middle" fill="{cor}">{escape(texto)}</text>')
    return partes


def desenhar(onda: Onda, so: list[str] | None = None) -> str:
    sinais = [s for s in onda.sinais if not so or s.nome.rsplit(".", 1)[-1] in so]
    altura = ALTURA_LINHA * (len(sinais) + 1)
    largura = LARGURA_NOMES + LARGURA_ONDA + 20
    partes = [(f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
               'font-family="monospace" font-size="12">'),
              f'<rect width="{largura}" height="{altura}" fill="white"/>']
    for n, sinal in enumerate(sinais):
        y = n * ALTURA_LINHA
        partes.append(f'<text x="4" y="{y + 18}">{escape(sinal.nome)}</text>')
        desenho = _bit if sinal.largura == 1 else _barramento
        partes.extend(desenho(sinal, onda.fim, y))
    rodape = len(sinais) * ALTURA_LINHA + 18
    partes.append(f'<text x="{LARGURA_NOMES}" y="{rodape}" fill="#555">0</text>')
    partes.append(f'<text x="{LARGURA_NOMES + LARGURA_ONDA}" y="{rodape}" text-anchor="end" '
                  f'fill="#555">{onda.fim} × {escape(onda.unidade or "?")}</text>')
    partes.append("</svg>")
    return "\n".join(partes) + "\n"


def main(argv: list[str]) -> int:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("vcd", type=Path)
    args.add_argument("svg", type=Path)
    args.add_argument("--so", default="", help="nomes separados por vírgula, sem o escopo")
    opcoes = args.parse_args(argv)
    onda = ler_vcd(opcoes.vcd.read_text(encoding="utf-8", errors="replace"))
    so = [n for n in opcoes.so.split(",") if n] or None
    opcoes.svg.write_text(desenhar(onda, so), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
