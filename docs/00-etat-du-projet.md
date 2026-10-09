# Carte de nos voyages ❤️ — État du projet

*Dernière mise à jour : 9 octobre 2026*

Ce document est le point d'entrée du projet. Il résume ce qui existe, les choix faits et toutes les idées en attente. La roadmap viendra ensuite.

## Le projet en une phrase
Une web app romantique, offerte à ma femme pour son anniversaire : une carte du monde où brillent les pays que nous avons visités ensemble, avec pour chacun nos photos et nos souvenirs. Elle consulte, moi seul je modifie. L'app doit continuer à vivre après l'anniversaire, comme un carnet de voyage numérique.

Le cahier des charges complet est dans `01-cahier-des-charges.md`.

## Contraintes à respecter
- **100 % gratuit** : pas d'abonnement, pas d'API payante, pas d'hébergement ni de base de données payants.
- **iPhone d'abord** : Safari iPhone, tactile, gros boutons, installable sur l'écran d'accueil (PWA).
- **Je travaille depuis mon Mac** pour construire et mettre à jour l'app ; je ne suis pas développeur, chaque étape doit être expliquée simplement. L'app elle-même reste pensée pour l'iPhone de ma femme.
- Expérience voulue : romantique → personnelle → visuelle → interactive → simple.

## Décisions prises
| Sujet | Choix | Pourquoi |
|---|---|---|
| Type d'app | Web app (PWA) plutôt qu'app iOS native | Gratuit (pas de compte développeur Apple), installable via « Sur l'écran d'accueil » |
| Hébergement | GitHub Pages | Gratuit |
| Stockage du code | Dépôt GitHub `nos-voyages`, travaillé avec Claude Code | Tout l'historique est conservé ; `CLAUDE.md` donne le contexte à chaque session |
| Données + photos | Supabase (offre gratuite) | Base de données + stockage photos + connexion admin, sans frais |
| Carte | Leaflet + contours des pays Natural Earth, sans fond de carte | Gratuit, sans clé d'API, rendu épuré |
| Code | Un seul fichier `index.html`, sans outil de build | Simple à modifier et à republier |
| Accès admin | 5 touches rapides sur le ❤️ ou adresse terminée par `#admin`, puis e-mail + mot de passe Supabase | Invisible pour ma femme, sécurisé côté serveur |
| Sécurité | Lecture publique, écriture réservée au compte admin connecté ; inscriptions désactivées | La clé « anon » peut être publique, les règles protègent les données |
| Photos | Compressées sur le téléphone avant envoi (JPEG, 1800 px max) | Reste largement dans les limites gratuites |
| Mode démo | Si la config Supabase est vide, données stockées sur l'appareil seulement | Pour tester avant d'installer |

## Ce qui est déjà construit (version 1)
**Côté ma femme**
- Écran d'accueil : ciel étoilé, cœur qui bat, « Joyeux anniversaire mon amour ❤️ », bouton « Ouvrir mon cadeau » avec animation d'ouverture.
- Carte de nuit plein écran : pays visités en rose lumineux, pays rêvés en doré, autres pays sombres et discrets. Zoom et déplacement au doigt.
- Compteur « X pays découverts ensemble », légende, bouton 🌍 pour recentrer.
- Fiche pays : drapeau, statut, villes et lieux, galerie photo (visionneuse plein écran, balayage), souvenirs datés.
- Liste « Nos pays » (☰) pour accéder directement à chaque pays.

**Côté moi (mode édition)**
- Marquer un pays « Visité », « Un jour » (voyage rêvé) ou le retirer.
- Modifier les villes et lieux.
- Ajouter plusieurs photos d'un coup, supprimer une photo.
- Ajouter, modifier, supprimer un souvenir.

**Fichiers** (à la racine du dépôt GitHub)
`index.html`, `setup.sql`, `sw.js`, `manifest.webmanifest`, et 3 icônes PNG (cœur rose sur fond nuit, dans le zip `nos-voyages.zip`).

## Où on en est
- [x] Cahier des charges rédigé
- [x] Version 1 du code écrite et vérifiée
- [x] Guide d'installation depuis le Mac (`02-guide-installation-mac.md`)
- [x] Projet Supabase créé et configuré
- [x] Dépôt GitHub créé et code poussé
- [x] App publiée sur GitHub Pages : https://mplaa8.github.io/nos-voyages/ (ORDRE-001, contenu de test conservé pour l'instant)
- [ ] Carte remplie (pays, photos, souvenirs)
- [ ] Testée sur iPhone, puis offerte 🎁

## Idées à trier pour la roadmap

**Venant du cahier des charges**
- Ajouter les futurs voyages à la carte (déjà amorcé avec le statut « Un jour ✨ »).
- Faire grandir la carte voyage après voyage, au fil des années.
- Afficher les anecdotes et ce qu'on a aimé dans chaque pays (aujourd'hui : texte libre dans les souvenirs).

**Pistes apparues pendant la construction** (à valider ou écarter)
- Dates des voyages (année, mois) et frise chronologique de notre histoire.
- Plusieurs voyages dans un même pays, chacun avec ses photos et souvenirs.
- Points sur la carte pour les villes visitées, pas seulement les pays.
- Légende ou commentaire sous chaque photo, et choix d'une photo de couverture par pays.
- Statistiques douces : nombre de pays, de continents, pourcentage du monde découvert.
- Message ou surprise personnalisée à l'ouverture (lettre, musique, révélation pays par pays).
- Permettre à ma femme d'ajouter elle aussi ses propres souvenirs.
- Compte à rebours vers le prochain voyage prévu.
- Sauvegarde/export de toutes nos données (pour ne jamais rien perdre).
- Mode hors ligne plus complet (consulter photos et souvenirs sans réseau).

## Points de vigilance
- Supabase gratuit met en pause un projet inactif depuis environ une semaine. Les données restent ; on le réactive en un clic depuis le tableau de bord.
- Toute personne qui a le lien peut voir la carte (sans rien modifier) : ne pas partager le lien publiquement.
- Après une modification du code, incrémenter `CACHE` dans `sw.js` (actuellement `nos-voyages-v2`) pour forcer la mise à jour sur l'iPhone.
