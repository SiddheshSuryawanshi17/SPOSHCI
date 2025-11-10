#!/usr/bin/env python3
"""
macro_pass2.py

Pass-II of a two-pass macro-processor (Python).

Usage:
    python3 macro_pass2.py intermediate.txt MNT.txt MDT.txt

If arguments are omitted, the program will prompt for filenames.

Input formats (as produced by Pass-I):
 - MNT.txt: NAME<TAB>MDT_INDEX<TAB>NUM_PARAMS   (header allowed)
 - MDT.txt: MDT_INDEX<TAB>TEXT                  (index and the stored line)
 - intermediate.txt: original source lines (macro definitions removed)

Output:
 - expanded.txt : source with macro calls expanded (parameter substitution done)

Notes:
 - MDT parameter placeholders are expected in the form: (P,i) where i is 1-based.
 - Actual arguments in macro call are taken positionally (comma-separated).
"""

import sys
import os
import re
from typing import Dict, List, Tuple

PARAM_TOKEN_RE = re.compile(r"\(P\s*,\s*(\d+)\)")  # matches (P,1) or (P, 1) etc.

def read_mnt(mnt_path: str) -> Dict[str, Tuple[int, int]]:
    """
    Read MNT.txt and return dict: macro_name -> (mdt_index, num_params)
    Allows header line; ignores blank lines.
    """
    mnt = {}
    with open(mnt_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # skip header if present
            if line.upper().startswith("NAME") and "MDT" in line.upper():
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            name = parts[0]
            try:
                mdt_index = int(parts[1])
            except ValueError:
                # if second token isn't an int, skip
                continue
            num_params = 0
            if len(parts) >= 3:
                try:
                    num_params = int(parts[2])
                except ValueError:
                    num_params = 0
            mnt[name] = (mdt_index, num_params)
    return mnt

def read_mdt(mdt_path: str) -> Dict[int, str]:
    """
    Read MDT.txt and return dict: index -> text (text as stored in MDT)
    """
    mdt = {}
    with open(mdt_path, 'r') as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            # allow header line "MDT_INDEX\tTEXT"
            if line.upper().startswith("MDT_INDEX"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 1:
                try:
                    idx = int(parts[0])
                    mdt[idx] = ""
                except ValueError:
                    continue
            else:
                try:
                    idx = int(parts[0])
                    text = parts[1]
                    mdt[idx] = text
                except ValueError:
                    # If parsing fails, skip
                    continue
    return mdt

def parse_macro_call_line(line: str, mnt: Dict[str, Tuple[int,int]]) -> Tuple[str, str, List[str]]:
    """
    Try to detect a macro call in the given source line.
    Returns (prefix, macro_name, arg_list) if a macro call found,
    where 'prefix' is the part before macro name (may include label/indentation),
    else returns (None, None, None).
    We look for the first token that matches any macro name in MNT.
    """
    stripped = line.rstrip("\n")
    if not stripped.strip():
        return None, None, None

    # split into tokens preserving the left prefix
    # We'll split at whitespace to get tokens, but we need the prefix (text before macro name).
    tokens = stripped.split()
    # If no tokens, no macro.
    if not tokens:
        return None, None, None

    # Find first token that matches a macro name (exact match)
    for idx, tok in enumerate(tokens):
        if tok in mnt:
            # rebuild prefix as the text up to this token occurrence
            # Find the position of tok in the original line to preserve spacing
            tok_pos = stripped.find(tok)
            prefix = stripped[:tok_pos]
            # The rest after tok
            rest = stripped[tok_pos + len(tok):].strip()
            # If rest starts with something like 'X,Y' or ' X, Y' -> that's actual args
            args = []
            if rest:
                # sometimes invocation may have a label or colon — we assume tok is opcode/macro name
                # Split args by comma
                args = [a.strip() for a in rest.split(',') if a.strip() != ""]
            return prefix, tok, args
    return None, None, None

def substitute_params_in_mdt_line(mdt_line: str, actual_args: List[str]) -> str:
    """
    Replace all occurrences of (P,i) in mdt_line with the corresponding actual argument.
    If i is out of range, replace with empty string.
    """
    def repl(match):
        i_str = match.group(1)
        try:
            i = int(i_str)
            if 1 <= i <= len(actual_args):
                return actual_args[i-1]
            else:
                return ""  # missing argument
        except Exception:
            return ""
    return PARAM_TOKEN_RE.sub(repl, mdt_line)

def expand_intermediate(intermediate_path: str, mnt: Dict[str, Tuple[int,int]], mdt: Dict[int,str], output_path: str):
    """
    Read intermediate file and write expanded file.
    """
    # Build a sorted list of MDT indices for deterministic traversal
    mdt_indices_sorted = sorted(mdt.keys())

    with open(intermediate_path, 'r') as inf, open(output_path, 'w') as outf:
        for raw_line in inf:
            line = raw_line.rstrip("\n")
            prefix, macro_name, actual_args = parse_macro_call_line(line, mnt)

            if macro_name is None:
                # no macro call: write line as-is
                outf.write(line + "\n")
                continue

            # macro call found: get MDT start index
            mdt_start, expected_params = mnt[macro_name]
            # If actual_args length differs, we accept positional mapping (missing -> empty)
            # Expand MDT from mdt_start until 'MEND' line
            idx = mdt_start
            while True:
                if idx not in mdt:
                    # malformed MDT: stop expansion
                    break
                mdt_text = mdt[idx].rstrip()
                # stop if MEND
                if mdt_text.strip().upper() == "MEND":
                    break
                # If MDT header line contains macro name, it might be something like:
                # "INCR (P,1),(P,2)" — we typically don't output the header; we output body lines only.
                # Many academic Pass-II implementations output only the body (not the header).
                # Heuristic: skip the header line if it starts with the macro name.
                first_token = mdt_text.strip().split(None,1)[0] if mdt_text.strip() else ""
                if first_token == macro_name:
                    # header line — skip output (but still perform substitution if needed)
                    # If you prefer to keep header, uncomment the following lines:
                    # substituted = substitute_params_in_mdt_line(mdt_text, actual_args)
                    # outf.write(prefix + substituted + "\n")
                    pass
                else:
                    # substitute positional param tokens with actual arguments
                    substituted = substitute_params_in_mdt_line(mdt_text, actual_args)
                    # Write with the same leading prefix (so labels/indentation before macro call are preserved)
                    outf.write(prefix + substituted + "\n")
                idx += 1
            # finished expanding this macro call; continue with next input line
    print(f"Expansion complete. Wrote expanded source to: {output_path}")

def main():
    if len(sys.argv) >= 4:
        interm = sys.argv[1]
        mntf = sys.argv[2]
        mdtf = sys.argv[3]
    else:
        interm = input("Intermediate filename (e.g. intermediate.txt): ").strip()
        mntf = input("MNT filename (e.g. MNT.txt): ").strip()
        mdtf = input("MDT filename (e.g. MDT.txt): ").strip()

    if not os.path.exists(interm):
        print("Intermediate file not found:", interm)
        return
    if not os.path.exists(mntf):
        print("MNT file not found:", mntf)
        return
    if not os.path.exists(mdtf):
        print("MDT file not found:", mdtf)
        return

    mnt = read_mnt(mntf)
    mdt = read_mdt(mdtf)

    # Debug print (optional)
    print("MNT loaded:", mnt)
    print("MDT loaded (first 10 lines):")
    for k in sorted(mdt.keys())[:20]:
        print(k, "->", mdt[k])

    outpath = "expanded.txt"
    expand_intermediate(interm, mnt, mdt, outpath)

if __name__ == "__main__":
    main()

'''### **Pass 2 of a Macro Processor (in short):**

**Purpose:**
To **expand the macros** using the information stored during Pass 1 and produce the **final expanded source program**.

---

**Main Functions of Pass 2:**

1. **Read the intermediate code** generated by Pass 1.
2. **Detect macro calls** using the **MNT (Macro Name Table)**.
3. **Use MDT (Macro Definition Table)** to fetch the macro’s body.
4. **Use ALA (Argument List Array)** to substitute **formal parameters** with **actual arguments**.
5. **Write the fully expanded source program** as the final output.

---

**In short:**
 **Pass 2** = *Expand macros by replacing macro calls with their definitions (using MNT, MDT, and ALA) to produce the final program ready for assembly.*
'''