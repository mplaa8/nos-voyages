# ORDRE-008 — Fondations : sauvegarde automatique et anti-mise en veille

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire
**À exécuter** : à partir du jeudi 15 octobre 2026 (après l'anniversaire, code gelé jusque-là)
**Prérequis côté utilisateur** : créer un dépôt GitHub **privé** `mplaa8/nos-voyages-sauvegarde` (vide) et donner accès à l'app Claude sur ce dépôt.

## Objectif
1. **Ne jamais perdre un souvenir** : une copie complète (données + photos) est faite automatiquement chaque semaine, dans un endroit privé, et on sait la restaurer.
2. **Ne jamais trouver l'app « en pause »** : Supabase gratuit met en pause un projet inactif environ une semaine ; on l'empêche automatiquement.
Le tout **sans rien changer à l'app** (`index.html` n'est pas modifié) et **100 % gratuit**.

## Conception (décidée par l'architecte)

### Où ça tourne
Tout se passe dans le **dépôt privé** `nos-voyages-sauvegarde`, avec **GitHub Actions** :
- les sauvegardes y sont privées (photos et souvenirs ne sont pas exposés comme dans le dépôt public) ;
- les commits hebdomadaires de sauvegarde gardent ce dépôt « actif », ce qui évite que GitHub désactive les tâches planifiées après 60 jours sans activité ;
- quota gratuit des dépôts privés : largement suffisant (quelques minutes par semaine).

**Aucun secret n'est nécessaire** : les tables et le bucket `photos` sont en lecture publique, la clé publishable suffit. Ne jamais mettre la clé `service_role` / secret dans un workflow ni dans un dépôt.

### Workflow 1 — `reveil.yml` (anti-mise en veille)
- Planifié tous les 3 jours (`cron`), plus déclenchable à la main (`workflow_dispatch`).
- Fait une vraie requête de lecture à l'API Supabase (par ex. `GET /rest/v1/countries?select=code&limit=1` avec la clé publishable).
- Échoue clairement (statut ≠ 200) pour que l'utilisateur reçoive l'e-mail d'échec de GitHub si la base ne répond plus.
- Vérifie dans la documentation Supabase actuelle qu'une requête API compte bien comme activité ; sinon, propose une alternative gratuite dans le compte rendu.

### Workflow 2 — `sauvegarde.yml` (sauvegarde hebdomadaire)
- Planifié une fois par semaine (dimanche nuit, heure de Paris), plus `workflow_dispatch`.
- Exporte en JSON lisible (une ligne par enregistrement, trié par identifiant pour des différences propres) : `countries`, `memories`, `photos`, `picks`, `members` (sans e-mail : seuls `user_id` et `prenom` sont lisibles, c'est voulu). Pagination si besoin (l'API limite le nombre de lignes par requête).
- Télécharge **uniquement les nouvelles photos** du bucket public `photos` (en se basant sur la table `photos` et les fichiers déjà présents), en conservant les mêmes chemins.
- Écrit un `RESUME.md` : date, nombre de pays / souvenirs / photos / choix, taille totale.
- Commit (« Sauvegarde du JJ/MM/AAAA ») et push dans le dépôt privé, seulement s'il y a des changements. Ne supprime jamais une photo de la sauvegarde, même si elle a été supprimée dans l'app (on garde tout ; les suppressions sont listées dans le résumé).
- Alerte dans le résumé (et échec du workflow) si la taille du dépôt approche 1 Go, avec une recommandation pour la suite.

### Restauration
- `RESTAURATION.md` dans le dépôt privé : en langage simple pour l'utilisateur (quand s'en servir, ce qu'il doit faire), puis la procédure exacte pour Claude Code.
- Un script `restaurer.py` (ou équivalent) qui réimporte les données et renvoie les photos dans un projet Supabase. Il demande la clé `service_role` **au moment de l'exécution** (variable d'environnement saisie par l'utilisateur), ne l'écrit jamais nulle part, et s'arrête si la base cible n'est pas vide (sauf confirmation explicite).
- Le restaurer doit pouvoir recréer le schéma via `setup.sql` du dépôt public.

### Côté dépôt public
- `docs/02-guide-installation.md` : section « Sauvegarde et réveil automatiques » (où ça se trouve, comment lancer une sauvegarde à la main, que faire si un e-mail d'échec arrive).
- `CLAUDE.md` : une ligne dans « Architecture » sur le dépôt de sauvegarde.
- **Pas de changement de `sw.js`** (aucun fichier de l'app n'est modifié).

## Ce que l'utilisateur devra faire (à lui expliquer pas à pas, en français simple)
1. github.com → **+** → **New repository** → nom `nos-voyages-sauvegarde`, **Private**, rien de coché → **Create repository**.
2. Donner accès à l'app Claude sur ce dépôt (https://github.com/apps/claude/installations/select_target → mplaa8 → ajouter `nos-voyages-sauvegarde`).
3. Après le travail de Claude Code : onglet **Actions** du dépôt privé → lancer « Sauvegarde » et « Réveil » une première fois à la main, vérifier les coches vertes.

## Tests
1. Exécution locale des scripts contre un faux serveur (ou des réponses enregistrées) : export complet, pagination, téléchargement des seules nouvelles photos, aucune modification quand rien n'a changé.
2. Restauration testée de bout en bout sur une base PostgreSQL locale qui imite Supabase (comme pour l'ORDRE-006).
3. Vérification qu'aucun secret n'est présent dans les fichiers.
4. Après le lancement manuel par l'utilisateur : lecture du `RESUME.md` produit (comptes cohérents avec l'app).

## Critères de fin
- [ ] Deux workflows dans le dépôt privé, lancés une fois avec succès
- [ ] Première sauvegarde complète présente (données + photos), `RESUME.md` cohérent
- [ ] Procédure et script de restauration testés
- [ ] Aucun secret dans aucun dépôt ; `index.html` et `sw.js` inchangés
- [ ] Guide et `CLAUDE.md` à jour, état du projet à jour
- [ ] Commit et push, résumé de 5 lignes pour l'architecte

## Compte rendu (à remplir par Claude Code)
