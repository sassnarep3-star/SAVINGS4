import csv
import json
import math
import unittest
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from build import build, ROOT, OUT
from model import OPENED, HORIZONS, factor, interest, headroom_principal, referral_factor

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.refs=[];self.ids=[];self.rows=[];self.active_row=None;self.has_main=False;self.h1=0
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='main':self.has_main=True
        if tag=='h1':self.h1+=1
        if tag=='tr':self.active_row={'data':False,'official':False}
        if tag=='td' and self.active_row is not None:self.active_row['data']=True
        if tag=='a' and a.get('href','').startswith('https://') and self.active_row is not None:self.active_row['official']=True
        for attr in ['href','src']:
            if attr in a:self.refs.append(a[attr])
    def handle_endtag(self,tag):
        if tag=='tr' and self.active_row is not None:
            self.rows.append(self.active_row);self.active_row=None

class Models(unittest.TestCase):
    def test_horizons(self):
        self.assertEqual([(end-OPENED).days for _,end in HORIZONS],[92,182,365])
    def test_apy_not_double_compounded(self):
        self.assertAlmostEqual(interest(100000,3.5,365),3500,7)
        self.assertAlmostEqual(interest(240000,3.5,365),8400,7)
        self.assertAlmostEqual(factor(0,365),1)
    def test_headroom_ceiling(self):
        for apy in [3.1,3.2,3.5]:
            for days in [92,182,365]:
                for bonus in [0,200]:
                    p=headroom_principal(apy,days,bonus)
                    self.assertLessEqual((p+bonus)*factor(apy,days),249999+1e-7)
                    self.assertGreater((p+.01+bonus)*factor(apy,days),249999)
                    self.assertEqual(round(p,2),p)
    def test_coverage_stress(self):
        self.assertGreater(250000*factor(3.5,365),250000)
        self.assertGreater(240000*factor(4.5,365),250000)
    def test_missing_input_never_zero(self):
        with self.assertRaises(ValueError):factor(None,365)
        with self.assertRaises(ValueError):factor(-1,365)
    def test_referral_is_temporary(self):
        self.assertAlmostEqual(referral_factor(365),factor(3.5,273)*factor(4.5,92))
        self.assertLess(referral_factor(365),factor(4.5,365))
        self.assertGreater(referral_factor(365),factor(3.5,365))

class DataAndSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.accounts=json.loads((ROOT/'data/accounts.json').read_text())
        cls.sources=json.loads((ROOT/'data/sources.json').read_text())
        cls.flags=json.loads((ROOT/'data/flags.json').read_text())
        cls.docs={p:Document(p.read_text()) for p in OUT.rglob('*.html')}
    def test_evidence_integrity(self):
        ids=[s['id'] for s in self.sources]
        self.assertEqual(len(ids),len(set(ids)))
        allowed={'www.fdic.gov','www.marcus.com','banking.us.barclays','www.ally.com','www.americanexpress.com','www.synchrony.com','www.capitalone.com','www.discover.com','www.chase.com','www.bankofamerica.com','www.wellsfargo.com','www.citi.com','www.pnc.com'}
        for s in self.sources:
            self.assertIn(urlsplit(s['url']).netloc,allowed)
            self.assertTrue(s['url'].startswith('https://'))
            self.assertEqual(s['checked'],'2026-10-22')
            self.assertTrue(s['excerpt'])
            if s['asOf']:self.assertLessEqual(date.fromisoformat(s['asOf']),OPENED)
        for item in self.accounts+self.flags:
            self.assertTrue(item['sources'])
            self.assertTrue(set(item['sources'])<=set(ids))
    def test_accounts_and_missing_values(self):
        self.assertEqual(len(self.accounts),12)
        self.assertEqual(len({a['bank'] for a in self.accounts}),11)
        expected={'marcus':3.5,'barclays':3.5,'amex':3.2,'ally':3.1}
        fids={f['id'] for f in self.flags}
        for a in self.accounts:
            self.assertEqual(a['apy'],expected.get(a['id']))
            self.assertEqual(a['modelEligible'],a['id'] in expected)
            self.assertTrue(set(a['flags'])<=fids)
            if a['apy'] is None:self.assertIsNone(a['rateAsOf'])
            else:self.assertTrue(a['rateAsOf'])
            if a['bonus'] is not None:self.assertTrue(a['bonusSources'])
    def test_local_links_and_fragments(self):
        for path,doc in self.docs.items():
            for ref in doc.refs:
                u=urlsplit(ref)
                if u.scheme or u.netloc:continue
                dest=(path.parent/unquote(u.path)).resolve() if u.path else path
                self.assertTrue(dest.is_relative_to(OUT.resolve()),f'Outside site: {ref}')
                self.assertTrue(dest.is_file(),f'{path}: missing {ref}')
                if u.fragment and dest.suffix=='.html':
                    self.assertIn(unquote(u.fragment),self.docs[dest].ids,f'{path}: broken #{u.fragment}')
    def test_every_table_row_has_official_source(self):
        allowed={s['url'] for s in self.sources}
        for path,doc in self.docs.items():
            for r in doc.rows:
                if r['data']:self.assertTrue(r['official'],f'Unsourced data row in {path}')
            for ref in doc.refs:
                if ref.startswith('https://'):self.assertIn(ref,allowed,f'Unreviewed source URL in {path}: {ref}')
    def test_landmarks_and_unique_ids(self):
        self.assertEqual(len(self.docs),7)
        for path,doc in self.docs.items():
            self.assertTrue(doc.has_main)
            self.assertEqual(doc.h1,1)
            self.assertEqual(len(doc.ids),len(set(doc.ids)),f'duplicate IDs in {path}')
    def test_legacy_publication_outputs_match(self):
        for relative in ['index.html','data/accounts.csv','.nojekyll'] + [str(p.relative_to(OUT)) for p in (OUT/'pages').glob('*.html')]:
            self.assertEqual((ROOT/relative).read_bytes(),(OUT/relative).read_bytes())

    def test_csv_preserves_blanks(self):
        with (OUT/'data/accounts.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),12)
        for a,r in zip(self.accounts,rows):
            self.assertTrue(r['official_sources'])
            if a['apy'] is None:self.assertEqual(r['apy_percent'],'')
            if a['bonus'] is None:self.assertEqual(r['confirmed_offer'],'')
    def test_no_runtime_external_dependencies(self):
        for path,doc in self.docs.items():
            text=path.read_text()
            self.assertNotIn('localhost',text)
            self.assertNotIn('127.0.0.1',text)
            self.assertNotIn('cdn.',text)
            self.assertIn('2026-10-22',text)

if __name__=='__main__':unittest.main()
