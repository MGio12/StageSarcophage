# Guide Utilisateur — Modes Dégradés

## Sommaire

1. [Connexion / Déconnexion](#1-connexion--déconnexion)
2. [Tableau de bord](#2-tableau-de-bord)
3. [Gérer les sources](#3-gérer-les-sources)
4. [Consulter les documents](#4-consulter-les-documents)
5. [Télécharger des documents](#5-télécharger-des-documents)
6. [Consulter les journaux](#6-consulter-les-journaux)
7. [Exporter des rapports](#7-exporter-des-rapports)
8. [Administration](#8-administration)

---

## 1. Connexion / Déconnexion

### Se connecter

1. Accédez à l'application via votre navigateur : `http://<adresse-serveur>:5000`
2. Saisissez votre **nom d'utilisateur** et **mot de passe**
3. Cliquez sur **Connexion**

> **Note** : Un compte administrateur doit être créé par l'équipe technique avant la première utilisation.

> **Authentification Active Directory** : Si l'intégration LDAP est configurée, vous pouvez utiliser vos identifiants Windows habituels. Un compte local sera créé automatiquement à la première connexion.

### Se déconnecter

Cliquez sur **Déconnexion** dans la barre de navigation (coin supérieur droit).

---

## 2. Tableau de bord

Le tableau de bord s'affiche après connexion. Il présente :

- **Compteurs** : nombre de sources actives, documents collectés, alertes
- **Alertes récentes** : documents en statut critique ou avertissement
- **Dernières synchronisations** : historique des collectes récentes

---

## 3. Gérer les sources

### Voir la liste des sources

Menu **Sources** > vous voyez toutes les sources actives avec leur statut.

### Ajouter une nouvelle source

1. Menu **Sources** > **Nouvelle source**
2. Remplissez le formulaire :
   - **Nom** : identifiant unique de la source
   - **Description** : (optionnel) notes sur cette source
   - **Type de serveur** : Linux ou Windows
   - **Protocole** : SFTP, SMB ou Local
   - **Adresse** : IP ou nom d'hôte du serveur
   - **Port** : port de connexion (22 pour SFTP, 445 pour SMB)
   - **Chemin distant** : dossier contenant les PDF à collecter
   - **Login / Mot de passe** : identifiants de connexion
   - **Filtre fichiers** : motif de fichiers (ex: `*.pdf`)
   - **Fréquence de sync** : intervalle en minutes
   - **Rétention** : durée de conservation en jours
   - **Seuils d'alerte** : avertissement et critique en jours
3. Cliquez sur **Enregistrer**

### Tester la connexion

1. Allez sur le détail d'une source
2. Cliquez sur **Tester la connexion**
3. Le système affiche le résultat :
   - **Succès** : connexion établie
   - **Nouvelle clé SSH** (SFTP) : cliquez sur **Accepter** pour valider l'empreinte du serveur
   - **Erreur** : vérifiez les paramètres de connexion

### Synchronisation manuelle

1. Détail de la source > **Synchroniser maintenant**
2. La collecte démarre immédiatement
3. Un message confirme le nombre de fichiers collectés

### Purge manuelle

1. Détail de la source > **Purger les anciens documents**
2. Confirmez l'action
3. Les documents dépassant la rétention sont supprimés

### Modifier une source

1. Détail de la source > **Modifier**
2. Modifiez les champs souhaités
3. **Enregistrer**

### Supprimer une source

1. Détail de la source > **Supprimer**
2. Confirmez
3. La source passe en statut "archivée" (suppression logique)

> Les sources archivées peuvent être restaurées via **Sources** > **Archivées** > **Restaurer**

---

## 4. Consulter les documents

### Accéder à la liste

Menu **Documents** > liste paginée de tous les documents collectés.

### Filtrer les documents

Utilisez les filtres en haut de page :

- **Source** : afficher uniquement les documents d'une source
- **Statut** : OK, Avertissement, Critique, Purgé
- **Date depuis** : documents collectés après cette date
- **Date jusqu'à** : documents collectés avant cette date

Cliquez sur **Filtrer** pour appliquer.

### Comprendre les statuts

| Statut | Signification |
|--------|---------------|
| **OK** | Document récent, dans les délais |
| **Avertissement** | Approche du seuil d'alerte |
| **Critique** | Dépasse le seuil critique |
| **Purgé** | Document supprimé (rétention dépassée) |

---

## 5. Télécharger des documents

### Télécharger un document

Dans la liste des documents, cliquez sur **Télécharger** à droite du document souhaité.

### Télécharger plusieurs documents (ZIP)

1. Cochez les documents souhaités dans la liste
2. Cliquez sur **Télécharger la sélection**
3. Un fichier ZIP est généré et téléchargé

> **Note** : Pour les très gros fichiers, le téléchargement peut prendre quelques secondes.

---

## 6. Consulter les journaux

### Accéder aux journaux

Menu **Journaux** > historique complet des événements.

### Types d'événements

| Type | Description |
|------|-------------|
| **sync** | Synchronisation (collecte de fichiers) |
| **purge** | Suppression de fichiers anciens |
| **erreur** | Erreur de connexion ou traitement |
| **connexion** | Test de connexion |
| **acces** | Téléchargement de document |

### Filtrer les journaux

- **Source** : événements d'une source spécifique
- **Type** : filtrer par type d'événement
- **Date depuis / jusqu'à** : plage de dates

### Exporter en CSV

1. Appliquez les filtres souhaités (optionnel)
2. Cliquez sur **Exporter CSV**
3. Un fichier CSV est téléchargé avec les colonnes :
   - Date
   - Type
   - Source
   - Utilisateur
   - Message
   - Détails

---

## 7. Exporter des rapports

### Rapport de conformité

Le tableau de bord propose deux formats d'export :

1. **Excel** : cliquez sur le bouton **Excel** dans la section "Rapports de conformité"
   - Feuille récapitulative par source
   - Une feuille détaillée par source avec tous les documents

2. **PDF** : cliquez sur le bouton **PDF**
   - Tableau récapitulatif
   - Liste des documents avec statuts colorés

Les rapports incluent tous les documents actifs avec leur statut (OK, Avertissement, Critique).

---

## 8. Administration

> **Note** : Ces fonctionnalités sont réservées aux administrateurs.

### Gérer les utilisateurs

Menu **Administration** > **Utilisateurs**

- **Créer un utilisateur** : cliquez sur "Nouvel utilisateur", renseignez nom, mot de passe et rôle
- **Modifier** : cliquez sur l'icône crayon
- **Activer/Désactiver** : un utilisateur désactivé ne peut plus se connecter

### Rôles disponibles

| Rôle | Permissions |
|------|-------------|
| **admin** | Toutes les permissions (gestion sources, utilisateurs, etc.) |
| **lecteur** | Consultation documents, journaux (lecture seule) |

### Gérer les tokens API

Menu **Administration** > **Tokens API**

Les tokens permettent d'accéder à l'API REST depuis des outils externes.

1. Cliquez sur **Nouveau token**
2. Choisissez un nom et un utilisateur associé
3. Définissez une durée de validité (optionnel)
4. **Copiez le token affiché** — il ne sera plus visible ensuite

Pour révoquer un token, cliquez sur l'icône de révocation.

### Configurer les notifications

Menu **Administration** > **Notifications**

Ajoutez des destinataires pour recevoir des alertes par email :
- **Documents critiques** : alerte quand des documents dépassent le seuil critique
- **Erreurs de connexion** : alerte après 3 échecs consécutifs sur une source

Utilisez le bouton **Envoyer un email test** pour vérifier la configuration SMTP.

---

## Questions fréquentes

### Je ne peux pas me connecter

- Vérifiez que le nom d'utilisateur et mot de passe sont corrects
- Après 5 tentatives échouées, attendez quelques minutes (protection anti-brute-force)
- Contactez l'administrateur si le problème persiste

### La synchronisation échoue

- Vérifiez les paramètres de la source (adresse, port, identifiants)
- Testez la connexion manuellement
- Pour SFTP : acceptez la clé SSH si elle est nouvelle
- Consultez les journaux pour voir le message d'erreur détaillé

### Un document est en statut "Critique"

Le document dépasse le seuil critique configuré pour cette source. Cela peut indiquer :
- Un problème de mise à jour du fichier source
- Un paramètre de seuil trop strict

Vérifiez la date de dernière modification et ajustez les seuils si nécessaire.

### Comment restaurer une source supprimée ?

1. Menu **Sources** > **Sources archivées**
2. Trouvez la source souhaitée
3. Cliquez sur **Restaurer**

### Comment utiliser l'API REST ?

1. Demandez à un administrateur de créer un **token API** pour vous
2. Utilisez le token dans vos requêtes avec le header `Authorization: Bearer <votre-token>`
3. Exemple : `curl -H "Authorization: Bearer abc123..." http://serveur/api/v1/sources`

### Je ne reçois pas les notifications par email

- Vérifiez que la configuration SMTP est correcte (demandez à l'administrateur)
- Vérifiez que votre adresse email est bien configurée dans Administration > Notifications
- Utilisez le bouton "Envoyer un email test" pour diagnostiquer

---

## Support

Pour toute question technique, contactez l'équipe informatique.
