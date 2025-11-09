#!/usr/bin/env python3
"""
assembler_pass1.py

Pass-I of a two-pass assembler for a pseudo-machine.
- Object-oriented design with Symbol and Literal tables.
- Supports a small instruction set and assembler directives.
- Produces an intermediate file and prints symbol/literal/pool tables.

Usage:
    python3 assembler_pass1.py source.asm
"""

import sys
import re
from typing import List, Tuple, Dict, Optional

# -------------------------
# Data classes / structures
# -------------------------
class Symbol:
    """Represents an entry in the symbol table."""
    def __init__(self, name: str, address: Optional[int] = None, defined: bool = False):
        self.name = name
        self.address = address
        self.defined = defined
        self.forward_references: List[int] = []  # list of line numbers where referenced before definition

    def __repr__(self):
        addr = self.address if self.address is not None else "?"
        return f"Symbol(name={self.name}, addr={addr}, defined={self.defined})"

class Literal:
    """Represents a literal (e.g. =5)."""
    def __init__(self, literal: str, address: Optional[int] = None):
        self.literal = literal  # like "=5" or "='A'"
        self.address = address

    def __repr__(self):
        addr = self.address if self.address is not None else "?"
        return f"Literal({self.literal} @ {addr})"

# -------------------------
# Assembler Pass I class
# -------------------------
class AssemblerPass1:
    """
    Implements pass-I of the assembler:
    - reads source lines
    - builds symbol table, literal table, pool table
    - emits an intermediate file with locctr and cleaned tokens for Pass-II
    """

    # A small sample opcode table (IS = Imperative Statements). All assumed length = 1 word.
    OPCODES = {
        "MOVER": ("IS", 1),
        "MOVEM": ("IS", 1),
        "ADD": ("IS", 1),
        "SUB": ("IS", 1),
        "MULT": ("IS", 1),
        "DIV": ("IS", 1),
        "BC": ("IS", 1),
        "COMP": ("IS", 1),
        "READ": ("IS", 1),
        "PRINT": ("IS", 1),
    }

    # Assembler directives with behaviour
    DIRECTIVES = {"START", "END", "ORIGIN", "EQU", "LTORG", "DS", "DC"}

    REGISTER_SET = {"AREG", "BREG", "CREG", "DREG"}

    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.symtab: Dict[str, Symbol] = {}
        self.littab: List[Literal] = []
        # pooltab contains 0-based indices into littab where each pool starts.
        # We start with an empty pool list; we'll append when the first literal is encountered.
        self.pooltab: List[int] = []
        self.locctr = 0
        self.start_address = 0
        self.intermediate_records: List[Tuple[Optional[int], str]] = []
        # Using a regex to detect integer literals and simple char literal forms
        self.literal_pattern = re.compile(r"^=('[^']'|\-?\d+)$")  # e.g. ='A' or =5 or =-3

    # -------------------------
    # helpers for tables
    # -------------------------
    def add_symbol(self, name: str, address: Optional[int], defined: bool, line_no: int):
        """Add or update symbol."""
        if name in self.symtab:
            sym = self.symtab[name]
            if address is not None:
                sym.address = address
                sym.defined = defined or sym.defined
        else:
            sym = Symbol(name, address, defined)
            self.symtab[name] = sym

        if not defined and line_no is not None:
            sym.forward_references.append(line_no)

    def add_literal(self, lit: str) -> int:
        """Add literal token to littab if not present, return its index."""
        for i, L in enumerate(self.littab):
            if L.literal == lit:
                return i
        # If this is the first literal of a new pool, record pool start index
        if not self.pooltab:
            self.pooltab.append(len(self.littab))
        self.littab.append(Literal(lit))
        return len(self.littab) - 1

    def process_literal_pool(self):
        """
        Assign addresses to literals in the current pool starting from LOCCTR.
        After processing, record next pool start index (which will be current littab length).
        """
        if not self.pooltab:
            return
        pool_start_idx = self.pooltab.pop()  # last started pool
        for i in range(pool_start_idx, len(self.littab)):
            lit = self.littab[i]
            if lit.address is None:
                lit.address = self.locctr
                self.locctr += 1
        # new pool (if later) will start at current littab length; do not append now unless new literal appears

    # -------------------------
    # parsing utilities
    # -------------------------
    def parse_line(self, line: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Tokenize a line into (label, opcode, operands)
        Accepts:
         - LABEL OPCODE OPERAND,OP2
         - OPCODE OPERAND
        """
        # Remove comments (anything after ';' or '#')
        line_nocom = re.split(r"[;#]", line)[0].strip()
        if not line_nocom:
            return None, None, None
        tokens = line_nocom.split()
        label = None

        # If first token ends with ':' treat as label
        if tokens and tokens[0].endswith(':'):
            label = tokens[0][:-1]
            tokens = tokens[1:]

        # Heuristic: if no initial label and token0 is not an opcode/directive/register/literal, treat as label
        if label is None and len(tokens) >= 2:
            t0 = tokens[0].upper()
            if t0 not in self.OPCODES and t0 not in self.DIRECTIVES and not self.is_register(t0) and not self.is_literal(t0):
                label = tokens[0]
                tokens = tokens[1:]

        if not tokens:
            return label, None, None

        opcode = tokens[0].upper()
        operands = " ".join(tokens[1:]) if len(tokens) > 1 else None
        if operands:
            operands = ",".join([op.strip() for op in operands.split(",")])
        return label, opcode, operands

    def is_literal(self, token: str) -> bool:
        return bool(self.literal_pattern.match(token.strip()))

    def is_register(self, token: str) -> bool:
        return token.upper() in self.REGISTER_SET

    def evaluate_expression(self, expr: str) -> Optional[int]:
        """
        Very simple evaluator for expressions like SYMBOL, SYMBOL+5, 100
        Returns None if unresolved.
        """
        expr = expr.replace(" ", "")
        if re.fullmatch(r"-?\d+", expr):
            return int(expr)
        m = re.match(r"^([A-Za-z_]\w*)([+-]\d+)?$", expr)
        if not m:
            return None
        sym_name = m.group(1)
        offset = m.group(2)
        if sym_name not in self.symtab or self.symtab[sym_name].address is None:
            return None
        base = self.symtab[sym_name].address
        if offset:
            return base + int(offset)
        return base

    # -------------------------
    # main processing (Pass-I)
    # -------------------------
    def process(self):
        line_no = 0
        started = False

        for raw_line in self.source_lines:
            line_no += 1
            label, opcode, operands = self.parse_line(raw_line)

            # blank/comment lines -> store as intermediate with no LOC
            if opcode is None and label is None:
                self.intermediate_records.append((None, raw_line.rstrip()))
                continue

            # START directive handling
            if opcode == "START":
                started = True
                if operands:
                    try:
                        self.start_address = int(operands)
                        self.locctr = self.start_address
                    except ValueError:
                        val = self.evaluate_expression(operands)
                        self.locctr = val if val is not None else 0
                else:
                    self.start_address = 0
                    self.locctr = 0
                if label:
                    self.add_symbol(label, self.locctr, True, line_no)
                self.intermediate_records.append((self.locctr, raw_line.rstrip()))
                continue

            # if not started, assume start at 0
            if not started:
                started = True
                self.start_address = 0
                self.locctr = 0

            # if label exists, define it now
            if label:
                self.add_symbol(label, self.locctr, True, line_no)

            # record current LOC for the line
            curr_loc = self.locctr
            self.intermediate_records.append((curr_loc, raw_line.rstrip()))

            # directives
            if opcode in self.DIRECTIVES:
                if opcode == "END":
                    # allocate any remaining literals in pools
                    # there may be multiple pools recorded; process all
                    while self.pooltab:
                        self.process_literal_pool()
                    # END does not consume memory
                elif opcode == "LTORG":
                    # allocate current literal pool
                    self.process_literal_pool()
                elif opcode == "ORIGIN":
                    if operands:
                        val = self.evaluate_expression(operands)
                        if val is None:
                            try:
                                val = int(operands)
                            except ValueError:
                                val = None
                        if val is not None:
                            self.locctr = val
                elif opcode == "EQU":
                    if label and operands:
                        val = self.evaluate_expression(operands)
                        # if unresolved, leave undefined (or you can handle forward symbol)
                        self.add_symbol(label, val, True if val is not None else False, line_no)
                elif opcode == "DS":
                    size = 1
                    if operands:
                        try:
                            size = int(operands)
                        except ValueError:
                            v = self.evaluate_expression(operands)
                            size = v if v is not None else 1
                    self.locctr += size
                elif opcode == "DC":
                    self.locctr += 1
                # other directives: no LOC change
                continue

            # instructions (IS)
            if opcode in self.OPCODES:
                ops = []
                if operands:
                    ops = [o.strip() for o in operands.split(",") if o.strip() != ""]
                for op in ops:
                    if self.is_register(op):
                        continue
                    if self.is_literal(op):
                        # add literal (address assigned at LTORG/END)
                        self.add_literal(op)
                        continue
                    if re.fullmatch(r"-?\d+", op):
                        continue
                    # symbol reference
                    if op not in self.symtab:
                        self.add_symbol(op, None, False, line_no)
                    else:
                        if not self.symtab[op].defined:
                            self.symtab[op].forward_references.append(line_no)
                # assume instruction length 1
                self.locctr += self.OPCODES[opcode][1]
                continue

            # unknown opcode: ignore LOC change but keep intermediate entry
            continue

        # After all source lines, allocate any remaining literal pools
        while self.pooltab:
            self.process_literal_pool()

        # Done

# -------------------------
# Utility / pretty-printing
# -------------------------
def print_tables(assembler: AssemblerPass1):
    # Print and save Symbol Table
    print("\n=== SYMBOL TABLE ===")
    print(f"{'Symbol':<15}{'Address':<10}{'Defined':<10}{'FwdRefs'}")
    with open('symtab.txt', 'w') as f:
        for name, sym in assembler.symtab.items():
            addr = sym.address if sym.address is not None else '-'
            print(f"{name:<15}{addr!s:<10}{str(sym.defined):<10}{sym.forward_references}")
            f.write(f"{name}\t{addr}\n")  # Simple format: name TAB address

    # Print and save Literal Table
    print("\n=== LITERAL TABLE ===")
    print(f"{'Index':<6}{'Literal':<12}{'Address'}")
    with open('littab.txt', 'w') as f:
        for i, lit in enumerate(assembler.littab):
            addr = lit.address if lit.address is not None else '-'
            print(f"{i:<6}{lit.literal:<12}{addr}")
            f.write(f"{lit.literal}\t{addr}\n")  # Simple format: literal TAB address

    print("\n=== POOL TABLE ===")
    print("Pool start indices into literal table (0-based):")
    # Note: pooltab may be empty if all pools were allocated at END/LTORG
    print(assembler.pooltab if assembler.pooltab else "[] (all pools allocated)")

    print("\n=== INTERMEDIATE FILE (first 200 lines) ===")
    for rec in assembler.intermediate_records[:200]:
        loc, line = rec
        loc_str = f"{loc}" if loc is not None else ""
        print(f"{loc_str:<6} {line.rstrip()}")
    print("\n(Intermediate also saved to 'intermediate.txt')")

# -------------------------
# Main commandline handling
# -------------------------
def main():
    if len(sys.argv) >= 2:
        src_filename = sys.argv[1]
    else:
        src_filename = input("Enter assembly source filename: ").strip()

    try:
        with open(src_filename, 'r') as f:
            src_lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {src_filename}")
        return

    assembler = AssemblerPass1(src_lines)
    assembler.process()

    # Write intermediate file
    with open("intermediate.txt", "w") as outf:
        for loc, line in assembler.intermediate_records:
            loc_str = str(loc) if loc is not None else ""
            outf.write(f"{loc_str:<6} {line}\n")

    # Print tables
    print_tables(assembler)

if __name__ == "__main__":
    main()


