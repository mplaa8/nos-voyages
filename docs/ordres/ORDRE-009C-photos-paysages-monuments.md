# ORDRE-009C — Des paysages et des monuments dans le jeu des envies

**Émis par** : Maxime (demande directe à Claude Code, à faire valider par l'architecte) · **Exécutant** : Claude Code · **Statut** : fait (validation sur iPhone par l'utilisateur)
**Prérequis côté utilisateur** : aucun (pas de migration, pas de Supabase)

## Demande
Retour de Maxime sur l'ORDRE-009B : « Je veux des photos de beaux paysages et/ou de monuments, pas forcément les photos de base. » Les photos complémentaires venaient des premières images de l'article Wikipédia du pays (souvent des cartes, des personnalités, des scènes de rue banales).

## Compte rendu (Claude Code)

**Fait — 13 octobre 2026**

**Nouvelle sélection** (toujours Wikimedia : gratuit, sans clé, lectures publiques) :
1. **Bannière Wikivoyage** du pays (inchangée : c'est déjà un grand panorama).
2. **Sites du patrimoine mondial de l'UNESCO** du pays (monuments **et** grands paysages naturels), les plus célèbres d'abord (classés par nombre de Wikipédia qui en parlent), via le service de requêtes Wikidata (`query.wikidata.org`, une seule requête en parallèle des deux autres). Un seul cliché par site, cartes/plans et non-JPG écartés. Pour les territoires séparés (Réunion, Guyane…), on cherche les sites situés dans le territoire (P131) au lieu du pays (P17).
3. **Repli** si le pays n'a pas (assez) de sites UNESCO ou si le service ne répond pas : les photos de l'**article Wikivoyage** (français, sinon anglais), choisies par des voyageurs, avec les mêmes filtres qu'avant.
Les photos de l'article **Wikipédia ne sont plus utilisées**.

**Légende** : le nom du lieu s'affiche dans la ligne de crédit, par ex. « 📍 Mont-Saint-Michel et sa baie · Photo : Auteur · Wikimedia Commons » (tronqué à 34 caractères, texte nettoyé ; un site sans nom français ni anglais n'a pas de légende).

**Mise à jour** : la mémoire des photos passe en `nos-voyages-photos-v2` (les anciennes sélections sont oubliées), `sw.js` ne met pas en cache `wikivoyage.org`, cache passé en `nos-voyages-v10`. Le repli silhouette (4 s), l'interrupteur `PHOTOS_ENVIES` et les gestes sont inchangés.

**Tests** (webapp-testing, 390 × 844, Wikimedia **simulé** car inaccessible depuis l'environnement de Claude Code) : `tests/test_photos_paysages.py` (adaptation de `test_ordre009b_photos.py`). **31/31** (sélection UNESCO, un cliché par site, légendes, repli Wikivoyage si pas de site ou service en panne, repli silhouette, service lent, image introuvable, interrupteur). Non-régression du jeu : ORDRE-009 **36/36**. `test_ordre009b_photos.py` décrit l'ancienne sélection (Wikipédia) et est remplacé par ce test. Captures : `docs/captures/paysages-*.png`.

**À vérifier sur l'iPhone** : la vraie qualité des photos (10–15 pays). Le service de requêtes Wikidata peut être un peu lent la toute première fois ; dans ce cas la carte reste en silhouette, puis les photos apparaissent aux parties suivantes (elles sont mémorisées).
