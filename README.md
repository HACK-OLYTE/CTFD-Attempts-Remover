# CTFD-Attempts-Remover

**CTFD-Attempts-Remover** est un plugin pour [CTFd](https://ctfd.io) permettant aux utilisateurs de demander un **déblocage de leurs tentatives** sur un challenge précis directement depuis l'interface de la plateforme CTFd. Fini les messages privés ou les requêtes sur Discord pour demander un reset !

---

## Fonctionnalités principales

- **Demande de déblocage intégrée** : Les équipes peuvent soumettre une demande de retrait de tentatives pour un challenge donné.
- **Système de malus configurable pour l'administration de l'évènement** :
  - **Malus fixe** : Retire un nombre précis de points lors du déblocage.
  - **Malus proportionnel** : Retire un pourcentage des points du challenge concerné.
- **Interface admin intuitive** :
  - Vue centralisée de toutes les demandes.
  - Validation en un clic.
  - Application automatique des malus.
  - Configuration du type de malus
  - ...


## Pourquoi ce plugin ?

> "Vous pouvez nous redonner des tentatives pour le challenge « TocTocToc » s’il vous plaît ?"

Avec ce plugin, plus besoin pour une équipe de passer par Discord ou d’envoyer des messages privés pour demander un déblocage.  
Les équipes peuvent désormais demander directement depuis la plateforme CTFd un déblocage sur un challenge précis et récupérer leurs tentatives.

Côté administration, un tableau de gestion complet permet de consulter les demandes, de valider les actions et d’appliquer les malus en un clic.

Grâce à ces nouveautés, tout le monde gagne en temps et en confort : les joueurs restent concentrés sur le jeu, et l’équipe organisatrice se libère des tâches manuelles répétitives.


## Installation

1. Clonez ce dépôt dans le dossier `CTFd/plugins` :
   
   ```bash
   cd /path/to/CTFd/plugins
   git https://github.com/HACK-OLYTE/CTFD-Attempts-Remover.git

3. Restart your CTFd instance to load the plugin.


## Configuration

Accédez au panneau d’administration **Plugins > Attempts-remover** pour :

- Activer ou désactiver le plugin (pour désactiver le plugin mettez les malus à 0).
- Choisir le type de malus appliqué (fixe ou proportionnel).
- Gérer et valider les demandes des équipes.

Voici une vidéo de démonstration du plugin : 


https://github.com/user-attachments/assets/656cb398-fd3a-4897-8855-0e86607e8a21


## Dépendances

- CTFd ≥ v3.x
- Compatible avec les installations Docker et locales.
- Un navigateur à jour et JavaScript d'activé.


## Support

Pour toute question ou problème, ouvrez une [issue](https://github.com/votre-utilisateur/CTFD-Attempts-Remover/issues). <br>
Ou contactez nous sur le site de l'association Hack'olyte : [contact](https://hackolyte.fr/contact/).


## Contribuer

Les contributions sont les bienvenues !  
Vous pouvez :

- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Soumettre des pull requests


## Licences 

Ce plugin est sous licence [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.fr).  
Merci de ne pas retirer le footer de chaque fichier HTML sans l'autorisation préalable de l'association Hack'olyte.


