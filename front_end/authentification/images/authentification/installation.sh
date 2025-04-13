
#!/bin/bash

# === Configuration de l'application TaskFlow ===

# Vérification des permissions Docker
echo "Vérification des permissions pour Docker..."
if [ ! -w /var/run/docker.sock ]; then
    echo "Les permissions Docker sont insuffisantes. Ajout des permissions..."
    sudo chmod 666 /var/run/docker.sock
fi

# Activation de X11 pour Docker
echo "Activation de X11 pour le conteneur Docker..."
xhost +local:

# Déplacement vers le dossier de l'application
echo "Accès au répertoire de l'application..."
cd "/home/vboxuser/Projet/save ok sans ui/SAE502-TaskFlow-test-docker/SAE502-TaskFlow-test-docker" || {
    echo "Erreur : Impossible d'accéder au répertoire."
    exit 1
}

# Reconstruction de l'image Docker
echo "Reconstruction de l'image Docker..."
docker-compose down --volumes --remove-orphans
docker-compose build

# Vérification des raccourcis et création si nécessaire
echo "Création du raccourci TaskFlow dans les applications..."
cat <<EOF > "TaskFlow.desktop"
[Desktop Entry]
Type=Application
Name=TaskFlow
Comment=Lance l'application TaskFlow via Docker
Exec=gnome-terminal -- bash -c "xhost +local: && cd '/home/vboxuser/Projet/save ok sans ui/SAE502-TaskFlow-test-docker/SAE502-TaskFlow-test-docker' && docker-compose up; echo 'Appuyez sur une touche pour fermer...' && read -n 1"
Icon=/home/vboxuser/Projet/save\ ok\ sans\ ui/SAE502-TaskFlow-test-docker/SAE502-TaskFlow-test-docker/front_end/authentification/images/authentification/logo.png
Terminal=false
EOF

# Déplacement du raccourci vers les applications
sudo mv TaskFlow.desktop /usr/share/applications/
sudo chmod +x /usr/share/applications/TaskFlow.desktop

# Message de confirmation
echo "L'installation est terminée ! Vous pouvez lancer TaskFlow depuis le menu Applications."
echo "Pour tester immédiatement, nous lançons le conteneur..."
