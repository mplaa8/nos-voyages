# ORDRE-009B — Des photos de présentation dans le jeu des envies

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : fait (validation sur iPhone et tag `v1.2-anniversaire` par l'utilisateur)
**Échéance stricte** : mardi 13 octobre 2026, **avant 19 h** (gel définitif du code ce soir, anniversaire demain)
**Prérequis côté utilisateur** : aucun (pas de migration, pas de Supabase)

## Objectif
Sur chaque carte du jeu « Nos envies de voyage », afficher **2 à 3 belles photos du pays** (comme les photos d'un profil), pour donner envie. On passe d'une photo à l'autre en **touchant la carte à gauche / à droite** (petites barres de progression en haut de la carte) ; **glisser** reste réservé à ❤️ / ✖️.

## Règles de sécurité (non négociables, vu la date)
- **Uniquement dans le jeu des envies.** Rien d'autre ne change.
- **Interrupteur** `PHOTOS_ENVIES = true` sous `DESTINATIONS_ACTIF` : `false` = cartes actuelles (silhouette), sans aucune requête externe.
- **Repli permanent** : tant qu'une photo n'est pas chargée, ou si le service ne répond pas, la carte affiche la silhouette actuelle. Jamais de carte vide, jamais d'erreur visible, jamais de blocage du geste.
- Aucune clé d'API, aucun service payant, aucune donnée envoyée (seulement des lectures publiques).

## Source des photos (décidée par l'architecte) : Wikimedia, gratuit et sans clé
1. **Photo principale = la bannière Wikivoyage du pays** : propriété Wikidata **P948** (« bannière de page »). Ce sont des photos panoramiques choisies à la main par les contributeurs de Wikivoyage, de très bonne qualité, disponibles pour presque tous les pays.
   - L'identifiant Wikidata du pays vient du champ `WIKIDATAID` du fichier Natural Earth déjà chargé. Pour les territoires séparés par l'ORDRE-004 (`GUF`, `GLP`, `MTQ`, `REU`, `MYT`, `BES`, `SJM`), ajoute une petite table de correspondance vers leurs identifiants Wikidata.
   - Requête : API Wikidata `wbgetentities` (avec `origin=*` pour le CORS), uniquement `claims`.
2. **Photos complémentaires (jusqu'à 2)** : images de l'article Wikipédia en français du pays (lien `frwiki` de Wikidata, puis l'API REST `page/media-list`). Filtrer strictement :
   - garder seulement les **JPG** (exclure SVG, PNG, GIF) ;
   - exclure les noms de fichiers contenant (sans tenir compte de la casse ni des accents) : flag, drapeau, map, carte, locator, location, orthographic, coat, blason, armoiries, emblem, emblème, logo, seal, sceau, graph, chart, diagram, population, portrait, president, président, signature ;
   - prendre les 2 premières restantes.
   Si le filtrage ne laisse rien, la carte n'a que la bannière ; s'il n'y a pas de bannière, les complémentaires suffisent ; s'il n'y a rien, la silhouette.
3. **Taille** : vignettes Wikimedia en **800 px de large** (`Special:FilePath/…?width=800` ou l'URL de vignette de l'API), soit environ 80 à 150 Ko par photo.
4. **Crédits** : une ligne discrète en bas de la photo, « Photo : {auteur} · Wikimedia Commons » (auteur via l'API Commons `imageinfo` / `extmetadata`, texte brut sans HTML, tronqué proprement) ; à défaut « Photo : Wikimedia Commons ».

## Performance (pour que ce ne soit pas lourd)
- Ne charger les photos que de la **carte affichée** et **précharger la suivante** uniquement (jamais tout le paquet).
- Mémoriser en mémoire les résultats des requêtes Wikidata/Wikipédia pendant la session ; et en `localStorage` (try/catch, petite taille) la liste des fichiers par pays, pour ne pas refaire les requêtes à la prochaine partie.
- `sw.js` : **ne pas** mettre en cache du service worker les requêtes vers `wikidata.org`, `wikipedia.org`, `wikimedia.org` (le cache du navigateur suffit ; évite qu'il grossisse sans limite). Passer `CACHE` à la version suivante (`nos-voyages-v9`).
- Délai maximal : si les photos d'une carte ne sont pas là après ≈ 4 s, rester sur la silhouette pour cette carte.

## Présentation (skill frontend-design)
- La photo occupe le haut de la carte (≈ 60 %, recadrage `object-fit: cover`, les bannières étant très larges), avec un léger dégradé vers le papier pour que le drapeau et le nom restent lisibles en dessous. La silhouette rose peut rester en petit à côté du nom.
- Barres de progression fines en haut (comme des stories) quand il y a plusieurs photos ; toucher à gauche = précédente, à droite = suivante.
- Apparition douce de la photo (fondu), respect de `prefers-reduced-motion`.
- Le tampon « ❤️ J'ai envie » / « ✖️ Bof » et l'inclinaison au glissement fonctionnent par-dessus la photo comme avant.

## Tests (webapp-testing, iPhone 390 × 844, mode démo)
Ton environnement ne peut probablement pas joindre Wikimedia : **simule les réponses** (Wikidata, Wikipédia, Commons, images) avec des données enregistrées réalistes, et teste :
1. Carte avec bannière + 2 complémentaires : barres de progression, toucher gauche/droite, crédits. Capture.
2. Le filtrage écarte drapeaux, cartes, blasons, portraits, SVG et PNG (cas de test dédiés).
3. Pas de bannière / pas de complémentaires / rien du tout : bons replis, silhouette en dernier recours.
4. Service lent (> 4 s) ou en erreur : silhouette, aucun message d'erreur, le geste ❤️ / ✖️ fonctionne immédiatement.
5. Glisser ❤️ / ✖️ sur une photo, « Annuler », correspondance « Destination en commun » : inchangés.
6. Seules la carte courante et la suivante déclenchent des requêtes (compter les requêtes).
7. `PHOTOS_ENVIES = false` : aucune requête externe, cartes identiques à aujourd'hui.
8. Toute la batterie des ORDRES 002 à 009 passe toujours, aucune erreur console.

## Ce que l'utilisateur devra faire
1. Fermer complètement l'app sur son iPhone, la rouvrir, puis ☰ → « 💞 Nos envies de voyage » → **Jouer**, et **regarder 10 à 15 cartes** de continents différents (sans forcément répondre : on peut quitter avec ×).
2. Si une photo est gênante ou hors sujet, le signaler (nom du pays + capture) ; si le résultat ne plaît pas, demander « mets `PHOTOS_ENVIES` à false ».
3. Une fois validé : créer le tag de repli **`v1.2-anniversaire`** sur GitHub (comme `v1.1`).

## Critères de fin
- [x] 2 à 3 photos par carte quand elles existent, crédits affichés, repli silhouette garanti
- [x] Chargement limité à la carte courante + la suivante, rien dans le cache du service worker
- [x] Interrupteur `PHOTOS_ENVIES`, cache `v9`
- [x] Tests passés (avec réponses simulées), captures dans `docs/captures/`, état du projet à jour
- [x] Commit et push sur `main` avant 19 h, résumé de 5 lignes + ce que l'utilisateur doit vérifier

## Compte rendu (à remplir par Claude Code)

**Fait — 13 octobre 2026**

**Source et requêtes** (lectures publiques, sans clé, `origin=*`). Pour chaque carte :
1. Wikidata `wbgetclaims` sur **P948** (bannière Wikivoyage ; rang « preferred » d'abord, « deprecated » ignoré) et `wbgetentities` réduit au lien `frwiki`, en parallèle. **Écart justifié** : l'ordre prévoyait `wbgetentities` avec `claims`, mais cela renvoie toute la fiche du pays, plusieurs centaines de Ko sur mobile ; ces deux requêtes ne pèsent que quelques Ko.
2. Wikipédia `page/media-list`. Filtre : JPG seulement, et exclusion (sans accents ni casse) de flag, drapeau, map, carte, locator, location, orthographic, coat, blason, armoiries, emblem, logo, seal, sceau, graph, chart, diagram, population, portrait, président, signature. Les 2 premières photos restantes sont gardées.
3. Une seule requête Commons `imageinfo` pour 3 fichiers au plus. Elle donne l'adresse de la vignette, la taille, l'auteur, et confirme que le fichier est bien sur Commons (un fichier local à Wikipédia est écarté).

L'identifiant Wikidata vient de `WIKIDATAID` (Natural Earth). Les territoires séparés ont leur propre correspondance : GUF Q3769, GLP Q17012, MTQ Q17054, REU Q17070, MYT Q17063, BES Q27561, SJM → Q25231 (Svalbard).

**Taille des images.** Photos en **960 px** de large : une taille standard des vignettes Wikimedia, au lieu de 800, et à peine plus lourde. **Bannières en 1920 px** (ou l'original s'il est plus petit) : ce sont des panoramas d'environ 7:1. En 800 px, une bannière ne fait qu'environ 115 px de haut, et recadrée sur 60 % de la carte elle serait agrandie environ 6 fois sur un écran Retina, donc floue.

**Crédits** : « Photo : {auteur} · Wikimedia Commons », ou « Photo : Wikimedia Commons » sans auteur. Le texte de l'auteur, modifiable par n'importe qui sur Commons, est converti en texte brut par un `DOMParser` inerte : aucun code n'est exécuté, c'est testé avec un `onerror` piégé. Il est tronqué à 40 caractères.

**Repli et performance.**
- Une carte s'affiche d'abord avec sa silhouette. Elle ne passe en photos que si la **1re photo est déjà chargée** dans les 4 s ; sinon elle reste sur la silhouette, sans aucun message.
- Une image introuvable est sautée, et retirée si elle échoue plus tard. S'il ne reste aucune image, retour à la silhouette.
- Seules la carte affichée et la suivante sont chargées ; la suivante est préchargée et arrive directement avec ses photos.
- Les listes de photos par pays sont gardées en mémoire et dans `localStorage` (`nos-voyages-photos-v1`, try/catch) : pas de nouvelle requête à la partie suivante.
- `sw.js` ne met pas en cache `wikidata.org`, `wikipedia.org` ni `wikimedia.org`. Cache passé en `nos-voyages-v9`.

**Présentation.**
- Photo sur 60 % du haut de la carte, recadrée en `cover`, avec un dégradé vers le papier.
- Drapeau, nom et petite silhouette rose sur une ligne, puis le continent et le crédit.
- Barres de progression façon « stories ». Un simple toucher (déplacement de moins de 8 px) à gauche ou à droite change de photo ; un glissement de plus de 100 px reste ❤️ / ✖️.
- Fondu à l'apparition (`prefers-reduced-motion` respecté). Les tampons sont sur fond papier par-dessus la photo.

**`PHOTOS_ENVIES = false`** : cartes identiques à l'ORDRE-009, et aucune requête externe (vérifié).

**Tests** (webapp-testing, 390 × 844, Wikimedia **simulé**, inaccessible depuis l'environnement de Claude Code) : `tests/test_ordre009b_photos.py` **26/26**. Points couverts :
- bannière « preferred » en 1920 px et 2 photos en 960 px, barres, crédits ;
- toucher à droite puis à gauche, nettoyage du crédit ;
- filtrage (SVG, PNG, GIF, drapeau, carte, blason, portrait, emblème, localisateur écartés) ;
- 2 pays interrogés à l'ouverture, puis 1 de plus par réponse ; aucune requête avant d'ouvrir le jeu, ni au retour sur des pays déjà vus ;
- glisser, « Annuler » et « Destination en commun » sur une carte avec photos ;
- replis : pas de bannière, pas de photos complémentaires, rien du tout, service lent (le geste reste immédiat, silhouette au-delà de 4 s), service en erreur, bannière introuvable (la carte passe aux 2 autres photos) ;
- photos désactivées.

Non-régression : ORDRE-002 14/14, 003 18/18, 004 18/18, 005 41/41, 006 47/47 et 15/15, 009 36/36. **Total 215/215.** Seules erreurs console : les 404, 400 et 500 volontaires des tests de secours, de mauvais code et de service en erreur. Captures : `docs/captures/ordre009b-*.png`.

**Non testé ici** : le vrai Wikimedia (formats d'API respectés d'après leur documentation publique, mais non confrontés au service réel). C'est la vérification sur iPhone qui fera foi.
