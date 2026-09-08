from pathlib import Path
import re, shutil

ROOT = Path(__file__).resolve().parent
old_cards = ROOT / "cards.py"
old_data = ROOT / "card"
new_data = ROOT / "cards"

if old_cards.exists():
    old_cards.unlink()

if old_data.exists():
    if new_data.exists():
        raise RuntimeError("cards/ already exists; refusing to merge automatically")
    old_data.rename(new_data)

for path in ROOT.rglob("*.py"):
    if any(part in {".git", ".plugin-validation-deps", "__pycache__"} for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    original = text

    # Split imports by responsibility. Handles the repository's current simple import forms.
    lines = text.splitlines()
    out=[]
    i=0
    while i < len(lines):
        line=lines[i]
        if line.startswith("from cards import ("):
            block=[line]; i+=1
            while i<len(lines):
                block.append(lines[i])
                if lines[i].strip()==")": break
                i+=1
            names=[x.strip().rstrip(",") for x in block[1:-1] if x.strip()]
            loader=[n for n in names if n in {"CARD_ROOT","load_card","load_card_definition"}]
            model=[n for n in names if n not in loader]
            if model:
                out.append("from card_definition import (")
                out += [f"    {n}," for n in model]
                out.append(")")
            if loader:
                out.append("from card_loader import (")
                out += [f"    {n}," for n in loader]
                out.append(")")
        elif line.startswith("from cards import "):
            names=[x.strip() for x in line[len("from cards import "):].split(",")]
            loader=[n for n in names if n in {"CARD_ROOT","load_card","load_card_definition"}]
            model=[n for n in names if n not in loader]
            if model: out.append("from card_definition import "+", ".join(model))
            if loader: out.append("from card_loader import "+", ".join(loader))
        else:
            out.append(line)
        i+=1
    text="\n".join(out)+("\n" if original.endswith("\n") else "")
    if text != original:
        path.write_text(text, encoding="utf-8")

print("Structure split applied. Now run:")
print('python -m unittest discover -s tests/test_02_cards -p "test_*.py" -v')
print('python -m unittest discover -s tests -p "test_*.py" -v')
