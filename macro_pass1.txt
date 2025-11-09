#!/usr/bin/env python3
"""
macro_pass1.py

Pass-I of a two-pass macro-processor (object-oriented implementation).

Usage:
    python3 macro_pass1.py source.asm

If no filename is provided, the program prompts for it.

Assumptions / syntax:
 - Macro start is a line containing the single token: MACRO
 - Next line is the macro header: NAME <param1,param2,...>
   where parameters begin with '&' (e.g. &ARG, &COUNT)
 - Macro body lines follow until a line containing the single token: MEND
 - Macro calls (invocations) are left unchanged in the intermediate file.
 - Parameter references in macro body are substituted with (P,i) in MDT,
   where i is the 1-based position of the formal parameter in ALA.

Output files:
 - intermediate.txt  : original source with macro definitions removed
 - MNT.txt           : Macro Name Table (name -> MDT index)
 - MDT.txt           : Macro Definition Table (indexed lines)
 - ALA_<macro>.txt   : Argument List Array for each macro (param -> position)
"""

import sys
import os
import re
from typing import List, Dict, Tuple

# ----------------------------
# Data classes
# ----------------------------
class Macro:
    """Representation of a macro's metadata produced in Pass-I."""
    def __init__(self, name: str, mdt_index: int):
        self.name = name
        self.mdt_index = mdt_index  # index (0-based) into the MDT where this macro's definition begins
        self.ala: Dict[str, int] = {}  # mapping formal param (like '&ARG') -> position (1-based)
        self.param_list: List[str] = []  # ordered list of formal params

    def __repr__(self):
        return f"Macro(name={self.name}, mdt_index={self.mdt_index}, params={self.param_list})"


class MacroProcessorPass1:
    """
    Implements Pass-I of a macro-processor:
      - Parses source, identifies macro definitions
      - Builds MNT, MDT, and ALA
      - Produces intermediate file (macros removed)
    """
    PARAM_RE = re.compile(r"&\w+")  # matches formal parameters like &ARG1

    def __init__(self, source_lines: List[str]):
        self.source_lines = [ln.rstrip('\n') for ln in source_lines]
        self.mnt: Dict[str, Macro] = {}  # macro name -> Macro object
        self.mdt: List[str] = []         # macro definition table: lines (with (P,i) tokens)
        self.intermediate: List[str] = []  # source lines with macro definitions removed (for pass-II)
        self.macro_def_count = 0

    def process(self):
        """Main pass-I processing loop."""
        i = 0
        n = len(self.source_lines)

        while i < n:
            line = self.source_lines[i].strip()
            if line.upper() == "MACRO":
                # start macro definition: next line should be header (name + params)
                i += 1
                if i >= n:
                    raise ValueError("Unexpected EOF after MACRO directive.")
                header_line = self.source_lines[i].strip()
                macro_name, param_list = self._parse_macro_header(header_line)
                if macro_name in self.mnt:
                    raise ValueError(f"Macro '{macro_name}' redefined.")
                # create Macro entry; mdt_index is current length of mdt
                m = Macro(macro_name, len(self.mdt))
                # build ALA
                for idx, param in enumerate(param_list, start=1):
                    m.ala[param] = idx
                    m.param_list.append(param)
                self.mnt[macro_name] = m
                # write header into MDT using positional parameter tokens
                mdt_header = self._replace_formals_with_pos_tokens(header_line, m.ala)
                self._mdt_append(mdt_header)
                # now read body until MEND
                i += 1
                while i < n:
                    body_line = self.source_lines[i].rstrip()
                    if body_line.strip().upper() == "MEND":
                        # write MEND to MDT and finish macro
                        self._mdt_append("MEND")
                        break
                    # replace formals with (P,i) tokens in MDT and append
                    mdt_body = self._replace_formals_with_pos_tokens(body_line, m.ala)
                    self._mdt_append(mdt_body)
                    i += 1
                else:
                    raise ValueError(f"Missing MEND for macro {macro_name}")
                # finished macro; do not copy macro lines to intermediate
                i += 1
                continue
            else:
                # non-macro line -> copy to intermediate
                self.intermediate.append(self.source_lines[i])
                i += 1

    # ---------------- helpers ----------------
    def _parse_macro_header(self, header_line: str) -> Tuple[str, List[str]]:
        """
        Parse macro header line: "NAME &ARG1,&ARG2" or "NAME" (no params).
        Returns (name, [param1, param2, ...]) with params in the form '&ARG'.
        """
        parts = header_line.split()
        if not parts:
            raise ValueError("Empty macro header.")
        name = parts[0].strip()
        params = []
        if len(parts) > 1:
            # rest may contain comma separated params
            param_text = " ".join(parts[1:]).strip()
            raw_params = [p.strip() for p in param_text.split(',') if p.strip() != ""]
            # ensure params begin with &
            for p in raw_params:
                if not p.startswith("&"):
                    raise ValueError(f"Macro parameter '{p}' should begin with '&'.")
                params.append(p)
        return name, params

    def _replace_formals_with_pos_tokens(self, text: str, ala: Dict[str, int]) -> str:
        """
        Replace occurrences of formal parameters (like &ARG) in text with positional tokens (P,i).
        Example: "MOV R1, &ARG" -> "MOV R1, (P,1)" assuming &ARG -> 1 in ala.
        """
        def repl(match):
            token = match.group(0)  # e.g. &ARG
            if token in ala:
                return f"(P,{ala[token]})"
            else:
                # if a macro body uses an unknown &token, keep it as is (or raise)
                return token

        return re.sub(self.PARAM_RE, repl, text)

    def _mdt_append(self, line: str):
        """Append a line to MDT and keep simple indexing (0-based)."""
        self.mdt.append(line)

    # ---------------- output writers ----------------
    def write_tables_and_intermediate(self, out_dir: str = "."):
        """Write MNT, MDT, ALA files and intermediate file to out_dir."""
        os.makedirs(out_dir, exist_ok=True)
        # Intermediate
        interm_path = os.path.join(out_dir, "intermediate.txt")
        with open(interm_path, "w") as f:
            for ln in self.intermediate:
                f.write(ln + "\n")

        # MNT
        mnt_path = os.path.join(out_dir, "MNT.txt")
        with open(mnt_path, "w") as f:
            f.write("NAME\tMDT_INDEX\tNUM_PARAMS\n")
            for name, macro in self.mnt.items():
                f.write(f"{name}\t{macro.mdt_index}\t{len(macro.param_list)}\n")

        # MDT
        mdt_path = os.path.join(out_dir, "MDT.txt")
        with open(mdt_path, "w") as f:
            f.write("MDT_INDEX\tTEXT\n")
            for idx, line in enumerate(self.mdt):
                f.write(f"{idx}\t{line}\n")

        # ALA per macro
        for name, macro in self.mnt.items():
            ala_path = os.path.join(out_dir, f"ALA_{name}.txt")
            with open(ala_path, "w") as f:
                f.write("PARAM\tPOSITION\n")
                for param, pos in macro.ala.items():
                    f.write(f"{param}\t{pos}\n")

        # Print summary to console
        print(f"Wrote intermediate to: {interm_path}")
        print(f"Wrote MNT to: {mnt_path}")
        print(f"Wrote MDT to: {mdt_path}")
        print("Wrote ALA files for each macro.")

    def print_tables(self):
        """Pretty-print MNT, MDT and ALA to console."""
        print("\n--- MNT (Macro Name Table) ---")
        print("NAME\tMDT_INDEX\tNUM_PARAMS")
        for name, macro in self.mnt.items():
            print(f"{name}\t{macro.mdt_index}\t{len(macro.param_list)}")

        print("\n--- MDT (Macro Definition Table) ---")
        for idx, line in enumerate(self.mdt):
            print(f"{idx}\t{line}")

        print("\n--- ALAs ---")
        for name, macro in self.mnt.items():
            print(f"\nALA for {name}:")
            for param, pos in macro.ala.items():
                print(f"  {param} -> {pos}")

# ----------------------------
# Main: command-line friendly
# ----------------------------
def main():
    if len(sys.argv) >= 2:
        src = sys.argv[1]
    else:
        src = input("Enter assembly source filename: ").strip()

    try:
        with open(src, "r") as f:
            src_lines = f.readlines()
    except FileNotFoundError:
        print(f"Source file not found: {src}")
        return

    mp = MacroProcessorPass1(src_lines)
    try:
        mp.process()
    except Exception as e:
        print("Error during Pass-I:", e)
        return

    mp.print_tables()
    mp.write_tables_and_intermediate(out_dir="output_pass1")
    print("\nPass-I completed. Files written to ./output_pass1")

if __name__ == "__main__":
    main()
