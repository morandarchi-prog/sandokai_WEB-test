# Sandokai — site bilingue et articles

Les six pages à la racine et dans `en/` sont les sources du site en préparation.
Modifier ces pages pour faire évoluer l’accueil, le Iaido ou le Jodo. Les anciens
fichiers `templates/pages/` ne sont plus utilisés par le générateur.

Les articles sont édités dans Decap et stockés dans `content/articles/*.json`.
Le générateur crée les index et les pages de lecture dans `_site/` :

```sh
python3 -X utf8 -m unittest discover -s tests -v
python3 -X utf8 tools/build.py
```

Netlify publie `_site/` depuis `main`. Le nouveau workflow `pages.yml` publie
également `_site/` sur GitHub Pages après sélection de **GitHub Actions** dans
**Settings > Pages > Source**. Une fusion dans `main` déclenche cette publication.

`SANDOKAI_SITE_URL` permet au workflow Pages d’utiliser son adresse propre,
sans changer l’adresse Netlify dans `site.config.json` ni la connexion Decap.
Le site reste en mode test `noindex,nofollow`; aucun domaine officiel n’est déplacé.

Les copies HTML d’articles versionnées sont un aperçu initial. Ne pas les éditer :
les futures modifications Decap se retrouvent dans le site reconstruit par Actions.
Consulter [le guide GitHub Articles](docs/GITHUB-ARTICLES.txt).
