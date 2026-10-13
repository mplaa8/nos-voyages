# Roadmap — Carte de nos voyages ❤️

*Établie le 9 octobre 2026 · Anniversaire : **mercredi 14 octobre 2026***

## Principe
Il reste 5 jours. Le jour J, ce qui compte est **le contenu** (nos pays, nos photos, nos souvenirs) et **une app qui marche parfaitement**, pas le nombre de fonctionnalités. Avant le 14, on n'ajoute que des petites touches sans risque, à forte valeur émotionnelle. Tout le reste vient après, l'app étant faite pour vivre au fil des années.

## Phase 1 — Le jour J

| Date | Qui | Quoi |
|---|---|---|
| Ven 9 → Dim 11 oct | Claude Code | ✅ ORDRE-001 (mise en ligne), ✅ 002 (lettre, stats, carte cadeau), ✅ 003 (globe), ✅ 004 (outre-mer, apostrophes), ✅ 005 (petits pays, recherche) — testé sur iPhone le 11 |
| Sam 10 → Lun 12 | Moi | **Remplir la carte** : pays visités, villes, photos, souvenirs, pays rêvés. C'est le cœur du cadeau. |
| Dim 11 oct | Moi | ✅ **Globe validé** sur iPhone |
| Dim 11 → Lun 12 oct | Claude Code + moi | ✅ code (dim. soir) · **ORDRE-006 — Palmarès** : 🌅 vue, 🍽️ assiette, 😂 drôle, 💗 préféré de chacun, animation « même moment » ; mêmes droits pour Max et Roxane, code secret pour Roxane. Moi : créer le compte de Roxane, lancer la migration SQL, faire mes choix |
| Lun 12 oct (00 h 30) | Moi | ✅ Tests Supabase réussis (migration, vérification des droits, code secret) |
| Lun 12 oct | Claude Code + moi | ✅ ORDRE-007 partie A (audit, 152 tests, tag `v1.0-anniversaire`) · ✅ palmarès testé en vrai |
| Lun 12 → Mar 13 oct | Claude Code + moi | ✅ **ORDRE-009 — Destinations en commun** (avancé avant le 14 à ma demande) : « Tinder des voyages » + tirage du prochain voyage. Migration 003 ✅, vérification des droits 6/6 ✅, secret vérifié ✅, tag `v1.1-anniversaire` ✅ |
| Mar 13 oct (avant 19 h) | Claude Code + moi | **ORDRE-009B — Photos dans le jeu des envies** (bannières Wikivoyage + photos Wikipédia, repli silhouette, interrupteur `PHOTOS_ENVIES`). Moi : vérifier 10–15 cartes, tag `v1.2-anniversaire` |
| Mar 13 oct (19 h 30) | Moi | **Décision : photos du jeu des envies désactivées pour le jour J** (`PHOTOS_ENVIES = false`, silhouettes seules). Les 699 lieux choisis (`lieux-envies.json`) et la page de revue sont conservés pour la phase 2 |
| Mar 13 oct (soir) | — | **Gel définitif du code** : plus aucune modification, sauf bug bloquant (repli possible sur `v1.1-anniversaire` avec le jeu, ou `v1.0-anniversaire` sans) |
| Mar 13 oct | Claude Code + moi | **ORDRE-007 — Recette finale** : test complet sur iPhone (accueil, carte, chaque fiche, photos, liste), suppression du contenu de test, vérification de la vitesse avec toutes les photos, test de l'installation sur l'écran d'accueil |
| Mer 14 oct | Moi | **Offrir** 🎁 |

### ORDRE-002 — Touches du jour J (validé et émis)
1. **Lettre d'ouverture** : après « Ouvrir mon cadeau », une courte lettre personnelle s'affiche avant la carte (texte écrit par moi), avec un bouton « Découvrir notre carte ».
2. **Statistiques douces** (« X pays · Y continents ») dans la liste « Nos pays » : nombre de pays et de continents découverts ensemble.
3. Corrections éventuelles remontées par le test en ligne.

### ORDRE-003 — Globe 3D (validé et émis)
Globe MapLibre qui tourne lentement, zoom jusqu'aux pays, mêmes fiches et données. Carte plate conservée en secours.

### La carte cadeau (incluse dans l'ORDRE-002)
Une carte à imprimer (ou à glisser dans une enveloppe) avec un QR code menant à l'app et un petit mot, pour l'effet « cadeau à ouvrir ».

## Phase 2 — Après l'anniversaire (validée le 12 octobre 2026)
Rythme conseillé : un ordre à la fois, testé sur iPhone avant de passer au suivant. Chaque ordre garde la règle « 100 % gratuit » et un interrupteur pour désactiver la nouveauté.

| Ordre | Contenu | Pourquoi à ce rang |
|---|---|---|
| **ORDRE-008 — Fondations** | Sauvegarde automatique hebdomadaire (données + photos) dans un dépôt GitHub privé ; anti-mise en veille de Supabase ; procédure de restauration | Deux téléphones ajoutent des photos : rien n'est plus grave que de perdre des souvenirs |
| ~~ORDRE-009 — Destinations en commun~~ | **Avancé avant le 14 octobre** (voir phase 1) | — |
| **ORDRE-010 — Nos voyages** | La notion de Voyage (titre, dates, pays, villes), migration douce du contenu existant, frise « Notre histoire », mode « voyage en cours » (ajout rapide pendant le voyage) | Pierre angulaire : débloque dates, frise, récap annuel, Oscars |
| **ORDRE-011 — Jeux et attentions** | « Devine où c'était » (5 photos, points, revanche) + mots doux cachés sur les photos | Fait vivre l'app entre deux voyages |
| **ORDRE-012 — Les Oscars** | Catégories du palmarès à la carte (« Plus belle chambre », « Meilleur cocktail », « Plus grosse galère »…) + cérémonie annuelle des Oscars (vote parmi les gagnants de tous les pays, révélation animée) | À livrer avant le **14 octobre 2027** pour la première cérémonie |

**À reprendre en priorité après le 14** : photos du jeu des envies — comprendre pourquoi la page `revue-photos.html` n'affiche rien sur iPhone, puis validation humaine photo par photo avant de réactiver.

**En réserve** (banque d'idées) : photos enrichies (légende, couverture), villes sur la carte, compte à rebours, hors ligne, « Je pense à toi », notre accord parfait, messages vocaux, livre photo.

## Points de vigilance
- Supabase gratuit met en pause un projet inactif ~1 semaine : l'ouvrir de temps en temps (ou réactiver en un clic) — résolu automatiquement par l'ORDRE-008.
- Chaque modification du code doit incrémenter la version du cache dans `sw.js`.
- Ne jamais partager publiquement l'adresse de l'app.
