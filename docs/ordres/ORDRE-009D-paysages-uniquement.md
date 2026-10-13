# ORDRE-009D — Jeu des envies : des paysages et monuments, et rien d'autre

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire
**Échéance stricte** : mardi 13 octobre 2026, **avant 18 h**, poussé **directement sur `main`** (gel du code ce soir, anniversaire demain)

## Constat (test de Maxime sur iPhone, 10 pays)
Au moins 8 pays sur 10 montraient des photos sans rapport avec un paysage ou un monument : **personnalités publiques, timbres, pièces de monnaie, affiches**. C'est typiquement le contenu des articles Wikipédia/Wikivoyage, pas des sites UNESCO ni des bannières.

## Règle absolue (demande de Maxime)
**Uniquement des paysages et des monuments. En cas de doute sur une photo, on ne l'affiche pas.** Une carte avec la seule silhouette vaut mieux qu'une photo hors sujet. Moins de photos, mais toujours justes.

## Sources autorisées : deux, pas une de plus
1. **La bannière Wikivoyage** du pays (Wikidata P948) — photo panoramique de paysage choisie par les contributeurs ; c'est la source la plus sûre.
2. **Les photos des sites du patrimoine mondial de l'UNESCO** du pays (requête SPARQL actuelle de l'ORDRE-009C, P1435 = Q9259, image P18), les plus célèbres d'abord, un cliché par site, légende « 📍 nom du site ».

**Supprimer entièrement** tout le reste : plus aucune image tirée d'articles Wikipédia ou Wikivoyage (`media-list`), ni d'aucune autre source. Si les deux sources ne donnent rien de valide → **silhouette**.

## Filtres obligatoires sur chaque photo (toutes les conditions, sinon rejet)
1. **Format** : JPEG uniquement.
2. **Orientation paysage** : largeur / hauteur ≥ 1,3 (élimine portraits, timbres, pièces, affiches, généralement verticaux ou carrés). Largeur d'origine ≥ 1 200 px.
3. **Nom de fichier** : rejet s'il contient un de ces mots **en tant que mot entier** (séparateurs : espace, `_`, `-`, `.`, `(`, `)`, `,`), sans tenir compte de la casse ni des accents : flag, drapeau, map, carte, plan, locator, location, orthographic, coat, blason, armoiries, emblem, emblème, logo, seal, sceau, graph, chart, diagram, population, portrait, president, président, minister, ministre, king, queen, roi, reine, prince, princess, princesse, signature, signing, meeting, visit, visite, ceremony, cérémonie, stamp, timbre, coin, pièce, monnaie, banknote, billet, poster, affiche, cover, couverture, ticket, postcard, carte postale, statue (garder « statue » seulement si le fichier vient de la bannière). *Passer à des mots entiers corrige aussi la limite relevée dans l'ORDRE-009C (Chartres, Mapungubwe ne sont plus écartés à tort).*
4. **Catégories Commons** : demander aussi `Categories` dans `iiextmetadatafilter` (avec `Artist`) et rejeter la photo si une catégorie contient (mots entiers, mêmes règles) : stamps, timbres, coins, banknotes, currency, posters, people, persons, portraits, politicians, presidents, men, women, children, logos, maps, flags, coats of arms, emblems, documents, books, paintings, drawings, illustrations, artworks, sculptures, statues, interiors (sauf si la photo vient de la bannière). Si les catégories ne peuvent pas être lues → **rejet** (on n'affiche pas ce qu'on n'a pas pu vérifier).
5. La bannière passe les filtres 1, 3 et 4 (pas la règle d'orientation, elle est panoramique par nature).

## Le reste ne change pas
Repli silhouette après 4 s, interrupteur `PHOTOS_ENVIES`, gestes, préchargement de la carte suivante seulement, crédits, légendes, exclusion des domaines Wikimedia du cache du service worker.
- Mémoire des photos : passer la clé à `nos-voyages-photos-v3` (pour oublier les anciennes listes sur les iPhone).
- `sw.js` : `CACHE` → `nos-voyages-v11`.

## Tests (réponses Wikimedia simulées, iPhone 390 × 844)
1. Jeu de cas « pièges » : une personnalité, un timbre, une pièce, un billet, une affiche, une carte, un drapeau, un tableau, un portrait vertical, une photo carrée, une photo sans catégories lisibles → **tous rejetés**.
2. Faux positifs corrigés : « Cathédrale de Chartres », « Mapungubwe », « Cartagena » → acceptés s'ils passent les autres filtres.
3. Bannière seule valide → une photo ; rien de valide → silhouette, sans erreur.
4. Aucune requête vers `media-list` de Wikipédia ou Wikivoyage (vérifier en comptant les requêtes).
5. Batterie existante (ORDRES 002 à 009C) : tout passe, aucune erreur console.

## Ce que Maxime devra faire
1. Attendre 2 minutes après le push (déploiement GitHub Pages), **fermer complètement l'app**, la rouvrir.
2. ☰ → Jouer → regarder 10 à 15 cartes de continents différents. Attendu : moins de photos, mais **uniquement des paysages et monuments** ; beaucoup de cartes en silhouette, c'est normal.
3. Si une seule photo hors sujet apparaît encore : pays + capture à l'architecte. Si le doute persiste : `PHOTOS_ENVIES = false`.
4. Si tout est bon : tag `v1.2-anniversaire` sur `main`.

## Critères de fin
- [ ] Deux sources seulement, filtres 1 à 4 appliqués, rejet en cas de doute
- [ ] Clé de mémoire `v3`, cache `v11`
- [ ] Tests passés, captures dans `docs/captures/`, état du projet à jour
- [ ] Commit et push **sur `main`** avant 18 h, résumé de 5 lignes

## Compte rendu (à remplir par Claude Code)
