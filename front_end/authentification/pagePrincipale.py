from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QMessageBox,
    QLabel,
    QVBoxLayout,
    QInputDialog,
    QListWidgetItem,
    QScrollArea,
    QWidget,
)
from backend.db_api import DB_API
import datetime
from typing import Optional


class InviteUsersDialog(QtWidgets.QDialog):
    """
    Cette classe gère le dialogue d'invitation des utilisateurs dans un projet.

    Cette classe renvoie une boîte de dialogue permettant de sélectionner des
    utilisateurs et de leur attribuer des droits.

    :param parent: Widget parent (optionnel)
    :param deny: Bool indiquant si l'accès doit être refusé
    :return: Boîte de dialogue d'invitation
    :raise: Exception si l'initialisation échoue

    Exemple:
    >>> dialog = InviteUsersDialog(parent=None)
    >>> if dialog.exec_():
    >>>     users = dialog.get_selected_users()
    """

    def __init__(self, parent=None, deny=False):
        super().__init__(parent)
        self.deny = deny
        self.setWindowTitle("Inviter des utilisateurs")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """
        Configure l'interface utilisateur du dialogue d'invitation.

        Cette fonction initialise tous les éléments de l'interface du dialogue
        d'invitation des utilisateurs.

        :param self: Instance de la classe
        :return: None
        :raise: Exception si l'initialisation des composants échoue

        Exemple:
        >>> dialog = InviteUsersDialog()
        >>> dialog.setup_ui()
        """
        layout = QVBoxLayout(self)
        if self.deny:
            error_label = QLabel(
                "Vous n'avez pas les permissions requises "
                "pour inviter des utilisateurs dans ce projet."
            )
            error_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
            layout.addWidget(error_label)

            close_button = QtWidgets.QPushButton("Fermer")
            close_button.clicked.connect(self.reject)
            layout.addWidget(close_button)
        else:
            # Liste des utilisateurs
            self.user_list = QtWidgets.QListWidget(self)
            self.user_list.setSelectionMode(QtWidgets.QListWidget.MultiSelection)
            layout.addWidget(QLabel("Sélectionnez les utilisateurs à inviter:"))
            layout.addWidget(self.user_list)

            # Droits d'accès
            rights_layout = QtWidgets.QHBoxLayout()
            self.rights_combo = QtWidgets.QComboBox(self)
            self.rights_combo.addItems(["lecture", "lecture + ecriture", "administrateur"])
            self.map_rights_combo = {"lecture": 0, "lecture + ecriture": 1, "administrateur": 2}
            rights_layout.addWidget(QtWidgets.QLabel("Droits d'accès:"))
            rights_layout.addWidget(self.rights_combo)
            layout.addLayout(rights_layout)

            # Boutons
            button_layout = QtWidgets.QHBoxLayout()
            self.invite_button = QtWidgets.QPushButton("Inviter")
            self.invite_button.setStyleSheet("""
                QPushButton {
                    background-color: #0066cc;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0080ff;
                }
            """)
            self.cancel_button = QtWidgets.QPushButton("Annuler")

            button_layout.addWidget(self.invite_button)
            button_layout.addWidget(self.cancel_button)
            layout.addLayout(button_layout)

            # Connexions
            self.invite_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

    def load_users(self, users):
        """
        Charge la liste des utilisateurs disponibles dans le dialogue.

        Cette fonction met à jour la liste des utilisateurs pouvant être invités
        dans le projet.

        :param users: Liste des utilisateurs à afficher
        :return: None
        :raise: Exception si le chargement échoue

        Exemple:
        >>> dialog = InviteUsersDialog()
        >>> dialog.load_users(['user1@email.com', 'user2@email.com'])
        """
        self.user_list.clear()
        for user in users:
            item = QListWidgetItem(f"{user}")
            item.setData(QtCore.Qt.UserRole, user)
            self.user_list.addItem(item)

    def get_selected_users(self):
        """
        Récupère la liste des utilisateurs sélectionnés avec leurs droits.

        Cette fonction renvoie un tuple contenant les utilisateurs sélectionnés
        et les droits qui leur ont été attribués.

        :return: Liste de tuples (user, permission)
        :raise: Exception si la récupération échoue

        Exemple:
        >>> dialog = InviteUsersDialog()
        >>> selected = dialog.get_selected_users()
        >>> if selected:
        >>>     print(f"Users selected: {selected}")
        """
        selected_items = self.user_list.selectedItems()
        users = []
        rights = self.rights_combo.currentText()
        for item in selected_items:
            user = item.data(QtCore.Qt.UserRole)
            users.append((user, self.map_rights_combo.get(rights)))
        return users


class Ui_MainWindow(object):
    def __init__(self):
        self.current_user = None
        self.user_id = None

    def setupUi(self, MainWindow):
        """
        Configure l'interface utilisateur de la fenêtre principale.

        Cette méthode configure la fenêtre principale, y compris sa taille, son icône,
        le widget central, la mise en page, les onglets et
        les connexions pour divers boutons et widgets.

        :param MainWindow: L'objet de la fenêtre principale à configurer.
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("images/authentification/logo_alternatif.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        MainWindow.setWindowIcon(icon)

        # Chargement du fichier de style
        try:
            with open("style.qss", "r") as f:
                style = f.read()
                MainWindow.setStyleSheet(style)
        except FileNotFoundError:
            pass

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.layout.setObjectName("layout")

        # Onglets : Projets, Tâches, Compte
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.project_tab = QtWidgets.QWidget()
        self.task_tab = QtWidgets.QWidget()
        self.account_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.project_tab, "Projets")
        self.tabs.addTab(self.task_tab, "Tâches")
        self.tabs.addTab(self.account_tab, "Compte")
        self.layout.addWidget(self.tabs)

        # Setup des onglets
        self._setup_project_tab()
        self._setup_task_tab()
        self._setup_account_tab()

        MainWindow.setCentralWidget(self.centralwidget)

        # Connexions
        self.add_project_button.clicked.connect(self.add_project)
        self.project_list_widget.currentRowChanged.connect(self.project_clicked)
        self.add_task_button.clicked.connect(self.add_task)
        self.add_subtask_button.clicked.connect(self.add_subtask)
        self.delete_task_button.clicked.connect(self.delete_task)
        self.complete_task_button.clicked.connect(self.mark_completed)
        self.uncomplete_task_button.clicked.connect(self.mark_uncompleted)
        self.modify_task_button.clicked.connect(self.modify_task)
        self.invite_users_button.clicked.connect(self.show_invite_dialog)
        self.tree.itemSelectionChanged.connect(self.update_subtask_availability)
        self.delete_account_button.clicked.connect(self.delete_account)
        self.delete_project_button.clicked.connect(self.delete_project)
        self.accept_project_button.clicked.connect(self.accept_project)
        self.refuse_project_button.clicked.connect(self.refuse_project)

        self.retranslateUi(MainWindow)

    def _setup_account_tab(self):
        """
        Configure l'onglet du compte utilisateur.

        Cette méthode initialise et configure tous les éléments de l'interface utilisateur
        pour l'onglet de gestion du compte, y compris les informations de l'utilisateur
        et les boutons d'action.

        :param self: Instance de la classe
        :return: None
        """
        layout = QtWidgets.QVBoxLayout(self.account_tab)

        # Groupe pour les informations du compte
        account_group = QtWidgets.QGroupBox("Informations du Compte")
        account_group.setStyleSheet("font-size: 16px;")
        account_layout = QtWidgets.QVBoxLayout(account_group)

        # Affichage du logo (si disponible)
        logo_label = QtWidgets.QLabel()
        try:
            pixmap = QtGui.QPixmap("images/authentification/logo_alternatif.png")
            pixmap = pixmap.scaledToWidth(150, QtCore.Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(QtCore.Qt.AlignCenter)
        except Exception as e:
            print(f"Impossible de charger le logo : {e}")
        account_layout.addWidget(logo_label)

        # Étiquettes pour les informations de l'utilisateur
        self.email_label = QtWidgets.QLabel("Email: ")
        self.email_label.setObjectName("email_label")
        self.email_label.setStyleSheet("font-size: 14px;")
        account_layout.addWidget(self.email_label)

        self.username_label = QtWidgets.QLabel("Nom d'utilisateur : Inconnu")
        self.username_label.setStyleSheet("font-size: 14px;")
        account_layout.addWidget(self.username_label)

        # Bouton de déconnexion
        deconnexion_button = QtWidgets.QPushButton("Se déconnecter")
        deconnexion_button.setObjectName("deconnexion_button")
        deconnexion_button.setStyleSheet(
            "background-color: red; color: white; font-weight: bold; font-size:14px;"
        )
        deconnexion_button.clicked.connect(self.deconnexion)
        account_layout.addWidget(deconnexion_button)

        # Bouton pour supprimer le compte
        self.delete_account_button = QtWidgets.QPushButton("Supprimer mon compte")
        self.delete_account_button.setStyleSheet(
            "background-color: #a40000; color: white; font-weight: bold; font-size:14px;"
        )
        account_layout.addWidget(self.delete_account_button)

        account_layout.addStretch(1)
        layout.addWidget(account_group)

    def _setup_project_tab(self):
        """
        Configure l'onglet de gestion des projets.

        Met en place :
        - Liste des projets actifs
        - Liste des projets en attente
        - Boutons d'action (Ajouter, Supprimer, etc.)
        - Mise en page et style
        """
        self.main_project_layout = QtWidgets.QHBoxLayout(self.project_tab)

        # Partie gauche - Projets actifs
        self.left_widget = QtWidgets.QWidget()
        self.left_layout = QtWidgets.QVBoxLayout(self.left_widget)

        self.project_label = QtWidgets.QLabel("Projets Actifs")
        self.project_label.setStyleSheet("font-size: 16px;")
        self.left_layout.addWidget(self.project_label)

        self.project_list_widget = QtWidgets.QListWidget()
        self.project_list_widget.setStyleSheet("font-size: 14px;")
        self.left_layout.addWidget(self.project_list_widget)

        self.project_buttons_frame = QtWidgets.QFrame()
        self.project_buttons_layout = QtWidgets.QHBoxLayout(self.project_buttons_frame)

        self.add_project_button = QtWidgets.QPushButton("Ajouter un Projet")
        self.delete_project_button = QtWidgets.QPushButton("Supprimer le Projet")
        self.delete_project_button.setStyleSheet(
            "background-color: #a40000; color: white; font-size: 14px;"
        )
        self.project_buttons_layout.addWidget(self.add_project_button)
        self.project_buttons_layout.addWidget(self.delete_project_button)
        self.left_layout.addWidget(self.project_buttons_frame)

        # Partie droite - Projets en attente
        self.right_widget = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout(self.right_widget)

        self.pending_label = QtWidgets.QLabel("Projets en Attente")
        self.pending_label.setStyleSheet("font-size: 16px;")
        self.right_layout.addWidget(self.pending_label)

        self.pending_project = QtWidgets.QListWidget()
        self.pending_project.setStyleSheet("font-size: 14px;")
        self.right_layout.addWidget(self.pending_project)

        self.pending_buttons_frame = QtWidgets.QFrame()
        self.pending_buttons_layout = QtWidgets.QHBoxLayout(self.pending_buttons_frame)

        self.accept_project_button = QtWidgets.QPushButton("Accepter Projet")
        self.refuse_project_button = QtWidgets.QPushButton("Refuser Projet")
        self.pending_buttons_layout.addWidget(self.accept_project_button)
        self.pending_buttons_layout.addWidget(self.refuse_project_button)
        self.right_layout.addWidget(self.pending_buttons_frame)

        self.main_project_layout.addWidget(self.left_widget)
        self.main_project_layout.addWidget(self.right_widget)

    def _setup_task_tab(self):
        """
        Configure l'onglet des tâches.

        Cette méthode initialise et configure tous les éléments de l'interface utilisateur
        pour l'onglet de gestion des tâches, y compris les étiquettes, les listes et les boutons.

        :param self: Instance de la classe
        :return: None
        """
        # Layout principal pour l'onglet des tâches
        self.task_layout = QtWidgets.QHBoxLayout(self.task_tab)

        # Partie gauche : Liste des tâches
        self.task_left_layout = QtWidgets.QVBoxLayout()

        self.title_label = QtWidgets.QLabel(self.task_tab)
        self.title_label.setText("Gestionnaire de Tâches")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setObjectName("title_label")
        self.title_label.setStyleSheet("font-size: 18px;")
        self.task_left_layout.addWidget(self.title_label)

        self.current_project_label = QtWidgets.QLabel(self.task_tab)
        self.current_project_label.setAlignment(QtCore.Qt.AlignCenter)
        self.current_project_label.setObjectName("current_project_label")
        self.current_project_label.setStyleSheet("font-size: 16px;")
        self.task_left_layout.addWidget(self.current_project_label)

        self.tree = QtWidgets.QTreeWidget(self.task_tab)
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(
            ["Tâche", "Date", "Commentaire", "Importance", "Utilisateurs assignés"]
        )
        self.tree.setStyleSheet("font-size: 14px;")
        self.task_left_layout.addWidget(self.tree)

        for i in range(4):
            self.tree.header().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        # Boutons de gestion des tâches
        self.button_layout = QtWidgets.QHBoxLayout()
        self.add_task_button = QtWidgets.QPushButton("Ajouter une Tâche", self.task_tab)
        self.add_task_button.setObjectName("add_task_button")  # Important

        self.add_subtask_button = QtWidgets.QPushButton("Ajouter Sous-Tâche", self.task_tab)
        self.add_subtask_button.setObjectName("add_subtask_button")  # Important

        self.delete_task_button = QtWidgets.QPushButton("Supprimer", self.task_tab)
        self.delete_task_button.setObjectName("delete_task_button")  # Important

        self.complete_task_button = QtWidgets.QPushButton("Marquer comme terminé", self.task_tab)
        self.complete_task_button.setObjectName("complete_task_button")  # Important

        self.uncomplete_task_button = QtWidgets.QPushButton(
            "Marquer comme non terminé", self.task_tab
        )
        self.uncomplete_task_button.setObjectName("uncomplete_task_button")  # Important

        self.invite_users_button = QtWidgets.QPushButton("Inviter des utilisateurs", self.task_tab)
        self.invite_users_button.setObjectName("invite_users_button")  # Important

        self.modify_task_button = QtWidgets.QPushButton("Modifier", self.task_tab)
        self.modify_task_button.setObjectName("modify_task_button")  # Important

        # Ajouter les boutons au layout
        self.button_layout.addWidget(self.add_task_button)
        self.button_layout.addWidget(self.add_subtask_button)
        self.button_layout.addWidget(self.delete_task_button)
        self.button_layout.addWidget(self.complete_task_button)
        self.button_layout.addWidget(self.uncomplete_task_button)
        self.button_layout.addWidget(self.invite_users_button)
        self.button_layout.addWidget(self.modify_task_button)

        self.task_left_layout.addLayout(self.button_layout)

        # Ajout de la partie gauche dans le layout principal
        self.task_layout.addLayout(self.task_left_layout)

        # Partie droite : Liste des utilisateurs assignés
        self.user_right_layout = QtWidgets.QVBoxLayout()

        self.user_title_label = QtWidgets.QLabel("Utilisateurs dans le projet")
        self.user_title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        self.user_right_layout.addWidget(self.user_title_label)

        # Création de la QScrollArea pour afficher les utilisateurs
        self.users_scroll_area = QScrollArea(self.task_tab)
        self.users_scroll_area.setWidgetResizable(True)
        self.users_scroll_area.setStyleSheet("background-color: #f9f9f9; border: none;")

        # Widget contenant les utilisateurs
        self.users_container = QWidget()
        self.users_container_layout = QVBoxLayout(self.users_container)
        self.users_container_layout.setContentsMargins(0, 0, 0, 0)
        self.users_container_layout.setSpacing(10)

        # Étendre la zone des utilisateurs
        self.users_scroll_area.setWidget(self.users_container)
        self.user_right_layout.addWidget(self.users_scroll_area)

        # Ajout de la partie droite dans le layout principal
        self.task_layout.addLayout(self.user_right_layout)

        # Ajouter un stretch qui poussera les widgets vers le haut
        self.user_right_layout.addStretch()

        # Ajout de la partie droite dans le layout principal
        self.task_layout.addLayout(self.user_right_layout)

    def set_current_user(self, email):
        """
        Définit l'utilisateur actuel en fonction de l'email
        fourni et met à jour l'interface utilisateur en conséquence.

        Cette méthode met à jour les informations de l'utilisateur
        actuel, telles que l'email, le nom d'utilisateur et le rôle,
        et charge les projets associés à cet utilisateur.

        :param email: L'email de l'utilisateur actuel.
        :return: None
        """
        self.current_user = email
        self.user_id = DB_API.get_userID_by_email(email)[0]
        self.email_label.setText(f"Email: {email}")
        # Récupération du username et du rôle depuis la DB
        try:
            # Vérifiez que la méthode get_user_info existe dans db_api.
            _user_info = DB_API.get_all_infos_from_email(email)
            user_info = {
                "userid": _user_info[0],
                "username": _user_info[1],
                "password": _user_info[2],
                "email": _user_info[3],
                "is_google_user": _user_info[4],
                "2fa": _user_info[5],
            }
            self.username_label.setText(
                f"Nom d'utilisateur : {user_info.get('username', 'Inconnu')}"
            )
            DB_API.set_user_status(self.user_id, 1)
        except Exception:
            self.username_label.setText("Nom d'utilisateur : Inconnu")

        self.load_projects()

    def deconnexion(self):
        """
        Déconnecte l'utilisateur actuel et retourne à la fenêtre d'authentification.

        Cette méthode ferme toutes les fenêtres ouvertes,
        met à jour le statut de l'utilisateur dans la base de données
        et affiche la fenêtre d'authentification.

        :return: None
        """
        from authentification import MainWindow as AuthMainWindow

        try:
            QMessageBox.information(None, "Déconnexion", "Vous êtes maintenant déconnecté.")
            QtWidgets.QApplication.closeAllWindows()

            self.auth_window = QtWidgets.QMainWindow()
            self.auth_ui = AuthMainWindow()
            self.auth_ui.setupUi(self.auth_window)
            self.auth_window.show()
            DB_API.set_user_status(self.user_id, 0)

            self.user_id = None
            self.current_user = None
        except Exception as e:
            print(e)

    def delete_account(self):
        """
        Supprime le compte de l'utilisateur actuel après confirmation.

        Cette méthode demande une confirmation à l'utilisateur
        avant de supprimer son compte de la base de données.
        Si la suppression est réussie, l'utilisateur est déconnecté
        et la fenêtre d'authentification est affichée.

        :return: None
        """
        try:
            # Demander confirmation avant de supprimer le compte
            reponse = QMessageBox.question(
                None,
                "Supprimer le compte",
                "Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reponse == QMessageBox.Yes:
                # Récupérer l'ID de l'utilisateur à partir de l'email
                user_id = DB_API.get_userID_by_email(self.current_user)
                if isinstance(user_id, Exception) or not user_id:
                    QMessageBox.critical(
                        None, "Erreur", "Impossible de récupérer l'ID de l'utilisateur."
                    )
                    return

                # Supprimer l'utilisateur et ses dépendances
                DB_API.delete_user_status(user_id[0])
                err = DB_API.delete_user(
                    user_id[0]
                )  # Appelle directement la fonction existante dans db_api.py
                if err is None:  # Si aucune erreur, suppression réussie
                    QMessageBox.information(None, "Succès", "Compte supprimé avec succès.")

                    # Fermer toutes les fenêtres et revenir à la fenêtre d'authentification
                    QtWidgets.QApplication.closeAllWindows()
                    from authentification import Ui_MainWindow as AuthMainWindow

                    self.auth_window = QtWidgets.QMainWindow()
                    self.auth_ui = AuthMainWindow()
                    self.auth_ui.setupUi(self.auth_window)
                    self.auth_window.show()
                    self.user_id = None
                    self.current_user = None
                else:
                    # Gérer les erreurs de suppression
                    QMessageBox.warning(
                        None, "Erreur", f"Impossible de supprimer le compte : {err}"
                    )
        except Exception as e:
            print(e)

    def add_project(self):
        """
        Ajoute un nouveau projet après avoir obtenu le nom du projet de l'utilisateur.

        Cette méthode affiche une boîte de dialogue pour
        que l'utilisateur entre le nom du projet.
        Si le projet n'existe pas déjà, il est ajouté à
        la base de données et l'utilisateur est ajouté au projet.

        :return: None
        """
        try:
            project_name, ok = QInputDialog.getText(None, "Nouveau Projet", "Nom du projet :")
            if not ok or not project_name.strip():
                return
            existant = DB_API.check_projects(project_name)
            if existant:
                return
            project_id = DB_API.add_project(project_name)
            permission = 2
            joined = 2
            DB_API.add_user_to_group(project_id, self.user_id, permission, joined)
            self.load_projects()
        except Exception as e:
            print(e)

    def load_projects(self):
        """
        Charge les projets associés à l'utilisateur actuel et met à jour l'interface utilisateur.

        Cette méthode récupère les projets actifs et en
        attente de l'utilisateur depuis la base de données
        et les affiche dans les listes correspondantes.

        :return: None
        """
        self.project_list_widget.clear()
        self.pending_project.clear()
        try:
            projects = DB_API.get_projects_by_user_id(self.user_id)
            if projects:
                for project in projects:
                    project_id, project_name, joined = project
                    if joined == 2:
                        self.project_list_widget.addItem(f"{project_name}")
            pending_project = self.get_invitation(user_id=self.user_id, only_pending=True)
            if pending_project:
                for p_project in pending_project:
                    project_id, project_name, permission, joined = p_project
                    self.pending_project.addItem(f"{project_name}")

        except Exception as e:
            QMessageBox.warning(None, "Erreur", f"Impossible de charger les projets : {e!s}")

    def project_clicked(self):
        """
        Gère l'événement lorsqu'un projet est cliqué dans la liste des projets.

        Cette méthode met à jour l'interface utilisateur
        pour afficher les tâches et les utilisateurs
        associés au projet sélectionné.

        :return: None
        """
        project_index = self.project_list_widget.currentRow()
        try:
            if project_index >= 0:
                project_name_with_details = self.project_list_widget.item(project_index).text()
                project_name = project_name_with_details.split(" (")[0]
                self.current_project = project_name
                self.current_project_label.setText(f"Projet sélectionné : {project_name}")
                self.tabs.setCurrentWidget(self.task_tab)
                self.load_tasks_for_project(project_name)
                self.load_users_for_project(project_name)
                self.display_users_in_project()
        except Exception as e:
            print(e)

    def display_users_in_project(self):
        """
        Affiche les utilisateurs du projet actuel et leur statut en
        ligne dans une nouvelle section de l'interface.

        Cette méthode crée une section dans l'onglet des tâches pour
        afficher les utilisateurs du projet actuel,
        ainsi que leur statut en ligne. Elle met également en place
        un minuteur pour mettre à jour périodiquement
        le statut des utilisateurs.

        :return: None
        """
        if not hasattr(self, "current_project") or not self.current_project:
            return

        try:
            # Vérifiez si la zone de défilement pour les utilisateurs existe déjà
            if not hasattr(self, "users_scroll_area"):
                # Widget principal pour la section des utilisateurs
                self.users_widget = QWidget(self.task_tab)
                self.users_widget.setStyleSheet("background-color: #f9f9f9;")
                users_layout = QVBoxLayout(self.users_widget)

                # Titre pour la liste des utilisateurs
                title_label = QLabel("Utilisateurs dans le projet")
                title_label.setStyleSheet(
                    "font-size: 16px; font-weight: bold; margin: 10px; color: #333;"
                )
                users_layout.addWidget(title_label)

                # Création de la zone de défilement pour afficher les utilisateurs
                self.users_scroll_area = QScrollArea(self.task_tab)
                self.users_scroll_area.setWidgetResizable(True)
                self.users_scroll_area.setStyleSheet("background-color: #ffffff; border: none;")
                self.users_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

                # Widget conteneur pour les utilisateurs
                self.users_container = QWidget()
                self.users_container_layout = QVBoxLayout(self.users_container)
                self.users_container_layout.setContentsMargins(0, 0, 0, 0)
                self.users_container_layout.setSpacing(10)
                self.users_scroll_area.setWidget(self.users_container)

                # Étendre la zone de défilement
                users_layout.addWidget(self.users_scroll_area)
                self.user_right_layout.addWidget(self.users_widget)

            # Effacer les widgets existants avant de recharger
            for i in reversed(range(self.users_container_layout.count())):
                item = self.users_container_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setParent(None)

            # Récupérer les utilisateurs et leurs statuts
            project_id = DB_API.get_project_id_by_project_name(self.current_project)[0]
            users_in_project = DB_API.get_users_in_project_by_project_id(project_id)
            _user_status = DB_API.get_all_status()
            user_status = {item[0]: item[1] for item in _user_status}

            # Permissions actuelles de l'utilisateur
            perms = next(user[2] for user in users_in_project if user[0] == self.user_id)

            # Ajouter chaque utilisateur à la liste
            for user in users_in_project:
                user_id = user[0]
                username = user[1]
                is_online = user_status.get(user_id, False)
                user_widget = UserStatusWidget(
                    username=username,
                    user_id=user_id,
                    is_online=is_online,
                    is_admin=True if perms == 2 else False,
                    project_id=project_id,
                    current_user_role=user[2],
                )
                self.users_container_layout.addWidget(user_widget)

            # Ajouter un espace flexible pour forcer l'extension
            self.users_container_layout.addStretch()

            # Ajuster la taille de la zone des utilisateurs pour qu'elle occupe tout l'espace
            self.users_scroll_area.setMinimumHeight(500)  # Ajustez cette valeur si nécessaire
            self.users_scroll_area.setMaximumHeight(600)  # Facultatif
            self.users_scroll_area.setMinimumWidth(self.user_right_layout.geometry().width() - 20)

            # Ajuster les proportions entre la zone des utilisateurs et le reste de l'interface
            self.task_layout.setStretch(0, 3)  # 3 parts pour la liste des tâches
            self.task_layout.setStretch(1, 4)  # 4 parts pour la section des utilisateurs

            # Mettre à jour automatiquement le statut des utilisateurs toutes les 30 secondes
            if not hasattr(self, "update_timer"):
                self.update_timer = QTimer()
                self.update_timer.timeout.connect(self.update_users_status)
                self.update_timer.start(30000)  # Mise à jour toutes les 30 secondes

        except Exception as e:
            QMessageBox.critical(
                None, "Erreur", f"Erreur lors de l'affichage des utilisateurs : {e!s}"
            )

    def update_users_status(self):
        """
        Met à jour le statut des utilisateurs périodiquement.

        Cette méthode est appelée périodiquement pour mettre à
        jour le statut en ligne des utilisateurs
        du projet actuel.

        :return: None
        """
        try:
            if hasattr(self, "current_project"):
                self.display_users_in_project()
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statuts : {e}")

    def load_users_for_project(self, project_name):
        """
        Charge les utilisateurs associés au projet spécifié.

        Cette méthode récupère les utilisateurs assignés au projet et les affiche dans les listes
        de l'interface utilisateur.

        :param project_name: Le nom du projet pour lequel charger les utilisateurs.
        :return: None
        """

        try:
            project_id = DB_API.get_project_id_by_project_name(project_name)
            users_in_project = DB_API.get_users_in_project_by_project_id(project_id[0])  # noqa
            # for user in users_in_project:
            #     self.assign_user_dropdown.addItem(user[1])
        except Exception as e:
            QMessageBox.warning(
                None, "Erreur", f"Impossible de charger les utilisateurs du projet : {e!s}"
            )

    def add_selected_user(self):
        """
        Ajoute l'utilisateur sélectionné à la liste des
        utilisateurs assignés.

        Cette méthode ajoute l'utilisateur sélectionné dans
        le menu déroulant à la liste des utilisateurs
        assignés à la tâche ou au projet.

        :return: None
        """
        selected_user = self.assign_user_dropdown.currentText().strip()
        try:
            if selected_user and not self.is_user_already_assigned(selected_user):
                self.assigned_users_list.addItem(selected_user)
        except Exception as e:
            print(e)

    def remove_selected_user_from_list(self):
        """
        Supprime l'utilisateur sélectionné de la liste des utilisateurs assignés.

        Cette méthode supprime l'utilisateur sélectionné dans la liste des utilisateurs assignés
        à la tâche ou au projet.

        :return: None
        """
        items = self.assigned_users_list.selectedItems()
        try:
            if items:
                for item in items:
                    self.assigned_users_list.takeItem(self.assigned_users_list.row(item))
        except Exception as e:
            print(e)

    def is_user_already_assigned(self, username: str) -> bool:
        """
        Vérifie si un utilisateur est déjà assigné.

        Cette méthode vérifie si l'utilisateur spécifié est
        déjà présent dans la liste des utilisateurs
        assignés à la tâche ou au projet.

        :param username: Le nom d'utilisateur à vérifier.
        :return: True si l'utilisateur est déjà assigné, False sinon.
        """
        try:
            for i in range(self.assigned_users_list.count()):
                if self.assigned_users_list.item(i).text() == username:
                    return True
            return False
        except Exception as e:
            print(e)

    def add_task(self):
        """
        Ajoute une nouvelle tâche au projet actuel.

        Cette méthode affiche une boîte de dialogue pour que
        l'utilisateur entre les détails de la tâche.
        Si la tâche est validée, elle est ajoutée à la base
        de données et à l'interface utilisateur.

        :return: None
        """
        try:
            if not self.current_project:
                QMessageBox.warning(None, "Erreur", "Veuillez sélectionner un projet.")
                return

            project_id = DB_API.get_project_id_by_project_name(self.current_project)
            permission = DB_API.get_user_permission(project_id[0], self.user_id)

            if permission[0] < 1:
                QMessageBox.warning(
                    None,
                    "Permission insuffisante",
                    "Vous n'avez pas la permission pour ajouter cette tâche.",
                )
                return
        except Exception as e:
            print(e)

        # Récupération des utilisateurs du projet
        try:
            users_in_project = DB_API.get_users_in_project_by_project_id(project_id[0])
            users = [user[1] for user in users_in_project]
        except Exception as e:
            QMessageBox.warning(
                None, "Erreur", f"Impossible de charger les utilisateurs du projet : {e!s}"
            )
            return

        # Création et affichage du dialogue
        dialog = TaskDialog(self.task_tab, users)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            form_data = dialog.get_form_data()

            if not form_data["title"]:
                QMessageBox.warning(None, "Erreur", "Veuillez entrer une tâche.")
                return

            if not form_data["assigned_users"]:
                QMessageBox.warning(None, "Erreur", "Veuillez assigner au moins un utilisateur.")
                return

            try:
                task_projectID = DB_API.add_task_group()
                task_info_id = DB_API.add_task_info(
                    status=0,
                    priority=form_data["priority"],
                    title=form_data["title"],
                    description=form_data["comment"],
                    dead_line=form_data["date"],
                    covered=0,
                    assign=task_projectID,
                )

                DB_API.add_task(
                    project_id=project_id[0], task_info_id=task_info_id, user_id=self.user_id
                )

                for username in form_data["assigned_users"]:
                    uid = DB_API.get_user_id_by_username(username)
                    if uid:
                        DB_API.add_user_to_task_group(task_projectID, uid)

                QMessageBox.information(None, "Succès", "Tâche ajoutée avec succès.")
                self.load_tasks_for_project(self.current_project)

            except Exception as e:
                QMessageBox.critical(
                    None,
                    "Erreur",
                    f"Une erreur s'est produite lors de l'ajout de la tâche : {e!s}",
                )

    def load_tasks_for_project(self, project_name):
        """
        Charge les tâches associées au projet spécifié.

        Cette méthode récupère les tâches du projet depuis la base de données et les affiche
        dans l'interface utilisateur.

        :param project_name: Le nom du projet pour lequel charger les tâches.
        :return: None
        """
        self.tree.clear()
        try:
            project_id = DB_API.get_project_id_by_project_name(project_name)
            tasks = DB_API.get_tasks_by_project_id(project_id[0])
            for task in tasks:
                task_item = QtWidgets.QTreeWidgetItem(self.tree)
                task_item.setText(0, task[1])  # Titre de la tâche
                deadline = task[7]
                formatted_date = (
                    deadline.strftime("%d/%m/%Y")
                    if isinstance(deadline, datetime.datetime)
                    else str(deadline)
                )
                task_item.setText(1, formatted_date)  # Date limite
                task_item.setText(2, task[2])  # Description
                priority = task[4]
                priority_text = (
                    "Haute" if priority == 2 else "Moyenne" if priority == 1 else "Basse"
                )
                task_item.setText(3, priority_text)  # Priorité

                assigned_users = DB_API.get_users_in_tasks_group_by_group_id(task[6])
                users_text = (
                    ", ".join([user[1] for user in assigned_users])
                    if assigned_users
                    else "Aucun utilisateur assigné"
                )
                task_item.setText(4, users_text)

                task_item.setData(0, QtCore.Qt.UserRole, task[0])

                if task[3] == 1:  # Statut = 1 signifie "terminé"
                    self.set_task_background(task_item, "green")
                else:
                    self.set_task_background(task_item, "white")

                # Charger les sous-tâches
                subtasks = DB_API.get_subtasks_by_task_id(task[0])
                for subtask in subtasks:
                    subtask_item = QtWidgets.QTreeWidgetItem(task_item)
                    subtask_item.setText(0, subtask[1])  # Titre de la sous-tâche
                    subtask_item.setText(1, subtask[7].strftime("%d/%m/%Y"))  # Date limite
                    subtask_item.setText(2, subtask[2])  # Description
                    subtask_item.setText(
                        3,
                        "Haute" if subtask[4] == 2 else "Moyenne" if subtask[4] == 1 else "Basse",
                    )
                    subtask_item.setData(0, QtCore.Qt.UserRole, subtask[0])  # ID de la sous-tâche

                    # Vérifier le statut en direct et appliquer la couleur verte si terminé
                    if subtask[3] == 1:  # Statut = 1 signifie "terminé"
                        self.set_task_background(subtask_item, "#DFF0D8", is_completed=True)
                    else:
                        self.set_task_background(subtask_item, "white")

            self.tree.setIndentation(20)

            # Mettre à jour les tâches périodiquement en cas de changement de statut
            self.refresh_task_status(project_id[0])

        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Impossible de charger les tâches : {e!s}")

    def set_task_background(self, item, color, is_completed=False):
        """
        Applique un fond coloré à un item.

        Cette méthode applique une couleur de fond à un item de la liste des tâches
        en fonction de son statut.

        :param item: L'item à colorer.
        :param color: La couleur à appliquer.
        :return: None
        """
        try:
            if is_completed:
                # Style pour les tâches terminées
                brush = QtGui.QBrush(QtGui.QColor("#DFF0D8"))  # Couleur de fond verte pâle
                font = QtGui.QFont()
                font.setBold(True)  # Met le texte en gras
                font.setItalic(True)  # Met le texte en italique

                for i in range(item.columnCount()):
                    item.setBackground(i, brush)
                    item.setForeground(
                        i, QtGui.QBrush(QtGui.QColor("#3C763D"))
                    )  # Couleur du texte
                    item.setFont(i, font)
            else:
                # Style par défaut pour les tâches non terminées
                brush = QtGui.QBrush(QtGui.QColor(color))
                for i in range(item.columnCount()):
                    item.setBackground(i, brush)
        except Exception as e:
            print(e)

    def refresh_task_status(self, project_id):
        """
        Rafraîchit périodiquement le statut des tâches et met à jour la couleur.

        Cette méthode est appelée périodiquement pour mettre à jour le statut des tâches
        et leur couleur de fond en fonction de leur statut.

        :param project_id: L'ID du projet pour lequel rafraîchir les tâches.
        :return: None
        """
        tasks = DB_API.get_tasks_by_project_id(project_id)
        try:
            for i in range(self.tree.topLevelItemCount()):
                task_item = self.tree.topLevelItem(i)
                task_id = task_item.data(0, QtCore.Qt.UserRole)
                for task in tasks:
                    if task[0] == task_id:
                        if task[3] == 1:
                            self.set_task_background(task_item, "green")
                        else:
                            self.set_task_background(task_item, "white")  # Couleur par défaut
                        break
        except Exception as e:
            print(e)

        QtCore.QTimer.singleShot(2000, lambda: self.refresh_task_status(project_id))

    def add_subtask(self):
        """
        Ajoute une sous-tâche à la tâche sélectionnée.

        Cette méthode affiche une boîte de dialogue pour que
        l'utilisateur entre les détails de la sous-tâche.
        Si la sous-tâche est validée, elle est ajoutée à la
        base de données et à l'interface utilisateur.

        :return: None
        """
        selected_items = self.tree.selectedItems()
        try:
            if not selected_items:
                QMessageBox.warning(None, "Erreur", "Veuillez sélectionner une tâche parente.")
                return

            project_id = DB_API.get_project_id_by_project_name(self.current_project)
            permission = DB_API.get_user_permission(project_id[0], self.user_id)
            if permission[0] < 1:
                QMessageBox.warning(
                    None,
                    "Permission insuffisante",
                    "Vous n'avez pas la permission pour ajouter cette tâche.",
                )
                return
        except Exception as e:
            print(e)

        # Récupérer les utilisateurs du projet
        users = []
        try:
            users_in_project = DB_API.get_users_in_project_by_project_id(project_id[0])
            users = [user[1] for user in users_in_project]
        except Exception as e:
            QMessageBox.warning(
                None, "Erreur", f"Impossible de charger les utilisateurs du projet : {e!s}"
            )
            return

        parent_item = selected_items[0]

        # Création et affichage du dialogue
        dialog = SubtaskDialog(self.task_tab, users)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            form_data = dialog.get_form_data()

            if not form_data["title"]:
                QMessageBox.warning(None, "Erreur", "Veuillez entrer une sous-tâche.")
                return

            if not form_data["assigned_users"]:
                QMessageBox.warning(None, "Erreur", "Veuillez assigner au moins un utilisateur.")
                return

            try:
                task_id = parent_item.data(0, QtCore.Qt.UserRole)
                if not task_id:
                    raise ValueError("ID de la tâche parente introuvable.")

                task_projectID = DB_API.add_task_group()

                subtask_info_id = DB_API.add_task_info(
                    status=0,
                    priority=form_data["priority"],
                    title=form_data["title"],
                    description=form_data["comment"],
                    dead_line=form_data["date"],
                    covered=0,
                    assign=task_projectID,
                )

                DB_API.add_subtask(task_id=task_id, task_info_id=subtask_info_id)

                for username in form_data["assigned_users"]:
                    user_id = DB_API.get_user_id_by_username(username)
                    if user_id:
                        DB_API.add_user_to_task_group(task_projectID, user_id)

                QMessageBox.information(None, "Succès", "Sous-tâche ajoutée avec succès.")
                self.load_tasks_for_project(self.current_project)

            except Exception as e:
                QMessageBox.critical(
                    None,
                    "Erreur",
                    f"Une erreur s'est produite lors de l'ajout de la sous-tâche : {e!s}",
                )

    def delete_task(self):
        """
        Supprime la tâche sélectionnée.

        Cette méthode demande une confirmation à l'utilisateur avant de supprimer la tâche
        sélectionnée de la base de données et de l'interface utilisateur.

        :return: None
        """
        selected_items = self.tree.selectedItems()
        project_id = DB_API.get_project_id_by_project_name(self.current_project)
        userID = DB_API.get_userID_by_email(self.current_user)
        permission = DB_API.get_user_permission(project_id[0], userID[0])
        try:
            if permission[0] < 1:
                QMessageBox.warning(
                    None,
                    "Permission insuffisante",
                    "Vous n'avez pas la permission pour supprimer cette tâche.",
                )
                return
            if not selected_items:
                QMessageBox.warning(None, "Erreur", "Veuillez sélectionner une tâche à supprimer.")
                return
            for item in selected_items:
                task_id = item.data(0, QtCore.Qt.UserRole)
                DB_API.delete_task(task_id)
                if item.parent():
                    parent = item.parent()
                    parent.removeChild(item)
                else:
                    index = self.tree.indexOfTopLevelItem(item)
                    self.tree.takeTopLevelItem(index)
        except Exception as e:
            print(e)

    def delete_project(self):
        """
        Supprime le projet sélectionné.

        Cette méthode demande une confirmation à l'utilisateur avant de supprimer le projet
        sélectionné de la base de données et de l'interface utilisateur.

        :return: None
        """
        current_item = self.project_list_widget.currentItem()
        try:
            if not current_item:
                QMessageBox.warning(None, "Erreur", "Veuillez sélectionner un projet à supprimer.")
                return

            project_name = current_item.text()

            project_id = DB_API.get_project_id_by_project_name(project_name)
            permission = DB_API.get_user_permission(project_id[0], self.user_id)
            if permission[0] != 2:
                QMessageBox.warning(
                    None,
                    "Permission insuffisante",
                    "Vous n'avez pas la permission de supprimer ce projet.",
                )
                return

            reponse = QMessageBox.question(
                None,
                "Supprimer le projet",
                f"Êtes-vous sûr de vouloir supprimer le projet "
                f"'{project_name}' ? Cette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No,
            )
        except Exception as e:
            print(e)

        if reponse == QMessageBox.Yes:
            DB_API.delete_user_group(project_id[0])
            """
            DB_API.delete_tasks_groups(project_id[0])
            DB_API.delete_tasks_infos(project_id[0])
            DB_API.delete_tasks(project_id[0])
            Faire en sorte que les tâches se suppriment avec le projet
            """
            err = DB_API.delete_project(project_id[0])
            if isinstance(err, Exception):
                print("Erreur lors de la suppression du projet")
                QMessageBox.critical(
                    None, "Erreur", f"Impossible de supprimer le projet : {err!s}"
                )
                return

            self.project_list_widget.takeItem(self.project_list_widget.row(current_item))
            self.current_project = None
            if hasattr(self, "current_project_label"):
                self.current_project_label.setText("Aucun projet sélectionné")
            if hasattr(self, "tree"):
                self.tree.clear()

            QMessageBox.information(None, "Succès", "Le projet a été supprimé avec succès.")

    def modify_task(self):
        """
        Modifie la tâche sélectionnée.

        Cette méthode affiche une boîte de dialogue pour que
        l'utilisateur modifie les détails de la tâche.
        Si la modification est validée, elle est mise à jour
        dans la base de données et dans l'interface utilisateur.

        :return: None
        """
        selected_items = self.tree.selectedItems()
        try:
            if not selected_items:
                QMessageBox.warning(None, "Erreur", "Veuillez sélectionner une tâche à modifier.")
                return

            project_id = DB_API.get_project_id_by_project_name(self.current_project)
            userID = DB_API.get_userID_by_email(self.current_user)
            permission = DB_API.get_user_permission(project_id[0], userID[0])

            if permission[0] < 1:
                QMessageBox.warning(
                    None,
                    "Permission insuffisante",
                    "Vous n'avez pas la permission pour modifier cette tâche.",
                )
                return

            selected_item = selected_items[0]
            parent_item = selected_item.parent()
            is_subtask = bool(parent_item)
            task_id = selected_item.data(0, QtCore.Qt.UserRole)

            if is_subtask:
                task_info = DB_API.get_subtask_info_by_subtask_id(task_id)
                task_info = task_info[0]
                task_infoID = DB_API.get_task_infoID_by_taskID(task_id)
            else:
                task_info = DB_API.get_task_info_by_task_id(task_id)
                task_info = task_info[0]
                task_infoID = DB_API.get_task_infoID_by_taskID(task_id)

            task_group_id = task_info[5]

            assigned_users = DB_API.get_users_in_tasks_group_by_group_id(task_group_id)
            all_users = DB_API.get_users_in_project_by_project_id(project_id[0])

            dialog = TaskEditDialog(
                parent=self.task_tab,
                task_info=task_info,
                assigned_users=assigned_users,
                all_users=all_users,
            )

            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                form_data = dialog.get_form_data()
                DB_API.update_task_title(form_data["title"], task_infoID[0])
                DB_API.update_task_description(form_data["comment"], task_infoID[0])
                DB_API.update_task_priority(form_data["priority"], task_infoID[0])
                DB_API.update_task_date(form_data["date"], task_infoID[0])
                DB_API.delete_users_from_users_tasks_groups(task_group_id)
                added_users = set()
                for username in form_data["assigned_users"]:
                    if username not in added_users:
                        user_id = DB_API.get_user_id_by_username(username)
                        if user_id:
                            DB_API.add_user_to_task_group(task_group_id, user_id)
                            added_users.add(username)

                selected_item.setText(0, form_data["title"])
                selected_item.setText(
                    1,
                    QtCore.QDate.fromString(form_data["date"], "yyyy-MM-dd").toString(
                        "dd/MM/yyyy"
                    ),
                )
                selected_item.setText(2, form_data["comment"])
                selected_item.setText(
                    3,
                    "Haute"
                    if form_data["priority"] == 2
                    else "Moyenne"
                    if form_data["priority"] == 1
                    else "Basse",
                )
                selected_item.setText(4, ", ".join(form_data["assigned_users"]))

                QMessageBox.information(None, "Succès", "Modifications appliquées avec succès.")
        except Exception as e:
            print(e)

    def mark_completed(self):
        """
        Marque la tâche sélectionnée comme terminée.

        Cette méthode met à jour le statut de la tâche sélectionnée dans la base de données
        et dans l'interface utilisateur pour indiquer qu'elle est terminée.

        :return: None
        """
        selected_items = self.tree.selectedItems()
        try:
            if not selected_items:
                QMessageBox.warning(
                    None, "Erreur", "Veuillez sélectionner une tâche à marquer comme terminée."
                )
                return

            project_id = DB_API.get_project_id_by_project_name(self.current_project)
            userID = DB_API.get_userID_by_email(self.current_user)
            permission = DB_API.get_user_permission(project_id[0], userID[0])

            if permission[0] < 1:
                QMessageBox.warning(
                    None,
                    "Permission insuffisante",
                    "Vous n'avez pas la permission pour modifier cette tâche.",
                )
                return

            selected_item = selected_items[0]
            parent_item = selected_item.parent()
            is_subtask = bool(parent_item)
            task_id = selected_item.data(0, QtCore.Qt.UserRole)
            if is_subtask:
                task_info_id = DB_API.get_task_infoID_by_subtaskID(task_id)
            else:
                task_info_id = DB_API.get_task_infoID_by_taskID(task_id)

            if not task_id:
                QMessageBox.warning(
                    None, "Erreur", "L'élément sélectionné ne contient pas un ID de tâche valide."
                )
                return

            if not task_info_id:
                QMessageBox.critical(
                    None,
                    "Erreur",
                    "Impossible de récupérer les informations de la tâche sélectionnée.",
                )
                return
            success = DB_API.update_task_status(int(task_info_id[0]), 1)
            self.load_tasks_for_project(self.current_project)

            if success:
                QMessageBox.information(None, "Succès", "La tâche a été marquée comme terminée.")
            else:
                QMessageBox.critical(
                    None,
                    "Erreur",
                    "Une erreur s'est produite lors de la mise à jour du statut de la tâche.",
                )
                return
        except Exception as e:
            print(e)

    def mark_uncompleted(self):
        """
        Marque la tâche sélectionnée comme non terminée.

        Cette méthode met à jour le statut de la tâche sélectionnée dans la base de données
        et dans l'interface utilisateur pour indiquer qu'elle n'est pas terminée.

        :return: None
        """
        selected_items = self.tree.selectedItems()
        try:
            if not selected_items:
                QMessageBox.warning(
                    None, "Erreur", "Veuillez sélectionner une tâche à marquer comme non terminée."
                )
                return

            project_id = DB_API.get_project_id_by_project_name(self.current_project)
            userID = DB_API.get_userID_by_email(self.current_user)
            permission = DB_API.get_user_permission(project_id[0], userID[0])

            if permission[0] < 1:
                QMessageBox.warning(
                    None,
                    "Permission insuffisante",
                    "Vous n'avez pas la permission pour modifier cette tâche.",
                )
                return

            selected_item = selected_items[0]
            parent_item = selected_item.parent()
            is_subtask = bool(parent_item)
            task_id = selected_item.data(0, QtCore.Qt.UserRole)

            if is_subtask:
                task_info_id = DB_API.get_task_infoID_by_subtaskID(task_id)
            else:
                task_info_id = DB_API.get_task_infoID_by_taskID(task_id)

            if not task_id:
                QMessageBox.warning(
                    None, "Erreur", "L'élément sélectionné ne contient pas un ID de tâche valide."
                )
                return

            if not task_info_id:
                QMessageBox.critical(
                    None,
                    "Erreur",
                    "Impossible de récupérer les informations de la tâche sélectionnée.",
                )
                return

            success = DB_API.update_task_status(int(task_info_id[0]), 0)

            if success:
                QMessageBox.information(
                    None, "Succès", "La tâche a été marquée comme non terminée."
                )

                self.set_task_background(selected_items[0], "white")
                self.load_tasks_for_project(self.current_project)

            else:
                QMessageBox.critical(
                    None,
                    "Erreur",
                    "Une erreur s'est produite lors de la mise à jour du statut de la tâche.",
                )
                return
        except Exception as e:
            print(e)

    def update_subtask_availability(self):
        """
        Met à jour la disponibilité des boutons de sous-tâche en fonction de la sélection actuelle.

        Cette méthode active ou désactive les boutons de sous-tâche en fonction de la sélection
        actuelle dans la liste des tâches.

        :return: None
        """
        selected_items = self.tree.selectedItems()
        try:
            if selected_items:
                self.add_subtask_button.setEnabled(True)
            else:
                self.add_subtask_button.setEnabled(False)
        except Exception as e:
            print(e)

    def retranslateUi(self, MainWindow):
        """
        Retraduit l'interface utilisateur.

        Cette méthode met à jour les textes de l'interface utilisateur en fonction de la langue
        sélectionnée.

        :param MainWindow: L'objet de la fenêtre principale à retraduire.
        :return: None
        """
        try:
            MainWindow.setWindowTitle("TaskFlow")
        except Exception as e:
            print(e)

    def accept_project(self):
        """
        Accepte le projet sélectionné dans la liste des projets en attente.

        Cette méthode met à jour le statut du projet sélectionné pour indiquer que l'utilisateur
        a accepté l'invitation à rejoindre le projet.

        :return: None
        """
        selected_item = self.pending_project.currentItem()
        try:
            if selected_item:
                project = selected_item.text()
                self.project_list_widget.addItem(project)
                self.pending_project.takeItem(self.pending_project.row(selected_item))
                project_id = DB_API.get_project_id_by_project_name(project)[0]
                self.set_invite(project_id=project_id, user_id=self.user_id, joined=True)
        except Exception as e:
            print(e)

    def refuse_project(self):
        """
        Refuse le projet sélectionné dans la liste des projets en attente.

        Cette méthode met à jour le statut du projet sélectionné pour indiquer que l'utilisateur
        a refusé l'invitation à rejoindre le projet.

        :return: None
        """
        selected_item = self.pending_project.currentItem()
        try:
            if selected_item:
                project = selected_item.text()
                self.pending_project.takeItem(self.pending_project.row(selected_item))
                project_id = DB_API.get_project_id_by_project_name(project)[0]
                self.set_invite(project_id=project_id, user_id=self.user_id, joined=False)
        except Exception as e:
            print(e)

    def delete_user(self, username: str, user_id: Optional[int] = None) -> bool:
        """
        Supprime un utilisateur de la base de données en utilisant son username ou son user_id.

        :param username: Le nom d'utilisateur (utilisé si user_id n'est pas fourni).
        :param user_id: L'ID de l'utilisateur (prioritaire sur username si fourni).
        :return: True si la suppression a réussi, False sinon.
        """
        try:
            # Si l'user_id n'est pas fourni, récupérez-le avec le username
            if not user_id:
                user_id = DB_API.get_user_id_by_username(username)
                if user_id is None or isinstance(user_id, Exception):
                    print(
                        f"Erreur : utilisateur '{username}' introuvable "
                        f"ou erreur lors de la recherche."
                    )
                    return False

            # Appeler la méthode de suppression
            result = DB_API.delete_user(user_id)
            if isinstance(result, Exception):
                print(
                    f"Erreur lors de la suppression de l'utilisateur avec "
                    f"l'ID {user_id} : {result}"
                )
                return False

            print(f"Utilisateur avec l'ID {user_id} supprimé avec succès.")
            return True

        except Exception as e:
            print(f"Erreur inattendue lors de la suppression de l'utilisateur : {e}")
            return False

    def send_invitation(self, project_id: int, user_id: int, permission: int):
        """
        Inviter un user dans son projet
        """
        try:
            user_group_id = DB_API.add_user_to_group(
                project_id=project_id, user_id=user_id, permission=permission, joined=False
            )
            if not user_group_id or isinstance(user_group_id, Exception):
                return None
            return user_group_id
        except Exception as e:
            print(e)

    def get_invitation(self, user_id: int, only_pending=False):
        """
        Cette fonction récupere les projets où l'utilisateur est invité

        Si only_pending = True, cela récupere seulement les invitations en attente,
        où il faut que l'utilisateur réponde, sinon la fonction revoie tous les
        projets dont l'utilisateur a accepté l'invitation

        :param user_id: ID de l'utilisateur
        :param only_pending: Récupère seulement les projets en attente
        """
        joined = 2
        try:
            if only_pending:
                joined = 0
            projects = DB_API.get_project_in_users_groups_userid(user_id=user_id)
            if not projects or isinstance(projects, Exception):
                return None
            return [item for item in projects if item[3] == joined]
        except Exception as e:
            print(e)

    def set_invite(self, project_id: int, user_id: int, joined: bool):
        """
        Met à jour le statut d'une invitation de projet.

        Cette méthode met à jour le statut de l'invitation pour
        l'utilisateur spécifié dans la base de données.

        :param project_id: L'ID du projet.
        :param user_id: L'ID de l'utilisateur.
        :param joined: Booléen indiquant si l'invitation est acceptée (True) ou refusée (False).
        :return: None
        """
        try:
            if joined:
                _joined = 2
            else:
                _joined = 1
            err = DB_API.set_invites_status(project_id=project_id, user_id=user_id, joined=_joined)
            if isinstance(err, Exception):
                return
            return
        except Exception as e:
            print(e)

    def get_user_to_invite(self, _list_users: list, _list_users_in_projects: list):
        """
        Affiche le dialogue d'invitation des utilisateurs.

        Cette méthode affiche une boîte de dialogue permettant d'inviter des utilisateurs
        au projet actuel.

        :return: None
        """
        try:
            list_users = [user[1] for user in _list_users]
            list_users_in_projects = [user[1] for user in _list_users_in_projects]
            return [user for user in list_users if user not in list_users_in_projects]
        except Exception as e:
            print(e)

    def show_invite_dialog(self):
        """
        Affiche le dialogue d'invitation des utilisateurs.

        Cette méthode affiche une boîte de dialogue permettant d'inviter des utilisateurs
        au projet actuel.

        :return: None
        """
        project_id = DB_API.get_project_id_by_project_name(self.current_project)[0]
        _list_users = DB_API.get_all_users()
        _list_users_in_projects = DB_API.get_users_in_project_by_project_id(project_id)
        perms = next(user[2] for user in _list_users_in_projects if user[0] == self.user_id)
        try:
            if perms == 2:
                users = self.get_user_to_invite(_list_users, _list_users_in_projects)
                dialog = InviteUsersDialog(self.task_tab)
                dialog.load_users(users)

                if dialog.exec_() == QtWidgets.QDialog.Accepted:
                    selected_users = dialog.get_selected_users()
                    for user, rights in selected_users:
                        user_id = next(u[0] for u in _list_users if u[1] == user)
                        self.send_invitation(project_id, user_id, rights)
            else:
                dialog = InviteUsersDialog(self.task_tab, deny=True)
                dialog.exec_()
        except Exception as e:
            print(e)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        """
        Initialise la classe Ui_MainWindow.

        Cette méthode initialise les valeurs de l'utilisateur actuel et de l'ID utilisateur.
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

    def closeEvent(self, event):
        DB_API.set_user_status(self.user_id, 0)
        event.accept()


class UserRoleDialog(QtWidgets.QDialog):
    """
    Boîte de dialogue pour modifier le rôle d'un utilisateur dans un projet.

    :param username: Le nom d'utilisateur.
    :param user_id: L'ID de l'utilisateur.
    :param project_id: L'ID du projet.
    :param current_user_role: Le rôle actuel de l'utilisateur.
    :param parent: Le parent de la boîte de dialogue (optionnel).
    """

    def __init__(self, username, user_id, project_id, current_user_role, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.project_id = project_id
        self.setWindowTitle("Rôle de l'utilisateur")
        self.map_rights_combo = {"lecture": 0, "lecture + ecriture": 1, "administrateur": 2}
        self.reverse_map_combo = {v: k for k, v in self.map_rights_combo.items()}
        self.username = username
        layout = QtWidgets.QFormLayout(self)

        self.username_label = QLabel(
            f"Nom de l'utilisateur : {self.username} "
            f"[{self.reverse_map_combo.get(current_user_role)}]"
        )
        layout.addRow(self.username_label)

        self.role_combo = QtWidgets.QComboBox(self)
        self.role_combo.addItems(["lecture", "lecture + ecriture", "administrateur"])
        layout.addRow("Rôle", self.role_combo)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def accept(self):
        """
        Accepte les modifications et met à jour le rôle de l'utilisateur dans la base de données.

        :return: None
        """
        selected_role = self.role_combo.currentText()
        role_id = self.map_rights_combo.get(selected_role, None)
        DB_API.set_user_permission(self.project_id, self.user_id, role_id)
        super().accept()


class UserStatusWidget(QWidget):
    """
    Widget pour afficher le statut d'un utilisateur.

    :param username: Le nom d'utilisateur.
    :param user_id: L'ID de l'utilisateur (optionnel).
    :param is_online: Booléen indiquant si l'utilisateur est en ligne.
    :param parent: Le parent du widget (optionnel).
    :param is_admin: Booléen indiquant si l'utilisateur est administrateur.
    :param project_id: L'ID du projet (optionnel).
    :param current_user_role: Le rôle actuel de l'utilisateur (optionnel).
    """

    def __init__(
        self,
        username,
        user_id=None,
        is_online=False,
        parent=None,
        is_admin=False,
        project_id=None,
        current_user_role=None,
    ):
        super().__init__(parent)
        self.is_admin = is_admin
        self.username = username
        self.project_id = project_id
        self.is_online = is_online
        self.user_id = user_id
        self.current_user_role = current_user_role

        # Layout principal
        layout = QVBoxLayout(self)

        # Conteneur utilisateur
        user_widget = QWidget()
        user_widget.setFixedHeight(50)  # Réduisez ou ajustez la hauteur ici
        user_widget.setAutoFillBackground(True)

        # Définition de la couleur de fond
        palette = user_widget.palette()
        bg_color = QColor("#E8F5E9") if is_online else QColor("#FFFFFF")
        palette.setColor(QPalette.Window, bg_color)
        user_widget.setPalette(palette)

        # Layout pour les informations utilisateur
        user_layout = QVBoxLayout(user_widget)
        user_layout.setContentsMargins(5, 5, 5, 5)  # Ajout de marges internes
        user_layout.setSpacing(0)  # Réduisez l'espacement interne

        # Nom de l'utilisateur
        username_label = QLabel(username)
        username_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # Statut en ligne / hors ligne
        status_text = "En ligne" if is_online else "Hors ligne"
        status_color = "#4CAF50" if is_online else "#757575"
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-size: 12px;")

        # Ajout des éléments au layout utilisateur
        user_layout.addWidget(username_label)
        user_layout.addWidget(status_label)

        # Ajout du widget utilisateur au layout principal
        layout.addWidget(user_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Réduisez l'espacement entre chaque widget utilisateur

    def mousePressEvent(self, event):
        """
        Gère l'événement de clic de la souris.

        :param event: L'événement de clic de la souris.
        :return: None
        """
        if event.button() == Qt.LeftButton and self.is_admin:
            self.on_user_clicked()

    def on_user_clicked(self):
        """
        Affiche la boîte de dialogue pour modifier le rôle de l'utilisateur.

        :return: None
        """
        dialog = UserRoleDialog(
            self.username, self.user_id, self.project_id, self.current_user_role
        )
        dialog.exec_()
        users_in_project = DB_API.get_users_in_project_by_project_id(self.project_id)
        self.current_user_role = next(
            user[2] for user in users_in_project if user[0] == self.user_id
        )


class TaskDialog(QtWidgets.QDialog):
    """
    Boîte de dialogue pour ajouter une nouvelle tâche.

    :param parent: Le parent de la boîte de dialogue (optionnel).
    :param users: Liste des utilisateurs disponibles pour l'assignation.
    """

    def __init__(self, parent=None, users=[]):  # noqa
        super().__init__(parent)
        self.setWindowTitle("Nouvelle Tâche")
        self.setModal(True)
        self.setup_ui()
        self.load_users(users)

    def setup_ui(self):
        """
        Configure l'interface utilisateur de la boîte de dialogue.

        :return: None
        """
        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        # Champs de saisie
        self.task_input = QtWidgets.QLineEdit()
        self.date_input = QtWidgets.QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QtCore.QDate().currentDate())
        self.comment_input = QtWidgets.QLineEdit()
        self.importance_input = QtWidgets.QComboBox()
        self.importance_input.addItems(["Faible", "Moyenne", "Haute"])

        # Configuration du groupe d'assignation
        assign_group = QtWidgets.QGroupBox("Assigner des utilisateurs")
        assign_layout = QtWidgets.QHBoxLayout(assign_group)

        self.assign_user_dropdown = QtWidgets.QComboBox()
        self.assign_user_dropdown.setFixedWidth(150)

        self.add_user_button = QtWidgets.QPushButton("+")
        self.add_user_button.setFixedWidth(30)
        self.add_user_button.setStyleSheet(
            "background-color: green; color: white; border-radius: 5px;"
        )

        self.remove_user_button = QtWidgets.QPushButton("-")
        self.remove_user_button.setFixedWidth(30)
        self.remove_user_button.setStyleSheet(
            "background-color: red; color: white; border-radius: 5px;"
        )

        self.assigned_users_list = QtWidgets.QListWidget()
        self.assigned_users_list.setFixedHeight(60)
        self.assigned_users_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        assign_layout.addWidget(self.assign_user_dropdown)
        assign_layout.addWidget(self.add_user_button)
        assign_layout.addWidget(self.remove_user_button)
        assign_layout.addWidget(self.assigned_users_list)

        # Ajout des champs au formulaire
        form_layout.addRow("Tâche :", self.task_input)
        form_layout.addRow("Date :", self.date_input)
        form_layout.addRow("Commentaire :", self.comment_input)
        form_layout.addRow("Importance :", self.importance_input)
        form_layout.addRow("Assigner des utilisateurs :", assign_group)

        # Boutons de validation
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Connexion des boutons d'assignation
        self.add_user_button.clicked.connect(self.add_selected_user)
        self.remove_user_button.clicked.connect(self.remove_selected_user)

        # Assemblage final
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

    def load_users(self, users):
        """
        Charge la liste des utilisateurs dans le menu déroulant.

        :param users: Liste des utilisateurs.
        :return: None
        """
        self.assign_user_dropdown.clear()
        self.assign_user_dropdown.addItems(users)

    def add_selected_user(self):
        """
        Ajoute l'utilisateur sélectionné à la liste des utilisateurs assignés.

        :return: None
        """
        selected_user = self.assign_user_dropdown.currentText()
        if selected_user and not self.is_user_already_assigned(selected_user):
            self.assigned_users_list.addItem(selected_user)

    def remove_selected_user(self):
        """
        Retire l'utilisateur sélectionné de la liste des utilisateurs assignés.

        :return: None
        """
        current_item = self.assigned_users_list.currentItem()
        if current_item:
            self.assigned_users_list.takeItem(self.assigned_users_list.row(current_item))

    def is_user_already_assigned(self, username):
        """
        Vérifie si l'utilisateur est déjà assigné.

        :param username: Le nom d'utilisateur.
        :return: Booléen indiquant si l'utilisateur est déjà assigné.
        """
        for i in range(self.assigned_users_list.count()):
            if self.assigned_users_list.item(i).text() == username:
                return True
        return False

    def get_form_data(self):
        """
        Récupère les données du formulaire.

        :return: Dictionnaire contenant les données du formulaire.
        """
        return {
            "title": self.task_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "comment": self.comment_input.text().strip(),
            "priority": self.importance_input.currentIndex(),
            "assigned_users": [
                self.assigned_users_list.item(i).text()
                for i in range(self.assigned_users_list.count())
            ],
        }


class SubtaskDialog(QtWidgets.QDialog):
    """
    Boîte de dialogue pour ajouter une sous-tâche.

    :param parent: Le parent de la boîte de dialogue (optionnel).
    :param users: Liste des utilisateurs disponibles pour l'assignation (optionnel).
    """

    def __init__(self, parent=None, users=None):
        super().__init__(parent)
        self.users = users or []
        self.setWindowTitle("Ajouter une sous-tâche")
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        """
        Configure l'interface utilisateur de la boîte de dialogue.

        :return: None
        """
        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        # Champs de saisie
        self.task_input = QtWidgets.QLineEdit()
        self.date_input = QtWidgets.QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QtCore.QDate().currentDate())
        self.comment_input = QtWidgets.QLineEdit()
        self.importance_input = QtWidgets.QComboBox()
        self.importance_input.addItems(["Faible", "Moyenne", "Haute"])

        # Configuration du groupe d'assignation
        assign_group = QtWidgets.QGroupBox("Assigner des utilisateurs")
        assign_layout = QtWidgets.QHBoxLayout(assign_group)

        self.assign_user_dropdown = QtWidgets.QComboBox()
        self.assign_user_dropdown.setFixedWidth(150)

        self.add_user_button = QtWidgets.QPushButton("+")
        self.add_user_button.setFixedWidth(30)
        self.add_user_button.setStyleSheet(
            "background-color: green; color: white; border-radius: 5px;"
        )

        self.remove_user_button = QtWidgets.QPushButton("-")
        self.remove_user_button.setFixedWidth(30)
        self.remove_user_button.setStyleSheet(
            "background-color: red; color: white; border-radius: 5px;"
        )

        self.assigned_users_list = QtWidgets.QListWidget()
        self.assigned_users_list.setFixedHeight(60)
        self.assigned_users_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        assign_layout.addWidget(self.assign_user_dropdown)
        assign_layout.addWidget(self.add_user_button)
        assign_layout.addWidget(self.remove_user_button)
        assign_layout.addWidget(self.assigned_users_list)

        # Ajout des champs au formulaire
        form_layout.addRow("Sous-tâche :", self.task_input)
        form_layout.addRow("Date :", self.date_input)
        form_layout.addRow("Commentaire :", self.comment_input)
        form_layout.addRow("Importance :", self.importance_input)
        form_layout.addRow("Assigner des utilisateurs :", assign_group)

        # Boutons de validation
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Connexion des boutons d'assignation
        self.add_user_button.clicked.connect(self.add_selected_user)
        self.remove_user_button.clicked.connect(self.remove_selected_user)

        # Assemblage final
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

    def load_users(self):
        """
        Charge la liste des utilisateurs dans le menu déroulant.

        :return: None
        """
        self.assign_user_dropdown.clear()
        for user in self.users:
            if isinstance(user, tuple):
                self.assign_user_dropdown.addItem(user[1])  # user[1] contient le nom d'utilisateur
            else:
                self.assign_user_dropdown.addItem(user)

    def add_selected_user(self):
        """
        Ajoute l'utilisateur sélectionné à la liste des utilisateurs assignés.

        :return: None
        """
        current_user = self.assign_user_dropdown.currentText()
        if current_user and not self.is_user_already_assigned(current_user):
            self.assigned_users_list.addItem(current_user)

    def remove_selected_user(self):
        """
        Retire l'utilisateur sélectionné de la liste des utilisateurs assignés.

        :return: None
        """
        current_item = self.assigned_users_list.currentItem()
        if current_item:
            self.assigned_users_list.takeItem(self.assigned_users_list.row(current_item))

    def is_user_already_assigned(self, username):
        """
        Vérifie si l'utilisateur est déjà assigné.

        :param username: Le nom d'utilisateur.
        :return: Booléen indiquant si l'utilisateur est déjà assigné.
        """
        for i in range(self.assigned_users_list.count()):
            if self.assigned_users_list.item(i).text() == username:
                return True
        return False

    def get_form_data(self):
        """
        Récupère les données du formulaire.

        :return: Dictionnaire contenant les données du formulaire.
        """
        return {
            "title": self.task_input.text(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "comment": self.comment_input.text(),
            "priority": self.importance_input.currentIndex(),
            "assigned_users": [
                self.assigned_users_list.item(i).text()
                for i in range(self.assigned_users_list.count())
            ],
        }


class TaskEditDialog(QtWidgets.QDialog):
    """
    Boîte de dialogue pour modifier une tâche existante.

    :param parent: Le parent de la boîte de dialogue (optionnel).
    :param task_info: Informations sur la tâche à modifier.
    :param assigned_users: Liste des utilisateurs assignés à la tâche.
    :param all_users: Liste de tous les utilisateurs disponibles pour l'assignation.
    """

    def __init__(self, parent=None, task_info=None, assigned_users=None, all_users=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier la tâche")
        self.setModal(True)
        self.resize(400, 500)

        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        self.title_input = QtWidgets.QLineEdit(self)
        self.title_input.setText(task_info[0] if task_info else "")

        self.date_input = QtWidgets.QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        if task_info:
            date = QtCore.QDate(task_info[6].year, task_info[6].month, task_info[6].day)
            self.date_input.setDate(date)

        self.comment_input = QtWidgets.QLineEdit(self)
        self.comment_input.setText(task_info[1] if task_info else "")

        self.importance_input = QtWidgets.QComboBox(self)
        self.importance_input.addItems(["Faible", "Moyenne", "Haute"])
        if task_info:
            self.importance_input.setCurrentIndex(task_info[3])

        # Section des utilisateurs assignés
        assign_group = QtWidgets.QGroupBox("Assigner des utilisateurs")
        assign_layout = QtWidgets.QVBoxLayout()

        # Liste des utilisateurs disponibles et assignés
        user_selection_layout = QtWidgets.QHBoxLayout()

        self.assign_user_dropdown = QtWidgets.QComboBox(self)
        if all_users:
            self.assign_user_dropdown.addItems([user[1] for user in all_users])

        self.add_user_button = QtWidgets.QPushButton("+")
        self.add_user_button.setFixedWidth(30)
        self.add_user_button.setStyleSheet("background-color: green; color: white;")

        user_selection_layout.addWidget(self.assign_user_dropdown)
        user_selection_layout.addWidget(self.add_user_button)

        self.assigned_users_list = QtWidgets.QListWidget(self)
        self.assigned_users_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        if assigned_users:
            for user in assigned_users:
                if user[1].strip():
                    self.assigned_users_list.addItem(user[1].strip())

        self.remove_user_button = QtWidgets.QPushButton("-")
        self.remove_user_button.setFixedWidth(30)
        self.remove_user_button.setStyleSheet("background-color: red; color: white;")

        assign_layout.addLayout(user_selection_layout)
        assign_layout.addWidget(self.assigned_users_list)
        assign_layout.addWidget(self.remove_user_button)
        assign_group.setLayout(assign_layout)

        # Ajout des champs au formulaire
        form_layout.addRow("Titre :", self.title_input)
        form_layout.addRow("Date :", self.date_input)
        form_layout.addRow("Commentaire :", self.comment_input)
        form_layout.addRow("Importance :", self.importance_input)

        layout.addLayout(form_layout)
        layout.addWidget(assign_group)

        # Boutons de confirmation
        button_box = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Annuler")
        self.apply_button = QtWidgets.QPushButton("Appliquer")
        self.apply_button.setStyleSheet("background-color: #4CAF50; color: white;")

        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.apply_button)
        layout.addLayout(button_box)

        # Connexions des signaux
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
        self.add_user_button.clicked.connect(self.add_selected_user)
        self.remove_user_button.clicked.connect(self.remove_selected_user)

    def add_selected_user(self):
        """
        Ajoute l'utilisateur sélectionné à la liste des utilisateurs assignés.

        :return: None
        """
        selected_user = self.assign_user_dropdown.currentText()
        if selected_user and not self.is_user_already_assigned(selected_user):
            self.assigned_users_list.addItem(selected_user)

    def remove_selected_user(self):
        """
        Retire l'utilisateur sélectionné de la liste des utilisateurs assignés.

        :return: None
        """
        current_item = self.assigned_users_list.currentItem()
        if current_item:
            self.assigned_users_list.takeItem(self.assigned_users_list.row(current_item))

    def is_user_already_assigned(self, username):
        """
        Vérifie si l'utilisateur est déjà assigné.

        :param username: Le nom d'utilisateur.
        :return: Booléen indiquant si l'utilisateur est déjà assigné.
        """
        for i in range(self.assigned_users_list.count()):
            if self.assigned_users_list.item(i).text() == username:
                return True
        return False

    def get_form_data(self):
        """
        Récupère les données du formulaire.

        :return: Dictionnaire contenant les données du formulaire.
        """
        return {
            "title": self.title_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "comment": self.comment_input.text().strip(),
            "priority": self.importance_input.currentIndex(),
            "assigned_users": [
                self.assigned_users_list.item(i).text()
                for i in range(self.assigned_users_list.count())
            ],
        }


if __name__ == "__main__":
    # u = Ui_MainWindow()
    # print(u.get_invitation(11, only_pending=True))
    # u.send_invitation(6, 25, 1)
    # u.send_invitation(9, 25, 1)
    # u.send_invitation(10, 25,1)
    # u.send_invitation(11, 25,1)
    # u.send_invitation(12, 25,1)
    # u.send_invitation(14, 25,1)
    # print(u.get_invitation(11, only_pending=True))
    # # u.send_invitation(11, 2, 12)
    # print(u.get_invitation(11, only_pending=True))

    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
