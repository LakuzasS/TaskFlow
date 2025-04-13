import datetime
import logging
from typing import Optional, Union

from argon2 import PasswordHasher
from argon2 import exceptions as argon2_exceptions

from mysql.connector.cursor import MySQLCursor
from backend.db_helper import cm_cursor, ResultType, cm_conn
from backend.db_requests import _Requests

_log = logging.getLogger(__name__)

ph = PasswordHasher()


class DB_API:
    """
    Classe permettant d'exécuter les commandes vers la DB SQL.
    """

    @staticmethod
    @cm_cursor()
    def check_user_credentials(email: str, plain_password: str, *, cursor: MySQLCursor) -> bool:
        """
        Vérifie si l'utilisateur 'email' existe et si le mot de passe 'plain_password'
        correspond (Argon2). Retourne True si OK, sinon False.

        :param email: Email de l'utilisateur
        :param plain_password: Mot de passe en clair de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si les identifiants sont corrects, False sinon

        Exemple:
        >>> is_valid = DB_API.check_user_credentials("email@example.com", "password123")
        >>> if is_valid:
        >>>     print("Identifiants valides")
        """
        cursor.execute(_Requests.get_password_from_email, (email,))
        row = cursor.fetchone()
        if not row:
            return False  # Email inconnu

        hashed_password = row[0]
        if not hashed_password:
            return False  # Pas de mot de passe stocké => compte Google ?

        try:
            ph.verify(hashed_password, plain_password)
            if ph.check_needs_rehash(hashed_password):
                new_hash = ph.hash(plain_password)
                cursor.execute(_Requests.update_user_password, (new_hash, email))
            return True
        except argon2_exceptions.VerifyMismatchError:
            return False
        except Exception:
            return False

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_user(
        username: str, password: str, email: str, is_google_user: bool, *, cursor: MySQLCursor
    ) -> Union[Exception, Optional[int]]:
        """
        Ajoute un nouvel utilisateur dans la DB.
        - Si is_google_user == False, hache le password (Argon2).
        - Sinon, on stocke un placeholder (ex: "").
        Retourne l'ID (userID) inséré, ou un objet Exception en cas d'erreur.

        :param username: Nom d'utilisateur
        :param password: Mot de passe de l'utilisateur
        :param email: Email de l'utilisateur
        :param is_google_user: Indique si l'utilisateur utilise un compte Google
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: ID de l'utilisateur inséré ou Exception en cas d'erreur

        Exemple:
        >>> user_id = DB_API.add_user("username", "password123", "email@example.com", False)
        >>> if not isinstance(user_id, Exception):
        >>>     print(f"Utilisateur ajouté avec l'ID: {user_id}")
        """
        if not is_google_user:
            try:
                password = ph.hash(password)
            except Exception as e:
                return e
        else:
            password = ""

        try:
            cursor.execute(_Requests.add_user, (username, password, email, is_google_user))
            return cursor.lastrowid
        except Exception as e:
            return e

    @staticmethod
    @cm_cursor()
    def get_task_infoID_by_taskID(task_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer l'ID des informations d'une tâche en fonction de son ID.

        Cette fonction renvoie un tuple comprenant l'ID des informations de la tâche.
        En cas d'échec, elle renverra None ou dans certains cas, un objet de type Exception.

        :param task_id: ID de la tâche
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: ID des informations de la tâche ou exception

        Exemple:
        >>> task_info_id = DB_API.get_task_infoID_by_taskID(1)
        >>> if task_info_id and not isinstance(task_info_id, Exception):
        >>>     print(task_info_id)
        """
        cursor.execute(_Requests.get_task_infoID_by_taskID, (task_id,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_cursor()
    def get_task_infoID_by_subtaskID(subtask_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer l'ID des informations d'une sous tâche en fonction de son ID.

        Cette fonction renvoie un tuple comprenant l'ID des informations de la sous tâche.
        En cas d'échec, elle renverra None ou dans certains cas, un objet de type Exception.

        :param subtask_id: ID de la sous tâche
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: ID des informations de la tâche ou exception

        Exemple:
        >>> task_info_id = DB_API.get_task_infoID_by_subtaskID(1)
        >>> if task_info_id and not isinstance(task_info_id, Exception):
        >>>     print(task_info_id)
        """
        cursor.execute(_Requests.get_task_infoID_by_subtaskID, (subtask_id,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_cursor()
    def get_all_infos_from_email(email: str, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer toutes les informations d'un utilisateur en fonction
        de son email dans la DB.

        Cette fonction renvoie un tuple comprenant toutes les informations liées
        à un utilisateur.
        Si une erreur survient, la fonction renvoie un objet de type Exception.

        :param email: Email de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: Résultat de la commande ou exception

        Exemple:
        >>> user_info = DB_API.get_all_infos_from_email("test@example.com")
        >>> if user_info and not isinstance(user_info, Exception):
        >>>     print(user_info)
        """
        cursor.execute(_Requests.get_all_infos_from_email, (email,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_user_status(userID: int, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Supprime le statut d'un utilisateur dans la base de données.

        Cette fonction exécute une requête pour supprimer le statut d'un utilisateur
        en fonction de son ID. En cas de succès, elle renvoie None. En cas d'échec,
        elle renvoie une exception.

        :param userID: ID de l'utilisateur dont le statut doit être supprimé
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: None en cas de succès, ou une exception en cas d'échec

        Exemple:
        >>> err = DB_API.delete_user_status(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Statut de l'utilisateur supprimé avec succès")
        """
        return cursor.execute(_Requests.delete_user_status, (userID,))

    @staticmethod
    @cm_cursor()
    def get_all_users(*, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer tous les utilisateurs de la DB.

        Cette fonction renvoie une liste de tuples comprenant les
        users sous la forme (userID, username, email, is_google_user).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> users = DB_API.get_all_users()
        >>> if users and not isinstance(users, Exception):
        >>>     print(users)

        """
        cursor.execute(_Requests.get_all_users)
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_project_id_by_project_name(project_name: str, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer le project id en fonction du project name de la DB.

        Cette fonction renvoie un tuple comprenant le project id
        sous la forme (project_id,).
        Cette fonction peut ne pas fonctionner, dans ce cas elle

        :param project_name: Nom du projet
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> project_id = DB_API.get_project_id_by_project_name()
        >>> if project_id and not isinstance(project_id, Exception):
        >>>     print(project_id)

        """
        cursor.execute(_Requests.get_project_id_by_project_name, (project_name,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_cursor()
    def get_projects_by_user_id(user_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer tous les projets d'un utilisateur en fonction de son userID.

        Cette fonction renvoie une liste de tuples comprenant les
        projets sous la forme (projectID, name, joined).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param user_id: ID de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> projects = DB_API.get_projects_by_user_id(1)
        >>> if projects and not isinstance(projects, Exception):
        >>>     print(projects)
        """
        cursor.execute(_Requests.get_projects_by_user_id, (user_id,))
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_tasks_by_project_id(project_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer toutes les taches d'un projet en fonction de son projectID.

        Cette fonction renvoie une liste de tuples comprenant les
        taches sous la forme (taskID, title, description, status,
        priority, covered, assign, dead_line).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param project_id: projectID
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> tasks = DB_API.get_tasks_by_project_id(1)
        >>> if tasks and not isinstance(tasks, Exception):
        >>>     print(tasks)
        """
        cursor.execute(_Requests.get_tasks_by_project_id, (project_id,))
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_subtasks_by_task_id(task_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer toutes les sous taches d'un projet en fonction de son taskID.

        Cette fonction renvoie une liste de tuples comprenant les
        sous taches sous la forme (subtaskID, title, description, status,
        priority, covered, assign, dead_line).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param task_id: taskID
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> subtasks = DB_API.get_subtasks_by_task_id(1)
        >>> if subtasks and not isinstance(subtasks, Exception):
        >>>     print(subtasks)
        """
        cursor.execute(_Requests.get_subtasks_by_task_id, (task_id,))
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_users_in_project_by_project_id(project_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer toutes users dans un projet en fonction du projectID.

        Cette fonction renvoie une liste de tuples comprenant les
        projets de l'user sous la forme (userID, username, permission).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param project_id: projectID
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> users_in_project = DB_API.get_users_in_project_by_project_id(1)
        >>> if users_in_project and not isinstance(users_in_project, Exception):
        >>>     print(users_in_project)
        """
        cursor.execute(_Requests.get_users_in_project_by_project_id, (project_id,))
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_users_in_tasks_group_by_group_id(group_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer tous les utilisateurs dans un groupe
        de tâches en fonction de son groupID.

        Cette fonction renvoie une liste de tuples comprenant les
        utilisateurs sous la forme (userID, username, task_projectID).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param group_id: groupID
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> users_in_group = DB_API.get_users_in_tasks_group_by_group_id(1)
        >>> if users_in_group and not isinstance(users_in_group, Exception):
        >>>     print(users_in_group)
        """
        cursor.execute(_Requests.get_users_in_tasks_group_by_group_id, (group_id,))
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_all_status(*, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récuperer les statuts de tous les users dans la DB.

        Cette fonction renvoie une liste de tuples comprenant les
        statuts sous la forme (userID, status), note : statut = (0 = deco; 1 = connect; 2 = idle).
        Cette fonction peut ne pas fonctionner, dans ce cas elle renvoie un objet
        de type Exception.
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        :return: resultat de la commande ou exception

        Exemple:
        >>> status = DB_API.get_all_status()
        >>> if status and not isinstance(status, Exception):
        >>>     print(status)
        """
        cursor.execute(_Requests.get_all_status)
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_project(name: str, *, cursor: MySQLCursor) -> Union[Exception, Optional[int]]:
        """
        Permet d'ajouter un nouveau projet à la DB.

        Cette fonction renvoie un boolean. En cas d'échec,
        elle renverra False et en cas de succes, elle renverra True.

        :param name: Nom du projet
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> project_id = DB_API.add_project("project_test")
        >>> if project_id and not isinstance(project_id, Exception):
        >>>     print(project_id)
        """
        cursor.execute(_Requests.add_project, (name,))
        return cursor.lastrowid

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_user_to_group(
        project_id: int, user_id: int, permission: int, joined: bool, *, cursor: MySQLCursor
    ) -> Union[Exception, Optional[int]]:
        """
        Permet d'ajouter un utilisateur à un groupe de projet.

        Cette fonction renvoie un boolean. En cas d'échec,
        elle renverra False et en cas de succes, elle renverra True.

        :param project_id: ID du projet
        :param user_id: ID de l'utilisateur
        :param permission: Permission de l'utilisateur dans le projet
        (0 = read, 1 = write, 2 = admin)
        :param joined: Date d'ajout à la groupe
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> user_group_id = DB_API.add_user_to_group(1, 1, 1, True)
        >>> if user_group_id and not isinstance(user_group_id, Exception):
        >>>     print(user_group_id)
        """
        cursor.execute(_Requests.add_user_to_group, (project_id, user_id, permission, joined))
        return cursor.lastrowid

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_task_info(
        status: int,
        priority: int,
        title: str,
        description: str,
        dead_line: datetime.datetime,
        covered: bool,
        assign: int,
        *,
        cursor: MySQLCursor,
    ) -> Union[Exception, Optional[int]]:
        """
        Permet d'ajouter des informations sur une tâche.

        Cette fonction renvoie un boolean. En cas d'échec,
        elle renverra False et en cas de succes, elle renverra True.

        :param status: Statut de la tâche
        :param priority: Priorité de la tâche (0 = basse; 1 = moyenne; 2= haute)
        :param title: Titre de la tâche
        :param description: Description de la tâche
        :param dead_line: Date limite de la tâche (datetime.datetime,
         le field dans la db est TIMESTAMP)
        :param covered: Informations sur la couverture de la tâche (bool)
        :param assign: task_projectID (lie la tache a un ou plusieurs
         user a travers la table tasks_groups)
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> taskinfo_id = DB_API.add_task_info(1, 2, "titre tache",
        "ceci est une description de la tache", datetime.datetime.now(), False, 1)
        >>> if taskinfo_id and not isinstance(taskinfo_id, Exception):
        >>>     print(taskinfo_id)
        """
        cursor.execute(
            _Requests.add_task_info,
            (status, priority, title, description, dead_line, covered, assign),
        )

        return cursor.lastrowid

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_task(
        project_id: int, task_info_id: int, user_id: int, *, cursor: MySQLCursor
    ) -> Union[Exception, Optional[int]]:
        """
        Permet d'ajouter une tâche à un projet.

        Cette fonction renvoie un boolean. En cas d'échec,
        elle renverra False et en cas de succes, elle renverra True.

        :param project_id: ID du projet
        :param task_info_id: ID des informations de la tâche
        :param user_id: ID de l'utilisateur assigné
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> task_id = DB_API.add_task(1, 1, 1)
        >>> if task_id and not isinstance(task_id, Exception):
        >>>     print(task_id)
        """
        cursor.execute(_Requests.add_task, (project_id, task_info_id, user_id))
        return cursor.lastrowid

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_subtask(
        task_id: int, task_info_id: int, *, cursor: MySQLCursor
    ) -> Union[Exception, Optional[int]]:
        """
        Permet d'ajouter une sous-tâche à une tâche.

        Cette fonction renvoie un boolean. En cas d'échec,
        elle renverra False et en cas de succes, elle renverra True.

        :param task_id: ID de la tâche parente
        :param task_info_id: ID des informations de la sous-tâche
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> subtask_id = DB_API.add_subtask(1, 1)
        >>> if subtask_id and not isinstance(subtask_id, Exception):
        >>>     print(subtask_id)
        """
        cursor.execute(_Requests.add_subtask, (task_id, task_info_id))
        return cursor.lastrowid

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_user_to_task_group(
        task_project_id: int, user_id: int, *, cursor: MySQLCursor
    ) -> Union[Exception, Optional[int]]:
        """
        Permet d'ajouter un utilisateur à un groupe de tâches.

        Cette fonction renvoie un boolean. En cas d'échec,
        elle renverra False et en cas de succes, elle renverra True.

        :param task_project_id: ID du projet de la tâche
        :param user_id: ID de l'utilisateur à ajouter
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> users_tasks_groups_id = DB_API.add_user_to_task_group(1, 1)
        >>> if users_tasks_groups_id and not isinstance(users_tasks_groups_id, Exception):
        >>>     print(users_tasks_groups_id)
        """
        cursor.execute(_Requests.add_user_to_task_group, (task_project_id, user_id))
        return cursor.lastrowid

    @staticmethod
    @cm_cursor()
    def get_user_id_by_username(username: str, *, cursor: MySQLCursor) -> Optional[int]:
        """
        Permet de recup les projets dans la db.

        Cette fonction renvoie l'user id.
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param username: Username de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> user_id = DB_API.get_user_id_by_username("toto")
        >>> if user_id and not isinstance(user_id, Exception):
        >>>     print(f"user_id = {user_id}")
        """
        cursor.execute(_Requests.get_userID_by_username, (username,))
        result = cursor.fetchone()
        return result[0]

    @staticmethod
    @cm_cursor()
    def get_all_projects(*, cursor: MySQLCursor) -> ResultType:
        """
        Permet de recup les projets dans la db.

        Cette fonction renvoie une liste de tuples comprenant les
        taches sous la forme (projectID, name).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> all_projects = DB_API.get_all_projects()
        >>> if all_projects and not isinstance(all_projects, Exception):
        >>>     print(f"all_projects = {all_projects}")
        """
        cursor.execute(_Requests.get_all_projects)
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_all_tasks(*, cursor: MySQLCursor) -> ResultType:
        """
        Permet de recup toutes les tasks dans la db.

        Cette fonction renvoie une liste de tuples comprenant les
        taches sous la forme (taskID, title, description, status,
        priority, covered, assign, dead_line).
        Cette fonction peut ne pas fonctionner, dans ce cas elle
        renvoie None ou dans certains cas, un objet de type Exception.

        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> all_tasks = DB_API.get_all_tasks()
        >>> if all_tasks and not isinstance(all_tasks, Exception):
        >>>     print(f"all_tasks = {all_tasks}")
        """
        cursor.execute(_Requests.get_all_tasks)
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_user_email(user_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de recup l'email de l'userid dans la db.

        Cette fonction renvoie un tuple ou None, une exception de façon rare.
        En cas d'échec, elle renverra une exc et en cas de succes,
        elle renverra le mail de l'user dans un tuple.

        :param user_id: L'id de l'user
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> email = DB_API.get_user_email(2)
        >>> if email and not isinstance(email, Exception):
        >>>     print(f"email = {email}")
        """
        cursor.execute(_Requests.get_user_email, (user_id,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_cursor()
    def get_email(email: str, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer l'email d'un utilisateur.

        Cette fonction renvoie un tuple représentant l'email ou une exception
        en cas d'erreur.

        :param email: Email de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> email_info = DB_API.get_email("exemple@domain.com")
        >>> if email_info and not isinstance(email_info, Exception):
        >>>     print(email_info)
        """
        cursor.execute(_Requests.get_email, (email,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_cursor()
    def get_user(username: str, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer les informations d'un utilisateur en fonction
        de son nom d'utilisateur.

        Cette fonction renvoie un tuple représentant les informations de
        l'utilisateur ou une exception en cas d'erreur.

        :param username: Nom d'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> user_info = DB_API.get_user("nom_utilisateur")
        >>> if user_info and not isinstance(user_info, Exception):
        >>>     print(user_info)
        """
        cursor.execute(_Requests.get_user, (username,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_cursor()
    def get_userID_by_email(email: str, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer l'ID d'un utilisateur en fonction de son email.

        Cette fonction renvoie un tuple représentant l'ID de l'utilisateur
        ou une exception en cas d'erreur.

        :param email: Email de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> user_id = DB_API.get_userID_by_email("exemple@domain.com")
        >>> if user_id and not isinstance(user_id, Exception):
        >>>     print(user_id)
        """
        cursor.execute(_Requests.get_userID_by_email, (email,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_user_status(
        user_id: int, status: int, *, cursor: MySQLCursor
    ) -> Union[Exception, Optional[int]]:
        """
        Ajoute un statut pour un utilisateur dans la base de données.

        Cette fonction exécute une requête pour ajouter un statut à un utilisateur
        en fonction de son ID. En cas de succès, elle renvoie l'ID du statut ajouté.
        En cas d'échec, elle renvoie une exception.

        :param user_id: ID de l'utilisateur
        :param status: Statut à ajouter (0 = déconnecté, 1 = connecté, 2 = inactif)
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: ID du statut ajouté en cas de succès, ou une exception en cas d'échec

        Exemple:
        >>> status_id = DB_API.add_user_status(1, 0)
        >>> if not isinstance(status_id, Exception):
        >>>     print(f"Statut ajouté avec l'ID: {status_id}")
        """
        cursor.execute(_Requests.add_user_status, (user_id, status))
        return cursor.lastrowid

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def add_task_group(*, cursor: MySQLCursor) -> Union[Exception, Optional[int]]:
        """
        Permet d'ajouter un groupe de tâches dans la base de données.

        Cette fonction renvoie l'ID du groupe de tâches ou une exception en
        cas d'échec.

        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> task_group_id = DB_API.add_task_group()
        >>> if task_group_id and not isinstance(task_group_id, Exception):
        >>>     print(f"ID du groupe de tâches = {task_group_id}")
        """
        cursor.execute(_Requests.add_task_group)
        return cursor.lastrowid

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_user(user_id, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de supprimer un utilisateur de la base de données.

        Cette fonction renvoie None en cas de succès ou une exception en cas
        d'échec.

        :param user_id: ID de l'utilisateur à supprimer
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> err = DB_API.delete_user(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Utilisateur supprimé avec succès")
        """
        return cursor.execute(_Requests.delete_user, (user_id,))

    @staticmethod
    @cm_cursor()
    def get_project_in_users_groups_userid(user_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer tous les projets où l'utilisateur est invité
        (accepté ou non).

        Cette fonction renvoie une liste de tuples représentant les projets
        ou une exception en cas d'erreur.

        :param user_id: ID de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> projects = DB_API.get_project_in_users_groups_userid(10)
        >>> if projects and not isinstance(projects, Exception):
        >>>     print(projects)
        """
        cursor.execute(_Requests.get_project_in_users_groups, (user_id,))
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_task(task_id, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de supprimer une tâche de la base de données et toutes ses
        dépendances.

        Cette fonction renvoie None en cas de succès ou une exception en
        cas d'échec.

        :param task_id: ID de la tâche à supprimer
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())

        Exemple:
        >>> err = DB_API.delete_task(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Tâche supprimée avec succès")
        """
        return cursor.execute(_Requests.delete_task, (task_id,))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def set_invites_status(
        project_id: int, user_id: int, joined: int, *, cursor: MySQLCursor
    ) -> Optional[Exception]:
        """
        Permet d'accepter ou refuser une invitation vers un projet.
        Cette fonction renvoie None ou une exception. En cas d'échec,
        elle renverra une exc et en cas de succes, elle renverra None.
        :param project_id: Le project_ID
        :param user_id: ID de l'utilisateur
        :param joined: Accepter ou pas l'invit
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        Exemple:
        >>> err = DB_API.set_invites_status(1, 1, False)
        >>> if not isinstance(err, Exception):
        >>>     print("modifié avec succes")
        """
        return cursor.execute(_Requests.set_invites_status, (joined, project_id, user_id))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def set_user_permission(
        project_id: int, user_id: int, permission: int, *, cursor: MySQLCursor
    ) -> Optional[Exception]:
        """
        Permet de changer les permissions d'un user dans le projet.
        Cette fonction renvoie None ou une exception. En cas d'échec,
        elle renverra une exc et en cas de succes, elle renverra None.
        :param project_id: Le project_ID
        :param user_id: ID de l'utilisateur
        :param permission: Permission de l'utilisateur dans le projet
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        Exemple:
        >>> err = DB_API.set_user_permission(1, 1, 2)
        >>> if not isinstance(err, Exception):
        >>>     print("modifié avec succes")
        """
        return cursor.execute(_Requests.update_user_perm, (permission, project_id, user_id))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def set_user_status(user_id: int, status: int, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de modifier le status de l'utilisateur.
        Cette fonction renvoie None ou une exception. En cas d'échec,
        elle renverra une exc et en cas de succes, elle renverra None.
        :param user_id: ID de l'utilisateur
        :param status: Status de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB
        (optionnel, géré automatiquement par le décorateur cm_cursor())
        Exemple:
        >>> err = DB_API.set_user_status(1, 0)
        >>> if not isinstance(err, Exception):
        >>>     print("delete avec succes")
        """
        return cursor.execute(_Requests.update_user_status, (status, user_id))

    @staticmethod
    @cm_cursor()
    def get_totp_secret(email: str, *, cursor: MySQLCursor) -> Optional[str]:
        """
        Récupère la clé secrète TOTP d'un utilisateur en fonction de son email.

        Cette fonction renvoie la clé secrète TOTP ou None en cas d'échec.

        :param email: Email de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: Clé secrète TOTP ou None

        Exemple:
        >>> totp_secret = DB_API.get_totp_secret("email@example.com")
        >>> if totp_secret:
        >>>     print(f"Clé secrète TOTP: {totp_secret}")
        """
        cursor.execute(_Requests.get_totp_secret, (email,))
        row = cursor.fetchone()
        if row:
            return row[0]  # la clé
        return None

    @staticmethod
    @cm_cursor()
    def get_user_permission(project_id: int, user_id: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer les permissions d'un utilisateur dans un projet.

        Cette fonction renvoie un tuple comprenant les permissions de l'utilisateur.
        En cas d'échec, elle renverra une exception.

        :param project_id: ID du projet
        :param user_id: ID de l'utilisateur
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: Permissions de l'utilisateur ou exception

        Exemple:
        >>> permissions = DB_API.get_user_permission(1, 1)
        >>> if permissions and not isinstance(permissions, Exception):
        >>>     print(permissions)
        """
        cursor.execute(_Requests.get_user_permission, (project_id, user_id))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def set_totp_secret(email: str, secret: str, *, cursor: MySQLCursor) -> bool:
        """
        Définit la clé TOTP pour un utilisateur donné par son email.

        Cette fonction renvoie True en cas de succès ou False en cas d'échec.

        :param email: Email de l'utilisateur
        :param secret: Clé TOTP à définir
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si la clé TOTP a été définie avec succès, False sinon

        Exemple:
        >>> success = DB_API.set_totp_secret("email@example.com", "secret_key")
        >>> if success:
        >>>     print("Clé TOTP définie avec succès")
        """
        cursor.execute(_Requests.set_totp_secret, (secret, email))
        return True

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_project(project_id: int, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de supprimer un projet de la base de données.

        Cette fonction renvoie None en cas de succès ou une exception en cas d'échec.

        :param project_id: ID du projet à supprimer
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: None ou exception

        Exemple:
        >>> err = DB_API.delete_project(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Projet supprimé avec succès")
        """
        return cursor.execute(_Requests.delete_project, (project_id,))

    @staticmethod
    @cm_cursor()
    def get_task_info_by_task_id(taskID: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer les informations d'une tâche en fonction de son ID.

        Cette fonction renvoie un tuple comprenant les informations de la tâche.
        En cas d'échec, elle renverra une exception.

        :param taskID: ID de la tâche
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: Informations de la tâche ou exception

        Exemple:
        >>> task_info = DB_API.get_task_info_by_task_id(1)
        >>> if task_info and not isinstance(task_info, Exception):
        >>>     print(task_info)
        """
        query = _Requests.get_task_info_by_task_id
        cursor.execute(query, (taskID,))
        result = cursor.fetchall()
        return result

    @staticmethod
    @cm_cursor()
    def get_subtask_info_by_subtask_id(subtaskID: int, *, cursor: MySQLCursor) -> ResultType:
        """
        Permet de récupérer les informations d'une sous-tâche en fonction de son ID.

        Cette fonction renvoie un tuple comprenant les informations de la sous-tâche.
        En cas d'échec, elle renverra une exception.

        :param subtaskID: ID de la sous-tâche
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: Informations de la sous-tâche ou exception

        Exemple:
        >>> subtask_info = DB_API.get_subtask_info_by_subtask_id(1)
        >>> if subtask_info and not isinstance(subtask_info, Exception):
        >>>     print(subtask_info)
        """
        query = _Requests.get_subtask_info_by_subtask_id
        cursor.execute(query, (subtaskID,))
        result = cursor.fetchone()
        return result

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_user_group(project_id: int, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de supprimer un groupe d'utilisateurs d'un projet.

        Cette fonction renvoie None en cas de succès ou une exception en cas d'échec.

        :param project_id: ID du projet
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: None ou exception

        Exemple:
        >>> err = DB_API.delete_user_group(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Groupe d'utilisateurs supprimé avec succès")
        """
        return cursor.execute(_Requests.delete_users_groups, (project_id,))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_tasks_groups(project_id: int, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de supprimer tous les groupes de tâches d'un projet.

        Cette fonction renvoie None en cas de succès ou une exception en cas d'échec.

        :param project_id: ID du projet
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: None ou exception

        Exemple:
        >>> err = DB_API.delete_tasks_groups(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Groupes de tâches supprimés avec succès")
        """
        return cursor.execute(_Requests.delete_tasks_groups, (project_id,))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_tasks_infos(project_id: int, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de supprimer toutes les informations de tâches d'un projet.

        Cette fonction renvoie None en cas de succès ou une exception en cas d'échec.

        :param project_id: ID du projet
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: None ou exception

        Exemple:
        >>> err = DB_API.delete_tasks_infos(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Informations de tâches supprimées avec succès")
        """
        return cursor.execute(_Requests.delete_tasks_infos, (project_id,))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_tasks(project_id: int, *, cursor: MySQLCursor) -> Optional[Exception]:
        """
        Permet de supprimer toutes les tâches d'un projet.

        Cette fonction renvoie None en cas de succès ou une exception en cas d'échec.

        :param project_id: ID du projet
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: None ou exception

        Exemple:
        >>> err = DB_API.delete_tasks(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Tâches supprimées avec succès")
        """
        return cursor.execute(_Requests.delete_tasks, (project_id,))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def check_projects(project_name: str, *, cursor: MySQLCursor) -> bool:
        """
        Vérifie si un projet existe dans la base de données en fonction de son nom.

        Cette fonction renvoie True si le projet existe, False sinon.

        :param project_name: Nom du projet
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si le projet existe, False sinon

        Exemple:
        >>> exists = DB_API.check_projects("Nom du Projet")
        >>> if exists:
        >>>     print("Le projet existe")
        """
        cursor.execute(_Requests.check_projects, (project_name,))
        result = cursor.fetchone()
        return result[0] > 0 if result else False

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def delete_users_from_users_tasks_groups(
        task_group_id: int, *, cursor: MySQLCursor
    ) -> Optional[Exception]:
        """
        Supprime les utilisateurs d'un groupe de tâches.

        Cette fonction renvoie None en cas de succès ou une exception en cas d'échec.

        :param task_group_id: ID du groupe de tâches
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: None ou exception

        Exemple:
        >>> err = DB_API.delete_users_from_users_tasks_groups(1)
        >>> if not isinstance(err, Exception):
        >>>     print("Utilisateurs supprimés du groupe de tâches avec succès")
        """
        return cursor.execute(_Requests.delete_users_from_users_tasks_groups, (task_group_id,))

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def update_task_status(task_info_id: int, status: int, *, cursor: MySQLCursor) -> bool:
        """
        Met à jour le statut de la tâche dans la table tasks_infos.

        Cette fonction renvoie True en cas de succès ou False en cas d'échec.

        :param task_info_id: ID des informations de la tâche
        :param status: Nouveau statut de la tâche
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si le statut a été mis à jour avec succès, False sinon

        Exemple:
        >>> success = DB_API.update_task_status(1, 0)
        >>> if success:
        >>>     print("Statut de la tâche mis à jour avec succès")
        """
        cursor.execute(_Requests.update_task_status, (status, task_info_id))
        return cursor.rowcount > 0

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def update_task_title(title: str, task_info_id: int, *, cursor: MySQLCursor) -> bool:
        """
        Met à jour le titre d'une tâche dans la table tasks_infos.

        Cette fonction renvoie True en cas de succès ou False en cas d'échec.

        :param task_info_id: ID des informations de la tâche
        :param title: Nouveau titre de la tâche
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si le titre a été mis à jour avec succès, False sinon

        Exemple:
        >>> success = DB_API.update_task_title("Nouveau Titre", 1)
        >>> if success:
        >>>     print("Titre de la tâche mis à jour avec succès")
        """
        query = _Requests.update_task_title
        cursor.execute(query, (title, task_info_id))
        return cursor.rowcount > 0

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def update_task_description(
        description: str, task_info_id: int, *, cursor: MySQLCursor
    ) -> bool:
        """
        Met à jour la description de la tâche dans la table tasks_infos.

        Cette fonction renvoie True en cas de succès ou False en cas d'échec.

        :param description: Nouvelle description de la tâche
        :param task_info_id: ID des informations de la tâche
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si la description a été mise à jour avec succès, False sinon

        Exemple:
        >>> success = DB_API.update_task_description("Nouvelle description", 1)
        >>> if success:
        >>>     print("Description de la tâche mise à jour avec succès")
        """
        query = _Requests.update_task_description
        cursor.execute(query, (description, task_info_id))
        return cursor.rowcount > 0

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def update_task_priority(priority: int, task_info_id: int, *, cursor: MySQLCursor) -> bool:
        """
        Met à jour la priorité d'une tâche dans la table tasks_infos.

        Cette fonction renvoie True en cas de succès ou False en cas d'échec.

        :param task_info_id: ID des informations de la tâche
        :param priority: Nouvelle priorité de la tâche
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si la priorité a été mise à jour avec succès, False sinon

        Exemple:
        >>> success = DB_API.update_task_priority(1, 2)
        >>> if success:
        >>>     print("Priorité de la tâche mise à jour avec succès")
        """
        query = _Requests.update_task_priority
        cursor.execute(query, (priority, task_info_id))
        return cursor.rowcount > 0

    @staticmethod
    @cm_conn()
    @cm_cursor()
    def update_task_date(date: datetime, task_info_id: int, *, cursor: MySQLCursor) -> bool:
        """
        Met à jour la date limite d'une tâche dans la table tasks_infos.

        Cette fonction renvoie True en cas de succès ou False en cas d'échec.

        :param date: Nouvelle date limite de la tâche
        :param task_info_id: ID des informations de la tâche
        :param cursor: Curseur d'une connexion vers une DB (optionnel,
        géré automatiquement par le décorateur cm_cursor())
        :return: True si la date a été mise à jour avec succès, False sinon

        Exemple:
        >>> success = DB_API.update_task_date(1, datetime.datetime.now())
        >>> if success:
        >>>     print("Date de la tâche mise à jour avec succès")
        """
        query = _Requests.update_task_date
        cursor.execute(query, (date, task_info_id))
        return cursor.rowcount > 0


if __name__ == "__main__":
    # print(DB_API.add_project('tebgfbgrsbs'))
    # t = (DB_API.add_user(username="vlad", password="trql",
    # email="email@vlad.com", is_google_user=False))
    t = DB_API.get_all_infos_from_email("miaw@redgally.xyz")
    print(type(t), t)
    pass
