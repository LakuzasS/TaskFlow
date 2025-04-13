# TaskFlow

<div align="center">
  <img src="data/logo.png" alt="Logo TaskFlow" width="400">
</div>
<br />
<div align="center">
  <a href="https://github.com/zzendor/SAE502-TaskFlow">
  </a>

  <h3 align="center">TaskFlow</h3>

  <p align="center">
    Une application collaborative de gestion de projets et de tâches.
    <br />
    <a href="https://github.com/zzendor/SAE502-TaskFlow/tree/main/docs/pdf"><strong>Explorez les documents d'installation et d'utilisation </strong></a>
    <br />
    <a href="https://github.com/zzendor/SAE502-TaskFlow/tree/main/docs/sphinx/build/html"><strong>Documentation du code </strong></a>
     <br />
    Pour consulter la documentation du code, clonez ce dépôt sur votre poste local, puis ouvrez le fichier suivant dans votre navigateur :
    `SAE502-TaskFlow/docs/sphinx/build/html/index.html`. Cela vous permettra d'explorer en détail les classes, fonctions et modules utilisés dans le projet.
    <br />
  </p>
</div>

---

## À propos du projet

TaskFlow est une application collaborative de gestion de projets et de tâches, développée en Python. Elle a été créée dans le cadre d'une **SAE** (Situation d'Apprentissage et d'Évaluation) par un groupe de 8 étudiants, dans le but de fournir une solution simple et efficace pour la gestion de projets en équipe. L'application permet de créer et de gérer des projets, d'attribuer des tâches, de suivre les progrès et de recevoir des rappels pour ne jamais manquer une échéance. Grâce à son interface conviviale et à ses fonctionnalités intelligentes, TaskFlow facilite l'organisation et la collaboration au sein des équipes de travail.

### Fonctionnalités principales

- **Gestion des projets** : Créez et gérez vos projets facilement.
- **Suivi des tâches** : Attribuez des tâches et sous-tâches aux membres de l'équipe.
- **Interface utilisateur intuitive** : Une expérience fluide pour tous les utilisateurs.

---

## Équipe et Rôles

Voici la liste des membres de l'équipe ayant contribué au projet et leurs rôles respectifs :

- **Hugo Grigord** : Chef de Projet
- **Kevin Lang** : SCRUM Master
- **Swann Marcuzzi** : Développeur
- **Haris UKA** : Développeur
- **Jules Goetz** : Développeur
- **Zacharie Assens** : Développeur
- **Maxime Brodin** : Développeur
- **Marius Breinlen** : Développeur

---

## Outils utilisés

Les outils suivants ont été utilisés dans le cadre de ce projet :

- **GitHub** : Gestion des versions et collaboration.
- **Trello** : Gestion des tâches et organisation du projet.
- **PyTest** : Tests unitaires pour garantir la qualité du code.
- **Sphinx** : Génération de la documentation technique.
- **Docker** : Conteneurisation de l'application pour simplifier son déploiement.
- **Conda** : Gestionnaire d'environnements pour les dépendances Python.
- **pre-commit** : Exécute automatiquement des outils de vérification et de formatage lors des commits pour garantir la qualité du code.
- **ruff** : Linter et formateur de code Python rapide et efficace.
- **mypy** : Vérification statique des types pour renforcer la robustesse et la maintenabilité du code.

---

## Configuration des outils supplémentaires

### **pre-commit**

`pre-commit` est configuré pour exécuter des vérifications automatiques (comme le linting avec `ruff` ou la vérification des types avec `mypy`) avant chaque commit. Pour activer cet outil, exécutez les commandes suivantes :

```bash
pip install pre-commit
pre-commit install
