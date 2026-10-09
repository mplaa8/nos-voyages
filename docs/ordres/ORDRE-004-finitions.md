# ORDRE-004 — Finitions avant le gel du code

**Émis par** : l'architecte · **Exécutant** : Claude Code · **Statut** : à faire
**Échéance** : dimanche 11 octobre 2026 (gel du code lundi 12 au soir)

## Contexte
Revue de l'architecte sur les ORDRES 002 et 003 : très bon travail, rendu conforme. Deux finitions avant le jour J, sans toucher à rien d'autre.

## 1. La France ne doit allumer que la France métropolitaine
**Constat** (capture `ordre003-2-globe-japon-usa.png`) : avec la France « visitée », des taches roses apparaissent aux Antilles, en Guyane et dans l'océan Indien. Dans le fichier Natural Earth `admin_0_countries`, la géométrie `FRA` contient les départements d'outre-mer (Guyane, Guadeloupe, Martinique, La Réunion, Mayotte). Avoir visité Paris ne doit pas allumer la Guyane. Le problème existe probablement aussi pour d'autres pays (par ex. Pays-Bas et leurs îles des Caraïbes, Norvège et le Svalbard) : vérifie dans les données.

**Résultat attendu**
- Marquer la France « visitée » allume **uniquement la France métropolitaine (Corse comprise)**.
- La Guyane, la Guadeloupe, la Martinique, La Réunion et Mayotte deviennent des territoires **sélectionnables séparément**, chacun avec sa fiche, son statut, son nom en français et un drapeau cohérent (drapeau français à défaut).
- Même logique pour les autres cas trouvés, si c'est simple ; sinon, liste-les dans le compte rendu.
- **Compatibilité des données** : la France métropolitaine garde le code `FRA` (et chaque pays déjà concerné garde son code actuel), pour que le contenu déjà saisi reste rattaché au bon endroit.
- Le comportement est identique sur le globe et sur la carte plate de secours.
- Les statistiques ne changent pas de logique : un territoire d'outre-mer compte comme un « pays » de plus seulement s'il est lui-même marqué visité, et son continent est celui de sa position (Amérique du Sud pour la Guyane, Afrique pour La Réunion et Mayotte, Amérique du Nord pour les Antilles).

**Piste technique (à ton choix, justifie dans le compte rendu)**
- soit le fichier Natural Earth `ne_50m_admin_0_map_units`, s'il sépare bien ces territoires (champ du type `GU_A3`), en conservant `FRA` pour la métropole ;
- soit, au chargement, découper la multi-géométrie `FRA` (et les autres cas) en entités séparées selon la position de chaque polygone, avec des codes dédiés (`GUF`, `GLP`, `MTQ`, `REU`, `MYT`).
Aucune donnée Supabase ne doit être modifiée.

## 2. Apostrophes typographiques dans la lettre
Dans `LETTRE.texte`, remplace les apostrophes droites `'` par des apostrophes typographiques `’` (« t’offrir », « jusqu’à »). C'est plus élégant dans la police Fraunces. Ne change aucun autre caractère du texte.

## 3. Version
Incrémente `CACHE` dans `sw.js` (`nos-voyages-v5`).

## Tests (webapp-testing, iPhone 390 × 844, mode démo)
1. France visitée : capture du globe montrant l'Europe et l'Atlantique → seule la métropole est rose, la Guyane et les Antilles restent sombres.
2. Toucher la Guyane ouvre la fiche « Guyane », indépendante de celle de la France.
3. Marquer La Réunion visitée → elle devient rose, les statistiques comptent bien un pays et un continent de plus.
4. Vol vers la France depuis ☰ : cadrage sur la métropole.
5. Carte plate (`?carte=plate`) : même comportement.
6. Lettre : apostrophes typographiques visibles. Capture.
7. Les 32 tests existants (ORDRES 002 et 003) passent toujours, aucune erreur console.

## Critères de fin
- [ ] Outre-mer séparé, métropole seule allumée, codes existants conservés
- [ ] Apostrophes typographiques
- [ ] Cache `v5`
- [ ] Tests passés, captures dans `docs/captures/`, état du projet à jour
- [ ] Commit et push sur `main`, résumé de 5 lignes pour l'architecte

## Compte rendu (à remplir par Claude Code)
