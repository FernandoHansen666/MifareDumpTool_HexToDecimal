# MIFARE Dump Analyzer - HexToDecimal

## Overview / Visão Geral

### EN

MIFARE Dump Analyzer is a tool for decoding, analyzing, and comparing Mifare Classic dump files. It is designed for users who have extracted card keys using hardware such as Proxmark3 or Chameleon Ultra and exported the data via Mifare Classic Tools (MCT).

Since Mifare Value Blocks store numeric values in Little Endian format (reverse byte order), this application automatically reorders the bytes and converts them to decimal for easier interpretation.

### PT-BR

MIFARE Dump Analyzer é uma ferramenta para decodificação, análise e comparação de arquivos de dump Mifare Classic. Ela foi projetada para usuários que já extraíram as chaves do cartão utilizando hardware como Proxmark3 ou Chameleon Ultra e exportaram os dados via Mifare Classic Tools (MCT).

Como os Value Blocks do Mifare armazenam valores numéricos em formato Little Endian (ordem inversa dos bytes), esta aplicação reorganiza automaticamente os bytes e os converte para decimal para facilitar a interpretação.

---

## Features / Funcionalidades

* Modern GUI built with customtkinter (dark mode support)
* Side-by-side comparison of two dumps
* Automatic detection of valid Value Blocks (based on redundancy rules)
* Advanced search for decimal and hexadecimal values
* Synchronized scrolling between dump views
* Color-coded visualization:

  * Red: Differences between Dump 1 and Dump 2
  * Green: Valid Value Blocks
  * Yellow: Search matches

---

## Compatibility / Compatibilidade

Compatible with dump files exported from Mifare Classic Tools (MCT) after key extraction via Proxmark3 or Chameleon Ultra.

The dump model must follow the format of `ExemploModeloDeDump.mct`.
