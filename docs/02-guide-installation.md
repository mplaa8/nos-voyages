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
3. **SQL Editor → New query** : ouvre `setup.sql` avec TextEdit, copie tout, colle, **Run**.
4. **Authentication → Users → Add user → Create new user** : ton e-mail + mot de passe, coche **Auto Confirm User**.
5. **Authentication → Sign In / Providers** : désactive **Allow new users to sign up**.
6. **Project Settings → API** (ou « API Keys ») : copie la **Project URL** et la clé **anon public** (ou **publishable key**).

✅ « Success » après le SQL, ton e-mail dans la liste des utilisateurs, URL + clé copiées.

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

## Mettre à jour l'app plus tard
Modifier le fichier sur le Mac, puis sur GitHub : **Add file → Upload files** → glisser le fichier modifié → **Commit changes**. Penser à passer `nos-voyages-v1` à `v2` dans `sw.js` pour que l'iPhone récupère la nouvelle version.

## Bon à savoir
- Limites gratuites Supabase : 500 Mo de base de données, 1 Go de photos.
- Un projet Supabase inactif environ une semaine est mis en pause ; les données restent, réactivation en un clic.
- Toute personne ayant l'adresse peut voir la carte (sans la modifier).
