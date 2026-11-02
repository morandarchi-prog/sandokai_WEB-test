from pathlib import Path
from html.parser import HTMLParser
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('articles_builder',Path(__file__).resolve().parents[1]/'tools/build.py')
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.tags=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))

class GitHubArticlesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'site'
        shutil.copytree(builder.ROOT,self.root,ignore=shutil.ignore_patterns('.git','_site','__pycache__'))

    def test_latest_root_home_edits_are_used_without_rewriting_source(self):
        home=self.root/'index.html'
        original=home.read_text(encoding='utf-8')
        edited=original.replace('<main id="content">','<main id="content"><p>Current home edit preserved</p>',1)
        home.write_text(edited,encoding='utf-8')
        out=builder.build(self.root)
        self.assertIn('Current home edit preserved',(out/'index.html').read_text(encoding='utf-8'))
        self.assertEqual(home.read_text(encoding='utf-8'),edited)

    def test_existing_articles_menu_and_robots_are_not_duplicated(self):
        out=builder.build(self.root)
        for prefix in ['','en/']:
            for page in ['index.html','iaido.html','jodo.html']:
                tags=Tags((out/(prefix+page)).read_text(encoding='utf-8')).tags
                self.assertEqual(sum(t=='a' and a.get('href')=='articles.html' for t,a in tags),1)
                self.assertEqual(sum(t=='meta' and a.get('name')=='robots' for t,a in tags),1)

    def test_pages_url_override_does_not_change_netlify_or_cms_settings(self):
        config=self.root/'site.config.json'
        cms=self.root/'admin/config.yml'
        before=config.read_bytes(),cms.read_bytes()
        with patch.dict(os.environ,{'SANDOKAI_SITE_URL':'https://morandarchi-prog.github.io/sandokai_WEB-test'}):
            out=builder.build(self.root)
            tags=Tags((out/'articles.html').read_text(encoding='utf-8')).tags
            self.assertIn(('link',{'rel':'canonical','href':'https://morandarchi-prog.github.io/sandokai_WEB-test/articles.html'}),tags)
        self.assertEqual((config.read_bytes(),cms.read_bytes()),before)
        with patch.dict(os.environ):
            os.environ.pop('SANDOKAI_SITE_URL',None)
            out=builder.build(self.root)
            expected=json.loads(config.read_text(encoding='utf-8'))['url']+'articles.html'
            self.assertIn(('link',{'rel':'canonical','href':expected}),Tags((out/'articles.html').read_text(encoding='utf-8')).tags)

    def test_unpublishing_ignores_stale_tracked_html_snapshots(self):
        files=sorted((self.root/'content/articles').glob('*.json'))
        file=next(p for p in files if json.loads(p.read_text(encoding='utf-8')).get('published'))
        item=json.loads(file.read_text(encoding='utf-8'))
        for prefix in ['articles','en/articles']:
            stale=self.root/prefix/(item['slug']+'.html')
            stale.parent.mkdir(parents=True,exist_ok=True)
            stale.write_text('<p>Stale snapshot must not be published</p>',encoding='utf-8')
        item['published']=False
        file.write_text(json.dumps(item),encoding='utf-8')
        out=builder.build(self.root)
        for prefix in ['','en/']:
            self.assertFalse((out/prefix/'articles'/(item['slug']+'.html')).exists())
            self.assertNotIn('articles/'+item['slug']+'.html',(out/(prefix+'articles.html')).read_text(encoding='utf-8'))

if __name__=='__main__':
    unittest.main()
