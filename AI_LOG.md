# AI Log — Workshop TransConnect

## Entrée 29/09/2026

* **Outil IA utilisé :** ChatGPT

* **Prompt :** Comment créer et vérifier les modèles Django pour les différentes applications de mon projet TransConnect, et comment identifier les anomalies du modèle `Offre` fourni dans le workshop ?

* **Sortie obtenue (résumé) :** ChatGPT m'a aidée à comprendre et à vérifier les modèles Django `Utilisateur`, `Entreprise`, `Vehicule`, `Expedition` et `Offre`, ainsi que les relations entre les différentes entités et la génération des migrations.

* **Écarts identifiés vs cahier des charges :**

  1. Le champ `prix` était défini avec un `CharField`, alors qu'il représente un montant numérique pouvant contenir des décimales.
  2. Le champ `delai_jours` était défini avec un `IntegerField`, ce qui permet notamment des valeurs négatives.
  3. Le champ `date_proposition` utilisait `auto_now=True`, ce qui modifie la date à chaque sauvegarde de l'objet.
  4. Le champ `vehicule` utilisait `null=True`, ce qui permettait de créer une offre sans véhicule, alors que cette relation doit être obligatoire selon le modèle métier.

* **Correction apportée et justification :**

  1. `prix` a été remplacé par `DecimalField(max_digits=10, decimal_places=2)` afin de représenter correctement un montant monétaire avec deux décimales.
  2. `delai_jours` a été remplacé par `PositiveIntegerField()` afin d'empêcher les valeurs négatives pour un délai exprimé en jours.
  3. `auto_now=True` a été remplacé par `auto_now_add=True` afin que la date de proposition soit enregistrée lors de la création de l'offre et ne soit pas modifiée lors des sauvegardes suivantes.
  4. `null=True` a été supprimé du champ `vehicule` afin de rendre l'association avec un véhicule obligatoire, conformément au modèle métier.

* **Vérifications effectuées :**

  * Les migrations des applications `EntreprisesApp`, `VehiculesApp`, `ExpeditionsApp` et `OffresApp` ont été générées.
  * Les migrations ont été appliquées avec succès.
  * La base SQLite a été configurée avec le nom `Roua_Sdiri.sqlite3`.
  * Les migrations ont été vérifiées avec `showmigrations`.

