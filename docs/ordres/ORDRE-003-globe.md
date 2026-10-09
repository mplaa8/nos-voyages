# ORDRE-003 — Remplacer la carte plate par un globe 3D

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire
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
- [ ] Globe fonctionnel avec rotation automatique, zoom, sélection, vol vers un pays
- [ ] Bascules automatique et manuelle vers la carte plate vérifiées
- [ ] Rien de l'existant n'est cassé (fiches, lettre, stats, mode édition)
- [ ] Cache `sw.js` incrémenté
- [ ] Captures dans `docs/captures/`, `docs/00-etat-du-projet.md` mis à jour
- [ ] Commit et push sur `main`
- [ ] Résumé de 5 lignes pour l'architecte, avec **les 3 choses à tester par l'utilisateur sur son iPhone** pour la décision de dimanche

## Compte rendu (à remplir par Claude Code)
