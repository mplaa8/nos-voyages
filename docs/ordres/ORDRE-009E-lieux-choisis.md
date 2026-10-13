# ORDRE-009E — Jeu des envies : photos des lieux emblématiques choisis pour chaque pays

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : fait (lancé sur décision de Maxime)
**Échéance stricte** : mardi 13 octobre 2026, **avant 20 h**, poussé **directement sur `main`**

## Contexte
Avec l'ORDRE-009D, beaucoup de pays connus n'ont plus aucune photo. Des agents ont préparé **`lieux-envies.json`** (racine du dépôt) : pour 236 pays et territoires, **699 lieux emblématiques** (paysages et sites culturels), avec leur nom français et le **titre exact de leur article Wikipédia en anglais** (`wiki_en`), vérifié page par page pour la plupart.
Format : `{ "PER": { "pays": "Pérou", "lieux": [ { "nom_fr": "Machu Picchu", "type": "culture", "wiki_en": "Machu Picchu" }, … ] }, … }` — clés = codes pays de la carte (ADM0_A3 ; réconcilier avec `ISO_A3` / `ISO_A3_EH` de Natural Earth si un code diffère, et avec les territoires séparés de l'ORDRE-004).

## Nouvelle source des photos (remplace celle de l'ORDRE-009D)
Pour la carte affichée, jusqu'à 3 photos, dans cet ordre :
1. La **bannière Wikivoyage** du pays (comme aujourd'hui, mêmes filtres).
2. La **photo principale de l'article Wikipédia** de chaque lieu de `lieux-envies.json`, dans l'ordre du fichier, avec la légende « 📍 {nom_fr} ».
   - Une seule requête pour les lieux d'un pays : `https://en.wikipedia.org/w/api.php?action=query&format=json&origin=*&redirects=1&prop=pageimages|pageprops&piprop=thumbnail|name&pithumbsize=960&titles=A|B|C`.
   - Rejeter la photo si : page d'homonymie (`pageprops.disambiguation`), pas de vignette, fichier non JPEG, format non paysage (largeur / hauteur < 1,2), ou nom de fichier contenant un de ces mots entiers : map, carte, locator, location, satellite, montage, collage, flag, drapeau, logo, coat, seal, emblem, plan, diagram, portrait.
   - Crédit : « Photo : Wikimedia Commons » (pas d'appel supplémentaire pour l'auteur ce soir).
3. Plus aucune autre source (supprimer la requête UNESCO de l'ORDRE-009D).

Inchangés : repli silhouette (4 s), interrupteur `PHOTOS_ENVIES`, gestes, préchargement de la carte suivante seulement, domaines Wikimedia hors du cache du service worker. Clé de mémoire des photos → `nos-voyages-photos-v4`, `sw.js` → `nos-voyages-v12`.

## Page de revue visuelle pour Maxime : `revue-photos.html`
Les agents n'ont pas pu voir les images : la validation visuelle finale est humaine.
- Nouveau fichier à la racine, non lié depuis l'app, **jamais mis en cache** par `sw.js`.
- Affiche tous les pays (filtre par continent en haut), et pour chacun les photos exactement comme le jeu les choisirait (même code de sélection, réutilisé ou copié), en vignettes avec le nom du pays et la légende du lieu.
- Toucher une vignette la marque « ✖ refusée » (re-toucher annule). Les refus sont gardés en `localStorage`.
- Bouton « Copier la liste des refus » : copie un texte du type `REFUS: PER|Lake Titicaca, FRA|Eiffel Tower, …` à coller à Claude Code.
- Lisible sur Mac (grille large) et sur iPhone.

## Traitement des refus
Quand Maxime colle sa liste : retirer ces lieux de `lieux-envies.json` (et la bannière d'un pays si elle est refusée : liste `BANNIERES_REFUSEES` dans `index.html`), incrémenter le cache, pousser sur `main`.

## Tests (réponses Wikimedia simulées)
1. Sélection : bannière + lieux dans l'ordre, légendes, rejets (homonymie, PNG/SVG, portrait, mots interdits).
2. Aucune requête UNESCO ni `media-list`.
3. Repli silhouette, interrupteur, gestes, correspondances : inchangés.
4. `revue-photos.html` : affichage, refus, copie de la liste ; absente du cache.
5. Batterie existante (ORDRES 002 à 009D) : tout passe.

## Critères de fin
- [x] Photos des lieux choisis, légendes, filtres, repli silhouette
- [x] `revue-photos.html` opérationnelle
- [x] Clé `v4`, cache `v12`, tests passés, état du projet à jour
- [x] Push sur `main` avant 20 h, résumé de 5 lignes + lien de la page de revue

## Compte rendu (à remplir par Claude Code)

**Fait le 13 octobre 2026**, poussé sur `main`.

**Source des photos** (`index.html`, entre les repères `DÉBUT SÉLECTION PHOTOS` / `FIN SÉLECTION PHOTOS`) :
- Bannière Wikivoyage : inchangée (mêmes filtres 009D). Nouvelle liste `BANNIERES_REFUSEES` (vide) : un pays qui y figure n'interroge même plus Wikidata.
- Lieux : `lieux-envies.json` chargé une fois (au premier pays affiché), puis **une requête Wikipédia par pays** avec tous ses titres (`redirects=1`, `pageimages|pageprops`, vignette 960 px). Les titres normalisés et redirigés sont suivis. Photos dans l'ordre du fichier, légende « 📍 nom_fr », crédit « Photo : Wikimedia Commons », une même image n'est jamais montrée deux fois.
- Rejets : homonymie, page absente, pas de vignette, pas JPEG, largeur/hauteur < 1,2, mots interdits en mots entiers (liste de l'ordre). **Ajout, à valider** : la vignette doit venir de Wikimedia **Commons**. Les fichiers locaux de Wikipédia en anglais sont des images non libres (affiches, logos, pochettes) : rejetés par prudence.
- Requête UNESCO supprimée. Une erreur Wikipédia n'est pas mémorisée : retentée à la partie suivante. Clé `nos-voyages-photos-v4`, cache `nos-voyages-v12`.
- Codes : une seule clé différait de la carte, `ALA` (Åland), renommée `ALD` dans le JSON. Les 7 territoires séparés y figurent déjà. Sans lieux (13 codes, dont Antarctique, Somaliland, Chypre du Nord…) : bannière seule ou silhouette.

**`revue-photos.html`** : https://mplaa8.github.io/nos-voyages/revue-photos.html
- Elle relit `index.html` et exécute le code même de sélection : aucune copie, donc aucun écart possible avec le jeu. Elle reprend aussi les listes de pays, territoires, continents et exclusions du jeu, soit 244 pays.
- Filtre par continent. Les pays sont chargés au fil du défilement, 4 à la fois.
- Toucher pour « ✖ refusée », retoucher pour annuler. Les refus sont gardés dans le navigateur (`localStorage`).
- « Copier la liste des refus » donne `REFUS: PER|Lake Titicaca, PER|bannière`. Les lieux sont désignés par leur `wiki_en`, la bannière par « bannière ». Si la copie automatique échoue, le texte s'affiche à copier à la main.
- Mise en page : grille de 3 colonnes sur Mac, 1 sur iPhone. La page n'est liée nulle part et `sw.js` ne la met jamais en cache (comme `carte-cadeau.html`).

**Tests** (webapp-testing, Wikimedia simulé) : `tests/test_ordre009e_lieux.py` **33/33** :
- **Sélection** : bannière puis lieux dans l'ordre, légendes, redirections. Les 11 pièges sont rejetés : homonymie, PNG, SVG, portrait, presque carrée, carte de localisation, montage, satellite, sans vignette, page absente, hors Commons.
- **Bannière** : refusée ou au nom interdit → non affichée. Bannière seule → 1 photo. Rien de valide → silhouette.
- **Requêtes** : seulement la carte affichée et la suivante. Aucune requête UNESCO, `media-list`, Wikivoyage ni Wikipédia fr (398 requêtes comptées).
- **Comportements inchangés** : service lent, en erreur, image introuvable, interrupteur, gestes, correspondance.
- **Revue** : 244 pays, même sélection que le jeu, refus et annulation, refus gardés après rechargement, copie, filtre Océanie, grille Mac, page absente du cache.
- **Données** : les codes de `lieux-envies.json` correspondent tous à la carte.

**Non-régression** : ORDRES 002 (OK), 003 18/18, 004 18/18, 005 41/41, 006 47/47 + code secret 15/15, 009 36/36. Aucune erreur console hors erreurs volontaires. `tests/test_ordre009d_paysages.py` est remplacé par ce test. Le test 009 simule désormais Wikipédia en au lieu du service UNESCO. Captures : `docs/captures/009e-*.png`.

