"""One-time: add starter translator notes to the crux verses listed in docs/cruxes.md."""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "ingest"))
from build_verses import dump  # noqa: E402

NOTES = {
    "0.1.2": "German Hetzjagd is a hunt (a chase with hounds). Moore's 'holy alliance' alludes to the Holy Alliance of 1815 and is not in the German. See glossary: heilige Hetzjagd.",
    "I.1.1": "Engels's note N2 (1888) limits this to written history.",
    "I.12.3": "Staatsgewalt is state power. Moore has 'the executive of the modern state'. See glossary: Staatsgewalt.",
    "I.18.5": "Free rendering in 1888. Literally: everything belonging to the estates and everything standing evaporates. See glossary: Stand.",
    "I.23.2": "Idiotismus is not 'idiocy' (Idiotie). Hal Draper argued it carries the Greek sense of the idiotes, the private person cut off from public life, and rendered it 'the privatized isolation of rural life'. See glossary.",
    "I.23.3": "19th-century vocabulary of 'barbarian' and 'civilised' nations. Translate as written and explain; see docs/cruxes.md.",
    "I.49.1": "Moore avoids the German term. '[lumpenproletariat]' in the English column is an MIA insertion.",
    "II.13.1": "Aufhebung, not Abschaffung. See glossary: Aufhebung.",
    "II.39.1": "Aufhebung, not Abschaffung. '[Aufhebung]' in the English column is an MIA insertion. See glossary.",
    "II.61.1": "II.61.1 to II.61.4 voice an objector, in quotation marks. The authors' reply starts at II.62.1.",
    "II.65.1": "See glossary: Erkämpfung der Demokratie, and docs/cruxes.md.",
    "II.66.1": "Read with P1872.2.6 (the Commune and the ready-made state machinery). See docs/cruxes.md.",
    "II.67.1": "The 1888 English adds 'necessitate further inroads upon the old social order', which is not in the German.",
    "II.81.1": "One online copy of MEW drops 'die Bedingung für' from this sentence; see SOURCES.md.",
    "IV.12.1": "'Workers of the world, unite!' is the popular form and is in neither edition. See glossary.",
    "P1872.2.4": "'This passage' is the end of Section II, the ten measures (II.67.1 to II.79.1).",
    "P1872.2.6": "Cross-reference II.66.1.",
}


def main():
    done = set()
    for f in sorted((ROOT / "text").glob("*/*.yaml")):
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        changed = False
        for v in doc["verses"]:
            if v["id"] in NOTES and not v.get("notes"):
                v["notes"] = NOTES[v["id"]]
                done.add(v["id"])
                changed = True
        if changed:
            verses = doc.pop("verses")
            dump(f, doc, verses)
    missing = set(NOTES) - done
    print(f"notes added to {len(done)} verses", "missing:" if missing else "", sorted(missing) if missing else "")


if __name__ == "__main__":
    main()
