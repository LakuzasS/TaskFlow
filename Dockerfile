# Utiliser Miniconda comme base
FROM continuumio/miniconda3:latest

# Définir le répertoire de travail
WORKDIR /app

# Copier tous les fichiers dans le conteneur
COPY . .

# Mettre à jour Conda et créer l'environnement Conda
RUN conda update -n base -c defaults conda -y && \
    conda env create -f linux-conda.yml && \
    conda clean -a -y

# Activer l'environnement Conda
ENV PATH /opt/conda/envs/TaskFlow/bin:$PATH

# Ajouter /app au PYTHONPATH pour que les modules puissent être trouvés
ENV PYTHONPATH /app

# Installer les dépendances PyQt5 via pip
RUN conda run -n TaskFlow pip install \
    pyqt5==5.15.9 \
    mysql-connector-python==9.1.0 \
    zxcvbn \
    pyotp

# Installer les bibliothèques X11 nécessaires pour afficher PyQt5
RUN apt-get update && apt-get install -y \
    libxcb-xinerama0 \
    libxcb-randr0 \
    libxcb-xtest0 \
    libxkbcommon-x11-0 \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5x11extras5 \
    x11-apps && \
    apt-get clean

# Configurer l'affichage X11
ENV DISPLAY=:0

# Commande par défaut pour exécuter l'application
CMD ["bash", "-c", "cd front_end/authentification && python main.py"]
