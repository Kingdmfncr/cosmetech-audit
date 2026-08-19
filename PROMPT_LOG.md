# PROMPT LOG : comment j'ai construit ce projet avec l'IA

> Je n'ai pas de background développeur. La valeur n'est pas dans le code, elle est dans le cadrage du problème et la vérification de ce qui est réellement vrai avant de coder.

---

## Contexte de départ

Deuxième projet d'un brief pour préparer un échange avec le Business Manager d'une ESN, secteur cosmétique/agroalimentaire, pas une mission effectuée.

## Étape 1, trouver et vérifier une vraie source de données

Le brief proposait Open Food Facts pour des données cosmétiques. L'IA a vérifié qu'il existe un projet dédié aux cosmétiques, Open Beauty Facts, avec une API publique réelle, testée directement avant d'écrire le code d'ingestion (requête réelle sur des produits déodorants, crèmes, rouges à lèvres, avec inspection du format de réponse).

## Étape 2, vérifier la liste réglementaire avant de l'implémenter

Point le plus sensible du projet : afficher une liste de "substances à risque" sans base réglementaire vérifiée aurait été une invention. L'IA a recherché la liste officielle des 26 allergènes de parfum (Annexe III, règlement CE 1223/2009), l'a vérifiée sur 2 sources indépendantes pour s'assurer qu'aucune substance n'était inventée ou mal orthographiée, avant de l'écrire dans le code.

**Décision de cadrage explicite** : ne jamais présenter une détection d'allergène comme une non-conformité. Le règlement impose une déclaration au-delà d'un seuil de concentration qu'une simple liste d'ingrédients ne permet pas de vérifier. Le code et l'interface le disent explicitement plutôt que de laisser un raccourci trompeur.

## Étape 3, test sur données réelles

125 produits réels récupérés, 80 avec au moins un allergène détecté (64%). Les produits les plus concernés sont des déodorants de grandes marques (Dove, Mennen), cohérent avec le fait que les déodorants sont un segment historiquement chargé en parfum, un signal honnête plutôt qu'un résultat choisi pour la démonstration.

---

## Ce que ce projet prouve

| Compétence démontrée | Preuve |
|---|---|
| Gestion de données réelles via API publique | Open Beauty Facts, requêtes réelles testées avant codage |
| Rigueur réglementaire | Liste officielle vérifiée sur 2 sources, limite de la méthode documentée explicitement |
| Refus de sur-interpréter une donnée | Présence détectée jamais présentée comme un verdict de conformité |

---

## Ma conclusion

> Sur un sujet réglementaire, la vraie compétence n'est pas d'afficher une liste de substances qui a l'air sérieuse, c'est de vérifier la source officielle et de dire clairement ce que la donnée permet réellement de conclure, et ce qu'elle ne permet pas.

*Gisèle Metouck, Consultante Data Steward & Gouvernance*
