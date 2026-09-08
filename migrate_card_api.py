"""Migrate remaining CardDefinition legacy API references.

Run from repository root after the compatibility properties code/kind/trigger_marks
have been removed from card_definition.py.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SKIP_PARTS={".git",".plugin-validation-deps","__pycache__",".venv","venv"}

changed=[]
for path in ROOT.rglob("*.py"):
    if any(part in SKIP_PARTS for part in path.parts):
        continue
    text=path.read_text(encoding="utf-8")
    old=text

    # Mechanical, semantics-preserving field migration.
    text=re.sub(r"\.definition\.code\b", ".definition.card_number", text)
    text=re.sub(r"\bdefinition\.code\b", "definition.card_number", text)
    text=re.sub(r"\.definition\.trigger_marks\b", ".definition.trigger_icons", text)
    text=re.sub(r"\bdefinition\.trigger_marks\b", "definition.trigger_icons", text)

    # kind is now CardType. First convert field name.
    text=re.sub(r"\.definition\.kind\b", ".definition.card_type", text)
    text=re.sub(r"\bdefinition\.kind\b", "definition.card_type", text)

    # Keep comparisons behaviorally equivalent without relying on str-Enum equality.
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*==\s*"character"', r'\1 is CardType.CHARACTER', text)
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*!=\s*"character"', r'\1 is not CardType.CHARACTER', text)
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*==\s*"climax"', r'\1 is CardType.CLIMAX', text)
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*!=\s*"climax"', r'\1 is not CardType.CLIMAX', text)
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*==\s*"event"', r'\1 is CardType.EVENT', text)
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*!=\s*"event"', r'\1 is not CardType.EVENT', text)

    # Helpers such as damage tests compare against a variable `kind` containing
    # legacy strings. Preserve helper interface for now by comparing Enum.value.
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*==\s*kind\b', r'\1.value == kind', text)
    text=re.sub(r'(\b[\w.\[\]()]+\.card_type)\s*!=\s*kind\b', r'\1.value != kind', text)

    if text != old:
        # Add CardType import only where enum constants are actually used.
        if "CardType." in text and not re.search(r"from card_definition import [^\n]*\bCardType\b", text):
            if "from card_definition import (" in text:
                text=text.replace("from card_definition import (", "from card_definition import (\n    CardType,", 1)
            else:
                # Insert after future/module doc imports as a simple standalone import.
                lines=text.splitlines()
                pos=0
                # Safe standalone import near top; Python permits it before other imports.
                if lines and lines[0].startswith('"""'):
                    pos=1
                    while pos<len(lines) and '"""' not in lines[pos]:
                        pos+=1
                    pos=min(pos+1,len(lines))
                lines.insert(pos, "from card_definition import CardType")
                text="\n".join(lines)+("\n" if old.endswith("\n") else "")

        path.write_text(text,encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

# Hard audit: no legacy CardDefinition access may remain.
legacy=[]
patterns=[r"\.definition\.code\b",r"\.definition\.kind\b",r"\.definition\.trigger_marks\b",
          r"\bdefinition\.code\b",r"\bdefinition\.kind\b",r"\bdefinition\.trigger_marks\b"]
for path in ROOT.rglob("*.py"):
    if any(part in SKIP_PARTS for part in path.parts):
        continue
    text=path.read_text(encoding="utf-8")
    for no,line in enumerate(text.splitlines(),1):
        if any(re.search(p,line) for p in patterns):
            legacy.append(f"{path.relative_to(ROOT)}:{no}: {line.strip()}")

print("Changed files:")
for p in changed: print("  ",p)
if legacy:
    print("\nLEGACY REFERENCES STILL PRESENT:")
    for x in legacy: print("  ",x)
    raise SystemExit(1)

print("\nLegacy CardDefinition API audit: PASS")
print("\nNow run:")
print('python -m unittest discover -s tests/test_02_cards -p "test_*.py" -v')
print('python -m unittest discover -s tests -p "test_*.py" -v')
