# ORDRE-009 — Destinations en commun (le « Tinder des voyages ») et tirage du prochain voyage

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : fait (côté code ; il reste les étapes Supabase de l'utilisateur)
**Échéance stricte** : lundi 12 octobre 2026 au soir (l'anniversaire est le **mercredi 14**, deadline absolue)
**Prérequis côté utilisateur** : exécuter `migration-003-destinations.sql` dans Supabase (expliqué à la fin)

## Règles de sécurité de cet ordre (non négociables, vu la date)
- **Purement additif** : aucune modification du comportement existant (carte, fiches, palmarès, lettre, droits). Les tables existantes ne sont pas modifiées.
- **Migration additive** : une seule nouvelle table, aucune politique existante touchée.
- **Interrupteur** `DESTINATIONS_ACTIF = true` sous `PALMARES_ACTIF` : `false` masque toute la fonctionnalité.
- Si la table n'existe pas encore (migration pas lancée), l'app fonctionne exactement comme aujourd'hui et la fonctionnalité reste cachée, sans erreur.
- Filet de secours : le tag `v1.0-anniversaire` reste la version de repli.

## Objectif
Chacun, de son côté et **en secret**, passe en revue les pays que vous n'avez pas encore visités et répond :
- ❤️ **« J'ai envie »** (glisser à droite)
- ✖️ **« Bof »** (glisser à gauche)

Quand Roxane et Maxime répondent ❤️ **tous les deux** pour le même pays : animation **« Destination en commun 💞 »**, et le pays passe en **« Un jour… »** (doré) sur le globe.
Ensuite, parmi vos destinations en commun : **🎲 Tirer notre prochain voyage**, le globe tourne et s'arrête sur l'une d'elles.

Maxime fera ses réponses avant le 14 : le jour J, Roxane découvrira les correspondances au fil de ses réponses (même principe que le 💗).

## 1. Données — `migration-003-destinations.sql` (rejouable, additive)
- Table `wishes` :
  - `user_id uuid not null default auth.uid() references auth.users on delete cascade`
  - `country_code text not null` (code ADM0_A3 de la carte, y compris les territoires séparés comme `GUF` ; **pas** de clé étrangère vers `countries`, qui ne contient que nos pays marqués)
  - `answer text not null check (answer in ('oui','non'))`
  - `created_at timestamptz default now()`
  - clé primaire `(user_id, country_code)` (changer d'avis = remplacer)
- RLS : lecture publique (comme `picks`, le secret est géré dans l'interface) ; insertion, modification et suppression seulement si `user_id = auth.uid()` et `is_member()`.
- Ajout à la publication `supabase_realtime` (protégé pour être rejouable).
- Mettre aussi à jour `setup.sql` et `verification-droits.sql` (une ligne : un visiteur ne peut pas écrire dans `wishes`, un membre peut).

## 2. Le jeu « Nos envies de voyage »
**Point d'entrée** : dans la liste ☰, sous les statistiques, une carte « 💞 Nos envies de voyage » avec le nombre de destinations en commun et un bouton **« Jouer »**. Un visiteur non connecté qui touche « Jouer » voit la fenêtre du code secret existante (même parcours que « ➕ Ajouter nos souvenirs »).

**L'écran de jeu** (plein écran, ciel de nuit, skill frontend-design, dans l'esprit des fiches papier) :
- Une **carte à glisser** par pays : grand drapeau, nom en Fraunces, continent, et la **silhouette du pays** dessinée en rose à partir de la géométrie déjà chargée (SVG, pas de service externe ni d'image en ligne).
- Glisser à droite = ❤️, à gauche = ✖️, avec inclinaison de la carte et tampon « ❤️ J'ai envie » / « ✖️ Bof » qui apparaît pendant le geste. Deux gros boutons ✖️ et ❤️ en bas (≥ 56 px) pour qui ne glisse pas, plus « ↩︎ Annuler » (dernière réponse).
- **Paquet** : tous les pays et territoires **non visités** (y compris ceux déjà en « Un jour »), dans un ordre aléatoire stable par personne, sans ceux auxquels la personne a déjà répondu. Petits filtres par continent en haut (« Tous », « Europe », « Asie »…). Compteur discret « 12 / 180 ».
- On peut quitter à tout moment (×) et reprendre plus tard là où on en était.
- Fin du paquet : « Tu as fait le tour du monde 🌍 » + lien vers nos destinations en commun.
- **Secret** : les réponses de l'autre ne sont **jamais** affichées pendant le jeu, ni pays par pays ; seules les **correspondances ❤️ + ❤️** sont révélées. (Les ✖️ de l'autre ne sont jamais montrés, même après.)

## 3. La correspondance « Destination en commun 💞 »
- Déclenchée quand une réponse ❤️ crée une correspondance (l'autre avait déjà dit ❤️) : réutiliser l'animation « même moment » (pluie de cœurs, cadre papier) avec la silhouette + drapeau du pays et le texte « Destination en commun 💞 — {pays} ».
- À ce moment, si le pays n'est pas déjà « visité » ni « Un jour », le passer en **« Un jour… »** (statut `dream`) avec la fonction existante. Ne jamais rétrograder un pays visité.
- **Comme pour le 💗** : à l'ouverture de l'app, chaque correspondance créée par l'autre et pas encore vue sur cet appareil est célébrée une fois (mémoire `localStorage`, try/catch), jamais par-dessus l'accueil ou la lettre ; temps réel si l'app est ouverte.
- Plusieurs correspondances à célébrer d'un coup : les enchaîner (bouton « Suivante 💞 »), maximum 5 puis « … et N autres ! ».

## 4. Nos destinations en commun et le tirage
- Dans la carte « 💞 Nos envies de voyage » de ☰ : liste des destinations en commun (drapeau + nom), toucher = vol vers le pays et ouverture de sa fiche.
- Bouton **« 🎲 Tirer notre prochain voyage »** (visible dès 2 destinations en commun) : fermeture de la liste, le globe tourne vite puis ralentit (≈ 4 s) et s'arrête sur une destination tirée au hasard, qui s'illumine ; puis une carte « Et si c'était… {pays} ? ✈️ » avec « Ouvrir la fiche » et « Retirer au sort ». Respect de `prefers-reduced-motion` (vol direct). Sur la carte plate : vol direct vers le pays avec la même carte.

## 5. Version
`sw.js` : `CACHE` → version suivante (`nos-voyages-v8`).

## Tests (webapp-testing, iPhone 390 × 844, mode démo avec le sélecteur Maxime / Roxane)
1. En Maxime : 5 réponses (3 ❤️, 2 ✖️) par glissement et par boutons ; « Annuler » ; quitter et reprendre au même endroit. Captures.
2. En Roxane : les réponses de Maxime ne sont jamais visibles ; elle dit ❤️ à un pays où Maxime a dit ❤️ → animation « Destination en commun », le pays devient doré. Capture.
3. Elle dit ❤️ à un pays où Maxime a dit ✖️ → rien ne se passe, rien n'est révélé.
4. Correspondance créée par Maxime après Roxane → célébrée une seule fois à la réouverture en Roxane.
5. Pays déjà visité : absent du paquet ; pays « Un jour » : présent ; une correspondance ne rétrograde jamais un pays visité.
6. Filtres par continent, compteur, fin de paquet.
7. Tirage : avec 3 destinations en commun, le globe s'arrête sur l'une d'elles ; « Retirer au sort » ; version carte plate. Capture.
8. Visiteur non connecté : « Jouer » ouvre la fenêtre du code secret.
9. Table absente (simuler l'erreur) : aucune trace de la fonctionnalité, aucune erreur visible. `DESTINATIONS_ACTIF = false` : idem.
10. Toute la batterie des ORDRES 002 à 007 passe toujours, aucune erreur console.

## Ce que l'utilisateur devra faire (à lui expliquer pas à pas, en français simple)
1. Supabase → SQL Editor → New query → coller `migration-003-destinations.sql` → **Run** → « Success ».
2. Relancer `verification-droits.sql` : toutes les lignes en ✅.
3. Sur son iPhone (en étant connecté) : ☰ → « 💞 Nos envies de voyage » → **Jouer**, faire **ses** réponses.
4. En navigation privée, avec le code secret de Roxane : vérifier qu'aucune réponse de Maxime n'est visible, puis se déconnecter. **Ne pas répondre à la place de Roxane** (ses réponses compteraient).
5. Créer le tag de repli **`v1.1-anniversaire`** sur GitHub (Releases → nouvelle release, comme pour `v1.0`) une fois tout validé.

## Critères de fin
- [x] Migration additive rejouable, `setup.sql` et `verification-droits.sql` à jour
- [x] Jeu à glisser, secret respecté, correspondance animée + pays doré, célébration à l'ouverture
- [x] Liste des destinations en commun et tirage du prochain voyage
- [x] Interrupteur `DESTINATIONS_ACTIF`, fonctionnement inchangé si la table manque, cache `v8`
- [x] Tests passés, captures dans `docs/captures/`, état du projet à jour
- [x] Commit et push sur `main`, résumé de 5 lignes + marche à suivre pour l'utilisateur

## Compte rendu (à remplir par Claude Code)

**Fait — 12 octobre 2026**

**1. Données.**
- `migration-003-destinations.sql` : rejouable et **purement additive**. Elle ajoute une table `wishes`, une clé primaire `(user_id, country_code)`, des réponses `oui`/`non`, aucune clé étrangère, la lecture publique, l'écriture pour ses propres réponses si `is_member()`, et le temps réel. Elle refuse de s'appliquer si la migration 002 manque (message clair, rien de créé).
- `setup.sql` et `verification-droits.sql` sont à jour : 6 lignes, dont « Visiteur : répondre au jeu des envies » et « Maxime et Roxane : jeu des envies ». Tant que la migration n'est pas lancée, ces lignes affichent un ⚠️ « table absente ».
- **Testé sur un vrai PostgreSQL 16 imitant Supabase** (`tests/test_ordre009_sql.py`) : **20/20**. Points couverts :
  - base « jour J » (`setup.sql` du tag `v1.0-anniversaire`), puis migration 003 lancée deux fois : Success ;
  - **aucune règle existante modifiée**, comparaison faite avant et après ;
  - visiteur et compte non membre refusés ; chacun répond, change d'avis et annule pour lui-même seulement ;
  - Guyane acceptée (pas de clé étrangère) ;
  - installation neuve ; script de vérification avant et après.

**2. Le jeu.**
- Entrée : dans ☰, sous les statistiques, une carte « 💞 Nos envies de voyage » (nombre de destinations en commun, bouton **Jouer**). Un visiteur voit la fenêtre du code secret, puis le jeu s'ouvre.
- Écran plein, ciel de nuit. Chaque carte papier montre le drapeau, la **silhouette du pays en rose**, dessinée en SVG à partir de la géométrie déjà chargée (points simplifiés), le nom en Fraunces, le continent, et « ✨ Un jour… » si c'est déjà un rêve.
- Glisser à droite ou à gauche, avec inclinaison et tampons « ❤️ J'ai envie » / « ✖️ Bof ». Boutons ✖️ et ❤️ de 66 px, « ↩︎ Annuler », flèches du clavier.
- **Paquet** : tous les pays et territoires non visités, rêves compris, dans un ordre aléatoire **stable par personne** (hachage identifiant + code), sans ceux déjà répondus.
  - Écartés : l'Antarctique, le glacier de Siachen, les îles Heard (inhabitées), l'île Ashmore et Chagos (base militaire fermée).
  - Les îles « en pleine mer » de Natural Earth (Maldives, Seychelles, Maurice…) prennent le continent de leur région pour les filtres.
  - Filtres par continent, compteur « réponses / total ».
- On quitte avec × (retour à la liste ☰) et on reprend là où on en était.
- Fin du paquet : « Tu as fait le tour du monde 🌍 » (ou « Plus aucun pays à découvrir ici » avec un filtre), puis un lien vers nos destinations en commun.
- **Secret** : les réponses de l'autre ne sont jamais affichées. Seules les ❤️ + ❤️ apparaissent, et les ✖️ jamais.

**3. Correspondances.**
- L'animation « même moment » est réutilisée, avec la silhouette, le drapeau et « Destination en commun 💞 » + le pays.
- Le pays passe en « Un jour… » seulement s'il était « à découvrir » : jamais de rétrogradation d'un pays visité, et c'est testé.
- Célébration **à l'ouverture**, une fois par personne et par appareil (`localStorage`), jamais par-dessus l'accueil ou la lettre, et en temps réel quand l'app est ouverte.
- Plusieurs d'un coup : le bouton devient « Suivante 💞 », 5 au maximum, puis « … et N autres destinations en commun ! ».
- **Choix** : « Annuler » retire la réponse, mais ne repasse pas le pays de « Un jour » à « à découvrir » s'il l'était devenu (statut léger, modifiable dans la fiche).
- La vibration n'est tentée qu'après un premier toucher : Chrome la bloquait à l'ouverture et l'inscrivait en erreur console ; sans effet sur iPhone de toute façon.

**4. Destinations en commun et tirage.**
- Liste en pastilles (drapeau + nom) dans la carte ☰ ; toucher l'une d'elles fait voler la carte et ouvre la fiche.
- **🎲 Tirer notre prochain voyage** (à partir de 2 destinations) : le globe fait deux tours puis ralentit (4,2 s, décélération) et s'arrête sur la destination, qui s'illumine (contour blanc).
- Carte « Et si c'était… {pays} ? ✈️ » avec « Ouvrir la fiche » et « Retirer au sort », qui tire une autre destination que la précédente.
- Vol direct avec `prefers-reduced-motion` et sur la carte plate.

**5.** `DESTINATIONS_ACTIF` sous `PALMARES_ACTIF`. Table absente, donc migration pas encore lancée : rien n'apparaît et aucun message ne s'affiche (seulement un 404 réseau dans la console du navigateur). `sw.js` passé à `nos-voyages-v8`. Rien de l'existant n'a été modifié en dehors de l'animation, rendue générique (moment, destination, « et N autres »), et de l'abonnement temps réel, étendu à `wishes`.

**Tests** (webapp-testing, 390 × 844) :
- `tests/test_ordre009_iphone.py` (démo, Maxime / Roxane) : **36/36**, tests 1 à 9. Le tirage est testé sur le globe et sur la carte plate.
- Table absente face au Supabase simulé : ajouté à `tests/test_ordre006_code_secret.py` (15/15).
- Non-régression : ORDRE-002 14/14, 003 18/18, 004 18/18, 005 41/41, 006 47/47 (démo).
- **Total 189/189.** Seules erreurs console : les 404 volontaires (secours, table absente) et le 400 d'un mauvais code.
- Captures : `docs/captures/ordre009-*.png`.

**Non testé ici** : le vrai Supabase et le glisser au vrai doigt sur iPhone (simulé à la souris : mêmes événements « pointer »).

**Reste à faire par l'utilisateur** : migration 003, vérification, ses réponses, puis le tag `v1.1-anniversaire` (voir la marche à suivre).
