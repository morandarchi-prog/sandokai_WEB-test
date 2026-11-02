"""Static bilingual build; Python standard library only. Never writes source pages."""
from pathlib import Path
import html
import json
import re
import shutil
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
esc = lambda value: html.escape(str(value), quote=True)


def build(root=ROOT, out=None):
    out = out or root / '_site'
    config = json.loads((root / 'site.config.json').read_text())
    base = config['url']
    parsed = urlparse(base)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.query or parsed.fragment or not base.endswith('/'):
        raise ValueError('url doit être une URL HTTPS terminée par /')
    prod = config.get('production') is True
    if prod and (parsed.hostname.endswith('github.io') or config.get('production_confirmed') is not True):
        raise ValueError('Production : domaine final et production_confirmed=true requis')
    if config.get('cms_enabled'):
        if not (root / 'admin/config.yml').is_file():
            raise ValueError('Configuration OAuth absente')
        if '.invalid' in (root / 'admin/config.yml').read_text():
            raise ValueError('Configurer le véritable hôte OAuth')
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for name in ['assets', 'admin']:
        shutil.copytree(root / name, out / name)
    for name in ['styles.css', 'script.js', 'articles.css']:
        shutil.copy2(root / name, out / name)
    (out / '.nojekyll').write_text('')
    paths = []
    titles = set()

    def absolute(path):
        return base + path

    def seo(path, lang, title, description, other, article=False, approved=True):
        if title in titles:
            raise ValueError('Titre HTML dupliqué : ' + title)
        titles.add(title)
        robot = 'index,follow' if prod and approved else 'noindex,nofollow'
        data = {'@context': 'https://schema.org', '@type': 'BlogPosting' if article else 'WebPage',
                'name': title, 'description': description, 'url': absolute(path), 'inLanguage': lang + '-CA'}
        org = {'@type': 'Organization', 'name': 'Sandokai Kobudō Shugyōkai',
               'url': absolute('index.html'), 'logo': absolute('assets/logo.png')}
        if article:
            data.update(headline=title, publisher=org, mainEntityOfPage=absolute(path))
        else:
            data['about'] = org
        alternate = {'fr': other if lang == 'en' else path, 'en': other if lang == 'fr' else path}
        tags = f'<meta name="robots" content="{robot}"><link rel="canonical" href="{esc(absolute(path))}">'
        for code, target in alternate.items():
            tags += f'<link rel="alternate" hreflang="{code}-CA" href="{esc(absolute(target))}">'
        tags += f'<link rel="alternate" hreflang="x-default" href="{esc(absolute(alternate["fr"]))}">'
        for key, value in {'title': title, 'description': description, 'url': absolute(path),
                           'type': 'article' if article else 'website', 'locale': lang + '_CA',
                           'image': absolute('assets/logo.png'), 'image:alt': 'Sandokai Kobudo Shugyokai'}.items():
            tags += f'<meta property="og:{key}" content="{esc(value)}">'
        tags += '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
        return tags

    sources = {}
    for lang in ['fr', 'en']:
        prefix = '' if lang == 'fr' else 'en/'
        for page in ['index.html', 'iaido.html', 'jodo.html']:
            path = prefix + page
            source = (root / 'templates/pages' / path).read_text()
            # Preserve authored page body; only remove links dependent on the retiring site.
            source = re.sub(r'<a class="source-link".*?</a>', '', source)
            source = source.replace('<a href="#contact">Contact</a>', '<a href="articles.html">Articles</a><a href="#contact">Contact</a>')
            title = re.search(r'<title>(.*?)</title>', source)[1]
            title += ' — Montréal' if lang == 'fr' else ' — Montreal'
            if lang == 'en':
                title += ' (English)'
            source = re.sub(r'<title>.*?</title>', '<title>' + title + '</title>', source)
            description = re.search(r'<meta name="description" content="(.*?)">', source)[1]
            other = ('en/' if lang == 'fr' else '') + page
            source = re.sub(r'<link rel="alternate"[^>]*>', '', source)
            source = source.replace('</head>', seo(path, lang, title, description, other) + '</head>')
            target = out / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source)
            paths.append(path)
            if page == 'index.html':
                sources[lang] = source

    def image(src, alt, rel):
        # CMS stores /assets/... paths. Render relative links for GitHub project Pages.
        if not isinstance(src, str) or not src.startswith('/assets/') or '..' in src.split('/'):
            raise ValueError('Image locale /assets/ requise')
        local = root / src.lstrip('/')
        if not local.is_file() or local.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.avif'}:
            raise ValueError('Image absente ou format non accepté : ' + src)
        if not isinstance(alt, str) or not alt.strip():
            raise ValueError('Description ALT obligatoire')
        return f'<img src="{rel}{esc(src.lstrip("/"))}" alt="{esc(alt)}" loading="lazy" decoding="async">'

    def render_blocks(blocks, rel):
        if not isinstance(blocks, list) or not blocks:
            raise ValueError('Contenu intégral requis dans chaque langue')
        result = []
        heading = False
        for block in blocks:
            kind = block['type']
            if kind == 'image':
                result.append('<figure>' + image(block['src'], block['alt'], rel) + '</figure>')
            else:
                tag = {'paragraph': 'p', 'heading': 'h2', 'subheading': 'h3', 'quote': 'blockquote'}.get(kind)
                if not tag or not isinstance(block.get('text'), str) or not block['text'].strip():
                    raise ValueError('Bloc de contenu invalide')
                if kind == 'subheading' and not heading:
                    raise ValueError('Un H3 doit suivre un H2')
                heading = heading or kind == 'heading'
                result.append(f'<{tag}>' + esc(block['text']) + f'</{tag}>')
        return '\n'.join(result)

    articles = []
    slugs = set()
    for file in sorted((root / 'content/articles').glob('*.json')):
        item = json.loads(file.read_text())
        slug = item['slug']
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs or file.stem != slug:
            raise ValueError('Adresse permanente invalide ou dupliquée : ' + slug)
        slugs.add(slug)
        if type(item.get('published')) is not bool or type(item.get('english_approved')) is not bool:
            raise ValueError('Statuts de publication requis')
        for lang in ['fr', 'en']:
            tr = item[lang]
            if any(not isinstance(tr.get(k), str) or not tr[k].strip() for k in ['title', 'description']):
                raise ValueError('Titre et description bilingues requis')
            render_blocks(tr['blocks'], '')
            if tr.get('image'):
                image(tr['image'], tr.get('alt'), '')
        if item['published']:
            articles.append(item)

    def shell(lang, path, title, description, other, body, article=False, approved=True):
        prefix = '' if lang == 'fr' else 'en/'
        rel = '../' * (len(Path(path).parts) - 1)
        # Reuse the real header, footer and contact section, with links adapted to depth.
        source = sources[lang]
        header = re.search(r'<body>(.*?)<main id="content">', source, re.S)[1]
        header = re.sub(r'<nav class="languages".*?</nav>',
                        '<nav class="languages" aria-label="FR / EN">' +
                        ''.join(f'<a lang="{code}" hreflang="{code}-CA" href="{rel}{target}"' +
                                (' aria-current="true"' if lang == code else '') + f'>{code.upper()}</a>'
                                for code, target in [('fr', path if lang == 'fr' else other), ('en', path if lang == 'en' else other)]) + '</nav>', header)
        header = header.replace(' aria-current="page"', '')
        for name in ['index.html', 'iaido.html', 'jodo.html', 'articles.html']:
            header = header.replace(f'href="{name}"', f'href="{rel}{prefix}{name}"')
        header = re.sub(r'src="(?:\.\./)?assets/', f'src="{rel}assets/', header)
        contact = re.search(r'(<section class="contact wrap".*?</main>)', source, re.S)[1].removesuffix('</main>')
        footer = source.split('</main>', 1)[1]
        text = f'<!doctype html>\n<html lang="{lang}-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#012F6A"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><link rel="stylesheet" href="{rel}styles.css"><link rel="stylesheet" href="{rel}articles.css"><script src="{rel}script.js" defer></script>'
        text += seo(path, lang, title, description, other, article, approved) + '</head><body>' + header + '<main id="content">' + body + contact + '</main>' + footer
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        if approved:
            paths.append(path)

    for lang in ['fr', 'en']:
        prefix = '' if lang == 'fr' else 'en/'
        rel = '../' if lang == 'en' else ''
        intro = ('Textes et réflexions du Sandokai, école de Iaido et de Jodo à Montréal.' if lang == 'fr' else
                 'Writing and reflections from Sandokai, a school of Iaido and Jodo in Montreal.')
        body = f'<section class="article-intro wrap"><p class="eyebrow">Sandokai</p><h1>Articles</h1><p class="lead">{intro}</p></section><section class="article-list wrap" aria-label="Articles">'
        if not articles:
            body += '<p>' + ('Les articles historiques seront disponibles après leur migration.' if lang == 'fr' else 'Historical articles will be available following their migration.') + '</p>'
        for item in articles:
            tr = item[lang]
            path = prefix + 'articles/' + item['slug'] + '.html'
            other = ('en/' if lang == 'fr' else '') + 'articles/' + item['slug'] + '.html'
            approved = lang == 'fr' or item['english_approved']
            warning = '' if approved else '<p class="translation-notice" role="note">Provisional English translation — awaiting review and approval.</p>'
            cover = image(tr['image'], tr.get('alt'), rel) if tr.get('image') else ''
            body += f'<article>{cover}<h2><a href="articles/{item["slug"]}.html">{esc(tr["title"])}</a></h2><p>{esc(tr["description"])}</p>{warning}</article>'
            article_rel = '../../' if lang == 'en' else '../'
            content = f'<article class="article-body wrap"><a class="back" href="../articles.html">← Articles</a><h1>{esc(tr["title"])}</h1>{warning}'
            if tr.get('image'):
                content += image(tr['image'], tr.get('alt'), article_rel)
            content += render_blocks(tr['blocks'], article_rel) + '</article>'
            content += '<nav class="article-related wrap" aria-label="' + ('Explorer aussi' if lang == 'fr' else 'Explore further') + '">'
            for name in ['iaido', 'jodo']:
                content += f'<a href="{article_rel}{prefix}{name}.html">{name.capitalize()}</a> '
            content += '<a href="#contact">Contact</a></nav>'
            shell(lang, path, tr['title'] + (' — Sandokai (English)' if lang == 'en' else ' — Sandokai'), tr['description'], other, content, True, approved)
        body += '</section>'
        shell(lang, prefix + 'articles.html', 'Articles — Sandokai' + (' (English)' if lang == 'en' else ''), intro,
              ('en/' if lang == 'fr' else '') + 'articles.html', body)

    if config.get('cms_enabled'):
        admin = out / 'admin/index.html'
        admin.write_text('<!doctype html><html lang="fr-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Decap — Sandokai</title></head><body><script src="https://cdn.jsdelivr.net/npm/decap-cms@3.8.3/dist/decap-cms.js"></script></body></html>')
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    if prod:
        for path in paths:
            ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = absolute(path)
    ET.ElementTree(sitemap).write(out / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (out / 'robots.txt').write_text('User-agent: *\nDisallow: /\n' if not prod else 'User-agent: *\nDisallow: /admin/\nSitemap: ' + absolute('sitemap.xml') + '\n')
    print(f'{len(list(out.rglob("*.html")))} pages HTML générées; production={prod}; articles={len(articles)}')
    return out

if __name__ == '__main__':
    build()
