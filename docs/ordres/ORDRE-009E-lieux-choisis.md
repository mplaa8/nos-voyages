# ORDRE-009E — Jeu des envies : photos des lieux emblématiques choisis pour chaque pays

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire (à lancer seulement sur décision de Maxime)
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
- [ ] Photos des lieux choisis, légendes, filtres, repli silhouette
- [ ] `revue-photos.html` opérationnelle
- [ ] Clé `v4`, cache `v12`, tests passés, état du projet à jour
- [ ] Push sur `main` avant 20 h, résumé de 5 lignes + lien de la page de revue

## Compte rendu (à remplir par Claude Code)
