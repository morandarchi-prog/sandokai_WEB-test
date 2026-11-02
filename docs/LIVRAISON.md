# Analyse et livraison — 30 octobre 2026

## État et limites

**Fondations réalisées; intégration historique et mise en service non terminées.** L’archive `Sandokai-blogue-bilingue-Decap(1).zip` n’était ni jointe à la conversation, ni présente sous `/workspace` ou dans le dépôt. Aucun article historique ou traduction n’a été inventé. Les deux index présentent un état d’attente; il n’y a aucune fausse carte d’article. Les critères portant sur les sept textes restent bloqués par cette absence.

Le connecteur GitHub a permis de lire le dépôt mais a refusé la création de `feat/articles-bilingues-decap` avec HTTP 403, `Resource not accessible by integration`. Le jeton CLI n’est pas utilisable; le clone a aussi échoué car le proxy HTTP local était inaccessible. La branche de travail et les commits existent donc uniquement dans la copie locale. Aucune Pull Request n’a pu être créée et aucune fusion n’a eu lieu. Il faudra appliquer le patch fourni dans un clone Git authentifié, pousser la branche puis créer la PR décrite dans `docs/PULL_REQUEST.md`.

## Analyse préalable

Révision distante examinée : `a32dc11a17bc18293ed53e6bcef47e8b30ee5999` de `main`. La copie locale provient des fichiers retournés par le connecteur GitHub, y compris les deux ressources binaires reçues en base64; son historique Git est un historique local de travail, pas celui du dépôt distant. Ne pas forcer son envoi sur le dépôt distant.

- Six pages : `index.html`, `iaido.html`, `jodo.html` et leurs équivalents `en/`.
- `styles.css` : bleu `#012F6A`, Nimbus Sans local, menu natif `details`, règles tablette/téléphone.
- `script.js` : année courante, fermeture du menu par Échap et au clic. Aucun changement au script.
- Contact dans chaque page, lien mail existant, Facebook et Instagram conservés. Pas de page Contact autonome à inventer.
- Logo PNG, SVG original et police avec leurs licences conservés; aucun téléchargement depuis l’ancien site.
- Quatre liens documentaires vers l’ancien site retirés des pages servies. Leurs sources restent dans les gabarits originaux et `LISEZ-MOI.txt` à titre documentaire, hors contenu HTML servi.
- Aucun gestionnaire de dépendances, CMS, workflow ou générateur présent initialement; l’ancien guide mentionnait un générateur situé hors dépôt, donc inaccessible.
- Comparaison ZIP/dépôt impossible sans archive; aucun fichier de l’archive supposé ni écrasé.

## Résultat technique

Le générateur Python standard produit le site statique complet dans `_site/`, réutilise les gabarits des six pages et ajoute les deux index Articles. Un fichier JSON bilingue produit deux pages permanentes, les index et métadonnées automatiquement; les traductions anglaises restent provisoires jusqu’à approbation explicite. Les blocs CMS privilégient la saisie simple sans HTML exécutable. Les fichiers sources JSON sont validés, les brouillons omis et les anciens fichiers générés effacés à la reconstruction. Le style Articles reprend la palette et les ressources locales.

Les pages générées ont des titres distincts, descriptions, canoniques, alternances FR/EN, Open Graph et JSON-LD; les articles ont des liens Iaido/Jodo/Contact. Les gabarits des pages existantes conservent leurs textes. Les images de contenu doivent être locales, présentes, d’un format autorisé et décrites. L’absence d’images historiques empêche leur optimisation réelle. Pas de paquet tiers à installer pour la génération. Decap sera la seule dépendance distante de l’administration, après activation et vérification de sa version.

La génération automatique et l’archive de vérification sont configurées dans GitHub Actions. Aucun déploiement, service OAuth ou authentification réelle n’a été activé. Le workflow distant n’a pas été exécuté faute de branche poussée.

## Tests exécutés

- `python3 -m unittest discover -s tests -v` : **8 tests réussis**. Liens internes et ancres de toutes les pages générées, images locales, un H1 par page publique, canoniques, FR/EN réciproques, texte échappé, brouillons, nettoyage après suppression, image absente/externe refusée, traduction provisoire hors sitemap de production et verrouillage de la configuration production/OAuth.
- `python3 tools/build.py` : **9 pages HTML**, dont 6 existantes, 2 index Articles et 1 administration inactive; **0 article historique**.
- `node --check script.js` : réussi, syntaxe du script existant vérifiée.
- Contrôle des ressources et conservation des textes existants : effectué par comparaison automatisée du corps HTML des six pages; empreintes Git du logo PNG, du SVG original, de la police et du script identiques à celles du dépôt distant; les tests utilisent des données synthétiques uniquement en répertoire temporaire, jamais dans le contenu livrable.

## Tests non exécutables ici

- Affichage réel mobile/ordinateur et interactions JavaScript : Playwright est installé mais son navigateur Chromium est absent. Le démarrage d’un serveur HTTP local est également interdit dans ce bac à sable (`Operation not permitted`). Les règles responsive ont été examinées, sans prétendre à une validation visuelle. Refaire la vérification à 375, 768 et 1440 pixels, tester le menu clavier, les liens FR/EN et l’absence d’erreurs console.
- Authentification OAuth, interface Decap, téléversement et publication réels : service, application OAuth et accès utilisables absents. La configuration est un gabarit désactivé, pas une preuve de fonctionnement.
- Chargement des liens sociaux externes, vérification CDN et audit des avis de sécurité Decap : accès réseau de l’exécuteur indisponible. Les tests couvrent les ressources locales; aucun audit de vulnérabilités distant réussi n’est revendiqué.
- Contenu des sept articles, fidélité des traductions, droits et optimisation de leurs images : archive absente.
- SEO externe, performance navigateur, déploiement GitHub Pages et contrôles GitHub Actions : à effectuer sur l’aperçu hébergé autorisé.

Le site actuellement en production, le domaine et les DNS n’ont pas été modifiés.
