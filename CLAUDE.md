# Carte de nos voyages ❤️ — consignes pour Claude

## Le projet
Web app (PWA) offerte par l'auteur à sa femme pour son anniversaire : une carte du monde où brillent les pays visités ensemble, avec pour chacun photos et souvenirs. Elle consulte ; lui seul modifie (mode édition). L'app doit continuer à vivre après l'anniversaire.
- Cahier des charges : `docs/01-cahier-des-charges.md`
- État, décisions, idées en attente : `docs/00-etat-du-projet.md` (à tenir à jour)
- Installation pas à pas : `docs/02-guide-installation.md`

## Méthode de travail : architecte et exécutant
- **L'architecte** (Claude, dans le projet claude.ai « App Roxe ») décide de la conception et rédige des **ordres de travail** dans `docs/ordres/ORDRE-NNN-sujet.md`.
- **Toi, Claude Code, tu es l'exécutant** : tu réalises l'ordre demandé étape par étape, tu testes, tu commits et tu pousses sur `main`.
- Si un ordre est ambigu ou qu'une étape te paraît mauvaise, demande à l'utilisateur au lieu d'improviser une autre conception ; tu peux proposer une alternative dans le compte rendu.
- À la fin de chaque ordre : remplis la section « Compte rendu » de l'ordre, passe son statut à « fait », mets à jour `docs/00-etat-du-projet.md`, commit et push. Termine en donnant à l'utilisateur un résumé de 5 lignes maximum qu'il pourra transmettre à l'architecte.

## L'utilisateur
Francophone, travaille depuis un Mac, **n'est pas développeur**. Répondre en français, expliquer simplement, une étape à la fois.

## Contraintes non négociables
- **100 % gratuit** : GitHub Pages (hébergement), Supabase plan Free (données, photos, connexion admin), Leaflet + Natural Earth (carte, sans clé d'API). Aucun service payant, aucune clé payante.
- **iPhone d'abord** : Safari iOS, tactile, boutons ≥ 44 px, champs en 16 px (sinon zoom iOS), safe-area, installable « Sur l'écran d'accueil ».
- Expérience : romantique → personnelle → visuelle → interactive → simple.

## Architecture
- Pas de build, pas de framework : tout le HTML/CSS/JS est dans `index.html` à la racine (servi tel quel par GitHub Pages).
- `CONFIG` en haut du script : `SUPABASE_URL` + `SUPABASE_ANON_KEY`. La clé anon/publishable est publique par conception ; la sécurité vient des règles RLS de `setup.sql`. **Ne jamais committer** de clé `service_role`/secret ni de mot de passe.
- Config vide → « mode démo » (localStorage, un seul appareil).
- Tables Supabase : `countries` (code ADM0_A3, name, status 'visited'|'dream', places), `memories`, `photos` (+ bucket storage public `photos`). Toute évolution du schéma va dans `setup.sql` sous forme de migration rejouable, avec les instructions pour l'appliquer dans le SQL Editor.
- Mode édition : 5 touches rapides sur le ❤️ ou URL terminée par `#admin`.
- `sw.js` : **incrémenter `CACHE` (`nos-voyages-vN`) à chaque modification d'un fichier de l'app**, sinon l'iPhone garde l'ancienne version.

## Avant de dire « c'est fini »
- Vérifier la syntaxe JS et tester l'app en local (mode démo) au format iPhone.
- Mettre à jour `docs/00-etat-du-projet.md` (avancement, décisions, idées).
