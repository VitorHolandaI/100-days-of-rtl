"""Testes do vcd2svg: ler um VCD do iverilog e desenhar a onda em SVG."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))

import vcd2svg

VCD = """$date hoje $end
$timescale 1ns $end
$scope module tb $end
$var wire 1 ! clk $end
$var reg 4 " conta [3:0] $end
$scope module dut $end
$var wire 1 # q $end
$upscope $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
0!
b0 "
x#
$end
#5
1!
#10
0!
b1010 "
1#
#20
1!
bz "
"""


class LerVcdTest(unittest.TestCase):
    def setUp(self) -> None:
        self.onda = vcd2svg.ler_vcd(VCD)

    def test_sinais_na_ordem_com_escopo_e_largura(self) -> None:
        nomes = [(s.nome, s.largura) for s in self.onda.sinais]
        self.assertEqual(nomes, [("tb.clk", 1), ("tb.conta", 4), ("tb.dut.q", 1)])

    def test_mudancas_com_tempo_e_valor(self) -> None:
        clk, conta, q = self.onda.sinais
        self.assertEqual(clk.mudancas, [(0, "0"), (5, "1"), (10, "0"), (20, "1")])
        self.assertEqual(conta.mudancas, [(0, "0"), (10, "1010"), (20, "z")])
        self.assertEqual(q.mudancas, [(0, "x"), (10, "1")])

    def test_fim_e_unidade(self) -> None:
        self.assertEqual((self.onda.fim, self.onda.unidade), (20, "1ns"))

    def test_vcd_sem_sinal_da_erro_dizendo_o_que_esperava(self) -> None:
        with self.assertRaisesRegex(ValueError, r"nenhum \$var"):
            vcd2svg.ler_vcd("$enddefinitions $end\n#0\n")


class ApelidoTest(unittest.TestCase):
    def test_mesmo_fio_no_tb_e_no_dut_aparece_uma_vez(self) -> None:
        vcd = ("$scope module tb $end $var wire 1 ! clk $end "
               "$scope module dut $end $var wire 1 ! clk $end $upscope $end $upscope $end "
               "$enddefinitions $end #0 0! #5 1!")
        onda = vcd2svg.ler_vcd(vcd)
        self.assertEqual([s.nome for s in onda.sinais], ["tb.clk"])
        self.assertEqual(onda.sinais[0].mudancas, [(0, "0"), (5, "1")])


class ValorTest(unittest.TestCase):
    def test_vetor_vira_hexa_e_x_z_ficam(self) -> None:
        self.assertEqual(vcd2svg.rotulo("1010", 4), "a")
        self.assertEqual(vcd2svg.rotulo("0", 8), "00")
        self.assertEqual(vcd2svg.rotulo("x", 4), "x")
        self.assertEqual(vcd2svg.rotulo("1z0", 3), "z")


class DesenharTest(unittest.TestCase):
    def test_svg_tem_nome_de_cada_sinal_e_valor_do_barramento(self) -> None:
        svg = vcd2svg.desenhar(vcd2svg.ler_vcd(VCD))
        self.assertTrue(svg.startswith("<svg"))
        for texto in ("tb.clk", "tb.conta", "tb.dut.q", ">a<", "1ns"):
            self.assertIn(texto, svg)

    def test_filtro_por_nome_deixa_so_os_pedidos(self) -> None:
        svg = vcd2svg.desenhar(vcd2svg.ler_vcd(VCD), so=["clk"])
        self.assertIn("tb.clk", svg)
        self.assertNotIn("tb.conta", svg)


if __name__ == "__main__":
    unittest.main()
