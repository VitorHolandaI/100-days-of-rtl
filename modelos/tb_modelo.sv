// Copie para a pasta do item como tb_<nome>.sv e troque o que está entre <>.
`timescale 1ns / 1ps

module tb_modelo;
  logic clk = 0;
  always #5 clk = ~clk;

  // <sinais do DUT>
  logic a, b;
  logic y;

  // <instância do design>
  // meu_modulo dut (.a(a), .b(b), .y(y));

  int erros = 0;

  task automatic conferir(input logic esperado, input string caso);
    if (y !== esperado) begin
      $display("FALHOU %s: y=%b, esperado %b", caso, y, esperado);
      erros++;
    end
  endtask

  initial begin
    $dumpfile("onda.vcd");
    $dumpvars(0, tb_modelo);
    // <estímulos e conferências>
    #20;
    if (erros == 0) $display("PASSOU");
    $finish;
  end
endmodule
