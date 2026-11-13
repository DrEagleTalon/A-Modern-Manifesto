"""One-time ingest for The German Ideology (GI).

German  Marx and Engels, Die deutsche Ideologie (written 1845-1846), MEW 3, pp. 9-530 (Dietz, Berlin 1969),
        as transcribed at mlwerke.de (github.com/wertform/mlwerke.de, me/me03/). The authors' footnotes
        (their marginal notes, the passages they struck out, their own notes) are on mlwerke's separate page
        me03_anm.htm and are linked from the text as (1) to (77). The zeno.org transcription of the same
        volume (MEW 3, 1958 printing, MARX-EBOOKS mirror, docs/MEW-ZENO/3/) is kept as a collation copy:
        it supplies one footnote and one editorial heading that the mlwerke pages leave out, and it is the
        check for every repair listed in CORRECTIONS.
English None. The 1938 and later English translations are not public domain; the modern draft is
        translated from the German.

Sections follow the authors' divisions:
  0       title, subtitle and the heading of volume I
  P1846   the Vorrede
  I       I. Feuerbach
  LK      Das Leipziger Konzil
  II      II. Sankt Bruno
  III     III. Sankt Max, with "1. Der Einzige und sein Eigentum" (the opening of the critique of Stirner)
  AT1-AT6 the six chapters of "Altes Testament: Der Mensch"
  NT1-NT4 the first four chapters of "Neues Testament: Ich"
  NT5A    5. Der Eigner, A) Meine Macht
  NT5B    [B) Mein Verkehr]
  NT5C    C) Mein Selbstgenuß
  NT6     6. Das hohe Lied Salomonis oder Der Einzige
  AK      2. Apologetischer Kommentar
  SLK     Schluß des Leipziger Konzils
  WS      volume II: its heading and the introduction "Der wahre Sozialismus"
  WSI     I. Die "Rheinischen Jahrbücher" oder Die Philosophie des wahren Sozialismus
  WSIV    IV. Karl Grün (chapters II and III of volume II are lost)
  WSV     V. Der Dr. Georg Kuhlmann aus Holstein
Paragraph 0 of each section holds its heading or headings (AT1.0.1 "Altes Testament", AT1.0.2 "1. Genesis").
The authors' footnotes are <section>.N<k>, numbered in order within each section.

Run once. After the lock file exists the YAML in text/ is the source of truth.
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import mew  # noqa: E402
import segment  # noqa: E402
import versify  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

RAW = WORK / "sources" / "raw" / "de"
FILES = ["me03_011.htm", "me03_017.htm", "me03_078.htm", "me03_101.htm", "me03_168.htm", "me03_222.htm",
         "me03_282.htm", "me03_331.htm", "me03_380.htm", "me03_430.htm", "me03_439.htm", "me03_473.htm",
         "me03_521.htm"]
SRC = ("MEW 3, S. {pages} (Dietz, Berlin 1969) via mlwerke.de; written 1845-1846, first printed in full 1932; "
       "the authors' footnotes from mlwerke's me03_anm.htm")
SRC_EN = "None: no public-domain English translation"

# Local to this ingest; the shared rules in scripts/lib are not changed.
segment.ABBR["de"] = segment.ABBR["de"] | {"Vgl", "i", "cap", "Cap", "Kap", "seqq", "sqq", "ff", "Abt", "Anm", "sog",
                                           "Jahrb", "Bdchen", "Ztg", "geb", "ital", "franz", "engl", "lat", "griech",
                                           "Esq", "ib", "ibid", "Ibid", "Philos", "Phil", "Hrn", "Hr", "Sr", "Matth",
                                           "Joh", "Luk", "MM", "sq", "pag", "Vergl", "vergl", "v", "Wig", "Mark", "Kor", "Mos", "Ps", "Spr", "Kol", "Gal", "Röm", "Offenb"}

# Where each section starts: (file, anchor name on the heading), or (file, None) for the first block.
STARTS = [
    ("me03_009.htm", None, "0"),
    ("me03_011.htm", "I_Vorrede", "P1846"),
    ("me03_017.htm", "I_I", "I"),
    ("me03_078.htm", "I_Das_Leipziger_Konzil", "LK"),
    ("me03_078.htm", "I_II", "II"),
    ("me03_101.htm", "I_III", "III"),
    ("me03_101.htm", "I_III_1_Altes_Testament", "AT1"),
    ("me03_101.htm", "I_III_1_2", "AT2"),
    ("me03_101.htm", "I_III_1_3", "AT3"),
    ("me03_101.htm", "I_III_1_4", "AT4"),
    ("me03_168.htm", "I_III_1_5", "AT5"),
    ("me03_168.htm", "I_III_1_6", "AT6"),
    ("me03_222.htm", "I_III_1_Neues_Testament", "NT1"),
    ("me03_222.htm", "I_III_1_2", "NT2"),
    ("me03_222.htm", "I_III_1_3", "NT3"),
    ("me03_282.htm", "I_III_1_4", "NT4"),
    ("me03_282.htm", "I_III_1_5", "NT5A"),
    ("me03_282.htm", "B_Mein_Verkehr", "NT5B"),     # heading restored from zeno.org, see INSERTS
    ("me03_380.htm", "I_III_1_5_C", "NT5C"),
    ("me03_380.htm", "I_III_1_6", "NT6"),
    ("me03_430.htm", "I_III_Apologetischer_Kommentar", "AK"),
    ("me03_430.htm", "I_Schluss_des_Leipziger_Konzils", "SLK"),
    ("me03_439.htm", "II", "WS"),
    ("me03_439.htm", "II_I", "WSI"),
    ("me03_473.htm", "II_IV", "WSIV"),
    ("me03_521.htm", None, "WSV"),
]

# section id -> (file name stem, English title)
OUT = {
    "0": ("00-title", "The German Ideology"),
    "P1846": ("01-preface", "Preface"),
    "I": ("02-feuerbach", "I. Feuerbach"),
    "LK": ("03-leipzig-council", "The Leipzig Council"),
    "II": ("04-saint-bruno", "II. Saint Bruno"),
    "III": ("05-saint-max/00-saint-max", "III. Saint Max"),
    "AT1": ("05-saint-max/01-old-testament-1", "Old Testament: Man. 1. Genesis, i.e. A Man's Life"),
    "AT2": ("05-saint-max/02-old-testament-2", "Old Testament, 2. The Economy of the Old Covenant"),
    "AT3": ("05-saint-max/03-old-testament-3", "Old Testament, 3. The Ancients"),
    "AT4": ("05-saint-max/04-old-testament-4", "Old Testament, 4. The Moderns"),
    "AT5": ("05-saint-max/05-old-testament-5", "Old Testament, 5. \"Stirner\" Delighted in His Construction"),
    "AT6": ("05-saint-max/06-old-testament-6", "Old Testament, 6. The Free Ones"),
    "NT1": ("05-saint-max/07-new-testament-1", "New Testament: \"I\". 1. The Economy of the New Covenant"),
    "NT2": ("05-saint-max/08-new-testament-2", "New Testament, 2. The Phenomenology of the Egoist in Agreement with Himself"),
    "NT3": ("05-saint-max/09-new-testament-3", "New Testament, 3. The Revelation of John the Divine"),
    "NT4": ("05-saint-max/10-new-testament-4", "New Testament, 4. Peculiarity"),
    "NT5A": ("05-saint-max/11-new-testament-5a", "New Testament, 5. The Owner. A) My Power"),
    "NT5B": ("05-saint-max/12-new-testament-5b", "New Testament, 5. The Owner. B) My Intercourse"),
    "NT5C": ("05-saint-max/13-new-testament-5c", "New Testament, 5. The Owner. C) My Self-Enjoyment"),
    "NT6": ("05-saint-max/14-new-testament-6", "New Testament, 6. The Song of Songs, or The Unique"),
    "AK": ("05-saint-max/15-apologetic-commentary", "2. Apologetic Commentary"),
    "SLK": ("06-close-of-the-leipzig-council", "Close of the Leipzig Council"),
    "WS": ("07-true-socialism/00-true-socialism", "Volume II. True Socialism"),
    "WSI": ("07-true-socialism/01-rheinische-jahrbucher", "I. The \"Rheinische Jahrbücher\", or The Philosophy of True Socialism"),
    "WSIV": ("07-true-socialism/04-karl-grun", "IV. Karl Grün, or The Historiography of True Socialism"),
    "WSV": ("07-true-socialism/05-georg-kuhlmann", "V. Dr. Georg Kuhlmann of Holstein, or The Prophecy of True Socialism"),
}

# Greek set in the Symbol font on mlwerke.de comes out as Latin letters ("sojoz"). Each span is replaced by
# the Greek MEW prints, with accents (Symbol has none). Checked against zeno.org's transliteration.
GREEK = [
    ('<FONT FACE="Symbol"><P ALIGN="RIGHT">a</FONT>', '<P ALIGN="RIGHT">α'),
    ('<FONT FACE="Symbol"><P ALIGN="RIGHT">b</FONT>', '<P ALIGN="RIGHT">β'),
    ('<FONT FACE="Symbol">sojoz</FONT>', "σοφός"),
    ('<FONT FACE="Symbol">wra</FONT>', "ὥρα"),
    ('<FONT FACE="Symbol">eudumia</FONT>', "εὐθυμία"),
    ('<FONT FACE="Symbol">sundhch</FONT>', "συνθήκη"),
    ('<FONT FACE="Symbol">h nohsiz</FONT> <FONT FACE="Symbol">h</FONT> <FONT FACE="Symbol">cad</FONT> <FONT FACE="Symbol">authn</FONT>',
     "ἡ νόησις ἡ καθ' αὑτήν"),
    ('<FONT FACE="Symbol">Auton</FONT> <FONT FACE="Symbol">de</FONT> <FONT FACE="Symbol">noei</FONT> <FONT FACE="Symbol">o</FONT> <FONT FACE="Symbol">nouz</FONT>',
     "αὑτὸν δὲ νοεῖ ὁ νοῦς"),
    ('<FONT FACE="Symbol">h</FONT> <FONT FACE="Symbol">nohsiz</FONT> <FONT FACE="Symbol">thz</FONT> <FONT FACE="Symbol">nohsewz</FONT>',
     "ἡ νόησις τῆς νοήσεως"),
    ('<FONT FACE="Symbol">o</FONT> <FONT FACE="Symbol">deoz</FONT> <FONT FACE="Symbol">agaph</FONT> <FONT FACE="Symbol">estin</FONT>',
     "ὁ θεὸς ἀγάπη ἐστίν"),
    ('<FONT FACE="Symbol">Erox</FONT>', "Ἔρως"),
    ('<FONT FACE="Symbol">agaph</FONT> &lt;(christliche)', "ἀγάπη &lt;(christliche)"),
    ('<FONT FACE="Symbol">etox</FONT>', "ἔρως"),
]

# Transcription slips on mlwerke.de, repaired here and listed in SOURCES.md. Each repair agrees with the
# zeno.org transcription. (old, new) pairs; each old string must occur exactly once in the extracted text.
CORRECTIONS = [
    ('Handel wurde n älteren', 'Handel wurde in älteren'),
    ('wie heim heiligen Bruno', 'wie beim heiligen Bruno'),
    ('werden wir heim "politischen', 'werden wir beim "politischen'),
    ('wenn er heim Einsteigen', 'wenn er beim Einsteigen'),
    ('drum unerträgliche Machte', 'drum unerträgliche Mächte'),
    ('diese transzendenten Machte', 'diese transzendenten Mächte'),
    ('des l8ten Jahrhunderts', 'des 18ten Jahrhunderts'),
    ('wie die ihn umgehende sinnliche', 'wie die ihn umgebende sinnliche'),
    ('damit die ihn umgehende Welt', 'damit die ihn umgebende Welt'),
    ('Produkionskräfte', 'Produktionskräfte'),
    ('entwicklungsfahigste', 'entwicklungsfähigste'),
    ('"ewiges Gesetz ausgesprochen', '"ewiges Gesetz" ausgesprochen'),
    ('Gnostizismus au verantworten', 'Gnostizismus zu verantworten'),
    ('pro ans et focis', 'pro aris et focis'),
    ('Transsubstantion', 'Transsubstantiation'),
    ('omelettel', 'omelette!'),
    ('den leeren Blattern', 'den leeren Blättern'),
    ('zu einem Obergange', 'zu einem Übergange'),
    ('Stoß gehen muß', 'Stoß geben muß'),
    ('Sankt Mix', 'Sankt Max'),
    ('Güter dieser Weit', 'Güter dieser Welt'),
    ('gegenwärtige Weit', 'gegenwärtige Welt'),
    ('bürgerlichen Weit', 'bürgerlichen Welt'),
    ('unmittelbaren Umgehung zum', 'unmittelbaren Umgebung zum'),
    ('unmittelbaren Umgehung.', 'unmittelbaren Umgebung.'),
    ("Der Schlichter schlacht't", "Der Schlächter schlacht't"),
    ('den Schlichter henken', 'den Schlächter henken'),
    ('Der Jochen, schneidt', 'Der Jochem, schneidt'),
    ('Totenbeistattung', 'Totenbestattung'),
    ('im isolierten Lehen, [- -]', 'im isolierten Leben, [- -]'),
    ('"im isolierten Lehen, nicht', '"im isolierten Leben, nicht'),
    ('gegegenübertritt', 'gegenübertritt'),
    ('[cap. Xl]', '[cap. XI]'),
    ('Luther dgibt', 'Luther gibt'),
    ('allen Dingei,', 'allen Dingen,'),
    ('Jacques je bonhomme', 'Jacques le bonhomme'),
    ('"der Geschworen uns', '"der Geschwornen uns'),
    ('WeltverbesserungspIäne', 'Weltverbesserungspläne'),
    ('III, p. 9l)', 'III, p. 91)'),
    ('Paffentums', 'Pfaffentums'),
    ('salasiert', 'salariert'),
    ('Nämlich der Jehildete', 'Nämlich der Jebildete'),
    ('stößt der Ungebildete', 'stößt der Unjebildete'),
    ('auf einer spätem Seite', 'auf einer spätern Seite'),
    ('so ergehen sich hieraus', 'so ergeben sich hieraus'),
    ('Konstruktion ergehen sich', 'Konstruktion ergeben sich'),
    ('(ihid.)', '(ibid.)'),
    ('betrübten Lege', 'betrübten Lage'),
    ('werkltätige', 'werkeltägige'),
    ('Gesinung', 'Gesinnung'),
    ('einen hoher Beruf', 'einen hohen Beruf'),
    ('toutes ccs belles', 'toutes ces belles'),
    ('diese Zweideutig zu', 'diese Zweideutigkeit zu'),
    ('Sozialsten', 'Sozialisten'),
    ('naturalibusa', 'naturalibus'),
    ('in obiger Steile', 'in obiger Stelle'),
    ('keine Pharisaer', 'keine Pharisäer'),
    ('mit den erstem,', 'mit den erstern,'),
    ('Gemülsaffektion', 'Gemütsaffektion'),
    ('Begierden beistimmen [lasse', 'Begierden be]stimmen [lasse'),
    ('als antreibendens', 'als antreibenden'),
    ('Zusammenghangslosigkeit', 'Zusammenhangslosigkeit'),
    ('räsornert', 'räsoniert'),
    ('kräftiglich au vermahnen', 'kräftiglich zu vermahnen'),
    ('Sancho kümmert ich', 'Sancho kümmert sich'),
    ('Ihr Einein', 'Ihr Einen'),
    ('was Mit Recht ist', 'was Mir Recht ist'),
    ('Klugheitsmaxirnen', 'Klugheitsmaximen'),
    ('bewußtlosen Laib', 'bewußtlosen Leib'),
    ('Mir wiederfahren', 'Mir widerfahren'),
    ('Rechtbegriffs', 'Rechtsbegriffs'),
    ('Recht mit dein Meinigen', 'Recht mit dem Meinigen'),
    ('-- Mach, Recht Meiner', '-- Macht, Recht Meiner'),
    ('Anthithesen', 'Antithesen'),
    ('"an Bedingen,', '"an Bedingungen,'),
    ('bestände diese Versuch', 'bestände dieser Verbrauch'),
    ('die unangenehmst Tätigkeit', 'die unangenehmste Tätigkeit'),
    ('"Zunchächst"', '"Zunächst"'),
    ('Registrationshill', 'Registrationsbill'),
    ('die reine Tal des', 'die reine Tat des'),
    ('Roß Clavileno besiegen', 'Roß Clavileno bestiegen'),
    ('ein Raffel steckt', 'ein Raffael steckt'),
    ('eine sociéte"', 'eine société"'),
    ('diese "sociéte"', 'diese "société"'),
    ('appos[itioneml', 'appos[itionem]'),
    ('Metallgeld für des wichtigste', 'Metallgeld für das wichtigste'),
    ('so sehr vorn Handel', 'so sehr vom Handel'),
    ('sondern vorn "Verein"', 'sondern vom "Verein"'),
    ('gehören,1.a. auch', 'gehören, u. a. auch'),
    ('Exploititionstheorie', 'Exploitationstheorie'),
    ('um sie sm Verein', 'um sie im Verein'),
    ('Hier hin ich Mensch', 'Hier bin ich Mensch'),
    ('Deine Rand ist', 'Deine Hand ist'),
    ('e bellicosa Qus o peito', 'e bellicosa Que o peito'),
    ('Cesee tudo', 'Cesse tudo'),
    ('nur der - Urmensch."', 'nur der - Unmensch."'),
    ('"sicli nur', '"sich nur'),
    ('p. l80.', 'p. 180.'),
    ('Voraussetzung bat.', 'Voraussetzung hat.'),
    ('Philos[phiae]', 'Philos[ophiae]'),
    ('(p. l89)', '(p. 189)'),
    ('folglich such nicht', 'folglich auch nicht'),
    ('so muß such Alles', 'so muß auch Alles'),
    ('im Worte, im Lagos,', 'im Worte, im Logos,'),
    ('soberano Dc Alexandría', 'soberano De Alexandría'),
    ('Soziaismus', 'Sozialismus'),
    ('Einwendugen', 'Einwendungen'),
    ('Noi me tangere', 'Noli me tangere'),
    ('aufreihende Anspannung', 'aufreibende Anspannung'),
    ('zum wahren Lehen', 'zum wahren Leben'),
    ('Mein ganzes Lehen', 'Mein ganzes Leben'),
    ('Schar junger Rasse"', 'Schar junger Rosse"'),
    ('Genusse meines Liebens', 'Genusse meines Lebens'),
    ('von Munds', 'von Mundts'),
    ('freien Menschentuns', 'freien Menschentums'),
    ("'Phönomenologie '", "'Phänomenologie'"),
    ('seit Leasing und Kant', 'seit Lessing und Kant'),
    ('Luis Blanc', 'Louis Blanc'),
    ('Heßschcn', 'Heßschen'),
    ('comte de Gabarrus', 'comte de Cabarrus'),
    ('Karl dem Grollen', 'Karl dem Großen'),
    ('Hauptwerke seine, Lebens', 'Hauptwerke seines Lebens'),
    ("Tout par I'industrie", "Tout par l'industrie"),
    ('allgemeine Setze aus', 'allgemeine Sätze aus'),
    ('Zitate mir folgenden', 'Zitate mit folgenden'),
    ('aux prêtes Égyptiens', 'aux prêtres Égyptiens'),
    ('p. 47l-482', 'p. 471-482'),
    ('Gerechtigkeit uns raubt', 'Gerechtigkeit und raubt'),
    ('Jeder Uberfluß', 'Jeder Überfluß'),
    ('Durcbpeitschens', 'Durchpeitschens'),
    ('allen ihren Gutern', 'allen ihren Gütern'),
    ('Vabet irrt', 'Cabet irrt'),
    ('Cahet fährt', 'Cabet fährt'),
    ('diesem Drangen und', 'diesem Drängen und'),
    ('A. Communismus, Socialismus, Humanismus"', 'A. "Communismus, Socialismus, Humanismus"'),
    ('"des "Buchs"', '"des Buchs"'),
    # words broken across a page whose joined form zeno.org does not have
    ('italie- [[S345]] nischen', '[[S345]] italienischen'),
    ('Kno- [[S347]] chenmehl', '[[S347]] Knochenmehl'),
    ('An-und-für- [[S349]] sich-Seienden', '[[S349]] An-und-für-sich-Seienden'),
    ('Ritterlich- [[S383]] keit', '[[S383]] Ritterlichkeit'),
    ('National- [[S412]] sprache', '[[S412]] Nationalsprache'),
]

# The same for the footnote page me03_anm.htm.
NOTE_CORRECTIONS = [
    ("[Randbemerkung von Marx:)", "[Randbemerkung von Marx:]"),
    ("Verhältnis zu meiner Umgehung", "Verhältnis zu meiner Umgebung"),
    ("Guilliotine", "Guillotine"),
    ("gestrichen:] Da: wirkliche", "gestrichen:] Das wirkliche"),
    ("plus au moins", "plus ou moins"),
    ("im direkten Widerspruch sieht", "im direkten Widerspruch steht"),
    ("grau werden, Womit", "grau werden, womit"),
]

# Text the mlwerke.de pages leave out, restored from zeno.org: MEW's editorial heading "[B) Mein Verkehr]".
# (text it follows or precedes, inserted text, "after", "before" or "heading-before")
INSERTS = [
    ("[...] zeigt er nur wieder seine Leichtgläubigkeit", "[B) Mein Verkehr]", "heading-before"),
]

# A footnote whose text is missing from me03_anm.htm (the page links it as a bare "(99)"); text from zeno.org.
EXTRA_NOTES = {99: ['Vgl. "Die heilige Familie", p. 266.']}


# ---------------------------------------------------------------- reading mlwerke.de

def decode(path):
    b = Path(path).read_bytes()
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252")       # œ and Œ as 0x9c and 0x8c, § as 0xa7


CONNECTOR = re.compile(r"^[}{=\-\s]*$")


def _cell(html):
    return mew._text(mew._mark(html))


def _tables(html):
    """Equation tables and parallel columns become ordinary <P> blocks.

    Parallel columns (two prose columns side by side, Stirner and the authors' parody of him, Grün and
    Cabet) are read column by column. Every other table is read row by row: cells that are only braces,
    dashes or "=" are layout and become " = " or " - "; a row whose first cell is empty continues the
    equation chain of the row above."""
    def conv(m):
        rows = []
        for tr in re.finditer(r"<TR\b.*?(?=<TR\b|</TABLE>)", m.group(0), re.S | re.I):
            cells = re.findall(r"<TD\b[^>]*>(.*?)(?=<TD\b|</TR>|<TR\b|$)", tr.group(0), re.S | re.I)
            rows.append(cells)
        texts = [[_cell(c) for c in r] for r in rows]
        content = [[t for t in r if t and not CONNECTOR.match(t)] for r in texts]
        parallel = (all(len(r) <= 2 for r in content) and not any(CONNECTOR.match(t) and t for r in texts for t in r)
                    and any(len(r) == 2 and min(len(r[0]), len(r[1])) > 60 and not re.match(r"^[=-]", r[1]) for r in content))
        out = []
        if parallel:
            for col in (0, 1):
                for r in rows:
                    nonempty = [c for c in r if _cell(c)]
                    if len(nonempty) > col:
                        out.append('<P CLASS="PAR">' + re.sub(r"</?P\b[^>]*>", " ", nonempty[col]) + "</P>")
            return "\n".join(out)
        for r, tx in zip(rows, texts):
            parts = []
            for c, t in zip(r, tx):
                if not t:
                    continue
                if CONNECTOR.match(t):
                    sym = "=" if "=" in t else ("-" if "-" in t else "")
                    if sym:
                        parts.append(sym)
                    continue
                parts.append(re.sub(r"</?P\b[^>]*>", " ", c))
            if not parts:
                continue
            cont = bool(re.match(r"^(=|-)", " ".join(t for t in tx if t and not re.fullmatch(r"(\[\[S\d+\]\]\s*)+", t))))
            out.append(f'<P CLASS="{"ROWC" if cont else "ROW"}">{" ".join(parts)}</P>')
        return "\n".join(out)
    return re.sub(r"<TABLE\b.*?</TABLE>", conv, html, flags=re.S | re.I)


# Links to the footnote page come in several shapes: "(12)" inside the link, "(54" inside it and ")" after
# the back anchor, with <FONT> tags in between. The number shown, not the link target, names the note: the
# link for (36) points at #M35.
NOTE_LINK = re.compile(r'<A HREF="me03_anm\.htm#M\d+">((?:(?!</A>).)*?)</A>((?:\s*<A NAME="Z\d+">\s*</A>)?(?:\s*</?FONT[^>]*>)*\s*\))?', re.I | re.S)


def _note_marker(m):
    inner = re.sub(r"<[^>]+>", "", m.group(1))
    n = re.search(r"\((\d+)", inner).group(1)
    tail = m.group(2) or ""
    if ")" in inner and tail:
        return f" [[F{n}]] " + tail      # the bracket after belongs to the text
    return f" [[F{n}]] "


def read_page(name):
    """Blocks of one mlwerke.de page: {kind, text, anchors, file}. Inline markers as in parse_mew:
    [[S17]] MEW page 17 starts here; [[F12]] the authors' footnote 12 (mlwerke numbering) attaches here."""
    raw = decode(RAW / name).replace("\r", "")
    body = re.split(r"<BODY[^>]*>", raw, flags=re.I)[1]
    body = re.split(r"</BODY>", body, flags=re.I)[0]
    for a, b in GREEK:
        if a in body:
            body = body.replace(a, b)
    body = re.sub(NOTE_LINK, _note_marker, body)
    body = body.replace("Tochter (99) ist", "Tochter [[F99]] ist")
    body = re.sub(r'<A HREF="#S\d+">(.*?)</A>', r"\1", body, flags=re.I | re.S)
    body = _tables(body)
    body = mew._mark(body)
    out = []
    for m in re.finditer(r"<P\b([^>]*)>(.*?)(?=<P\b|$)", body, flags=re.S | re.I):
        attr, inner = m.group(1), m.group(2)
        anchors = [a for a in re.findall(r'<A NAME="([A-Za-z][A-Za-z0-9_]*)"', inner, re.I) if not re.fullmatch(r"[SZM]\d+", a)]
        inner = re.sub(r"<BR\s*/?>", " ", inner, flags=re.I)
        txt = mew._text(inner)
        if not txt:
            continue
        al = re.search(r'ALIGN="(\w+)"', attr, re.I)
        cl = re.search(r'CLASS="(\w+)"', attr, re.I)
        out.append({"align": al.group(1).upper() if al else "", "cls": cl.group(1) if cl else "",
                    "anchors": anchors, "text": txt, "file": name})
    return out


def title_page():
    """Title and subtitle from MEW's title page (me03_009.htm); the rest of that page is MEW's editorial note."""
    html = decode(RAW / "me03_009.htm")
    title = mew._text(re.search(r"<h1>(.*?)</h1>", html, re.S).group(1))
    sub = mew._text(re.sub(r"<br\s*/?>", " ", re.search(r"</h1>\s*<p>(.*?)</p>", html, re.S).group(1)))
    return [{"align": "CENTER", "cls": "", "anchors": [], "text": title, "file": "me03_009.htm"},
            {"align": "", "cls": "", "anchors": [], "text": sub, "file": "me03_009.htm"}]


def read_notes():
    """The authors' footnotes from me03_anm.htm: {n: [paragraph, ...]}."""
    raw = decode(RAW / "me03_anm.htm").replace("\r", "")
    body = re.split(r"<BODY[^>]*>", raw, flags=re.I)[1]
    # three anchor forms on this page: <A NAME="M1">(1)</A>, (51<A NAME="M51"></A>) and one anchor
    # left open across a paragraph end (note 14)
    body = re.sub(r'<A NAME="M(\d+)"></P>\s*<P>\((\d+)\)</A>', r'</P>\n<P><A NAME="M\1">(\2)</A>', body)
    body = re.sub(r'\((\d+)<A NAME="M(\d+)"></A>\)', r'<A NAME="M\2">(\1)</A>', body)
    notes, cur, applied = {}, None, []
    for m in re.finditer(r"<P\b([^>]*)>(.*?)(?=<P\b|</BODY>|$)", body, flags=re.S | re.I):
        inner = m.group(2)
        start = re.search(r'<A NAME="M(\d+)">\((\d+)\)</A>', inner, re.I)
        if start:
            cur = int(start.group(1))
            notes[cur] = []
            inner = inner[:start.start()] + inner[start.end():]
        if cur is None:
            continue
        end = re.search(r'<A HREF="[^"]*#Z\d+">&lt;=</A>', inner, re.I)
        if end:
            inner = inner[:end.start()]
        inner = re.sub(r"<BR\s*/?>", " ", inner, flags=re.I)
        txt = mew._text(inner)
        for a, b in NOTE_CORRECTIONS:
            if a in txt:
                txt = txt.replace(a, b)
                applied.append(a)
        if txt:
            notes[cur].append(txt)
        if end:
            cur = None
    assert sorted(applied) == sorted(a for a, _ in NOTE_CORRECTIONS), "note correction not applied"
    return notes


def zeno_words():
    """Every word of the zeno.org transcription, for checking re-joined words."""
    words = set()
    for f in sorted(RAW.glob("ME03-*.html")):
        body = f.read_text(encoding="utf-8").partition("<aside")[0]
        words |= set(re.findall(r"[\wäöüÄÖÜß]+", BeautifulSoup(body, "html.parser").get_text(" ")))
    return words


def rejoin(text, vocab, log):
    """Words the transcriber left broken: at a line end ("aber- gläubige") or across a page marker
    ("Wechsel [[S18]] reiterei"). A pair is joined only when zeno.org has the joined word."""
    def hy(m):
        w = m.group(1) + m.group(2)
        if w in vocab and m.group(2) not in ("und", "oder", "bis", "wie", "als"):
            log.append(f"{m.group(1)}- {m.group(2)}")
            return w
        return m.group(0)
    text = re.sub(r"\b([A-Za-zäöüÄÖÜß]+)- ([a-zäöüß][a-zäöüß]+)", hy, text)

    def pg(m):
        w = m.group(1) + m.group(3)
        if w in vocab and m.group(3) not in ("und", "oder", "sein", "zu"):
            log.append(f"{m.group(1)} {m.group(2)} {m.group(3)}")
            return f"{m.group(2)} {w}"
        return m.group(0)
    return re.sub(r"\b([A-Za-zäöüÄÖÜß]+)-? (\[\[S\d+\]\]) ([a-zäöüß][a-zäöüß]+)", pg, text)


# ---------------------------------------------------------------- blocks -> paragraphs

CENTER_AS_P = ("Freiheit des Menschen - Freiheit Meiner", "Der Begriff Mensch ist nicht wirklicher Mensch")
SIGNATURE = ("Ende des Alten Testaments",)


def classify(b):
    t = versify.clean_text(b["text"])
    if not re.search(r"[A-Za-zÄÖÜäöüß0-9]", t):
        return None                                      # separator rules "__________", "*"
    if b["align"] == "CENTER" and b["cls"] == "":
        if t.startswith(SIGNATURE):
            return "signature"
        if t.startswith(CENTER_AS_P):
            return "p"
        return "heading"
    return "p"


def stream():
    vocab = zeno_words()
    joins = []
    blocks = title_page()
    for f in FILES:
        for b in read_page(f):
            b["text"] = rejoin(b["text"], vocab, joins)
            blocks.append(b)
    # repairs and insertions, each applied exactly once
    for a, new in CORRECTIONS:
        hits = [b for b in blocks if a in b["text"]]
        assert len(hits) == 1 and hits[0]["text"].count(a) == 1, f"correction {a!r}: {len(hits)} blocks"
        hits[0]["text"] = hits[0]["text"].replace(a, new)
    for ctx, ins, where in INSERTS:
        hits = [i for i, b in enumerate(blocks) if ctx in b["text"]]
        assert len(hits) == 1, f"insert at {ctx!r}: {len(hits)} blocks"
        b = blocks[hits[0]]
        if where == "after":
            b["text"] = b["text"].replace(ctx, ctx + ins, 1)
        elif where == "before":
            b["text"] = b["text"].replace(ctx, ins + ctx, 1)
        elif where == "heading-before":
            blocks.insert(hits[0], {"align": "CENTER", "cls": "", "anchors": ["B_Mein_Verkehr"], "text": ins, "file": b["file"]})
    return blocks, joins


def sections(blocks):
    starts = {(f, a): sid for f, a, sid in STARTS}
    secs, cur, seen_file = [], None, set()
    for b in blocks:
        sid = None
        for a in b["anchors"]:
            sid = sid or starts.get((b["file"], a))
        if b["file"] not in seen_file:
            seen_file.add(b["file"])
            sid = sid or starts.get((b["file"], None))
        kind = classify(b)
        if sid:
            cur = {"sid": sid, "paras": []}
            secs.append(cur)
        if kind is None:
            continue
        prev = cur["paras"][-1] if cur["paras"] else None
        if b["cls"] == "ROWC" and prev is not None and prev.get("row"):
            prev["text"] += " " + b["text"]          # "= ..." continues the equation of the row above
            continue
        cur["paras"].append(P(kind, b["text"], row=b["cls"] in ("ROW", "ROWC"), par=b["cls"] == "PAR"))
    return secs


# ---------------------------------------------------------------- sentences

CITATION = re.compile(r"""^["']?\s*\(?\s*(?:(?:p|pp|pag|S)\.\s*[\[\d][\d\[\]\s,.;f-]*|ibid\.?|ib\.|l\.\s?c\.(?:\s*p\.\s*[\d\[][\d\[\]\s,f.-]*)?)\)?[.;,]?\s*$""")


PAREN_TAG = re.compile(r"^\((?:[^()]{1,45}|ibidem\.?)\)\.?$")    # "(Hegel.)", "(138.)", "(Hiob 26,14.)"
BARE_PAGES = re.compile(r"^\d{1,3}(?:[,.]\s*\d{1,3})*\.$")      # "335." after "p. 334."


def _split(text, lang):
    """The shared splitter, plus rules kept local to this work:
    - a page citation standing alone after a quotation ("(p. 17.)", "(ibid.)", '" p. 156.') stays with
      the sentence it cites;
    - "NB." and "N.B." stay with the sentence they introduce;
    - a page marker between two sentences moves to the start of the second."""
    raw = segment.split_sentences(text, lang)
    out = []
    for s in raw:
        bare = re.sub(r"\s*\[\[[A-Z]\d+\]\]\s*", " ", s).strip()
        prev = re.sub(r"\[\[[A-Z]\d+\]\]", "", out[-1]).strip() if out else ""
        if out and (CITATION.match(bare) or PAREN_TAG.match(bare) or BARE_PAGES.match(bare) or not re.search(r"[A-Za-zÄÖÜäöüß0-9]", bare)):
            out[-1] += " " + s
        elif out and re.match(r"""^["']?[a-zäöüß]""", bare):
            out[-1] += " " + s                        # '... (umgekehrt)... "bedingt ist.' is one sentence
        elif out and (re.fullmatch(r"N\.?\s?B\.", prev) or re.search(r"""\bd\.\s?h\.["']?$""", prev)):
            out[-1] += " " + s
        elif out and not re.search(r"[A-Za-zÄÖÜäöüß0-9]", prev):
            out[-1] += " " + s                        # a leading "[..." joins the sentence after it
        else:
            out.append(s)
    for i in range(len(out) - 1):
        m = re.search(r"(?:\s*\[\[S\d+\]\])+$", out[i])
        if m:
            out[i], out[i + 1] = out[i][:m.start()].rstrip(), m.group(0).strip() + " " + out[i + 1]
    return out


versify.split_sentences = _split


# ---------------------------------------------------------------- build

PAR_REASON = ("MEW prints this passage in two columns side by side (the quoted text and the authors' version of it); "
              "the left column is read first, then the right. Check that the pairing still reads clearly")


def head_count(paras):
    n = 0
    for p in paras:
        if p["kind"] != "heading":
            break
        n += 1
    return n


def build(sec, notes, page_state):
    sid, paras = sec["sid"], sec["paras"]
    # footnotes: mlwerke numbers -> numbers local to the section
    order = []
    for p in paras:
        for n in re.findall(r"\[\[F(\d+)\]\]", p["text"]):
            if int(n) not in order:
                order.append(int(n))
    local = {n: k for k, n in enumerate(order, start=1)}
    for p in paras:
        p["text"] = re.sub(r"\[\[F(\d+)\]\]", lambda m: f"[[F{local[int(m.group(1))]}]]", p["text"])
    nh = head_count(paras)
    # a page that starts with the first paragraph of a section starts with its heading
    if nh and len(paras) > nh:
        m = re.match(r"^((?:\[\[S\d+\]\]\s*)+)", paras[nh]["text"])
        if m:
            paras[0]["text"] = m.group(1).strip() + " " + paras[0]["text"]
            paras[nh]["text"] = paras[nh]["text"][m.end():]
    pids = [f"{sid}.0"] * nh + [f"{sid}.{k}" for k in range(1, len(paras) - nh + 1)]
    vs, _ = build_section(sid, sid, "de", paras, [], single=True, pids=pids)
    # several headings share paragraph 0: number their verses 0.1, 0.2 ...
    count = {}
    for v in vs:
        pid = v["id"].rsplit(".", 1)[0]
        count[pid] = count.get(pid, 0) + 1
        v["id"] = f"{pid}.{count[pid]}"
    par = {pid for pid, p in zip(pids, paras) if p.get("par")}
    for v in vs:
        if v["id"].rsplit(".", 1)[0] in par:
            v["review"] = True
            v["review_reason"] = PAR_REASON
    attach_apparatus(vs, {}, f"{sid}.", page_state)
    for n, k in local.items():
        text = notes.get(n) or EXTRA_NOTES.get(n)
        assert text, f"no text for footnote {n}"
        nv, _ = build_section("N", f"{sid}.N{k}", "de", [P("note", t) for t in text], [], single=True, para0_heading=False)
        attach_apparatus(nv, {}, f"{sid}.", {})
        vs += nv
    return finalise(vs), order


def main():
    blocks, joins = stream()
    secs = sections(blocks)
    assert [s["sid"] for s in secs] == [s for _, _, s in STARTS], [s["sid"] for s in secs]
    notes = read_notes()
    out = WORK / "text"
    page_state, counts, used = {}, {}, []
    for sec in secs:
        sid = sec["sid"]
        first_page = page_state.get("p")
        vs, order = build(sec, notes, page_state)
        used += order
        pages = [v["mew_page"] for v in vs if v.get("mew_page")]
        span = f"{pages[0].split('-')[0]}-{pages[-1].split('-')[-1]}" if pages else (first_page or "11")
        title_o = " ".join(versify.clean_text(p["text"]) for p in sec["paras"][:head_count(sec["paras"])])
        stem, title_en = OUT[sid]
        authors = "Karl Marx, Friedrich Engels"
        dump(out / f"{stem}.yaml",
             {"section": sid, "title_original": title_o, "title_en": title_en, "author": authors, "date": "1845-1846",
              "original_language": "de", "anchor_language": "de", "source_original": SRC.format(pages=span),
              "source_en": SRC_EN}, vs)
        counts[sid] = (len(sec["paras"]), len(vs), len(order))
    total = sum(c[1] for c in counts.values())
    print("GI", total, "verses")
    for sid, (np_, nv, nn) in counts.items():
        print(f"  {sid:6} paragraphs {np_:4}  verses {nv:5}  notes {nn}")
    print("footnotes placed:", len(used), "; not placed:", sorted(set(notes) - set(used)))
    print("words re-joined:", len(joins))
    (WORK / "ingest" / "rejoined.txt").write_text("\n".join(joins) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
