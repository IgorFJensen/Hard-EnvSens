#!/usr/bin/env python3
"""Pega simbolos/footprints/3D soltos em libs/ e coloca na biblioteca EnvSens.

Uso: copie os arquivos baixados (.kicad_sym, .kicad_mod, .step) para libs/ e rode
    python scripts/organizar_libs.py
(com o Editor de Simbolos fechado)."""
import os, re, sys, glob, shutil

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
LIB = "EnvSens"
LIBS = os.path.join(ROOT, "libs")
SYM = os.path.join(LIBS, LIB + ".kicad_sym")
PRETTY = os.path.join(LIBS, LIB + ".pretty")
SHAPES = os.path.join(LIBS, LIB + ".3dshapes")
BK = os.path.join(ROOT, "_backup_libs_antigas", "importados")

def rd(p):
    with open(p, encoding="utf-8", newline="") as f: return f.read()
def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f: f.write(s)

def top_children(text):
    i = text.index("(") + 1; depth = 0; out = []; start = None; s = False
    while i < len(text):
        c = text[i]
        if s:
            if c == "\\": i += 2; continue
            if c == '"': s = False
        elif c == '"': s = True
        elif c == "(":
            if depth == 0: start = i
            depth += 1
        elif c == ")":
            if depth == 0: break
            depth -= 1
            if depth == 0: out.append((start, i + 1))
        i += 1
    return out

K10 = [r"\(show_name (?:yes|no)\)", r"\(do_not_autoplace (?:yes|no)\)", r"\(in_pos_files (?:yes|no)\)",
       r"\(duplicate_pin_numbers_are_jumpers (?:yes|no)\)", r"\(duplicate_pad_numbers_are_jumpers (?:yes|no)\)"]
def strip_k10(s):
    for t in K10: s = re.sub(r"[ \t]*" + t + r"[ \t]*\r?\n?", "", s)
    return s

def add_model(fp_path, step):
    s = rd(fp_path)
    if "(model" in s: return False
    s = s.rstrip()
    s = s[:-1].rstrip() + ('\n\t(model "${KIPRJMOD}/libs/%s.3dshapes/%s"\n\t\t(offset (xyz 0 0 0))\n'
                           '\t\t(scale (xyz 1 1 1))\n\t\t(rotate (xyz 0 0 0))\n\t)\n)\n' % (LIB, step))
    wr(fp_path, s); return True

os.makedirs(BK, exist_ok=True); os.makedirs(PRETTY, exist_ok=True); os.makedirs(SHAPES, exist_ok=True)
loose_sym = [p for p in glob.glob(os.path.join(LIBS, "*.kicad_sym")) if os.path.abspath(p) != os.path.abspath(SYM)]
loose_fp = glob.glob(os.path.join(LIBS, "*.kicad_mod"))
loose_step = glob.glob(os.path.join(LIBS, "*.step")) + glob.glob(os.path.join(LIBS, "*.stp"))
if not (loose_sym or loose_fp or loose_step):
    print("Nada novo em libs/."); sys.exit(0)

for p in loose_fp:
    name = os.path.basename(p)[:-10]
    s = rd(p)
    if re.search(r"\(version 202[6-9]\d+\)", s):
        s = re.sub(r"\(version 202[6-9]\d+\)", "(version 20241229)", s)
        s = s.replace('(generator_version "10.0")', '(generator_version "9.0")'); s = strip_k10(s)
    wr(os.path.join(PRETTY, name + ".kicad_mod"), s)
    shutil.move(p, os.path.join(BK, os.path.basename(p))); print("Footprint:", name)
for p in loose_step:
    shutil.copy2(p, os.path.join(SHAPES, os.path.basename(p)))
    shutil.move(p, os.path.join(BK, os.path.basename(p))); print("3D:", os.path.basename(p))

lib = rd(SYM)
nl = "\r\n" if "\r\n" in lib else "\n"
for p in loose_sym:
    t = rd(p)
    for a, b in top_children(t):
        ch = t[a:b]
        if not ch.startswith("(symbol "): continue
        nm = re.match(r'\(symbol "([^"]+)"', ch).group(1)
        ch = strip_k10(ch)
        fpname = None
        def fix(m):
            global fpname
            fpname = m.group(2).split(":", 1)[-1]
            return m.group(1) + '"%s:%s"' % (LIB, fpname) if fpname else m.group(0)
        ch = re.sub(r'(\(property "Footprint" )"([^"]*)"', fix, ch)
        # remove simbolo com o mesmo nome (atualizacao)
        for a2, b2 in top_children(lib):
            if re.match(r'\(symbol "%s"' % re.escape(nm), lib[a2:b2]):
                lib = lib[:a2].rstrip(" \t\r\n") + lib[b2:]; print("  (substituindo versao antiga de %s)" % nm); break
        end = lib.rstrip().rfind(")")
        lib = lib[:end].rstrip() + nl + "\t" + ch + nl + ")" + nl
        print("Simbolo: %s -> footprint %s:%s" % (nm, LIB, fpname))
        fp_path = os.path.join(PRETTY, (fpname or "") + ".kicad_mod")
        for ext in (".step", ".stp"):
            if fpname and os.path.exists(os.path.join(SHAPES, nm + ext)) and os.path.exists(fp_path):
                if add_model(fp_path, nm + ext): print("  3D %s%s ligado ao footprint %s" % (nm, ext, fpname))
        if fpname and not os.path.exists(fp_path):
            print("  ! ATENCAO: footprint %s nao existe em EnvSens.pretty" % fpname)
    shutil.move(p, os.path.join(BK, os.path.basename(p)))
wr(SYM, lib)

for junk in ("how-to-import.htm", "*.bak", "*.lck"):
    for p in glob.glob(os.path.join(LIBS, junk)):
        shutil.move(p, os.path.join(BK, os.path.basename(p)))
print("Pronto. Reabra o Editor de Simbolos/Footprints para ver as pecas novas.")
