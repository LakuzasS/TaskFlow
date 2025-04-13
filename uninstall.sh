#!/bin/bash

echo "Désinstallation de l'application TaskFlow..."

# Arrêter et supprimer le conteneur TaskFlow et les ressources associées
echo "Arrêt et suppression des conteneurs et images Docker liés à TaskFlow..."
docker-compose down --remove-orphans
docker-compose rm -f
docker rmi sae502-taskflow-main-taskflow-app:latest

# Supprimer le raccourci de l'application
if [ -f "/usr/share/applications/TaskFlow.desktop" ]; then
    echo "Suppression du raccourci TaskFlow..."
    sudo rm -f /usr/share/applications/TaskFlow.desktop
else
    echo "Le raccourci TaskFlow n'a pas été trouvé."
fi

# Supprimer les volumes associés
echo "Suppression des volumes Docker liés..."
docker volume prune --force

# Supprimer les données Docker liées uniquement à ce projet
echo "Nettoyage des images de construction Docker inutilisées..."
docker image prune --filter "label=project=TaskFlow" --force

# Instructions finales
echo "Désinstallation terminée. TaskFlow a été complètement supprimé."
