"""O plano tem 100 dias, todo item aparece uma vez e o README do dia sai certo."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))

import plano


class PlanoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dias = plano.carregar()

    def test_cem_dias_em_sequencia_e_nenhum_vazio(self) -> None:
        self.assertEqual([d["dia"] for d in self.dias], list(range(1, 101)))
        self.assertTrue(all(d["itens"] for d in self.dias))

    def test_item_aparece_uma_vez_e_hdlbits_tem_link(self) -> None:
        itens = [i for d in self.dias for i in d["itens"]]
        ids = [i["id"] for i in itens]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(i["tipo"] == "hdlbits" for i in itens), 244)
        self.assertTrue(all(i["link"].startswith("https://www.hdlbits.com/")
                            for i in itens if i["tipo"] == "hdlbits"))

    def test_ula_antes_do_prazo(self) -> None:
        datas = [d["data"] for d in self.dias for i in d["itens"] if i["tipo"] == "ula"]
        self.assertTrue(datas and max(datas) < "2026-12-09", datas)

    def test_readme_do_dia_tem_checklist_e_onda_de_cada_item(self) -> None:
        texto = plano.readme_do_dia(self.dias[0])
        self.assertIn("- [ ] [A Single Wire](https://www.hdlbits.com/", texto)
        self.assertIn("(first-steps-wire/onda.svg)", texto)

    def test_item_sem_link_mostra_a_origem(self) -> None:
        item: plano.Item = {"tipo": "bloco", "id": "15-mux", "nome": "15-mux",
                            "origem": "bloco de Verilog do meu estudo"}
        self.assertEqual(plano.linha_do_item(item), "- [ ] 15-mux · bloco de Verilog do meu estudo")


if __name__ == "__main__":
    unittest.main()
