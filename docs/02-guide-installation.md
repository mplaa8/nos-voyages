# Guide d'installation — depuis le Mac

Durée : environ 30 minutes. Tout se fait dans le navigateur du Mac (Safari ou Chrome), sans rien installer.

## Étape 0 — Tester l'app tout de suite (2 min)
1. Télécharge `nos-voyages.zip` et double-clique dessus : un dossier `nos-voyages` apparaît dans Téléchargements.
2. Double-clique sur `index.html` : l'app s'ouvre dans le navigateur en **mode démo**.
3. Pour la voir comme sur iPhone : dans Safari, menu **Développement → Passer en mode Conception adaptative** (ou dans Chrome : clic droit → Inspecter → icône téléphone).
4. Touche 5 fois le ❤️ en haut à gauche pour essayer le mode édition.

✅ La carte s'affiche et tu peux marquer un pays « Visité ». En mode démo, rien n'est enregistré ailleurs que dans ce navigateur.

## Étape 1 — Base de données Supabase (10 min)
1. supabase.com → **Start your project** → crée un compte.
2. **New project** : nom `nos-voyages`, mot de passe généré (inutile ensuite), région Europe, plan **Free**.
3. **Authentication → Users → Add user → Create new user**, deux fois, en cochant **Auto Confirm User** :
   - ton compte : ton e-mail et ton mot de passe ;
   - celui de Roxane : l'adresse **fictive** écrite dans `CONFIG.ROXANE_EMAIL` (`index.html`, par défaut `roxane@nos-voyages.fr`) et, comme mot de passe, **le code secret** (au moins 6 caractères). Aucun e-mail n'est jamais envoyé.
4. **SQL Editor → New query** : ouvre `setup.sql` avec TextEdit, copie tout, colle. Tout en bas, remplace `EMAIL-DE-MAXIME` et `EMAIL-DE-ROXANE` par les deux adresses de l'étape 3 (garde les apostrophes), puis **Run**.
5. **Authentication → Sign In / Providers** : désactive **Allow new users to sign up**.
6. **Project Settings → API** (ou « API Keys ») : copie la **Project URL** et la clé **anon public** (ou **publishable key**).

✅ « Success » après le SQL (sinon, le message en rouge dit quelle adresse est introuvable, et rien n'a été modifié), deux comptes dans la liste des utilisateurs, URL + clé copiées.

## Étape 2 — Brancher l'app sur Supabase (2 min)
1. Clic droit sur `index.html` → **Ouvrir avec → TextEdit**. (Si TextEdit affiche la page au lieu du code : TextEdit → Réglages → Ouvrir et enregistrer → coche « Afficher les fichiers HTML en tant que code HTML ».)
2. Cmd + F → cherche `CONFIG` et colle tes valeurs entre les guillemets :
   ```
   SUPABASE_URL: "https://xxxx.supabase.co",
   SUPABASE_ANON_KEY: "ta-clé"
   ```
3. Cmd + S pour enregistrer. Rouvre `index.html` dans le navigateur avec `#admin` à la fin de l'adresse et connecte-toi.

✅ Connexion réussie, et un pays ajouté reste visible après rechargement de la page.

## Étape 3 — Mettre en ligne avec GitHub Pages (10 min)
1. github.com → crée un compte (le pseudo apparaîtra dans l'adresse).
2. **+ → New repository** : nom `nos-voyages`, **Public**, **Create repository**.
3. Lien **« uploading an existing file »** : glisse les 8 fichiers du dossier (pas le dossier lui-même) → **Commit changes**.
4. **Settings → Pages** : Source **Deploy from a branch**, branche **main**, dossier **/ (root)** → **Save**.

✅ Après 1 à 2 minutes : `https://ton-pseudo.github.io/nos-voyages/` s'affiche en haut de la page Pages.

## Étape 4 — Remplir la carte
Ouvre l'adresse avec `#admin`, connecte-toi, puis pour chaque pays : statut, villes, photos, souvenirs. Les photos peuvent venir du Mac (Photos → glisser vers un dossier) ou être ajoutées depuis l'iPhone en ouvrant la même adresse. Supprime le contenu de test, puis **Quitter**.

## Étape 5 — Offrir 🎁
Sur l'iPhone de ta femme : Safari → l'adresse → **Partager → Sur l'écran d'accueil → Ajouter**.

## Mise à jour d'octobre 2026 : nos deux téléphones et le palmarès
Pour une base installée avant octobre 2026 (sinon, rien à faire : `setup.sql` contient déjà tout).
1. **Authentication → Users → Add user → Create new user** : l'adresse fictive de Roxane (`CONFIG.ROXANE_EMAIL`, par défaut `roxane@nos-voyages.fr`), **le code secret comme mot de passe** (au moins 6 caractères), **Auto Confirm User** coché.
2. **SQL Editor → New query** : colle tout `migration-002-palmares.sql`, remplace `EMAIL-DE-MAXIME` (ton adresse de connexion, telle qu'elle apparaît dans Authentication → Users) et `EMAIL-DE-ROXANE` (l'adresse fictive), puis **Run**. Attendu : « Success ». Si un message rouge dit qu'un compte est introuvable, **rien n'a été modifié** : corrige l'adresse et relance. Le script peut être relancé sans risque.
3. **Vérifier les droits** : SQL Editor → New query → colle `verification-droits.sql` → **Run**. Un petit tableau s'affiche : les 4 lignes doivent commencer par ✅ (un visiteur ne peut rien écrire, Maxime et Roxane peuvent tout faire). Ce script ne modifie rien.
4. **Sur ton iPhone** : vérifie que tu peux toujours modifier un pays. Puis, **en navigation privée** (jamais sur l'iPhone de Roxane avant le jour J) : ouvre la carte, un pays, touche « ➕ Ajouter nos souvenirs », entre le code secret, ajoute une photo de test, supprime-la, puis ☰ → **Se déconnecter**.

Dans l'app : « Quitter » sort du mode édition sans déconnecter (les choix du palmarès restent possibles) ; « Se déconnecter » se trouve en bas de la liste ☰. Pour masquer le palmarès sans toucher à la base : `PALMARES_ACTIF = false` dans `index.html`.

## Mettre à jour l'app plus tard
Modifier le fichier sur le Mac, puis sur GitHub : **Add file → Upload files** → glisser le fichier modifié → **Commit changes**. Penser à incrémenter le numéro de `CACHE` dans `sw.js` (par ex. `nos-voyages-v7` → `v8`) pour que l'iPhone récupère la nouvelle version.

## Bon à savoir
- Limites gratuites Supabase : 500 Mo de base de données, 1 Go de photos.
- Un projet Supabase inactif environ une semaine est mis en pause ; les données restent, réactivation en un clic.
- Toute personne ayant l'adresse peut voir la carte (sans la modifier). Seuls les deux comptes inscrits dans la table `members` peuvent écrire.
