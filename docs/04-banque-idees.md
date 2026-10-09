# Banque d'idées — la vie de l'app après l'anniversaire

*Proposées par l'architecte le 9 octobre 2026. Rien n'est décidé : on pioche ici pour construire la phase 2.*

Légende de l'effort : ⚡ rapide (quelques heures) · 🔧 moyen (une journée) · 🏗️ gros (plusieurs jours)
Toutes les idées respectent la contrainte « 100 % gratuit » sauf mention contraire.

## La pierre angulaire : la notion de « Voyage » 🏗️
Aujourd'hui, tout est rangé **par pays**. Beaucoup d'idées ci-dessous deviennent simples dès qu'on range aussi **par voyage** : un voyage = un titre (« Lune de miel au Portugal »), des dates, un ou plusieurs pays, des villes, ses photos et ses souvenirs. Un pays peut avoir plusieurs voyages.
Cela débloque la frise, les dates, le compte à rebours, « il y a un an », le récap annuel, le livre photo…
Migration douce : le contenu actuel de chaque pays devient automatiquement un premier voyage.

## 1. Pendant le voyage — l'app devient notre carnet de route
- **Mode « voyage en cours »** 🔧 : un gros bouton « ➕ Ajouter » sur l'écran principal pendant le voyage, pour poster en 2 gestes une photo ou une phrase du jour, rangées automatiquement dans le voyage en cours.
- **« On est ici »** ⚡ : un bouton qui utilise la localisation de l'iPhone pour ajouter la ville du moment sur la carte (géolocalisation du navigateur, gratuite).
- **Photos qui se rangent toutes seules** 🔧 : lire la date et le lieu enregistrés dans la photo (EXIF) pour proposer automatiquement le pays, la ville et la date. *À vérifier : selon le mode de sélection, iOS peut retirer la position des photos.*
- **Le journal du jour** ⚡ : un souvenir par jour, daté, qui forme le récit du voyage.
- **Mémos vocaux** 🔧 : enregistrer un souvenir à voix haute (le rire au restaurant, le bruit des vagues). L'enregistrement audio fonctionne dans Safari iPhone.
- **Hors ligne** 🏗️ : poster même sans réseau (avion, montagne), l'envoi se fait au retour du réseau.
- **Trajet du voyage** 🔧 : relier les villes visitées par une ligne sur le globe, dans l'ordre.

## 2. Revivre nos souvenirs
- **« Notre histoire »** 🔧 : une frise chronologique de tous nos voyages, du premier au dernier, avec une photo de couverture par voyage.
- **« Il y a un an aujourd'hui »** ⚡ : à l'ouverture, si un souvenir date de ce jour-là il y a 1, 2, 5 ans, il s'affiche.
- **« Surprends-moi »** ⚡ : un bouton qui fait tourner le globe et s'arrête sur un souvenir au hasard.
- **Diaporama d'un voyage** 🔧 : lecture plein écran des photos d'un voyage avec un lent effet de zoom (style Ken Burns), musique facultative avec nos propres fichiers.
- **Coups de cœur** ⚡ : des étiquettes sur les souvenirs (🍽️ meilleur repas, 🌅 plus belle vue, 😂 fou rire, 🏨 le lieu où on a dormi) et un filtre pour les retrouver.
- **Deux regards** 🔧 : chacun écrit sa version du même moment, affichées côte à côte (« Max se souvient… » / « Elle se souvient… »).
- **Ce qu'on a rapporté** ⚡ : rubriques par pays pour une recette apprise, des mots de la langue locale, un objet acheté.

## 3. Préparer les prochains voyages
- **Liste de rêves enrichie** 🔧 : pour chaque pays rêvé, pourquoi on veut y aller, la meilleure saison, des idées d'activités, des liens.
- **Tirer au sort notre prochaine destination** ⚡ : le globe tourne et s'arrête sur un de nos pays rêvés. Parfait avec le globe 3D.
- **Compte à rebours** ⚡ : « Plus que 23 jours avant Lisbonne ✈️ » sur l'écran d'accueil.
- **Votes à deux** 🔧 : chacun note ses envies, l'app montre nos destinations communes préférées.
- **Valise partagée** 🔧 : une liste de choses à emporter, cochable à deux.

## 4. Rituels et surprises
- **Lettres à ouvrir plus tard** 🔧 : une lettre cachée dans un pays rêvé, qui ne s'ouvre que le jour où on le marque « visité ». Une capsule temporelle.
- **Une lettre par anniversaire** ⚡ : chaque 14 octobre, une nouvelle lettre apparaît à l'ouverture. L'app devient un rituel annuel.
- **Notre année en voyages** 🔧 : chaque fin d'année, un récap animé : pays, kilomètres parcourus, nombre de photos, souvenir de l'année.
- **Étapes symboliques** ⚡ : des messages doux quand on franchit un cap (10ᵉ pays, nouveau continent, 5 ans de voyages).
- **Notifications** 🏗️ : l'iPhone peut recevoir des notifications d'une app installée sur l'écran d'accueil, mais il faut un petit service pour les envoyer. Faisable gratuitement avec Supabase, mais plus complexe.

## 5. Garder et partager
- **Livre photo** 🔧 : générer un PDF mis en page par voyage (photos et souvenirs), à faire imprimer.
- **Affiche « Nos pays »** ⚡ : une image du globe avec nos pays en rose, à imprimer et encadrer.
- **Partager un voyage** 🔧 : un lien en lecture seule vers un seul voyage, pour la famille.

## 6. Fondations — pour que l'app dure des années
- **Empêcher la mise en veille de Supabase** ⚡ : une tâche automatique gratuite (GitHub Actions) qui « réveille » la base tous les 3 jours.
- **Sauvegarde automatique** 🔧 : une copie hebdomadaire des données et des photos dans un dépôt GitHub **privé** séparé. Indispensable avant d'avoir des années de souvenirs.
- **Photos plus rapides** 🔧 : créer une miniature à l'envoi pour que les galeries s'affichent instantanément, même avec des centaines de photos.
- **Gestion des photos** ⚡ : réordonner les photos, choisir la photo de couverture, ajouter une légende.
- **Accès privé** 🔧 : un code à 4 chiffres (notre date ?) à la première ouverture, puisque l'adresse est publique.
- **Nom de domaine** (≈ 10 €/an, donc **pas gratuit**) : par ex. `nosvoyages.fr` au lieu de l'adresse GitHub. À n'envisager que si le gratuit n'est plus une contrainte.

## Recommandation de l'architecte pour la phase 2
1. **Fondations** : mise en veille empêchée et sauvegarde automatique. Rien n'est plus grave que perdre des souvenirs.
2. **La notion de Voyage**, la pierre angulaire.
3. **Mode « voyage en cours »** et « On est ici », pour l'utiliser vraiment au prochain voyage.
4. **Notre histoire** (frise), puis **Il y a un an aujourd'hui**.
5. **Prochaine destination** : compte à rebours et tirage au sort sur le globe.
