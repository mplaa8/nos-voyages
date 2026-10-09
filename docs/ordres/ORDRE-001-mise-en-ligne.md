# ORDRE-001 — Intégrer la version 1, la brancher sur Supabase et la mettre en ligne

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire

## Objectif
À la fin de cet ordre, l'app tourne en ligne sur `https://mplaa8.github.io/nos-voyages/`, branchée sur le projet Supabase de l'utilisateur, et le dépôt GitHub contient tout le code et la documentation.

## Contexte
- Le dépôt `mplaa8/nos-voyages` ne contenait qu'un README initial. La version 1 (code + docs + `CLAUDE.md`) a été fournie par l'architecte.
- Le projet Supabase est créé. Le script `setup.sql`, le compte admin et les clés sont peut-être déjà faits : demande à l'utilisateur où il en est.
- L'utilisateur n'est pas développeur : pour toute action qu'il doit faire lui-même (site Supabase, réglages GitHub), donne-lui des instructions courtes, en français, clic par clic.

## Étapes
1. **Intégrer la version 1**
   - Vérifie que la racine du dépôt contient : `index.html`, `sw.js`, `manifest.webmanifest`, `setup.sql`, `icon-180.png`, `icon-192.png`, `icon-512.png`, `.nojekyll`, `CLAUDE.md`, `README.md`, `docs/`.
   - Vérifie la syntaxe du JavaScript de `index.html` (par ex. avec `node`).
   - Commit « Version 1 de la Carte de nos voyages » sur `main` et push.
2. **Finir Supabase** (avec l'utilisateur)
   - Vérifie avec lui que `setup.sql` a été exécuté dans **SQL Editor** (résultat « Success »), qu'un compte admin existe (Authentication → Users, « Auto Confirm User ») et que les inscriptions sont désactivées (Authentication → Sign In / Providers → « Allow new users to sign up » désactivé). Guide-le pour ce qui manque.
   - Demande-lui la **Project URL** et la clé **anon public** (ou **publishable key**). Refuse et ne stocke jamais une clé `service_role` / secret.
3. **Brancher l'app**
   - Renseigne `SUPABASE_URL` et `SUPABASE_ANON_KEY` dans l'objet `CONFIG` de `index.html`.
   - Passe `CACHE` de `nos-voyages-v1` à `nos-voyages-v2` dans `sw.js`.
4. **Tester en ligne** *(modifié à la demande de l'utilisateur : Claude Code tourne dans le cloud, `localhost` n'est pas accessible depuis le Mac ; le test se fait après l'étape 5, sur `https://mplaa8.github.io/nos-voyages/#admin`)*
   - ~~Lance un serveur local~~ ~~(`python3 -m http.server 8000`) et fais ouvrir `http://localhost:8000/#admin` à l'utilisateur.~~
   - Il se connecte avec son compte admin, marque un pays « Visité », ajoute une photo et un souvenir, recharge : tout doit être conservé. Vérifie qu'il n'y a pas d'erreur dans la console.
   - Fais-lui supprimer le contenu de test (ou laisse-le s'il veut le garder).
   - Commit « Branchement Supabase » et push.
5. **Publier sur GitHub Pages**
   - Si la CLI `gh` est installée et connectée : `gh api -X POST repos/mplaa8/nos-voyages/pages -f "source[branch]=main" -f "source[path]=/"`.
   - Sinon, guide l'utilisateur : Settings → Pages → « Deploy from a branch » → `main` / `(root)` → Save.
6. **Vérifier en ligne**
   - Attends le déploiement, puis vérifie que `https://mplaa8.github.io/nos-voyages/` répond et que la carte se charge (fais-le confirmer à l'utilisateur sur son iPhone si possible).

## Critères de fin
- [ ] Dépôt à jour sur `main` (V1 + configuration Supabase)
- [ ] Connexion admin et enregistrement de données vérifiés
- [ ] App accessible à `https://mplaa8.github.io/nos-voyages/`
- [ ] `docs/00-etat-du-projet.md` mis à jour (cases cochées)
- [ ] Compte rendu rempli ci-dessous, commit et push

## Compte rendu (à remplir par Claude Code)
*Ce qui a été fait, ce qui reste, problèmes rencontrés, décisions prises en cours de route.*
