"""Lê o plano.json (os 100 dias) e escreve o PLANO.md e a pasta de um dia.

Uso:
  python3 ferramentas/plano.py md          # reescreve PLANO.md a partir do plano.json
  python3 ferramentas/plano.py dia 7       # cria dias/dia-007/ com README e uma pasta por item
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TypedDict

RAIZ = Path(__file__).resolve().parent.parent


class Item(TypedDict, total=False):
    tipo: str
    id: str
    nome: str
    topico: str
    peso: int
    origem: str
    nivel: str
    link: str


class Dia(TypedDict):
    dia: int
    data: str
    itens: list[Item]


def carregar(caminho: Path = RAIZ / "plano.json") -> list[Dia]:
    try:
        plano: list[Dia] = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erro:
        raise ValueError(f"plano inválido em {caminho}: {erro}; esperado a lista dos 100 dias") from erro
    return plano


def linha_do_item(item: Item) -> str:
    nivel = f" ({item['nivel']})" if "nivel" in item else ""
    nome = f"[{item['nome']}]({item['link']})" if "link" in item else item["nome"]
    origem = "" if item["tipo"] == "hdlbits" else f" · {item['origem']}"
    return f"- [ ] {nome}{nivel}{origem}"


def temas(dia: Dia) -> str:
    return ", ".join(dict.fromkeys(i["topico"] for i in dia["itens"]))


def plano_md(plano: list[Dia]) -> str:
    partes = ["# Plano dos 100 dias", "",
              ("Gerado de `plano.json` por `python3 ferramentas/plano.py md`. "
               "Marque o `[x]` no README do dia, não aqui."), ""]
    for dia in plano:
        partes += [f"## Dia {dia['dia']:03d} · {dia['data']} · {temas(dia)}", ""]
        partes += [linha_do_item(i) for i in dia["itens"]] + [""]
    return "\n".join(partes)


def readme_do_dia(dia: Dia) -> str:
    partes = [f"# Dia {dia['dia']:03d} · {temas(dia)}", "", f"Data prevista: {dia['data']}.", "",
              "## Itens", ""]
    partes += [linha_do_item(i) for i in dia["itens"]]
    partes += ["", "## Ondas", ""]
    partes += [f"### {i['nome']}\n\n![onda de {i['nome']}]({i['id']}/onda.svg)\n"
               for i in dia["itens"]]
    partes += ["## O que aprendi", "", "- ", ""]
    return "\n".join(partes)


def criar_dia(numero: int, plano: list[Dia]) -> Path:
    dia = next((d for d in plano if d["dia"] == numero), None)
    if dia is None:
        raise ValueError(f"dia {numero} não está no plano; esperado 1 a {len(plano)}")
    pasta = RAIZ / "dias" / f"dia-{numero:03d}"
    if pasta.exists():
        raise ValueError(f"{pasta} já existe; apague ou edite à mão")
    for item in dia["itens"]:
        (pasta / item["id"]).mkdir(parents=True)
    (pasta / "README.md").write_text(readme_do_dia(dia), encoding="utf-8")
    return pasta


def main(argv: list[str]) -> int:
    plano = carregar()
    if argv == ["md"]:
        (RAIZ / "PLANO.md").write_text(plano_md(plano), encoding="utf-8")
        return 0
    if len(argv) == 2 and argv[0] == "dia" and argv[1].isdigit():
        print(criar_dia(int(argv[1]), plano))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
