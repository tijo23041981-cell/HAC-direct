# HAC Direct — suivre l’actualité du HAC en quasi temps réel

Un site qui se met à jour tout seul : un robot (GitHub Actions) tourne toutes les 10 minutes, récupère les actus et les scores, et le site relit les données chaque minute.

## Mise en place (environ 15 minutes, gratuit)

1. **Crée un compte GitHub** puis un dépôt public, par exemple `hac-direct`.
2. **Envoie tous les fichiers de ce dossier** dans le dépôt (bouton « Add file » > « Upload files »). Pense à inclure le dossier `.github` (fichier caché).
3. **Active le site** : Settings > Pages > Source « Deploy from a branch » > branche `main`, dossier `/ (root)`. L’adresse sera `https://TON-PSEUDO.github.io/hac-direct/`.
4. **Scores et classement (facultatif mais conseillé)** : crée un compte gratuit sur football-data.org, copie ta clé d’API, puis dans GitHub : Settings > Secrets and variables > Actions > New repository secret, nom `FOOTBALL_DATA_TOKEN`, valeur = ta clé.
5. **Premier lancement** : onglet Actions > « Mise à jour HAC » > Run workflow. Ensuite il se relance seul toutes les 10 minutes.

Sans clé d’API, les actualités fonctionnent quand même ; seuls les scores, le calendrier et le classement restent vides.

## Installer comme une application sur le téléphone

Ouvre le site dans le navigateur, puis « Ajouter à l’écran d’accueil ».

## Ce que fait le robot

- **Actualités** : flux d’actualités Google News sur « Havre Athletic Club » et « Le Havre HAC Ligue 1 », qui regroupent de nombreux médias. Pour ajouter d’autres flux RSS, modifie la liste `FEEDS` dans `scripts/update.py`. N’ajoute que des sites qui autorisent la lecture automatique.
- **Scores / classement / calendrier** : API football-data.org (Ligue 1). Si le numéro de compétition ou le nom du club change, adapte `FL1` et `is_hac` dans le même fichier.

## Limites à connaître

- « Temps réel » veut dire une mise à jour toutes les 10 minutes environ. GitHub peut retarder les exécutions planifiées de quelques minutes. Pour un score minute par minute pendant les matchs, il faudrait un petit serveur dédié.
- Le score « en direct » dépend de l’offre gratuite de l’API, qui peut avoir quelques minutes de retard.
- Ce projet n’a pas pu être testé avec un vrai accès internet avant livraison : lance le workflow une fois et regarde l’onglet Actions pour vérifier qu’il est vert. S’il y a une erreur, envoie-la-moi.
