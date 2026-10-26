"""Check evidence structure and optional full-document reading coverage, not factual truth."""
import argparse
import csv
import json
from pathlib import Path
import sys


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ['Ledger must be a JSON object.']
    for key in ('documents', 'coverage', 'items', 'unresolved'):
        if not isinstance(data.get(key), list):
            errors.append(f'{key} must be an array.')
    if errors:
        return errors
    docs = {}
    for doc in data['documents']:
        if not isinstance(doc, dict) or not doc.get('id') or not doc.get('title'):
            errors.append('Each document needs id and title.'); continue
        key = doc['id']
        if not isinstance(key, str) or key in docs:
            errors.append(f'Duplicate or invalid document id: {key}'); continue
        if doc.get('format', 'pdf') == 'pdf' and (type(doc.get('page_count')) is not int or doc['page_count'] < 1):
            errors.append(f'{key}: positive integer page_count required.'); continue
        docs[key] = doc
    if not docs:
        errors.append('At least one valid source document is required.')

    def check_refs(refs, label):
        if not isinstance(refs, list) or not refs:
            errors.append(f'{label}: nonempty source_refs required.'); return
        for ref in refs:
            if not isinstance(ref, dict) or ref.get('document') not in docs:
                errors.append(f'{label}: unknown document in source_refs.'); continue
            doc = docs[ref['document']]
            if doc.get('format', 'pdf') == 'pdf':
                pages = ref.get('pdf_pages')
                maximum = doc['page_count']
                if (not isinstance(pages, list) or not pages or
                    any(type(p) is not int or not 1 <= p <= maximum for p in pages)):
                    errors.append(f'{label}: invalid PDF page index (valid: 1..{maximum}).')
                if not ref.get('printed_pages'):
                    errors.append(f'{label}: printed_pages required; use explicit n/a when unnumbered.')
            elif not isinstance(ref.get('locator'), str) or not ref['locator'].strip():
                errors.append(f'{label}: non-PDF source needs a section/line locator.')

    ids = set()
    for item in data['items']:
        if not isinstance(item, dict):
            errors.append('Each item must be an object.'); continue
        key = item.get('id')
        if not isinstance(key, str) or not key or key in ids:
            errors.append(f'Duplicate or invalid item id: {key}'); continue
        ids.add(key)
        if item.get('kind') not in ('concept','formula','derivation','method','example','figure'):
            errors.append(f'{key}: invalid kind.')
        for field in ('statement', 'output_anchor'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f'{key}: {field} required.')
        if item.get('verification') != 'verified':
            errors.append(f'{key}: item has not been verified.')
        check_refs(item.get('source_refs'), key)
        if item.get('kind') == 'formula':
            conditions = item.get('conditions')
            if not isinstance(conditions, list) or not conditions or not all(isinstance(v,str) and v.strip() for v in conditions):
                errors.append(f'{key}: formula conditions required.')
            if not isinstance(item.get('symbols'), str) or not item['symbols'].strip():
                errors.append(f'{key}: formula symbols and units required.')
    scope = data.get('scope')
    if not isinstance(scope, dict) or not isinstance(scope.get('sections'), list) or not scope['sections']:
        errors.append('scope.sections must be a nonempty array.'); sections = []
    else:
        sections = scope['sections']
        if not all(isinstance(s,str) and s for s in sections):
            errors.append('scope.sections entries must be nonempty strings.'); sections=[]
        if len(set(sections)) != len(sections):
            errors.append('Duplicate scope sections.')
        if not isinstance(scope.get('exam_evidence'), list):
            errors.append('scope.exam_evidence must be an array.')
    seen = set()
    for row in data['coverage']:
        if not isinstance(row, dict):
            errors.append('Each coverage row must be an object.'); continue
        section = row.get('section')
        if not isinstance(section,str) or section not in sections or section in seen:
            errors.append(f'Duplicate or out-of-scope coverage: {section}'); continue
        seen.add(section)
        decision = row.get('decision')
        if decision not in ('keep','merge','rewrite','defer','omit'):
            errors.append(f'{section}: invalid decision.')
        if not isinstance(row.get('reason'),str) or not row['reason'].strip():
            errors.append(f'{section}: decision reason required.')
        check_refs(row.get('source_refs'), section)
        targets = row.get('output_ids', [])
        if not isinstance(targets,list) or any(not isinstance(t,str) or t not in ids for t in targets):
            errors.append(f'{section}: unknown or invalid output_ids.')
        if decision != 'omit' and not targets:
            errors.append(f'{section}: retained or deferred content needs output_ids.')
    for missing in set(sections) - seen:
        errors.append(f'Missing coverage for section {missing}.')
    if data['unresolved']:
        errors.append(f'{len(data["unresolved"])} unresolved issue(s) remain.')
    return errors


def validate_reading(path, documents, full=False):
    errors, seen = [], set()
    docs = {d['id']:d['page_count'] for d in documents if d.get('format', 'pdf') == 'pdf'}
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not {'document','pdf_page','printed_page','status','note'}.issubset(reader.fieldnames or []):
            return ['Reading log headers must be document,pdf_page,printed_page,status,note.']
        for row in reader:
            try:
                doc, page = row['document'], int(row['pdf_page'])
                if doc not in docs or not 1 <= page <= docs[doc]:
                    raise ValueError()
            except (ValueError, TypeError):
                errors.append('Reading log has an unknown document or out-of-range page.'); continue
            key = (doc,page)
            if key in seen:
                errors.append(f'Duplicate reading entry: {key}')
            seen.add(key)
            if row['status'] not in ('read','non-content'):
                errors.append(f'{key}: reading/visual review is incomplete.')
    if full:
        missing = sum((doc,p) not in seen for doc,count in docs.items() for p in range(1,count+1))
        if missing:
            errors.append(f'Full reading log is missing {missing} page(s).')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger')
    parser.add_argument('--reading-log')
    parser.add_argument('--full-reading',action='store_true')
    args=parser.parse_args()
    try:
        data=json.loads(Path(args.ledger).read_text(encoding='utf-8-sig'))
        errors=validate(data)
        if args.full_reading and not args.reading_log:
            errors.append('--full-reading requires --reading-log.')
        if args.reading_log and not errors:
            errors += validate_reading(args.reading_log,data['documents'],args.full_reading)
    except (OSError,ValueError,KeyError,TypeError) as error:
        errors=[str(error)]
    if errors:
        print('\n'.join('ERROR: '+error for error in errors),file=sys.stderr)
        return 1
    print('Evidence structure passed. This does not certify factual accuracy or actual reading.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
