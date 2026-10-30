# Configuration restante

## Hébergement statique

GitHub Pages peut servir le résultat `_site/`, mais ne fournit ni serveur OAuth Decap ni construction Python intégrée au mode « branch/Jekyll ». Le workflow fourni construit une archive statique automatiquement à chaque changement de `main` ou PR, sans déploiement. Après choix de l’hébergement et autorisation, utiliser une publication GitHub Actions vers Pages (artefact `_site/`, permissions Pages minimales, environnement protégé) ou publier le même dossier sur un hébergement statique économique. Ne pas activer simplement la publication de la racine : les copies HTML initiales ne se mettraient pas à jour après édition CMS.

Aucun fichier CNAME, changement de domaine, DNS ou déploiement n’est inclus. Une mise en ligne finale exige l’autorisation de l’utilisateur. Les aperçus GitHub Actions doivent être testés avant de remplacer l’ancien hébergement.

## OAuth GitHub / Decap

Le fichier `admin/config.template.yml` décrit le backend GitHub et le workflow éditorial; ce n’est pas une configuration opérationnelle. La page `/admin/` explique que l’administration attend sa configuration. `cms_enabled` vaut `false`. Aucune clé ni jeton n’est enregistré dans le dépôt.

GitHub Pages seul ne suffit pas. Solution possible à faible coût : un petit service OAuth compatible avec le backend GitHub Decap sur une fonction HTTPS serverless disposant d’un palier gratuit, ou un serveur déjà détenu par l’organisme. Évaluer les limites et conditions actuelles du fournisseur avant choix; aucun abonnement n’a été créé. Le service doit échanger le code OAuth côté serveur et communiquer avec Decap selon son protocole d’authentification. Cette livraison ne fournit pas de serveur OAuth et ne prétend pas l’avoir testé.

Avant activation :

1. Choisir et auditer l’implémentation du service. Créer une application OAuth GitHub avec URL de rappel HTTPS correspondant exactement au service choisi. Configurer un compte GitHub avec droits d’écriture et protection de `main` adaptée au circuit éditorial.
2. Stocker le secret client dans le gestionnaire de secrets du service, jamais dans YAML, HTML, Git ou JavaScript public. Limiter les permissions demandées au nécessaire pour ce dépôt public (`public_repo` si l’implémentation OAuth classique le nécessite); vérifier la portée réelle de l’accès accordé. Une application OAuth classique peut accorder des droits sur d’autres dépôts publics du compte.
3. Exiger `state` aléatoire, à usage unique et expirant, vérifié au retour; URI de redirection fixe, origines de l’administration explicitement autorisées (y compris son sous-chemin), messages `postMessage` limités à l’origine attendue et contrôle de l’origine côté client. Aucun CORS générique, redirection ouverte, journalisation des codes ou jetons, ni secret dans l’URL d’un navigateur.
4. Copier `admin/config.template.yml` vers `admin/config.yml`, remplacer l’hôte `.invalid` par l’hôte réel et vérifier `auth_endpoint` contre le serveur choisi. Garder `branch: main` seulement après intégration de la présente branche. `public_folder: /assets/articles` est une convention de contenu : le générateur réécrit les images en liens relatifs compatibles avec le sous-chemin GitHub Pages.
5. Vérifier la disponibilité et les avis de sécurité de la version épinglée Decap `3.8.3` sur jsDelivr avant activation; le script distant n’a pas pu être chargé dans cet environnement. Si nécessaire choisir une version stable vérifiée et la mettre à jour dans `tools/build.py`. La désactivation actuelle évite toute dépendance CMS au chargement du site public. Une copie locale vérifiée et licenciée du script peut remplacer le CDN.
6. Passer `cms_enabled` à `true` seulement sur un aperçu contrôlé. Tester une connexion autorisée, un refus d’accès, une annulation, un retour OAuth invalide ou rejoué, la fermeture de la fenêtre, puis une révocation de l’accès.
7. Tester bout en bout : téléversement d’image, brouillon, modification bilingue, aperçu, contrôle GitHub, publication après validation, mise à jour de l’index et des deux pages, suppression du contenu de test et révocation du jeton de test. Tester aussi la protection de branche et les droits des personnes qui publient. Noter les résultats avant ouverture de l’administration.

La publication de contenu via Decap fusionne des PR. Les protections de branche peuvent nécessiter une approbation GitHub supplémentaire. Ne pas les affaiblir pour contourner un échec.

## Référencement et futur domaine

`site.config.json` utilise l’adresse de test et `production: false`. Toutes les pages générées ont `noindex,nofollow`, `robots.txt` interdit l’exploration et le sitemap reste vide. Les copies HTML initiales à la racine portent aussi `noindex`. Ces mesures réduisent l’indexation accidentelle, sans rendre un dépôt ou un site public confidentiel.

Après autorisation de mise en production : définir `url` sur l’URL HTTPS définitive, avec son sous-chemin éventuel et un `/` final; activer `production: true` et `production_confirmed: true`. Le générateur refuse le domaine GitHub Pages en mode production afin d’éviter l’indexation du site de test. Il recrée canoniques, Open Graph, liens `hreflang` réciproques et sitemap. L’administration reste `noindex`; les versions anglaises non approuvées aussi et sont exclues du sitemap. Vérifier les redirections des anciennes URL historiques seulement après réception de leur liste et choix de l’hébergement. Ne pas inventer d’URL de redirection.

Les données structurées emploient Organization et BlogPosting, avec seulement les faits disponibles. Aucun horaire, tarif, enseignant, adresse physique, date de publication ou auteur n’a été ajouté. Les métadonnées ne garantissent pas de résultat enrichi Google; un contrôle Rich Results en production restera utile.
