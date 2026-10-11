# ORDRE-007 — Recette finale et version du jour J

**Émis par** : l'architecte · **Exécutant** : Claude Code + l'utilisateur · **Statut** : partie A faite ; partie B (iPhone) à cocher par l'utilisateur
**Échéance** : mardi 13 octobre 2026 · **Code gelé depuis** : lundi 12 au soir (après l'ORDRE-006)

## Objectif
Vérifier une dernière fois l'app **avec le vrai contenu**, puis figer une version de référence restaurable en une commande. **Aucune nouvelle fonctionnalité.** Seule une correction de bug bloquant est autorisée, après accord de l'utilisateur.

## Partie A — Claude Code
1. **Audit du code** (lecture seule, ne rien modifier sans accord) :
   - aucune clé `service_role` / secret, aucun mot de passe dans le dépôt (tout l'historique, pas seulement `main`) ;
   - `CONFIG` pointe bien vers le projet Supabase de l'utilisateur ;
   - `CARTE_PAR_DEFAUT = 'globe'` ;
   - `LETTRE` : texte et signature « Max » exacts ;
   - `PALMARES_ACTIF = true`, `ROXANE_EMAIL` fictif (aucune adresse personnelle), aucun e-mail réel dans `migration-002-palmares.sql` ;
   - aucun `console.log` de débogage oublié, aucune donnée de démo forcée hors mode démo ;
   - `carte-cadeau.html` : le QR décode toujours `https://mplaa8.github.io/nos-voyages/`.
2. **Tests** : relance toute la batterie (ORDRES 002 à 006) en mode démo, viewport iPhone. Tout doit passer.
3. **Version de référence** : crée le tag git `v1.0-anniversaire` sur le commit validé et pousse-le. Note dans `docs/02-guide-installation.md` comment revenir à cette version en cas de souci (en langage simple pour l'utilisateur, et la commande exacte pour Claude Code).
4. **Compte rendu** et mise à jour de `docs/00-etat-du-projet.md` (« Idées » : renvoyer vers `docs/04-banque-idees.md`).

## Partie B — L'utilisateur (sur son iPhone, en mode visiteur, pas en mode édition)
Fermer complètement l'app, puis ouvrir `https://mplaa8.github.io/nos-voyages/` **sans** `#admin`.

- [ ] Le contenu de test a été supprimé (pays, photo, souvenir ajoutés lors des essais)
- [ ] Accueil : le cœur bat, « Ouvrir mon cadeau » fonctionne
- [ ] Lettre : texte complet, signée Max, bouton « Découvrir notre carte »
- [ ] Globe : tous nos pays visités sont roses, nos rêves sont dorés, les petits pays ont leur point
- [ ] Le compteur en haut affiche le bon nombre de pays
- [ ] Ouvrir **chaque** pays visité : villes, photos (visionneuse, balayage), souvenirs sans faute de frappe
- [ ] Les photos s'affichent en moins de 2–3 secondes en 4G
- [ ] ☰ : statistiques justes, recherche, « 💌 Relire ta lettre »
- [ ] Palmarès : mes choix (🌅 🍽️ 😂 💗) sont faits dans chaque pays ; mon 💗 apparaît caché (🔒) en visiteur
- [ ] Code secret de Roxane testé **sur un autre appareil ou en navigation privée** (puis se déconnecter), jamais sur son iPhone avant le jour J
- [ ] Aucun bouton « Modifier », « Supprimer » ou « Mode édition » visible (on est bien en visiteur)
- [ ] **Partager → Sur l'écran d'accueil** : l'icône ❤️ apparaît, l'app s'ouvre en plein écran
- [ ] Carte cadeau imprimée, QR scanné avec l'appareil photo de l'iPhone → ouvre bien l'app
- [ ] Dernière étape : **Quitter** le mode édition sur mon propre iPhone

Tout problème trouvé : le décrire à Claude Code (ou à l'architecte) avec une capture d'écran.

## Critères de fin
- [x] Audit et tests OK
- [x] Tag `v1.0-anniversaire` poussé (créé par l'utilisateur sur GitHub, release « Version du jour J », commit `2226711`) ; procédure de retour arrière documentée
- [ ] Check-list de l'utilisateur entièrement cochée
- [ ] Compte rendu rempli, statut « fait », commit et push

## Compte rendu (à remplir par Claude Code)

**Partie A — 12 octobre 2026**

**Audit** (lecture seule, aucune modification de l'app) :
- **Secrets** : les 24 commits de l'historique ont été parcourus (`git log -p --all`). Aucune clé `service_role` ou secrète, aucun jeton JWT, aucun mot de passe. La seule clé est la clé **publishable**, publique par conception.
- **E-mails** : aucune adresse réelle dans le contenu des fichiers, sur tout l'historique. L'adresse de Maxime n'apparaît que comme auteur du tout premier commit, créé sur GitHub ; ce sont des métadonnées, pas le contenu. Le reste n'est que des adresses fictives ou d'exemple : `roxane@nos-voyages.fr`, `maxime@exemple.fr` dans les tests, `john@example.com` dans l'exemple du skill. `migration-002-palmares.sql` et `setup.sql` ne contiennent que les marqueurs `EMAIL-DE-…`.
- **Réglages** :
  - `CONFIG` pointe vers `https://rmlpgirrwvuoruwixrbo.supabase.co` ;
  - `CARTE_PAR_DEFAUT = 'globe'` et `PALMARES_ACTIF = true` ;
  - `ROXANE_EMAIL` est fictif, et l'indice est « Notre date secrète (JJMMAAAA) 💕 » ;
  - `LETTRE` est exacte (texte avec apostrophes typographiques, ORDRE-004), signée « Max » ;
  - `sw.js` est en `nos-voyages-v7`.
- **Débogage** : aucun `console.log`, `console.info` ni `console.debug` dans `index.html`, `sw.js` ou `carte-cadeau.html`. Les données de démo (sélecteur « Je suis », comptes `demo-…`) ne servent que si `CONFIG` est vide. Le sélecteur est masqué avec un vrai Supabase (bug corrigé et testé dans l'ORDRE-006).
- **Carte cadeau** : le QR, décodé par OpenCV, donne bien `https://mplaa8.github.io/nos-voyages/`.

**Tests** : toute la batterie a été relancée en mode démo, au format iPhone 390 × 844, sur le globe et la carte plate. **152/152** :
- ORDRE-002 : 14/14 ;
- ORDRE-003 : 18/18 ;
- ORDRE-004 : 18/18 ;
- ORDRE-005 : 41/41 ;
- ORDRE-006 : 47/47 en démo, et 14/14 pour le code secret face au Supabase simulé.

Seules erreurs console, attendues : les deux 404 volontaires du test de secours, et le 400 renvoyé par le serveur à un mauvais code. Un contrôle (« lettre masquée ») était fragile, à cause d'une attente fixe sous rendu logiciel : il attend maintenant que la lettre soit masquée. **Aucun changement de l'app.** La migration SQL n'a pas été relancée ici : elle a été testée 42/42 dans l'ORDRE-006, et l'utilisateur a validé `verification-droits.sql` sur son vrai Supabase (4 ✅).

**Version de référence** : le tag `v1.0-anniversaire` a été créé localement, mais **son envoi est refusé par l'accès GitHub de la session Claude Code** : les branches passent, pas les tags. Il est donc à créer par l'utilisateur sur GitHub (Releases → Draft a new release → tag `v1.0-anniversaire`, cible `main`), et le dernier commit de `main` est la version validée. La procédure de retour arrière est dans `docs/02-guide-installation.md` : en langage simple pour l'utilisateur, avec les commandes pour Claude Code. Elle passe par `git restore`, sans réécrire l'historique, puis demande d'incrémenter `CACHE` au-delà du dernier numéro, sans quoi les iPhone garderaient la version plus récente en cache.

**Partie B** : check-list transmise à l'utilisateur, à cocher sur son iPhone.

**Mise à jour** : tag `v1.0-anniversaire` créé par l'utilisateur via une release GitHub « Version du jour J » sur le commit `2226711` (vérifié depuis Claude Code avec `git ls-remote --tags`).
