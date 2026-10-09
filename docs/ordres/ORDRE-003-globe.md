# ORDRE-003 — Remplacer la carte plate par un globe 3D

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : fait (décision garder / revenir : dimanche 11)
**Prérequis** : ORDRE-002 terminé et poussé (évite les conflits dans `index.html`)
**Échéance** : samedi 10 octobre 2026 · **Décision garder / revenir** : dimanche 11 au soir, après test de l'utilisateur sur iPhone

## Objectif
À l'ouverture, ma femme voit **la Terre en 3D** sur le ciel de nuit, qui tourne lentement. Elle la fait tourner du doigt, zoome sur un pays (le globe s'aplatit naturellement en carte), touche un pays et retrouve sa fiche, comme aujourd'hui.

**Seul le bloc « carte » change.** Fiches pays, photos, souvenirs, liste, lettre, statistiques, mode édition et données Supabase restent identiques. Pas de modification du schéma.

## Choix techniques (décidés par l'architecte)
- **MapLibre GL JS v5** (open source, gratuit, sans clé d'API) avec `projection: { type: 'globe' }`. Épingle une version 5.x précise et vérifie qu'elle existe sur le CDN (cdnjs, sinon unpkg ou jsdelivr — listes autorisées par l'app).
- **Aucun fond de tuiles** : un style construit dans le code avec
  - une couche `background` couleur nuit (`--night`) ;
  - une source GeoJSON `pays` alimentée par le **même fichier Natural Earth** qu'aujourd'hui (`GEO_URLS`), avec `promoteId: 'ADM0_A3'` ;
  - une couche `fill` dont la couleur dépend de `feature-state` : `visited` → `--glow`, `dream` → `--dream`, sinon `--land` ;
  - une couche `line` pour les frontières (fines et discrètes pour les pays non visités, plus claires pour les visités) et un contour blanc pour le pays sélectionné (`feature-state` `selected`) ;
  - un **halo lumineux** autour des pays visités (par ex. une seconde couche `line` floutée, `line-blur`, en `--glow`), pour garder l'effet « points lumineux » ;
  - une **atmosphère** discrète autour du globe (propriété `sky` du style, réglages d'atmosphère), teintée bleu nuit / rose très léger. Les étoiles de l'écran d'accueil peuvent rester visibles derrière le globe si c'est simple (fond transparent au-delà de la sphère) ; sinon, fond uni.
- **L'Antarctique est conservé** sur le globe (sinon un trou au pôle Sud), au statut « à découvrir ».
- **Interactions** : glisser = faire tourner le globe, pincer = zoomer, toucher un pays = ouvrir sa fiche (fonction `openCountry` existante). Désactiver l'inclinaison et la rotation du nord (`touchPitch`, `dragRotate`, rotation au pincement) pour garder un geste simple. Zoom de 0 (globe entier) à ≈ 6.
- **Rotation automatique** lente (≈ un tour en 2 minutes, d'ouest en est) tant que personne ne touche le globe. Elle s'arrête au premier contact, quand une fiche est ouverte, et reprend après ≈ 15 s d'inactivité si aucune fiche n'est ouverte et que le zoom est proche de la vue d'ensemble. Pas de rotation automatique si `prefers-reduced-motion`.
- **Aller vers un pays** (liste « Nos pays ») : `fitBounds` sur le plus grand polygone du pays (même logique que `mainBounds` actuelle, adaptée au GeoJSON), en laissant la moitié basse de l'écran pour la fiche, zoom max ≈ 5, animation ≈ 1,2 s.
- **Bouton 🌍** : retour à la vue d'ensemble (globe entier centré sur l'Europe) et reprise de la rotation.
- Appeler `map.resize()` quand l'écran d'accueil / la lettre disparaissent.

## Filet de sécurité (obligatoire)
- Isole la carte derrière une petite interface commune, par ex. `MapView = { init(geo), refresh(), flyTo(code), worldView() }`, avec deux implémentations : **`GlobeView`** (MapLibre) et **`FlatView`** (le code Leaflet actuel, déplacé tel quel).
- **Bascule automatique sur `FlatView`** si : WebGL indisponible, MapLibre ne se charge pas, ou erreur à l'initialisation du globe. Leaflet n'est alors chargé qu'à ce moment-là (chargement dynamique du script et de la feuille de style), pour ne pas alourdir le cas normal.
- **Bascule manuelle** : l'adresse `?carte=plate` force la carte plate (utile pour comparer dimanche).
- **Retour arrière en une ligne** : une constante `CARTE_PAR_DEFAUT = 'globe'` sous `LETTRE`, commentée. La passer à `'plate'` suffit pour revenir à la carte actuelle.

## Performance iPhone
- Le globe doit rester fluide (≈ 60 i/s visés) : une seule source GeoJSON, pas de couches inutiles, pas de recalcul de style à chaque frame (seulement `setFeatureState` quand un statut change).
- Mettre à jour les couleurs via `setFeatureState` après chargement des données et après chaque modification en mode édition (équivalent de `refreshMap`).

## Version
- `sw.js` : passer `CACHE` à la version suivante (`nos-voyages-v4` si l'ORDRE-002 a mis `v3`). Le service worker doit mettre en cache MapLibre comme les autres librairies.

## Tests (skill webapp-testing, viewport iPhone 390 × 844, mode démo)
Si WebGL n'est pas disponible dans le navigateur de test sans tête, active le rendu logiciel (par ex. arguments Chromium `--use-gl=angle --use-angle=swiftshader` ou `--enable-unsafe-swiftshader`). Indique dans le compte rendu ce qui a pu être testé ou non.
1. Accueil → lettre → globe entier visible, qui tourne. Capture.
2. Marquer 3 pays visités (dont un en Asie) et 1 rêvé en mode démo : couleurs et halo corrects. Capture du globe et d'un zoom sur l'Europe.
3. Toucher un pays ouvre sa fiche ; la rotation s'arrête ; fermer la fiche n'entraîne pas de saut de la vue.
4. Depuis « Nos pays », toucher un pays fait voler le globe jusqu'à lui et ouvre sa fiche. Capture.
5. Bouton 🌍 : retour à la vue d'ensemble.
6. `?carte=plate` : la carte plate actuelle fonctionne comme avant. Simuler l'échec de MapLibre (URL de script invalide en test) : bascule automatique sur la carte plate.
7. `#admin` : mode édition, changement de statut → couleur mise à jour immédiatement sur le globe.
8. Aucune erreur dans la console.

## Critères de fin
- [x] Globe fonctionnel avec rotation automatique, zoom, sélection, vol vers un pays
- [x] Bascules automatique et manuelle vers la carte plate vérifiées
- [x] Rien de l'existant n'est cassé (fiches, lettre, stats, mode édition)
- [x] Cache `sw.js` incrémenté
- [x] Captures dans `docs/captures/`, `docs/00-etat-du-projet.md` mis à jour
- [x] Commit et push sur `main`
- [x] Résumé de 5 lignes pour l'architecte, avec **les 3 choses à tester par l'utilisateur sur son iPhone** pour la décision de dimanche

## Compte rendu (à remplir par Claude Code)

**Fait — 9 octobre 2026**

- **Globe** : MapLibre GL JS **5.24.0** (avril 2026), chargé à la demande depuis jsdelivr, avec unpkg en secours. cdnjs n'a pas pu être vérifié depuis l'environnement de Claude Code, alors que jsdelivr et unpkg reprennent toutes les versions publiées sur npm.
- **Style construit dans le code**, avec une seule source GeoJSON `pays` (même fichier Natural Earth, `promoteId: 'ADM0_A3'`, Antarctique conservé) et cinq couches : fond nuit, remplissage selon `feature-state`, halo flouté rose pour les pays visités, frontières, contour blanc de sélection.
- **Atmosphère discrète** et **espace transparent** : le ciel étoilé de l'accueil (nouveau `#sky`) reste visible derrière la sphère. Un essai d'éclairage (côté jour délavé) a été abandonné.
- **Interactions** : glisser pour tourner, pincer pour zoomer (zoom 0 à 6), toucher un pays pour ouvrir sa fiche. Inclinaison et rotation du nord désactivées.
- **Rotation automatique** : un tour en 2 minutes, d'ouest en est. Elle s'arrête au premier contact ou quand une fiche est ouverte, et reprend après 15 s d'inactivité si aucune fiche n'est ouverte et que le zoom est proche de la vue d'ensemble. Désactivée si `prefers-reduced-motion`. **Ajout** : la rotation est aussi en pause tant que l'accueil ou la lettre couvre la carte, pour ne pas dessiner un globe caché ; les animations sont plus fluides et la batterie est épargnée.
- **Vol vers un pays** : `fitBounds` sur le plus grand polygone, moitié basse de l'écran laissée libre, zoom max 5, 1,2 s. Le bouton 🌍 ramène au globe entier centré sur l'Europe et relance la rotation.
- **Filet de sécurité** :
  - Interface `MapView` avec deux implémentations : `GlobeView` et `FlatView` (le code Leaflet d'origine, déplacé tel quel).
  - Bascule automatique sur la carte plate si WebGL est absent, si MapLibre ne se charge pas ou si l'initialisation échoue (délai maximal 15 s). Leaflet n'est alors chargé qu'à ce moment-là.
  - `?carte=plate` force la carte plate et reste dans l'adresse après `#admin`, ce qui a demandé une correction.
  - `CARTE_PAR_DEFAUT = 'globe'` sous `LETTRE` : passer à `'plate'` suffit pour revenir à l'ancienne carte.
- **Performance** : les couleurs ne sont mises à jour que par `setFeatureState`, à chaque `refresh`, sans recalcul de style.
- `sw.js` passé à `nos-voyages-v4`. MapLibre est mis en cache comme les autres librairies (règle « cache d'abord » pour les ressources externes, inchangée).

**Tests** (skill webapp-testing, 390 × 844, mode démo, Chromium sans tête avec WebGL logiciel SwiftShader, script `tests/test_ordre003_iphone.py`) : **18/18**.
- Le globe s'affiche après la lettre et tourne.
- France, Italie et Japon (Asie) en rose avec leur halo, États-Unis en doré.
- Le vol depuis « Nos pays » ouvre la fiche, et fermer la fiche ne déplace pas la vue (écart inférieur à 1 px).
- Pas de rotation quand la carte est zoomée. Toucher un pays ouvre sa fiche. 🌍 ramène la vue d'ensemble et relance la rotation.
- En `#admin`, passer à « Un jour » rend la France dorée immédiatement, puis « Visité » la remet en rose.
- `?carte=plate` donne une carte Leaflet qui fonctionne.
- MapLibre en échec (simulé par des erreurs 404) : bascule automatique sur la carte plate.
- Statistiques intactes. Aucune erreur console, hors les deux 404 volontaires du test de secours.

Les tests de l'ORDRE-002 repassent aussi (14/14, sans erreur console). Captures dans `docs/captures/ordre003-*.png`.

**Non testé ici** :
- La fluidité réelle (60 i/s) et les gestes tactiles (glisser, pincer) sur un vrai iPhone : le navigateur de test rend le globe sans carte graphique et simule les touchers par des clics.
- Le chargement réel depuis jsdelivr et unpkg : ces sites sont bloqués dans l'environnement de Claude Code, et les tests utilisent des copies identiques venant de npm.
