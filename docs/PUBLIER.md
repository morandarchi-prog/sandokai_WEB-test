# Publier un article

L’interface `/admin/` est volontairement inactive tant que le service OAuth n’est pas configuré et testé. Ce guide décrit le fonctionnement prévu après activation; aucune connexion réelle n’a pu être validée dans cette session.

1. Ouvrir `/admin/` et se connecter avec un compte GitHub autorisé sur le dépôt.
2. Dans **Articles bilingues**, créer une entrée. Choisir une adresse permanente en minuscules et tirets; ne plus changer cette adresse après publication.
3. Saisir en français et en anglais le titre, la description SEO et le contenu intégral. Ajouter les paragraphes, intertitres H2, sous-titres H3 après un H2, citations et images avec les blocs proposés. Le texte est du texte simple : les caractères HTML sont affichés comme texte, le Markdown n’est pas interprété. Ne pas coller une transcription HTML dans un paragraphe. Conserver les textes historiques mot pour mot, avec leurs paragraphes et intertitres.
4. Ajouter au besoin une image de présentation et sa description ALT dans chaque langue. Utiliser des fichiers PNG, JPEG, WebP ou AVIF détenus ou autorisés par l’organisme; préférer des noms descriptifs, une largeur adaptée (environ 1600 px maximum) et une compression raisonnable. Les fichiers sont stockés dans `assets/articles/`, sans dépendance à l’ancien site. Ne pas téléverser d’information confidentielle.
5. Enregistrer le brouillon avec **Publier après validation française** désactivé. Le workflow éditorial Decap conserve le travail dans une branche/PR; la visibilité GitHub du dépôt reste publique, y compris pour les brouillons.
6. Après relecture française, activer **Publier après validation française**. Laisser **Traduction anglaise approuvée** désactivé jusqu’à révision autorisée. Les deux versions seront consultables; l’anglaise portera un avis provisoire et restera `noindex` même en production.
7. Faire vérifier l’aperçu et les contrôles GitHub. Dans le circuit éditorial Decap, publier après validation fusionne les changements de contenu vers `main`. Cette action est réservée aux personnes autorisées; aucune fusion n’a été effectuée dans cette livraison.
8. Le workflow génère automatiquement les pages HTML, les index et les fichiers SEO dans l’archive `sandokai-site-a-valider`. La mise en ligne automatique nécessite ensuite le branchement à l’hébergement retenu, après autorisation distincte. Durant la préparation actuelle, télécharger et vérifier l’archive; rien n’est déployé automatiquement.

Les URL suivent `articles/adresse-permanente.html` et `en/articles/adresse-permanente.html`. Le lien FR / EN conserve le même article; les liens de navigation et de contact conservent la langue.

## Importer les sept articles historiques

Fournir `Sandokai-blogue-bilingue-Decap(1).zip`. L’examiner sans écraser les fichiers existants, établir pour chaque texte la source, la langue, les images autorisées et leur empreinte de contrôle, puis importer dans `content/articles/<adresse>.json` selon les champs du gabarit Decap. Le schéma préparé ici peut différer de celui de l’archive : adapter l’import après examen, jamais remplacer les textes par des résumés. Vérifier le texte extrait de chaque page générée contre la source. Les dates et auteurs sont volontairement absents du schéma provisoire : les ajouter seulement si les sources permettent de les établir.
