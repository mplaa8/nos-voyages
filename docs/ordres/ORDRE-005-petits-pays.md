# ORDRE-005 — Rendre les petits pays et les îles touchables (Maldives en tête)

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire
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
- [ ] Maldives et petits pays touchables et visibles, sur le globe et la carte plate
- [ ] Recherche de pays dans la liste
- [ ] Aucune régression sur les grands pays
- [ ] Cache `v6`, captures dans `docs/captures/`, état du projet à jour
- [ ] Commit et push sur `main`, résumé de 5 lignes pour l'architecte

## Compte rendu (à remplir par Claude Code)
