# ORDRE-006 — Recette finale et version du jour J

**Émis par** : l'architecte · **Exécutant** : Claude Code + l'utilisateur · **Statut** : à faire
**Échéance** : mardi 13 octobre 2026 · **Code gelé depuis** : lundi 12 au soir

## Objectif
Vérifier une dernière fois l'app **avec le vrai contenu**, puis figer une version de référence restaurable en une commande. **Aucune nouvelle fonctionnalité.** Seule une correction de bug bloquant est autorisée, après accord de l'utilisateur.

## Partie A — Claude Code
1. **Audit du code** (lecture seule, ne rien modifier sans accord) :
   - aucune clé `service_role` / secret, aucun mot de passe dans le dépôt (tout l'historique, pas seulement `main`) ;
   - `CONFIG` pointe bien vers le projet Supabase de l'utilisateur ;
   - `CARTE_PAR_DEFAUT = 'globe'` ;
   - `LETTRE` : texte et signature « Max » exacts ;
   - aucun `console.log` de débogage oublié, aucune donnée de démo forcée hors mode démo ;
   - `carte-cadeau.html` : le QR décode toujours `https://mplaa8.github.io/nos-voyages/`.
2. **Tests** : relance toute la batterie (ORDRES 002 à 005) en mode démo, viewport iPhone. Tout doit passer.
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
- [ ] Aucun bouton « Modifier », « Supprimer » ou « Mode édition » visible (on est bien en visiteur)
- [ ] **Partager → Sur l'écran d'accueil** : l'icône ❤️ apparaît, l'app s'ouvre en plein écran
- [ ] Carte cadeau imprimée, QR scanné avec l'appareil photo de l'iPhone → ouvre bien l'app
- [ ] Dernière étape : **Quitter** le mode édition sur mon propre iPhone

Tout problème trouvé : le décrire à Claude Code (ou à l'architecte) avec une capture d'écran.

## Critères de fin
- [ ] Audit et tests OK
- [ ] Tag `v1.0-anniversaire` poussé, procédure de retour arrière documentée
- [ ] Check-list de l'utilisateur entièrement cochée
- [ ] Compte rendu rempli, statut « fait », commit et push

## Compte rendu (à remplir par Claude Code)
