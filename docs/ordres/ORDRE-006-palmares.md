# ORDRE-006 — Nos deux téléphones : contenu partagé, palmarès et « même moment »

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire
**Échéance** : lundi 12 octobre 2026, avant le gel du code du soir
**Prérequis côté utilisateur** : compte de Roxane créé dans Supabase + migration SQL exécutée (voir partie 1)
**Révision du 11/10, 20 h 50** : Roxane doit aussi pouvoir **ajouter du contenu** (elle a des photos que Maxime n'a pas). Seuls les deux téléphones, Maxime et Roxane, peuvent écrire. Les parties 1 et 2 bis ont été revues en conséquence.

## Objectif
Pour chaque pays, on peut récompenser nos photos et nos souvenirs dans 4 catégories :

| Catégorie | Emoji | Qui choisit |
|---|---|---|
| Plus belle vue | 🌅 | Roxane et Maxime, chacun son choix |
| Plus belle assiette | 🍽️ | Roxane et Maxime, chacun son choix |
| Moment le plus drôle | 😂 | Roxane et Maxime, chacun son vote |
| Moment préféré | 💗 | Roxane et Maxime, chacun le sien |

**Le cœur émotionnel : le « même moment ».** Quand Roxane et Maxime choisissent le **même moment préféré** pour un pays, une animation se déclenche (pluie de cœurs + « Vous avez choisi le même moment 💞 »). Maxime fera ses choix avant le 14 : le jour J, Roxane découvrira les correspondances en choisissant les siens.

**Règle du secret** : pour la catégorie 💗, le choix de l'autre reste caché (« 🔒 Choisis le tien pour découvrir celui de Maxime ») tant que la personne qui regarde n'a pas fait le sien pour ce pays. Elle ne peut donc pas copier : la correspondance est sincère. Les 3 autres catégories sont visibles directement.

Un « moment » est **une photo ou un souvenir écrit**.

## 1. Comptes et sécurité (le point le plus délicat)
Principe : **seuls les deux membres (Maxime et Roxane) écrivent**, chacun depuis son téléphone. Tous les autres (toute personne ayant le lien) ne font que regarder. Les deux peuvent **ajouter** du contenu. Pour éviter qu'une fausse manipulation efface les souvenirs de l'autre :

| Action | Maxime (`admin`) | Roxane (`membre`) |
|---|---|---|
| Marquer un pays « Visité » / « Un jour », modifier les villes | ✅ | ✅ |
| Ajouter des photos et des souvenirs | ✅ | ✅ |
| Modifier / supprimer **ses propres** photos et souvenirs | ✅ | ✅ |
| Modifier / supprimer les photos et souvenirs **de l'autre** | ✅ | ❌ |
| Retirer un pays de la carte (efface tout son contenu) | ✅ | ❌ |
| Faire ses choix du palmarès | ✅ | ✅ |

### Migration SQL — `migration-002-palmares.sql` (à créer, rejouable)
Dans l'ordre exact suivant (sinon Maxime perd l'accès à l'édition) :
1. Table `members (user_id uuid pk → auth.users on delete cascade, prenom text not null, role text not null check in ('admin','membre'))`, lecture publique (pour afficher les prénoms), aucune écriture depuis l'app.
2. Insertion des deux membres **par e-mail**, avec des marqueurs à remplacer par l'utilisateur dans le SQL Editor (ne jamais committer de vrais e-mails) :
   `insert into members select id, 'Maxime', 'admin' from auth.users where email = 'EMAIL-DE-MAXIME' on conflict do nothing;` (idem `'Roxane', 'membre'` avec `'EMAIL-DE-ROXANE'`).
   Le script doit **s'arrêter avec un message clair** si l'admin n'a pas été trouvé (bloc `do $$ … raise exception … $$`), pour ne jamais appliquer l'étape 3 sans admin.
3. Auteur des contenus : colonne `author_id uuid default auth.uid() references auth.users on delete set null` sur `memories` et `photos`. Les lignes existantes restent sans auteur et sont considérées comme celles de Maxime (seul l'admin peut les modifier ou supprimer).
   Fonctions `is_member()` et `is_admin()` (`security definer`, `stable`, `search_path` fixé), puis remplacement des politiques d'écriture « authenticated » selon le tableau ci-dessus :
   - `countries` : insertion et modification si `is_member()` ; suppression si `is_admin()` ;
   - `memories` et `photos` : insertion si `is_member()` (et `author_id = auth.uid()`) ; modification et suppression si `is_admin()` ou `author_id = auth.uid()` ;
   - stockage `photos` : ajout si `is_member()` ; suppression si `is_admin()` ou si l'objet appartient à l'utilisateur (colonne propriétaire de `storage.objects`).
   La lecture publique ne change pas.
4. Table `picks` :
   - `id uuid pk`, `user_id uuid not null default auth.uid() → auth.users on delete cascade`, `country_code → countries(code) on delete cascade`, `category text check in ('vue','assiette','drole','prefere')`, `photo_id → photos(id) on delete cascade` (nullable), `memory_id → memories(id) on delete cascade` (nullable), `created_at` ;
   - contrainte : exactement un des deux (`photo_id`, `memory_id`) renseigné ;
   - `unique (user_id, country_code, category)` : un seul choix par personne, par pays, par catégorie (changer d'avis = remplacer) ;
   - RLS : lecture publique ; insertion, modification, suppression seulement si `user_id = auth.uid()` **et** l'utilisateur est dans `members`.
5. Bonus temps réel : `alter publication supabase_realtime add table picks;` (protégé pour être rejouable).

Mets aussi à jour `setup.sql` pour qu'une installation neuve ait directement ce modèle, et documente la procédure dans `docs/02-guide-installation.md`.

### Connexion de Roxane : un « code secret », pas un formulaire
- Nouvelles entrées dans `CONFIG` : `ROXANE_EMAIL` (adresse **fictive et non personnelle**, par ex. `roxane@nos-voyages.fr`, aucun e-mail n'est jamais envoyé grâce à « Auto Confirm ») et `INDICE_CODE` (texte affiché, par ex. « Notre date secrète (JJMMAAAA) 💕 »).
- Points d'entrée pour un visiteur non connecté : toucher un bouton de choix du palmarès, **ou** un bouton discret « ➕ Ajouter nos souvenirs » en bas de chaque fiche pays (et en bas de la liste ☰). Une jolie fenêtre demande alors : « Pour ajouter tes photos et choisir tes moments, entre notre code secret » + l'indice + un seul champ (clavier numérique si possible, 16 px). Connexion via `signInWithPassword({ email: CONFIG.ROXANE_EMAIL, password: code })`. La session reste ensuite mémorisée sur son iPhone.
- Message d'erreur doux si le code est faux. Aucune mention du mode édition dans cette fenêtre.
- Maxime reste connecté comme aujourd'hui (5 touches sur le ❤️ ou `#admin`).

### Rôles dans l'app
- Après connexion, lire `members` pour l'utilisateur courant : `prenom` et `role`.
- **Mode édition pour les deux membres**, avec les droits du tableau : pour Roxane, les boutons « Supprimer » / « Modifier » n'apparaissent que sur **ses** photos et souvenirs, et l'option « Pas encore » (retirer un pays) est masquée. La pastille « Mode édition · Quitter » est commune ; après « Quitter », Roxane redevient visiteuse et retrouve le bouton « ➕ Ajouter nos souvenirs » (sans redemander le code tant que la session est valide, ou en le redemandant : à ton choix, justifie).
- Chaque souvenir écrit affiche discrètement son auteur (« — Roxane », « — Maxime ») ; rien pour les anciens souvenirs sans auteur.
- Les prénoms affichés viennent de `members` (pas codés en dur).
- Mode démo (sans Supabase) : simuler les deux personnes avec un sélecteur discret « Je suis : Maxime / Roxane » pour pouvoir tester.

## 2 bis. Roxane ajoute ses photos
Même parcours que Maxime (ajout multiple, compression avant envoi, messages de progression). Vérifier que l'ajout depuis la photothèque de l'iPhone fonctionne pour un membre non admin (politiques de stockage).

## 2. Choisir
- **Dans la visionneuse photo** (plein écran) : une barre en bas avec 4 boutons ronds 🌅 🍽️ 😂 💗 (≥ 44 px), visibles pour tout membre connecté (et pour le visiteur non connecté, qui déclenche la fenêtre du code). Toucher = « ce moment est mon choix pour cette catégorie dans ce pays » ; re-toucher = retirer. Un bouton actif est mis en valeur.
- **Sur chaque souvenir écrit** : un petit bouton « 🏅 » qui ouvre les 4 mêmes choix.
- Retour visuel immédiat et discret à chaque choix (petit toast : « 🌅 Ta plus belle vue au Portugal »).

## 3. Afficher : le bloc « Notre palmarès » dans la fiche pays
En haut de la fiche (sous les lieux, avant les photos), si au moins un choix existe :
- une ligne par catégorie : emoji + intitulé + vignette(s) du ou des moments choisis + qui l'a choisi (« Roxane », « Maxime », ou **« Vous deux »** si même moment) ;
- 💗 : deux colonnes « Préféré de Roxane » / « Préféré de Maxime », avec la règle du secret ; si même moment : une seule vignette avec « Votre moment préféré à tous les deux 💞 » ;
- toucher une vignette ouvre la photo (ou fait défiler jusqu'au souvenir).
- Dans la galerie, les photos récompensées portent un petit emoji en coin.
- Style : skill frontend-design, dans l'esprit papier et Fraunces des souvenirs. Pas de bloc vide si aucun choix.

## 4. L'animation « même moment »
- **Quand** :
  1. juste après un choix 💗 qui crée la correspondance (pour la personne qui vient de choisir) ;
  2. **à l'ouverture de l'app sur l'iPhone de Roxane**, pour chaque correspondance qu'elle n'a pas encore vue (Maxime ayant choisi après elle) — mémoriser les correspondances déjà célébrées dans `localStorage` (try/catch) ;
  3. bonus si simple : en temps réel via Supabase Realtime si l'app est ouverte au moment où l'autre choisit.
- **Quoi** : voile nuit, pluie de cœurs roses qui montent (CSS, ≈ 2,5 s), la photo (ou le souvenir) au centre dans un cadre papier, texte en Fraunces italique « Vous avez choisi le même moment 💞 » + nom du pays, bouton « 🥰 ». Vibration légère si disponible (`navigator.vibrate`, sans effet sur iPhone : ne pas en dépendre). Respect de `prefers-reduced-motion` (fondu simple).
- L'animation ne s'affiche jamais par-dessus l'écran d'accueil ou la lettre : attendre l'arrivée sur la carte.

## 5. Interrupteur et version
- Constante `PALMARES_ACTIF = true` sous `CARTE_PAR_DEFAUT`, commentée : `false` masque toute la fonctionnalité (retour arrière immédiat sans toucher à la base).
- `sw.js` : `CACHE` → `nos-voyages-v7`.

## Tests (webapp-testing, iPhone 390 × 844, mode démo avec le sélecteur Maxime / Roxane)
1. En Maxime : choisir 🌅 une photo, 💗 une photo, 😂 un souvenir dans un pays → bloc palmarès correct, emojis sur les vignettes.
2. En Roxane, même pays : le 💗 de Maxime est caché (🔒) ; elle choisit **une autre** photo → les deux préférés se révèlent, pas d'animation.
3. Roxane change d'avis et choisit **la même** photo que Maxime → animation, puis « Votre moment préféré à tous les deux 💞 ». Captures.
4. Correspondance créée par Maxime après Roxane → à la réouverture en Roxane, l'animation se joue une seule fois.
5. 😂 avec deux votes différents → les deux s'affichent ; même vote → « Vous deux ».
6. Visiteur non connecté (hors démo, avec un Supabase fictif ou simulé) : toucher 💗 ouvre la fenêtre du code secret ; mauvais code → message doux.
7. En Roxane : ajouter une photo et un souvenir, marquer un nouveau pays « Visité » → OK ; elle peut supprimer **sa** photo, pas celle de Maxime (bouton absent) ; l'option « Pas encore » est absente ; son souvenir affiche « — Roxane ».
8. Supprimer une photo récompensée (en admin) → son choix disparaît proprement, pas d'erreur.
8 bis. Contrôle des politiques SQL : écrire un script de vérification (à lancer par l'utilisateur dans le SQL Editor, ou décrit pas à pas) qui confirme qu'un membre non admin ne peut ni supprimer un pays ni supprimer la photo de l'autre.
9. `PALMARES_ACTIF = false` → aucune trace de la fonctionnalité.
10. Globe et carte plate ; tous les tests des ORDRES 002 à 005 passent, aucune erreur console.

## Ce que l'utilisateur devra faire (à lui expliquer pas à pas, en français simple)
1. Supabase → Authentication → Users → Add user : l'adresse fictive de Roxane + **le code secret comme mot de passe** (au moins 6 caractères), « Auto Confirm User » coché.
2. SQL Editor : coller `migration-002-palmares.sql`, remplacer `EMAIL-DE-MAXIME` et `EMAIL-DE-ROXANE`, **Run**, vérifier « Success ».
3. Sur son iPhone : vérifier qu'il peut toujours modifier un pays (sinon, la migration n'a pas trouvé son e-mail : relancer l'étape 2). Tester le code secret de Roxane **en navigation privée** (ajouter une photo de test, la supprimer, se déconnecter), jamais sur l'iPhone de Roxane avant le jour J.
4. Faire **ses** choix (surtout 💗) dans chaque pays avant le 14.

## Critères de fin
- [ ] Migration rejouable, `setup.sql` à jour, aucun vrai e-mail ni mot de passe dans le dépôt
- [ ] Deux membres qui écrivent (droits du tableau respectés) ; Roxane se connecte par code secret, ajoute ses photos et souvenirs, et choisit
- [ ] 4 catégories, palmarès dans la fiche, règle du secret, animation « même moment » (au choix et à l'ouverture)
- [ ] Interrupteur `PALMARES_ACTIF`, cache `v7`
- [ ] Tests passés, captures dans `docs/captures/`, état du projet à jour
- [ ] Commit et push sur `main`, résumé de 5 lignes + la marche à suivre de l'utilisateur

## Compte rendu (à remplir par Claude Code)
