from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('builder', Path(__file__).resolve().parents[1] / 'tools/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.add(attrs['id'])


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        shutil.copytree(builder.ROOT, self.root, ignore=shutil.ignore_patterns('.git', '_site', '__pycache__'))

    def fixture(self, approved=False, published=True):
        # Synthetic test data exists only in a temporary directory, never in published content.
        tr = {'title': 'Titre <test>', 'description': 'Description & test',
              'blocks': [{'type': 'heading', 'text': 'Section'}, {'type': 'subheading', 'text': 'Suite'},
                         {'type': 'paragraph', 'text': '<script>alert(1)</script>\nTexte intégral.'},
                         {'type': 'image', 'src': '/assets/logo.png', 'alt': 'Logo test'}]}
        item = {'slug': 'test-article', 'published': published, 'english_approved': approved,
                'fr': tr, 'en': {**tr, 'title': 'English test'}}
        (self.root / 'content/articles/test-article.json').write_text(json.dumps(item))
        return item

    def check_links(self, out):
        pages = {p: Page(p.read_text()) for p in out.rglob('*.html')}
        for path, page in pages.items():
            for tag, attrs in page.tags:
                for key in ['href', 'src']:
                    if key not in attrs:
                        continue
                    url = urlparse(attrs[key])
                    if url.scheme or url.netloc:
                        continue
                    target = (path.parent / unquote(url.path)).resolve() if url.path else path
                    self.assertTrue(target.is_file(), f'{path}: {attrs[key]}')
                    if url.fragment and target in pages:
                        self.assertIn(url.fragment, pages[target].ids)
            if path.parent.name != 'admin':
                self.assertEqual(sum(t == 'h1' for t, a in page.tags), 1)
                self.assertTrue(any(t == 'meta' and a.get('name') == 'robots' for t, a in page.tags))
                canon = [a['href'] for t, a in page.tags if t == 'link' and a.get('rel') == 'canonical']
                self.assertEqual(len(canon), 1)
                self.assertTrue(canon[0].startswith('https://'))

        def test_empty_site_and_assets(self):
            for article in (self.root / 'content/articles').glob('*.json'):
                article.unlink()
            out = builder.build(self.root)
            self.check_links(out)
            self.assertIn('Disallow: /', (out / 'robots.txt').read_text())
            self.assertEqual(len(ET.parse(out / 'sitemap.xml').getroot()), 0)
            self.assertFalse(list((out / 'articles').glob('*.html')))

    def test_bilingual_generation_safe_content_and_reciprocal_languages(self):
        self.fixture()
        out = builder.build(self.root)
        self.check_links(out)
        fr = (out / 'articles/test-article.html').read_text()
        en = (out / 'en/articles/test-article.html').read_text()
        self.assertIn('&lt;script&gt;', fr)
        self.assertNotIn('<script>alert', fr)
        self.assertIn('awaiting review and approval', en)
        self.assertIn('href="../en/articles/test-article.html"', fr)
        self.assertIn('href="../../articles/test-article.html"', en)
        self.assertIn('hreflang="en-CA" href="https://morandarchi-prog.github.io/sandokai_WEB-test/en/articles/test-article.html"', fr)
        self.assertIn('hreflang="fr-CA" href="https://morandarchi-prog.github.io/sandokai_WEB-test/articles/test-article.html"', en)
        # Regeneration removes deleted articles, with no stale index or pages.
        (self.root / 'content/articles/test-article.json').unlink()
        builder.build(self.root)
        self.assertFalse((out / 'articles/test-article.html').exists())

    def test_production_sitemap_excludes_unapproved_translation(self):
        self.fixture()
        (self.root / 'site.config.json').write_text(json.dumps({'url': 'https://example.org/ecole/', 'production': True, 'production_confirmed': True}))
        out = builder.build(self.root)
        xml = (out / 'sitemap.xml').read_text()
        self.assertIn('https://example.org/ecole/articles/test-article.html', xml)
        self.assertNotIn('en/articles/test-article.html', xml)
        self.assertIn('content="noindex,nofollow"', (out / 'en/articles/test-article.html').read_text())
        self.assertIn('content="index,follow"', (out / 'articles/test-article.html').read_text())

    def test_drafts_not_published(self):
        self.fixture(published=False)
        out = builder.build(self.root)
        self.assertFalse((out / 'articles/test-article.html').exists())

    def test_missing_image_and_external_image_rejected(self):
        item = self.fixture()
        for src in ['/assets/missing.png', 'https://example.org/a.png', '/assets/../index.html']:
            item['fr']['blocks'][-1]['src'] = src
            (self.root / 'content/articles/test-article.json').write_text(json.dumps(item))
            with self.assertRaises(ValueError):
                builder.build(self.root)

    def test_existing_page_bodies_preserved(self):
        out = builder.build(self.root)
        for prefix in ['', 'en/']:
            for name in ['index.html', 'iaido.html', 'jodo.html']:
                path = prefix + name
                original = (self.root / 'templates/pages' / path).read_text()
                expected = re.sub(r'<a class="source-link".*?</a>', '', original.split('<body>', 1)[1])
                actual = (out / path).read_text().split('<body>', 1)[1]
                actual = actual.replace('<a href="articles.html">Articles</a>', '')
                self.assertEqual(actual, expected, path)

    def test_cms_requires_configuration(self):
        (self.root / 'site.config.json').write_text(json.dumps({'url': 'https://example.org/', 'cms_enabled': True}))
        with self.assertRaises(ValueError):
            builder.build(self.root)

    def test_production_requires_confirmation(self):
        (self.root / 'site.config.json').write_text(json.dumps({'url': 'https://example.org/', 'production': True}))
        with self.assertRaises(ValueError):
            builder.build(self.root)

if __name__ == '__main__':
    unittest.main()
