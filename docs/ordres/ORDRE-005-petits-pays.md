# ORDRE-005 — Rendre les petits pays et les îles touchables (Maldives en tête)

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : fait
**Échéance** : lundi 12 octobre 2026, avant le gel du code du soir · **Nature** : correction de bug (prioritaire)

## Constat (retour de l'utilisateur sur iPhone)
Les **Maldives** se voient sur la carte, mais **impossible de toucher dessus** : rien ne s'ouvre.

**Cause** : sur le globe, la touche ne marche que si le doigt tombe exactement sur un pixel du pays (`gl.on('click', 'pays', …)`, ligne ~500). Les Maldives sont une poussière d'atolls de quelques pixels : impossible à viser au doigt. Même problème pour tous les très petits pays et îles (Malte, Singapour, Seychelles, Maurice, Bahreïn, Luxembourg, Andorre, Monaco, Saint-Martin, Martinique, La Réunion, les petites îles du Pacifique et des Caraïbes…), et sur la carte plate de secours.

**Second problème, émotionnel** : si les Maldives sont marquées « visitées », leur rose est quasi invisible à l'échelle du globe. Un pays visité doit **se voir** et **se toucher**.

## Résultat attendu
1. On peut **toucher les Maldives** (et tout petit pays) au doigt, à toutes les échelles, et sa fiche s'ouvre.
2. Les petits pays **visités** ou **rêvés** sont **visibles** même globe entier.
3. Le comportement des grands pays ne change pas : toucher la France ouvre toujours la France, jamais un voisin.

## Conception (décidée par l'architecte)

### A. Repères pour les petits pays (globe et carte plate)
- Au chargement des données (après `splitTerritories`), calcule pour chaque entité la surface de sa géométrie (approximation en degrés² suffisante) et son **point d'ancrage** : le centre de son plus grand polygone (pour les Maldives, un point au milieu des atolls).
- Est « petit pays » toute entité sous un seuil de surface à calibrer (cible indicative : Luxembourg compris, Belgique exclue). Liste les petits pays retenus dans le compte rendu.
- Globe (MapLibre) : une source GeoJSON de **points** (un par petit pays, `promoteId` = code) et deux couches :
  - `petits-pays` (circle, visible) : petit point de 4 à 5 px, couleur selon le `feature-state` comme les pays (`visited` → `--glow` avec léger halo, `dream` → `--dream`, sinon `--land` avec bord discret), contour blanc si sélectionné. Les points « à découvrir » restent discrets pour ne pas encombrer le globe ;
  - `petits-pays-zone` (circle, transparent, rayon ≈ 22 px soit 44 px de cible) : uniquement pour la détection de la touche.
  - Les couches de points masquent les points sur la face cachée du globe (comportement natif de MapLibre en projection globe, à vérifier).
- Carte plate (Leaflet) : même logique avec des `circleMarker` (petit point visible + rayon de clic suffisant), au-dessus des polygones.
- Les états (`visited`, `dream`, sélection) sont mis à jour avec les mêmes fonctions que les pays (`refresh`), pour rester synchronisés en mode édition.

### B. Tolérance à la touche (globe)
Remplace la détection « pixel exact » par une détection tolérante, dans cet ordre :
1. si la touche tombe sur un point `petits-pays-zone` → ce petit pays (le plus proche s'il y en a plusieurs) ;
2. sinon, si elle tombe exactement sur un pays → ce pays (comportement actuel) ;
3. sinon, cherche dans une boîte de ±16 px autour du doigt (`queryRenderedFeatures`) et prend le pays **le plus proche** du point touché ;
4. sinon, rien (touche dans l'océan).
Ne déclenche pas d'ouverture à la fin d'un glissement (rotation du globe) : seule une vraie touche ouvre une fiche.

### C. Filet de sécurité : rechercher un pays
En haut de la liste « Nos pays » (☰), ajoute un champ **« Rechercher un pays… »** :
- il cherche parmi **tous** les pays et territoires de la carte (noms français, sans tenir compte des accents ni des majuscules : « maldives », « reunion » trouvent bien Maldives et La Réunion) ;
- les résultats (drapeau + nom + statut) s'affichent sous le champ ; en toucher un fait voler la carte jusqu'au pays et ouvre sa fiche ;
- champ vide → la liste habituelle de nos pays ;
- police 16 px (pas de zoom iOS), cible ≥ 44 px, style cohérent avec la fiche (skill frontend-design).
C'est utile à elle comme à moi : en mode édition, c'est aussi le moyen le plus rapide d'ajouter un pays.

### D. Vol vers un petit pays
Pour un petit pays, `flyTo` cadre sur l'ensemble de sa géométrie (pas seulement le plus grand polygone, qui ne fait qu'un atoll pour les Maldives), avec un zoom maximum adapté (≈ 6 à 7) pour voir l'archipel.

## Version
`sw.js` : `CACHE` → `nos-voyages-v6`.

## Tests (webapp-testing, iPhone 390 × 844, mode démo)
1. Globe entier : toucher le point des Maldives ouvre la fiche « Maldives ». Capture.
2. Marquer les Maldives « visitées » : le point devient rose et se voit globe entier. Capture.
3. Zoom sur l'océan Indien : les atolls sont visibles, toucher un atoll ou à côté (≤ 16 px) ouvre les Maldives.
4. Même chose pour Malte et Singapour.
5. Non-régression : toucher le centre de la France, de l'Italie, de la Belgique ouvre bien ces pays ; toucher en plein océan n'ouvre rien ; faire tourner le globe d'un glissement n'ouvre rien.
6. Recherche : « maldives », « reunion », « Côte » donnent les bons résultats ; toucher un résultat vole jusqu'au pays et ouvre sa fiche.
7. Carte plate (`?carte=plate`) : tests 1, 2 et 6.
8. Mode édition : marquer un petit pays depuis la recherche, sa couleur se met à jour immédiatement.
9. Les tests des ORDRES 002, 003 et 004 passent toujours, aucune erreur console (hors 404 volontaires du test de secours).

## Critères de fin
- [x] Maldives et petits pays touchables et visibles, sur le globe et la carte plate
- [x] Recherche de pays dans la liste
- [x] Aucune régression sur les grands pays
- [x] Cache `v6`, captures dans `docs/captures/`, état du projet à jour
- [x] Commit et push sur `main`, résumé de 5 lignes pour l'architecte

## Compte rendu (à remplir par Claude Code)

**Fait — 11 octobre 2026**

**A. Repères des petits pays.** `analyseGeo` (après `splitTerritories`) calcule pour chaque entité sa surface en degrés² corrigés de la latitude (× cos lat), son point d'ancrage et ses cadrages.
- Ancrage : centre de l'ensemble de la géométrie si elle est compacte (moins de 20° d'étendue, cas des Maldives : le point tombe au milieu des atolls), sinon centre du plus grand polygone (Kiribati, Fidji, qui traversent la ligne de changement de date).
- **Seuil : 1,25 degré²**, soit environ 15 000 km². Le Luxembourg (0,21) est inclus, la Belgique (2,48) exclue.
- **88 entités retenues** : Åland, Andorre, Anguilla, Antigua-et-Barbuda, Aruba, Bahamas, Bahreïn, Barbade, Bermudes, Brunei, Cap-Vert, Chypre, Chypre du Nord, Cité du Vatican, Comores, Curaçao, Dominique, États fédérés de Micronésie, Gambie, Géorgie du Sud-et-les Îles Sandwich du Sud, glacier de Siachen, Grenade, Guadeloupe, Guam, Guernesey, Hong Kong, île de Man, île Norfolk, îles Ashmore-et-Cartier, îles Caïmans, îles Cook, îles Féroé, îles Heard-et-MacDonald, îles Malouines, îles Mariannes du Nord, îles Marshall, îles Pitcairn, îles Turques-et-Caïques, îles Vierges britanniques, îles Vierges des États-Unis, Jamaïque, Jersey, Kiribati, Kosovo, La Réunion, Liban, Liechtenstein, Luxembourg, Macao, Maldives, Malte, Martinique, Maurice, Mayotte, Monaco, Monténégro, Montserrat, Nauru, Niue, Palaos, Palestine, Pays-Bas caribéens, Polynésie française, Porto Rico, Qatar, Saint-Barthélemy, Saint-Christophe-et-Niévès, Saint-Marin, Saint-Martin, Sint Maarten, Saint-Pierre-et-Miquelon, Saint-Vincent-et-les-Grenadines, Sainte-Hélène, Sainte-Lucie, Samoa, Samoa américaines, Sao Tomé-et-Principe, Seychelles, Singapour, Terres australes et antarctiques françaises, Territoire britannique de l'océan Indien, Territoires extérieurs australiens de l'océan Indien, Timor oriental, Tonga, Trinité-et-Tobago, Tuvalu, Vanuatu, Wallis-et-Futuna.
- **Globe** : source de points `petits` (`promoteId: 'code'`) et trois couches : `petits-halo` (halo rose flou, seulement si visité), `petits-pays` (point de 5 px si visité, 4,5 px si rêvé, 2,5 px discret si « à découvrir », contour blanc si sélectionné) et `petits-pays-zone` (rayon 22 px, transparent). **Face cachée** : vérifié sur capture, MapLibre masque bien les points derrière le globe ; Singapour, de dos dans la vue d'ensemble, n'est ni dessiné ni touchable.
- **Carte plate** : mêmes points en `circleMarker` au-dessus des polygones.
- **Synchronisation** : les états (visité, rêvé, sélection) passent par le même `refresh` que les pays.

**B. Touche tolérante** (`pickCountry`, commune au globe et à la carte plate) dans l'ordre demandé : zone d'un petit pays (le plus proche), puis pays exactement sous le doigt, puis pays le plus proche dans ±16 px (recherche par anneaux de 4 en 4 px), sinon rien.
- **Précision ajoutée à la règle 1**, après test : si le doigt est posé sur la terre d'un grand pays, ce grand pays l'emporte. Seul le point coloré d'un petit pays visité ou rêvé passe devant, s'il est touché à moins de 8 px. Sans cette règle, en vue d'ensemble, toucher le centre de l'Italie ouvrait le **Vatican** et celui de la Belgique le **Luxembourg**, ce qui enfreint « jamais un voisin ». En mer, la zone de 44 px s'applique toujours (Maldives, Malte, Seychelles…). Un petit pays « à découvrir » enclavé (Vatican, Saint-Marin) reste accessible en zoomant ou par la recherche.
- Un glissement n'ouvre rien : MapLibre et Leaflet n'émettent pas de `click` à la fin d'un glissement.
- Sur la carte plate, les polygones ne sont plus cliquables eux-mêmes. La détection passe par un test « point dans le polygone » sur les données, avec la même fonction de choix.

**C. Recherche** en haut de « Nos pays » : champ « Rechercher un pays… » (16 px, 48 px de haut, loupe discrète, effacement natif d'iOS).
- Recherche parmi les 249 entités, sans tenir compte des accents ni des majuscules ; les noms qui commencent par la saisie passent d'abord ; 40 résultats au maximum.
- Chaque résultat montre le drapeau, le nom et le statut. Le toucher fait voler la carte jusqu'au pays et ouvre sa fiche.
- Champ vide : la liste habituelle revient. Aucun résultat : un message l'indique.
- Natural Earth appelle « Saint-Martin » les parties française **et** néerlandaise de l'île : la partie néerlandaise s'affiche désormais « Sint Maarten » (`NOMS` dans le code).

**D. Vol vers un petit pays** : cadrage sur toute la géométrie (tout l'archipel des Maldives), zoom maximum 6,5. Le zoom maximum du globe passe de 6 à 7 pour que ce cadrage soit possible.

**Correction en passant (bug de l'ORDRE-003)** : sur la carte plate, le fond était **gris clair** au lieu de bleu nuit, parce que `leaflet.css`, chargé après l'app, écrasait notre règle. La règle est maintenant plus forte (`#map.leaflet-container`).

`sw.js` passé à `nos-voyages-v6`.

**Tests** (webapp-testing, 390 × 844, mode démo, `tests/test_ordre005_iphone.py`) : **41/41**, aucune erreur console. Sur le globe **et** sur la carte plate :
- Recherche : « maldives », « reunion » et « Côte » (Côte d'Ivoire) donnent les bons résultats. Message si aucun résultat, liste habituelle si le champ est vidé, champ en 16 px et 48 px de haut. Toucher un résultat fait voler la carte et ouvre la fiche.
- Vue d'ensemble : toucher le point doré des Maldives (et de Malte) ouvre leur fiche.
- En mode édition, marquer les Maldives « visitées » depuis la recherche les rend roses : atolls au zoom, point rose visible et touchable en vue d'ensemble.
- Toucher à 12 px d'un atoll ouvre les Maldives.
- Malte et Singapour : toucher le point ou à environ 17 px ouvre la fiche.

Sur le globe uniquement :
- Toucher le centre de la France, de l'Italie et de la Belgique ouvre le bon pays, au zoom du pays comme en vue d'ensemble.
- Toucher en plein océan n'ouvre rien, et un glissement non plus.

Non-régression : ORDRE-002 14/14, ORDRE-003 18/18, ORDRE-004 18/18, aucune erreur console hormis les deux 404 volontaires du test de secours. Captures dans `docs/captures/ordre005-*.png`.

**Non testé ici** : le vrai doigt sur iPhone. Les touchers sont simulés par des clics de souris, mais MapLibre et Leaflet traitent les deux de la même façon.
