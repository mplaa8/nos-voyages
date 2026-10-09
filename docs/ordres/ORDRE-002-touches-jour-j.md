# ORDRE-002 — Touches du jour J : lettre d'ouverture, statistiques, carte cadeau

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : fait
**Échéance** : samedi 10 octobre 2026 (gel du code le lundi 12 au soir, anniversaire le mercredi 14)

## Objectif
Ajouter trois touches à forte valeur émotionnelle, **sans aucun risque pour ce qui fonctionne déjà**. Pas de changement du schéma Supabase. Pas de refonte : on ajoute, on ne réécrit pas.

Avant tout ajout visuel, applique le skill **frontend-design** : les ajouts doivent prolonger le style existant (ciel de nuit, Fraunces italique pour l'émotion, Karla pour l'interface, papier `--paper` pour les cartes, rose `--glow`).

## 1. Lettre d'ouverture
**Parcours voulu** : écran d'accueil → « Ouvrir mon cadeau » → le cœur s'agrandit et disparaît (animation existante) → **la lettre apparaît en fondu** sur le même ciel étoilé → bouton « Découvrir notre carte » → la carte s'affiche.

- Texte exact (ponctuation comprise) :
  > Mon amour, en ce jour si spécial, je souhaite t'offrir un cadeau que nous utiliserons jusqu'à notre dernier voyage. Peu importe où nous irons, je sais que je me sentirai à ma place, car je serai à tes côtés.

  Signature, alignée à droite : **Max**
- Stocke le texte et la signature dans une constante `LETTRE = { texte, signature }` juste sous `CONFIG`, commentée en français, pour qu'on puisse les modifier facilement.
- Présentation : une carte papier (`--paper`, encre `--ink`), texte en Fraunces italique, grand et lisible sur iPhone (≈ 21–24 px), interligne généreux, largeur max ≈ 34 caractères par ligne. Apparition douce (fondu + léger mouvement vers le haut), respect de `prefers-reduced-motion`.
- Bouton « Découvrir notre carte » : même style que « Ouvrir mon cadeau », ≥ 44 px de haut, respect de la safe-area.
- Si l'adresse se termine par `#admin`, ni accueil ni lettre (comportement actuel conservé).
- **Relire la lettre** : en bas de la liste « Nos pays » (☰), un lien discret « 💌 Relire ta lettre » qui rouvre la lettre ; le bouton ramène alors à la carte.

## 2. Statistiques douces
- En haut de la liste « Nos pays », sous le titre : **« X pays · Y continents découverts ensemble »** (accords au singulier si 1 : « 1 pays · 1 continent découvert ensemble »).
- Ne compter que les pays au statut `visited` (pas les rêves).
- Continent : propriété `CONTINENT` de Natural Earth, mémorisée par pays au chargement de la carte, traduite en français (Europe, Asie, Afrique, Amérique du Nord, Amérique du Sud, Océanie). Ignorer `Antarctica` et `Seven seas (open ocean)`.
- Si aucun pays visité : ne rien afficher (le message vide existant suffit).

## 3. Carte cadeau à imprimer
Un nouveau fichier **`carte-cadeau.html`** à la racine (non lié depuis l'app, non mis en cache par `sw.js`), à ouvrir sur le Mac et imprimer.

- Format : carte A6 paysage (148 × 105 mm), deux exemplaires par feuille A4 avec traits de coupe discrets, via `@page` et CSS d'impression. À l'écran, afficher un aperçu centré et un bouton « Imprimer » (masqué à l'impression).
- Recto unique, style de l'app : fond nuit `#161b33`, petites étoiles, cœur rose, titre « Joyeux anniversaire mon amour » en Fraunces italique, ligne « Scanne-moi pour ouvrir ton cadeau 🎁 », et le **QR code** vers `https://mplaa8.github.io/nos-voyages/` (sans `#admin`).
- Le QR code doit être **intégré dans le fichier** (SVG en ligne, généré une fois par toi), pas chargé depuis un service externe. Niveau de correction M ou plus, marge blanche suffisante, sur fond blanc arrondi pour être lisible par l'appareil photo de l'iPhone. Vérifie le QR en le décodant (par ex. avec une bibliothèque de lecture de QR) : il doit redonner exactement l'URL.
- Prévoir que l'impression du fond foncé soit activée (`print-color-adjust: exact`) et le signaler à l'utilisateur (option « Imprimer les arrière-plans » de Safari/Chrome).

## 4. Version
- Passer `CACHE` de `nos-voyages-v2` à `nos-voyages-v3` dans `sw.js`.

## Tests (skill webapp-testing, viewport iPhone 390 × 844, mode démo)
1. Accueil → « Ouvrir mon cadeau » → la lettre s'affiche, texte complet visible sans défilement ou avec un défilement naturel → « Découvrir notre carte » → carte. Capture de chaque écran.
2. Mode démo : marquer 3 pays visités sur 2 continents + 1 pays rêvé → la liste affiche « 3 pays · 2 continents découverts ensemble ». Capture.
3. « 💌 Relire ta lettre » rouvre la lettre et revient à la carte.
4. `#admin` : pas d'accueil ni de lettre.
5. `carte-cadeau.html` : capture de l'aperçu, et QR décodé = URL attendue.
6. Aucune erreur dans la console sur l'ensemble.

## Critères de fin
- [x] Les 3 touches fonctionnent, rien de l'existant n'est cassé
- [x] Tests ci-dessus passés, captures jointes au compte rendu (ou décrites)
- [x] `sw.js` en `v3`
- [x] `docs/00-etat-du-projet.md` mis à jour
- [x] Commit et push sur `main`
- [x] Résumé de 5 lignes pour l'architecte, avec la marche à suivre pour imprimer la carte

## Compte rendu (à remplir par Claude Code)

**Fait — 9 octobre 2026**

1. **Lettre d'ouverture** : nouvelle section `#letter` sur le même ciel étoilé. Le cœur éclate, puis la lettre apparaît en fondu à 0,9 s et l'accueil est retiré. Carte papier `--paper` avec une pastille rose en guise de cachet, texte en Fraunces italique (≈ 22 px sur iPhone, interligne 1,62, 34 caractères maximum par ligne), signature « Max » à droite en rose. Bouton « Découvrir notre carte » au même style que « Ouvrir mon cadeau » (54 px de haut). Texte et signature modifiables dans `LETTRE`, sous `CONFIG`. Sur un petit écran, la lettre défile naturellement. `prefers-reduced-motion` est respecté par la règle globale existante. Avec `#admin`, ni accueil ni lettre. « 💌 Relire ta lettre » est ajouté en bas de la liste « Nos pays ».
2. **Statistiques** : « X pays · Y continents découverts ensemble » sous le titre de la liste. Seuls les pays `visited` sont comptés. Le continent vient de `CONTINENT` (Natural Earth), mémorisé par pays et traduit ; Antarctique et océans sont ignorés. Le mot « découvert » s'accorde avec le nombre de continents (« 1 pays · 1 continent découvert ensemble »). Rien n'est affiché si aucun pays n'est visité.
3. **`carte-cadeau.html`** : 2 cartes A6 paysage sur une feuille A4 avec traits de coupe, aperçu à l'écran et bouton « Imprimer ». QR code en SVG intégré, correction **Q**, avec marge blanche de 4 modules sur une tuile blanche arrondie, vers `https://mplaa8.github.io/nos-voyages/`. `print-color-adjust: exact` est activé. Le fichier est exclu explicitement du cache dans `sw.js`, qui sinon met en cache toutes les pages du site.
4. `sw.js` passé à `nos-voyages-v3`.

**Tests** (skill webapp-testing, 390 × 844, mode démo, script `tests/test_ordre002_iphone.py`) : les 14 vérifications passent.
- Parcours accueil → lettre → carte : texte exact, lettre entière visible sans défilement.
- Statistiques « 3 pays · 2 continents découverts ensemble » (France, Italie, Japon visités ; États-Unis rêvé), cas singulier, cas vide.
- « Relire ta lettre » aller-retour, et `#admin` sans accueil ni lettre.
- QR décodé par OpenCV = `https://mplaa8.github.io/nos-voyages/`.
- Aucune erreur dans la console.

Captures dans `docs/captures/ordre002-*.png`.

**Écarts et remarques**
- Les pays de test ont été préchargés dans le stockage de démo au lieu d'être cliqués sur la carte : cliquer un pays précis sur la carte (dessinée en canvas) n'est pas fiable en automatique.
- cdnjs et jsdelivr sont bloqués dans l'environnement de Claude Code : les tests utilisent des copies identiques (Leaflet 1.9.4, supabase-js 2, Natural Earth v5.1.2) récupérées sur npm et GitHub. L'app elle-même n'a pas changé.
- La lettre garde les apostrophes droites du texte fourni (« t'offrir »). Des apostrophes typographiques (’) seraient plus élégantes : à valider par l'architecte.
