# ORDRE-006 — Nos deux téléphones : contenu partagé, palmarès et « même moment »

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : fait (côté code ; il reste les étapes Supabase de l'utilisateur)
**Échéance** : lundi 12 octobre 2026, avant le gel du code du soir
**Prérequis côté utilisateur** : compte de Roxane créé dans Supabase + migration SQL exécutée (voir partie 1)
**Révision du 11/10, 20 h 55** : Roxane doit aussi pouvoir **ajouter du contenu** (elle a des photos que Maxime n'a pas). Seuls les deux téléphones, Maxime et Roxane, peuvent écrire, **avec exactement les mêmes droits**. Les parties 1 et 2 bis ont été revues en conséquence.

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
Principe : **seuls les deux membres (Maxime et Roxane) écrivent**, chacun depuis son téléphone, **avec exactement les mêmes droits** : marquer et retirer des pays, modifier les villes, ajouter, modifier et supprimer toutes les photos et tous les souvenirs, faire ses choix du palmarès. Tous les autres (toute personne ayant le lien) ne font que regarder. Pas de notion d'administrateur dans les droits.

### Migration SQL — `migration-002-palmares.sql` (à créer, rejouable)
Dans l'ordre exact suivant (sinon Maxime perd l'accès à l'édition) :
1. Table `members (user_id uuid pk → auth.users on delete cascade, prenom text not null)`, lecture publique (pour afficher les prénoms), aucune écriture depuis l'app.
2. Insertion des deux membres **par e-mail**, avec des marqueurs à remplacer par l'utilisateur dans le SQL Editor (ne jamais committer de vrais e-mails) :
   `insert into members select id, 'Maxime' from auth.users where email = 'EMAIL-DE-MAXIME' on conflict do nothing;` (idem `'Roxane'` avec `'EMAIL-DE-ROXANE'`).
   Le script doit **s'arrêter avec un message clair** si l'un des deux membres n'a pas été trouvé (bloc `do $$ … raise exception … $$`), pour ne jamais appliquer l'étape 3 et risquer de perdre l'accès à l'édition.
3. Auteur des contenus (pour la signature uniquement, pas pour les droits) : colonne `author_id uuid default auth.uid() references auth.users on delete set null` sur `memories` et `photos`. Les lignes existantes restent sans auteur.
   Fonction `is_member()` (`security definer`, `stable`, `search_path` fixé), puis remplacement des politiques d'écriture « authenticated » :
   - `countries`, `memories`, `photos` : insertion, modification et suppression si `is_member()` ;
   - stockage `photos` : ajout et suppression si `is_member()`.
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
- Après connexion, lire `members` pour l'utilisateur courant : `prenom`. Un compte absent de `members` reste visiteur.
- **Mode édition identique pour les deux membres** (mêmes boutons, mêmes droits). La pastille « Mode édition · Quitter » est commune ; après « Quitter », Roxane redevient visiteuse et retrouve le bouton « ➕ Ajouter nos souvenirs » (sans redemander le code tant que la session est valide, ou en le redemandant : à ton choix, justifie). Maxime garde aussi ses accès actuels (5 touches sur ❤️, `#admin`).
- Chaque souvenir écrit affiche discrètement son auteur (« — Roxane », « — Maxime ») ; rien pour les anciens souvenirs sans auteur.
- Les prénoms affichés viennent de `members` (pas codés en dur).
- Mode démo (sans Supabase) : simuler les deux personnes avec un sélecteur discret « Je suis : Maxime / Roxane » pour pouvoir tester.

## 2 bis. Roxane ajoute ses photos
Même parcours que Maxime (ajout multiple, compression avant envoi, messages de progression). Vérifier que l'ajout depuis la photothèque de l'iPhone fonctionne pour Roxane (politiques de stockage).

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
7. En Roxane : ajouter une photo et un souvenir, marquer un nouveau pays « Visité », supprimer une photo ajoutée par Maxime, retirer un pays → tout fonctionne, comme pour Maxime ; son souvenir affiche « — Roxane ».
8. Supprimer une photo récompensée → son choix disparaît proprement, pas d'erreur.
8 bis. Contrôle des politiques SQL : décrire pas à pas à l'utilisateur comment vérifier qu'un visiteur non connecté ne peut rien écrire, et que les deux membres peuvent tout faire.
9. `PALMARES_ACTIF = false` → aucune trace de la fonctionnalité.
10. Globe et carte plate ; tous les tests des ORDRES 002 à 005 passent, aucune erreur console.

## Ce que l'utilisateur devra faire (à lui expliquer pas à pas, en français simple)
1. Supabase → Authentication → Users → Add user : l'adresse fictive de Roxane + **le code secret comme mot de passe** (au moins 6 caractères), « Auto Confirm User » coché.
2. SQL Editor : coller `migration-002-palmares.sql`, remplacer `EMAIL-DE-MAXIME` et `EMAIL-DE-ROXANE`, **Run**, vérifier « Success ».
3. Sur son iPhone : vérifier qu'il peut toujours modifier un pays (sinon, la migration n'a pas trouvé son e-mail : relancer l'étape 2). Tester le code secret de Roxane **en navigation privée** (ajouter une photo de test, la supprimer, se déconnecter), jamais sur l'iPhone de Roxane avant le jour J.
4. Faire **ses** choix (surtout 💗) dans chaque pays avant le 14.

## Critères de fin
- [x] Migration rejouable, `setup.sql` à jour, aucun vrai e-mail ni mot de passe dans le dépôt
- [x] Deux membres qui écrivent avec les mêmes droits ; Roxane se connecte par code secret, ajoute ses photos et souvenirs, et choisit ; les visiteurs ne peuvent rien écrire
- [x] 4 catégories, palmarès dans la fiche, règle du secret, animation « même moment » (au choix et à l'ouverture)
- [x] Interrupteur `PALMARES_ACTIF`, cache `v7`
- [x] Tests passés, captures dans `docs/captures/`, état du projet à jour
- [x] Commit et push sur `main`, résumé de 5 lignes + la marche à suivre de l'utilisateur

## Compte rendu (à remplir par Claude Code)

**Fait — 11 octobre 2026**

**1. Base de données.**
- `migration-002-palmares.sql` : rejouable, dans l'ordre demandé, en **une seule transaction** (`begin … commit`). Si l'un des deux e-mails n'est pas remplacé ou introuvable, le script s'arrête avec un message clair et **ne change rien** : les anciennes règles restent, et Maxime garde l'édition.
- `setup.sql` : réécrit pour une installation neuve avec tout le modèle (même garde-fou sur les e-mails).
- `verification-droits.sql` (nouveau, pour le 8 bis) : à lancer dans le SQL Editor, il affiche un tableau ✅/❌ (un visiteur ne peut rien écrire ; Maxime et Roxane peuvent écrire pays, souvenir et palmarès). Chaque essai est annulé aussitôt.
- `docs/02-guide-installation.md` mis à jour (installation neuve et mise à jour d'octobre).
- **Testé sur un vrai PostgreSQL 16 imitant Supabase** (schémas `auth` et `storage`, rôles `anon` et `authenticated`, publication temps réel), script `tests/test_ordre006_sql.py` : **42/42**. Points couverts :
  - ancienne base, puis migration sans e-mails : refus, rien de modifié, Maxime écrit toujours ;
  - migration correcte, puis relancée : Success ;
  - visiteur et compte non membre : aucune écriture (pays, souvenir, photo, stockage, vote) ;
  - Maxime et Roxane : mêmes droits (Roxane supprime une photo de Maxime et son fichier) ; `author_id` rempli automatiquement ;
  - palmarès : on ne vote pas à la place de l'autre et on n'efface pas son choix ; changer d'avis remplace l'ancien choix ; supprimer une photo efface ses choix ; un choix vise une photo **ou** un souvenir ;
  - installation neuve avec `setup.sql`.
  Le script de vérification a lui aussi été testé : il signale bien une règle cassée ou un membre manquant, et ne laisse aucune trace.

**Connexion de Roxane.**
- `CONFIG.ROXANE_EMAIL` (`roxane@nos-voyages.fr`, adresse fictive) et `CONFIG.INDICE_CODE`.
- Fenêtre « Nos souvenirs, à deux » : indice, un seul champ (clavier numérique, 22 px), message doux si le code est faux, aucune mention du mode édition. Elle s'ouvre depuis un bouton du palmarès ou depuis « ➕ Ajouter nos souvenirs » (bas de chaque fiche et de la liste ☰).
- Après connexion, le geste en attente s'exécute : le choix touché est enregistré, ou le mode édition s'ouvre.

**Rôles.**
- Les prénoms viennent de `members`. Un compte absent de `members` est refusé (message « Ce compte ne fait pas partie de nos deux téléphones »).
- Mode édition identique pour les deux. Chaque souvenir écrit est signé « — Roxane » ou « — Maxime » ; les anciens souvenirs n'ont pas de signature.
- **Choix de conception** : « Quitter » **sort du mode édition sans déconnecter**, pour les deux. Les choix du palmarès restent donc possibles, et « ➕ Ajouter nos souvenirs » rouvre l'édition sans redemander le code : le code protège l'écriture, pas le téléphone qu'elle tient en main. Le mode édition est mémorisé par téléphone. Une vraie déconnexion se fait par « Se déconnecter (prénom) » en bas de la liste ☰.
- **Filet de sécurité** : tant que la migration n'est pas faite (table `members` absente), l'app garde l'ancien comportement (tout compte connecté peut éditer), et le palmarès reste masqué. La mise en ligne du code ne coupe donc pas l'édition de Maxime.
- **Mode démo** : sélecteur « Je suis : Maxime / Roxane / Visiteur » (démo seulement).

**2. Choisir.**
- Visionneuse : barre 🌅 🍽️ 😂 💗 (54 px). Le bouton est en surbrillance quand c'est mon choix ; re-toucher retire le choix.
- Souvenir : bouton 🏅, qui affiche aussi les récompenses visibles du souvenir et déplie les 4 choix.
- Toast avec la bonne préposition : « 🌅 Ta plus belle vue au Portugal », « en France », « aux Maldives », « à Malte ».

**3. Palmarès dans la fiche** (sous les lieux, avant les photos ; aucun bloc s'il n'y a aucun choix) :
- 🌅, 🍽️ et 😂 : vignette ou extrait du souvenir, avec « Maxime », « Roxane » ou « **Vous deux** ».
- 💗 : deux colonnes « Préféré de … ». **Règle du secret** : le 💗 de l'autre est caché (« 🔒 Choisis le tien pour découvrir celui de Maxime ») tant qu'on n'a pas choisi le sien. Elle vaut aussi pour les **visiteurs**, sinon Roxane, encore visiteuse le jour J, le verrait avant d'avoir choisi. Les emojis 💗 dans la galerie suivent la même règle.
- Si c'est le même moment : une seule vignette, « Votre moment préféré à tous les deux 💞 ».
- Toucher une vignette ouvre la photo, ou fait défiler jusqu'au souvenir, qui s'illumine.

**4. Même moment.**
- Voile nuit, pluie de cœurs (2,6 s), le moment dans un cadre papier, « Vous avez choisi le même moment 💞 » + pays, bouton 🥰, vibration si disponible. Simple fondu si `prefers-reduced-motion`.
- Se déclenche pour celui qui vient de créer la correspondance, et pour l'autre **à l'ouverture de l'app** (une seule fois : mémorisé par personne dans `localStorage`, avec try/catch).
- **Temps réel** (bonus) : abonnement Supabase Realtime à `picks`, sans écraser un champ en cours de saisie.
- Jamais par-dessus l'accueil ou la lettre : l'animation attend l'arrivée sur la carte.

**5.** `PALMARES_ACTIF` sous `CARTE_PAR_DEFAUT` : `false` masque tout le palmarès. L'accès par code de Roxane reste actif : c'est une question de droits, pas de palmarès. `sw.js` passé à `nos-voyages-v7`.

**Corrections et ajustements trouvés par les tests**
- Le sélecteur de démo restait visible **en production** (le `display:flex` l'emportait sur `hidden`) : corrigé.
- Le titre « Notre palmarès » n'était pas en Fraunces : corrigé.
- **Touche tolérante (ORDRE-005) affinée** : en vue d'ensemble, toucher le halo rose de l'Italie visitée, qui déborde en mer près de Rome, ouvrait le Vatican. En mer, un petit pays « à découvrir » ne gagne maintenant que s'il est plus proche que la côte d'un grand pays voisin. Les petits pays visités ou rêvés, et les îles isolées comme les Maldives, ne changent pas.

**Tests** (webapp-testing, 390 × 844), globe **et** carte plate pour le palmarès :
- `tests/test_ordre006_iphone.py` (démo, Maxime / Roxane) : **47/47**, tests 1 à 5, 7, 8 et 9.
- `tests/test_ordre006_code_secret.py` (visiteur face à un Supabase simulé : base, connexion, stockage, temps réel) : **14/14**, test 6. Cela couvre la fenêtre du code au-dessus de la photo, le mauvais code avec son message doux, le bon code qui enregistre le choix 💗 en attente avec le jeton de Roxane et déclenche l'animation, puis « ➕ » sans code.
- Seule erreur console : la réponse « 400 » du serveur à un mauvais code, que le navigateur affiche toujours quand un mot de passe est refusé.
- Non-régression : ORDRE-002 14/14, 003 18/18, 004 18/18, 005 41/41.
- Captures : `docs/captures/ordre006-*.png`.

**Non testé ici** : le vrai projet Supabase (inaccessible depuis l'environnement de Claude Code ; remplacé par le PostgreSQL local et le Supabase simulé), l'envoi d'une vraie photo depuis la photothèque d'un iPhone, et le temps réel entre deux vrais téléphones.
