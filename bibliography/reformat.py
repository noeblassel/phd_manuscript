import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import re
from collections import defaultdict

# Allowed fields based on refs.bib (expand as needed)
FIELD_ORDER = [
    'author', 'title', 'booktitle', 'journal', 'series', 'volume', 'number',
    'pages', 'year', 'publisher', 'editor', 'subtitle', 'issue', 'school'
]

# Journal and publisher deabbreviation maps (expand as needed)
JOURNAL_MAP = {
    'Phys. Rev. A': 'Physical Review A',
    'Phys. Rev. Lett.': 'Physical Review Letters',
    'J. Stat. Phys.': 'Journal of Statistical Physics',
    'Europhysics Letters': 'Europhysics Letters',
    'J Stat Phys': 'Journal of Statistical Physics',
    'Arch Rational Mech Anal': 'Archive for Rational Mechanics and Analysis',
    'Nanotechnology': 'Nanotechnology',
    'Advances in Physics': 'Advances in Physics',
    'BIT Numerical Mathematics': 'BIT Numerical Mathematics',
    'IMA J. Numer. Anal.': 'IMA Journal of Numerical Analysis',
    'Current Opinion in Solid State and Materials Science': 'Current Opinion in Solid State and Materials Science',
    'Physica D: Nonlinear Phenomena': 'Physica D: Nonlinear Phenomena',
    'Physical Review Letters': 'Physical Review Letters',
    'J Stat Phys': 'Journal of Statistical Physics',
    'J. Phys. C: Solid State Phys.': 'Journal of Physics C: Solid State Physics',
    'New J. Phys.': 'New Journal of Physics',
    'J. Phys. Soc. Jpn.': 'Journal of the Physical Society of Japan'
    # Add more as needed
}

PUBLISHER_MAP = {
    'APS': 'American Physical Society',
    'Springer': 'Springer',
    'Springer International Publishing': 'Springer International Publishing',
    'Elsevier': 'Elsevier',
    'John Wiley \\& Sons': 'John Wiley & Sons',
    'Oxford University Press': 'Oxford University Press',
    'Cambridge University Press': 'Cambridge University Press',
    'AIP Publishing': 'AIP Publishing',
    'ACS Publications': 'ACS Publications',
    # Add more as needed
}

def deabbreviate(entry):
    if 'journal' in entry:
        entry['journal'] = JOURNAL_MAP.get(entry['journal'], entry['journal'])
    if 'publisher' in entry:
        entry['publisher'] = PUBLISHER_MAP.get(entry['publisher'], entry['publisher'])
    return entry

def protect_title_capitals(title):
    # Protect capital letters except the first one
    if not title:
        return title
    # Find the first letter (skip leading braces and spaces)
    i = 0
    while i < len(title) and (title[i] == '{' or title[i].isspace()):
        i += 1
    protected = title[:i]
    first = True
    for c in title[i:]:
        if c.isupper() and not first:
            protected += '{' + c + '}'
        else:
            protected += c
        if c.isalpha():
            first = False
    return protected

def fix_field_names(entry):
    if 'journaltitle' in entry:
        entry['journal'] = entry.pop('journaltitle')
    if 'shortjournal' in entry:
        entry.pop('shortjournal')
    if 'data' in entry:
        entry['year'] = entry.pop('data')
    if 'adress' in entry:
        entry['address'] = entry.pop('adress')
    for k, v in entry.items():
        entry[k] = v.strip().rstrip(',')
    return entry

def filter_fields(entry):
    # Always keep ENTRYTYPE and ID
    return {k: v for k, v in entry.items() if k in FIELD_ORDER or k in ['ENTRYTYPE', 'ID']}

def order_fields(entry):
    ordered = {}
    for field in FIELD_ORDER:
        if field in entry:
            ordered[field] = entry[field]
    for field in entry:
        if field not in ordered and field != 'ENTRYTYPE':
            ordered[field] = entry[field]
    return ordered

def get_initials(author_str):
    # Split authors by 'and', then get initials of last names only
    authors = re.split(r'\s+and\s+', author_str)
    initials = []
    for author in authors:
        author = author.replace('{', '').replace('}', '').strip()
        # Split by comma if present (BibTeX "Last, First"), else by space
        if ',' in author:
            last_name = author.split(',')[0].strip()
        else:
            parts = author.split()
            last_name = parts[-1] if parts else ''
        # For compound last names, take all initials
        for part in re.split(r'[\s\-]+', last_name):
            if part:
                initials.append(part[0].upper())
    return ''.join(initials)

def generate_key(entry, key_count):
    author_str = entry.get('author', '')
    year_str = entry.get('year', '')
    initials = get_initials(author_str) if author_str else 'X'
    year_digits = year_str[-2:] if year_str and len(year_str) >= 2 else 'XX'
    base_key = f"{initials}{year_digits}"
    # Resolve clashes
    count = key_count[base_key]
    key_count[base_key] += 1
    if count == 0:
        return base_key
    else:
        return f"{base_key}{chr(ord('a') + count - 1)}"

def reformat_bibtex_file(input_path, output_path):
    with open(input_path, 'r') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    new_entries = []
    key_count = defaultdict(int)

    for entry in bib_database.entries:
        # Ensure ENTRYTYPE is present
        if 'ENTRYTYPE' not in entry:
            if 'type' in entry:
                entry['ENTRYTYPE'] = entry.pop('type')
            else:
                print("Entry type not standard. Not considered.", entry)
                continue
        
        if entry['ENTRYTYPE'] == 'article' and 'publisher' in entry:
            del entry['publisher']

        entry = fix_field_names(entry)
        if 'title' in entry:
            entry['title'] = protect_title_capitals(entry['title'])
        entry = deabbreviate(entry)
        # Lowercase entry type BEFORE filtering
        entry['ENTRYTYPE'] = entry['ENTRYTYPE'].lower()
        # Generate key before filtering
        key = generate_key(entry, key_count)
        entry['ID'] = key
        entry = filter_fields(entry)
        entry = order_fields(entry)
        # Ensure ENTRYTYPE and ID are present after ordering
        entry['ENTRYTYPE'] = entry.get('ENTRYTYPE', 'article')
        entry['ID'] = key
        new_entries.append(entry)

    db = BibDatabase()
    db.entries = new_entries

    writer = BibTexWriter()
    writer.indent = '  '
    writer.order_entries_by = None
    writer.comma_first = False

    with open(output_path, 'w') as bibfile:
        bibfile.write(writer.write(db))

if __name__ == "__main__":
    input_path = "refs_hors_eq.bib"
    output_path = "refs_hors_eq_reformatted.bib"
    reformat_bibtex_file(input_path, output_path)
    print(f"Reformatted file written to {output_path}")