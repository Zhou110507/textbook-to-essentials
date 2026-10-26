"""Behavioral checks for loss of source coverage and compilation false positives."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/textbook-to-essentials/scripts'

def module(name):
    spec=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'))
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

ledger=module('check_ledger')
builder=module('build_pdf')

def valid():
    return {
        'documents':[{'id':'T','title':'Source','page_count':10}],
        'scope':{'sections':['1.1','1.2'],'exam_evidence':[]},
        'coverage':[
            {'section':'1.1','decision':'keep','reason':'Core relation',
             'source_refs':[{'document':'T','pdf_pages':[2],'printed_pages':'1'}],
             'output_ids':['F1']},
            {'section':'1.2','decision':'omit','reason':'Repeated numerical substitution',
             'source_refs':[{'document':'T','pdf_pages':[3],'printed_pages':'2'}],
             'output_ids':[]}],
        'items':[{'id':'F1','kind':'formula','statement':'Model relation',
                  'source_refs':[{'document':'T','pdf_pages':[2],'printed_pages':'1'}],
                  'verification':'verified','conditions':['Linear constant model'],
                  'symbols':'x is a displacement in metres','output_anchor':'eq:F1'}],
        'unresolved':[]}

class EvidenceTests(unittest.TestCase):
    def test_markdown_uses_real_locator_without_fake_pdf_pages(self):
        data=valid(); data['documents'][0]={'id':'T','title':'Markdown source','format':'markdown'}
        for row in data['coverage'] + data['items']:
            row['source_refs']=[{'document':'T','locator':'rc-source.md section 1.1'}]
        self.assertEqual(ledger.validate(data),[])
        data['items'][0]['source_refs'][0]['locator']=''
        self.assertTrue(any('locator' in e for e in ledger.validate(data)))

    def test_valid_ledger(self):
        self.assertEqual(ledger.validate(valid()),[])

    def test_silently_lost_section_is_rejected(self):
        data=valid(); data['coverage'].pop()
        self.assertTrue(any('Missing coverage' in e for e in ledger.validate(data)))

    def test_formula_without_conditions_is_rejected(self):
        data=valid(); data['items'][0]['conditions']=[]
        self.assertTrue(any('conditions required' in e for e in ledger.validate(data)))

    def test_ocr_pending_and_invalid_page_cannot_pass(self):
        data=valid(); data['items'][0]['verification']='pending'
        data['items'][0]['source_refs'][0]['pdf_pages']=[0,11]
        errors=ledger.validate(data)
        self.assertTrue(any('not been verified' in e for e in errors))
        self.assertTrue(any('invalid PDF page' in e for e in errors))

    def test_merged_content_requires_real_target(self):
        data=valid(); data['coverage'][0]['decision']='merge'
        data['coverage'][0]['output_ids']=['NONEXISTENT']
        self.assertTrue(any('output_ids' in e for e in ledger.validate(data)))

    def test_reading_missing_page_is_rejected(self):
        from io import StringIO
        from unittest.mock import patch
        contents='document,pdf_page,printed_page,status,note\nT,1,1,read,reviewed\n'
        with patch.object(Path,'open',return_value=StringIO(contents)):
            path=Path('reading.csv')
            self.assertTrue(any('missing 9 page' in e for e in ledger.validate_reading(path,valid()['documents'],True)))

class BuildTests(unittest.TestCase):
    def test_final_pass_log_failures(self):
        self.assertIn('missing-glyph',builder.log_problems('Missing character: There is no X'))
        self.assertIn('undefined-reference',builder.log_problems("LaTeX Warning: Reference `eq:1' on page 1 undefined"))
        self.assertIn('horizontal-overflow',builder.log_problems('Overfull \\hbox (2.0pt too wide)'))
        self.assertEqual(builder.log_problems('Output written on main.pdf (2 pages).'),[])

    def test_missing_compiler_is_explicit(self):
        with self.assertRaisesRegex(ValueError,'not found'):
            builder.choose_engine('xelatex','nonexistent-compiler-for-skill-test')

if __name__=='__main__':
    unittest.main()
