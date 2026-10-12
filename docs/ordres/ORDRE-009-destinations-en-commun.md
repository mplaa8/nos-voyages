# ORDRE-009 — Destinations en commun (le « Tinder des voyages ») et tirage du prochain voyage

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire
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
- [ ] Migration additive rejouable, `setup.sql` et `verification-droits.sql` à jour
- [ ] Jeu à glisser, secret respecté, correspondance animée + pays doré, célébration à l'ouverture
- [ ] Liste des destinations en commun et tirage du prochain voyage
- [ ] Interrupteur `DESTINATIONS_ACTIF`, fonctionnement inchangé si la table manque, cache `v8`
- [ ] Tests passés, captures dans `docs/captures/`, état du projet à jour
- [ ] Commit et push sur `main`, résumé de 5 lignes + marche à suivre pour l'utilisateur

## Compte rendu (à remplir par Claude Code)
