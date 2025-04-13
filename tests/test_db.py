import datetime

from backend.db_api import DB_API
import pytest
from unittest.mock import Mock, patch
from mysql.connector.cursor import MySQLCursor

from backend.db_requests import _Requests


def create_mock_cursor(return_values=None):
    """
    Créer un faux MySQLCursor avec des valeurs de retour prédéfinies
    """
    mock_cursor = Mock(spec=MySQLCursor)

    if return_values is not None:
        mock_cursor.fetchall.return_value = return_values
        mock_cursor.fetchone.return_value = return_values[0] if return_values else None

    return mock_cursor


@pytest.fixture()
def mock_cursor():
    """
    Fixture pour fournir un curseur fictif pour les tests
    """
    return create_mock_cursor()


def test_get_all_users_success(mock_cursor):
    """
    Tester la méthode get_all_users dans un scénario réussi
    """
    test_users = [(1, "user1", "user1@example.com", 0), (2, "user2", "user2@example.com", 1)]
    mock_cursor.fetchall.return_value = test_users
    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_users(cursor=mock_cursor)

        assert result == test_users
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_users)


def test_get_all_users_empty(mock_cursor):
    """
    Tester la méthode get_all_users lorsqu'aucun utilisateur n'existe
    """
    mock_cursor.fetchall.return_value = []
    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_users(cursor=mock_cursor)
        assert result == []
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_users)


def test_get_all_users_exception(mock_cursor):
    """
    Tester la méthode get_all_users lorsqu'une exception se produit
    """
    mock_cursor.execute.side_effect = Exception("Database connection error")
    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_users(cursor=mock_cursor)
        assert isinstance(result, Exception)
        assert str(result) == "Database connection error"


def test_get_project_id_success(mock_cursor):
    """
    Tester la méthode get_project_id_by_project_name dans un scénario réussi
    """
    test_project_name = "Test Project"
    test_project_id = (42,)

    mock_cursor.fetchone.return_value = test_project_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_project_id_by_project_name(test_project_name, cursor=mock_cursor)

        assert result == test_project_id
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_project_id_by_project_name, (test_project_name,)
        )


def test_get_project_id_not_found(mock_cursor):
    """
    Tester la méthode get_project_id_by_project_name lorsqu'un projet n'est pas trouvé
    """
    mock_cursor.fetchone.return_value = None

    test_project_name = "Nonexistent Project"

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_project_id_by_project_name(test_project_name, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_project_id_by_project_name, (test_project_name,)
        )


@pytest.mark.integration()
def test_get_all_users_integration():
    """
    Test d'intégration qui se connecte réellement à la base de données
    """
    try:
        users = DB_API.get_all_users()

        assert isinstance(users, list)
        if users:
            user = users[0]
            assert len(user) == 4
            assert isinstance(user[0], int)  # ID utilisateur
            assert isinstance(user[1], str)  # nom d'utilisateur
            assert isinstance(user[2], str)  # email
            assert user[3] in (0, 1)  # is_google_user
    except Exception as e:
        pytest.fail(f"Échec de la connexion à la base de données ou de la requête: {e}")


def test_get_projects_by_user_id_success(mock_cursor):
    """
    Tester la méthode get_projects_by_user_id dans un scénario réussi.
    """
    test_projects = [(1, "Project 1"), (2, "Project 2")]

    mock_cursor.fetchall.return_value = test_projects

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_projects_by_user_id(1, cursor=mock_cursor)

        assert result == test_projects
        mock_cursor.execute.assert_called_once_with(_Requests.get_projects_by_user_id, (1,))


def test_get_projects_by_user_id_empty(mock_cursor):
    """
    Tester la méthode get_projects_by_user_id lorsqu'aucun projet n'existe.
    """
    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_projects_by_user_id(1, cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(_Requests.get_projects_by_user_id, (1,))


def test_get_tasks_by_project_id_success(mock_cursor):
    """
    Tester la méthode get_tasks_by_project_id dans un scénario réussi.
    """
    test_tasks = [
        (1, "Task 1", "Description 1", "Open", "High", "No", "User 1", "2024-12-31"),
        (2, "Task 2", "Description 2", "Closed", "Low", "Yes", "User 2", "2024-12-31"),
    ]

    mock_cursor.fetchall.return_value = test_tasks

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_tasks_by_project_id(1, cursor=mock_cursor)

        assert result == test_tasks
        mock_cursor.execute.assert_called_once_with(_Requests.get_tasks_by_project_id, (1,))


def test_get_subtasks_by_task_id_success(mock_cursor):
    """
    Tester la méthode get_subtasks_by_task_id dans un scénario réussi.
    """
    test_subtasks = [
        (1, "Subtask 1", "Description 1", "Open", "High", "No", "User 1", "2024-12-31"),
        (2, "Subtask 2", "Description 2", "Closed", "Low", "Yes", "User 2", "2024-12-31"),
    ]

    mock_cursor.fetchall.return_value = test_subtasks

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_subtasks_by_task_id(1, cursor=mock_cursor)

        assert result == test_subtasks
        mock_cursor.execute.assert_called_once_with(_Requests.get_subtasks_by_task_id, (1,))


def test_get_users_in_project_by_project_id_success(mock_cursor):
    """
    Tester la méthode get_users_in_project_by_project_id dans un scénario réussi.
    """
    test_users = [
        (1, "user1", "read"),
        (2, "user2", "write"),
    ]

    mock_cursor.fetchall.return_value = test_users

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_users_in_project_by_project_id(1, cursor=mock_cursor)

        assert result == test_users
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_users_in_project_by_project_id, (1,)
        )


def test_get_users_in_tasks_group_by_group_id_success(mock_cursor):
    """
    Tester la méthode get_users_in_tasks_group_by_group_id dans un scénario réussi
    """
    group_id = 1
    expected_users = [
        (1, "user1", 101),
        (2, "user2", 102),
    ]

    mock_cursor.fetchall.return_value = expected_users

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_users_in_tasks_group_by_group_id(group_id, cursor=mock_cursor)

        assert result == expected_users
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_users_in_tasks_group_by_group_id, (group_id,)
        )


def test_get_users_in_tasks_group_by_group_id_empty(mock_cursor):
    """
    Tester la méthode get_users_in_tasks_group_by_group_id lorsqu'aucun utilisateur n'est trouvé
    """
    group_id = 999
    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_users_in_tasks_group_by_group_id(group_id, cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_users_in_tasks_group_by_group_id, (group_id,)
        )


def test_get_users_in_tasks_group_by_group_id_exception(mock_cursor):
    """
    Tester la méthode get_users_in_tasks_group_by_group_id lorsqu'une exception se produit
    """
    group_id = 1
    mock_cursor.execute.side_effect = Exception("Erreur de base de données")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_users_in_tasks_group_by_group_id(group_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Erreur de base de données"


def test_get_all_status_success(mock_cursor):
    """
    Tester la méthode get_all_status dans un scénario réussi
    """
    expected_status = [
        (1, 1),
        (2, 0),
    ]

    mock_cursor.fetchall.return_value = expected_status

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_status(cursor=mock_cursor)

        assert result == expected_status
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_status)


def test_get_all_status_empty(mock_cursor):
    """
    Tester get_all_status lorsque aucun statut n'est trouvé
    """
    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_status(cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_status)


def test_get_all_status_exception(mock_cursor):
    """
    Tester get_all_status lorsqu'une exception se produit
    """
    mock_cursor.execute.side_effect = Exception("Erreur de base de données")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_status(cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Erreur de base de données"


def test_add_user_success(mock_cursor):
    """
    Tester add_user avec une insertion réussie
    """
    username = "test_user"
    password = "hashed_password"
    email = "test@example.com"
    is_google_user = False
    expected_user_id = 123
    hashed_password = "hashed_password"

    mock_cursor.lastrowid = expected_user_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ), patch("argon2.PasswordHasher.hash", return_value=hashed_password):
        result = DB_API.add_user(username, password, email, is_google_user, cursor=mock_cursor)

        assert result == expected_user_id
        mock_cursor.execute.assert_called_once_with(
            _Requests.add_user, (username, hashed_password, email, is_google_user)
        )


def test_add_user_exception(mock_cursor):
    """
    Tester add_user lorsqu'une exception se produit
    """
    username = "test_user"
    password = "hashed_password"
    email = "test@example.com"
    is_google_user = False

    mock_cursor.execute.side_effect = Exception("Erreur d'insertion")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_user(username, password, email, is_google_user, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Erreur d'insertion"


def test_add_project_success(mock_cursor):
    """
    Tester add_project avec une insertion réussie
    """
    name = "new_project"
    expected_project_id = 456

    mock_cursor.lastrowid = expected_project_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_project(name, cursor=mock_cursor)

        assert result == expected_project_id
        mock_cursor.execute.assert_called_once_with(_Requests.add_project, (name,))


def test_add_project_exception(mock_cursor):
    """
    Tester add_project lorsqu'une exception se produit
    """
    name = "new_project"

    mock_cursor.execute.side_effect = Exception("Erreur d'insertion")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_project(name, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Erreur d'insertion"


def test_add_user_to_group_success(mock_cursor):
    """
    Tester add_user_to_group avec une insertion réussie
    """
    project_id = 1
    user_id = 1
    permission = 1
    joined = True
    expected_user_group_id = 789

    mock_cursor.lastrowid = expected_user_group_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_user_to_group(
            project_id, user_id, permission, joined, cursor=mock_cursor
        )

        assert result == expected_user_group_id
        mock_cursor.execute.assert_called_once_with(
            _Requests.add_user_to_group, (project_id, user_id, permission, joined)
        )


def test_add_user_to_group_exception(mock_cursor):
    """
    Tester add_user_to_group lorsqu'une exception se produit
    """
    project_id = 1
    user_id = 1
    permission = 1
    joined = True

    mock_cursor.execute.side_effect = Exception("Erreur d'insertion")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_user_to_group(
            project_id, user_id, permission, joined, cursor=mock_cursor
        )

        assert isinstance(result, Exception)
        assert str(result) == "Erreur d'insertion"


def test_add_task_info_success(mock_cursor):
    """
    Tester add_task_info avec une insertion réussie
    """
    status = 1
    priority = 2
    title = "Task Title"
    description = "Task Description"
    dead_line = datetime.datetime(2024, 12, 31, 23, 59)
    covered = False
    assign = 1
    expected_task_info_id = 1011

    mock_cursor.lastrowid = expected_task_info_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_task_info(
            status, priority, title, description, dead_line, covered, assign, cursor=mock_cursor
        )

        assert result == expected_task_info_id
        mock_cursor.execute.assert_called_once_with(
            _Requests.add_task_info,
            (status, priority, title, description, dead_line, covered, assign),
        )


def test_add_task_info_exception(mock_cursor):
    """
    Tester add_task_info lorsqu'une exception se produit
    """
    status = 1
    priority = 2
    title = "Task Title"
    description = "Task Description"
    dead_line = datetime.datetime(2024, 12, 31, 23, 59)
    covered = False
    assign = 1

    mock_cursor.execute.side_effect = Exception("Erreur d'insertion")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_task_info(
            status, priority, title, description, dead_line, covered, assign, cursor=mock_cursor
        )

        assert isinstance(result, Exception)
        assert str(result) == "Erreur d'insertion"


def test_add_task_success(mock_cursor):
    """
    Test de la méthode add_task avec une insertion réussie
    """
    project_id = 1
    task_info_id = 1
    user_id = 1
    expected_task_id = 1200

    mock_cursor.lastrowid = expected_task_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_task(project_id, task_info_id, user_id, cursor=mock_cursor)

        assert result == expected_task_id
        mock_cursor.execute.assert_called_once_with(
            _Requests.add_task, (project_id, task_info_id, user_id)
        )


def test_add_task_exception(mock_cursor):
    """
    Test de la méthode add_task lorsqu'une exception se produit
    """
    project_id = 1
    task_info_id = 1
    user_id = 1

    mock_cursor.execute.side_effect = Exception("Insert error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_task(project_id, task_info_id, user_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Insert error"


def test_add_subtask_success(mock_cursor):
    """
    Test de la méthode add_subtask avec un scénario réussi
    """

    task_id = 1
    task_info_id = 1
    expected_subtask_id = 123

    mock_cursor.lastrowid = expected_subtask_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        subtask_id = DB_API.add_subtask(task_id, task_info_id, cursor=mock_cursor)

        assert subtask_id == expected_subtask_id
        mock_cursor.execute.assert_called_once_with(_Requests.add_subtask, (task_id, task_info_id))


def test_add_subtask_exception(mock_cursor):
    """
    Test de la méthode add_subtask lorsqu'une exception se produit
    """
    task_id = 1
    task_info_id = 1

    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.add_subtask(task_id, task_info_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Database error"


def test_add_user_to_task_group_success(mock_cursor):
    """
    Test de la méthode add_user_to_task_group avec un scénario réussi
    """

    task_project_id = 1
    user_id = 1
    expected_group_id = 456

    mock_cursor.lastrowid = expected_group_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        group_id = DB_API.add_user_to_task_group(task_project_id, user_id, cursor=mock_cursor)

        assert group_id == expected_group_id
        mock_cursor.execute.assert_called_once_with(
            _Requests.add_user_to_task_group, (task_project_id, user_id)
        )


def test_add_user_to_task_group_exception(mock_cursor):
    """
    Test de la méthode add_user_to_task_group lorsqu'une exception se produit
    """
    task_project_id = 1
    user_id = 1

    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.add_user_to_task_group(task_project_id, user_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Database error"


def test_get_user_id_by_username_success(mock_cursor):
    """
    Test de la méthode get_user_id_by_username avec un scénario réussi
    """

    username = "toto"
    expected_user_id = 1

    mock_cursor.fetchone.return_value = (expected_user_id,)

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        user_id = DB_API.get_user_id_by_username(username, cursor=mock_cursor)

        assert user_id == expected_user_id
        mock_cursor.execute.assert_called_once_with(_Requests.get_userID_by_username, (username,))


def test_get_user_id_by_username_not_found(mock_cursor):
    """
    Test de la méthode get_user_id_by_username lorsqu'aucun utilisateur n'est trouvé
    """
    username = "nonexistent_user"
    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        user_id = DB_API.get_user_id_by_username(username, cursor=mock_cursor)

        assert isinstance(user_id, Exception)
        assert str(user_id) == "'NoneType' object is not subscriptable"

        mock_cursor.execute.assert_called_once_with(_Requests.get_userID_by_username, (username,))


def test_get_all_projects_success(mock_cursor):
    """
    Test de la méthode get_all_projects avec un scénario réussi
    """

    test_projects = [(1, "Project 1"), (2, "Project 2")]

    mock_cursor.fetchall.return_value = test_projects

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        projects = DB_API.get_all_projects(cursor=mock_cursor)

        assert projects == test_projects
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_projects)


def test_get_all_projects_empty(mock_cursor):
    """
    Test de la méthode get_all_projects lorsqu'il n'y a pas de projets
    """

    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        projects = DB_API.get_all_projects(cursor=mock_cursor)

        assert projects == []
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_projects)


def test_get_all_tasks_success(mock_cursor):
    """
    Test de la méthode get_all_tasks avec un scénario réussi
    """
    test_tasks = [
        (1, "Task 1", "Description 1", "open", "high", 0, 1, "2024-12-31"),
        (2, "Task 2", "Description 2", "closed", "low", 1, 2, "2024-12-15"),
    ]

    mock_cursor.fetchall.return_value = test_tasks

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_tasks(cursor=mock_cursor)

        assert result == test_tasks
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_tasks)


def test_get_all_tasks_empty(mock_cursor):
    """
    Test de la méthode get_all_tasks lorsqu'il n'y a pas de tâches
    """

    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_tasks(cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(_Requests.get_all_tasks)


def test_get_user_email_success(mock_cursor):
    """
    Test de la méthode get_user_email avec un scénario réussi
    """
    test_user_id = 1
    test_email = ("user1@example.com",)

    mock_cursor.fetchone.return_value = test_email

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_user_email(test_user_id, cursor=mock_cursor)

        assert result == test_email
        mock_cursor.execute.assert_called_once_with(_Requests.get_user_email, (test_user_id,))


def test_get_user_email_not_found(mock_cursor):
    """
    Test de la méthode get_user_email lorsqu'aucun utilisateur n'est trouvé
    """
    test_user_id = 9999

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_user_email(test_user_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.get_user_email, (test_user_id,))


def test_add_task_group_success(mock_cursor):
    """
    Test de la méthode add_task_group avec un scénario réussi
    """
    mock_cursor.lastrowid = 1

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.add_task_group(cursor=mock_cursor)

        assert result == 1
        mock_cursor.execute.assert_called_once_with(_Requests.add_task_group)


def test_delete_user_success(mock_cursor):
    """
    Test de la méthode delete_user avec un scénario réussi
    """
    mock_cursor.execute.return_value = None
    test_user_id = 1

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_user(test_user_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.delete_user, (test_user_id,))


def test_delete_task_success(mock_cursor):
    """
    Test de la méthode delete_task avec un scénario réussi
    """
    test_task_id = 1
    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_task(test_task_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.delete_task, (test_task_id,))


def test_update_task_title_success(mock_cursor):
    """
    Tester la méthode update_task_title dans un scénario réussi
    """
    task_info_id = 1
    title = "Nouveau Titre"

    mock_cursor.rowcount = 1

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.update_task_title(title, task_info_id, cursor=mock_cursor)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_title, (title, task_info_id)
        )


def test_update_task_description_success(mock_cursor):
    """
    Tester la méthode update_task_description dans un scénario réussi
    """
    task_info_id = 1
    description = "Nouvelle description"

    mock_cursor.rowcount = 1

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.update_task_description(description, task_info_id, cursor=mock_cursor)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_description, (description, task_info_id)
        )


def test_update_task_priority_success(mock_cursor):
    """
    Tester la méthode update_task_priority dans un scénario réussi
    """
    task_info_id = 1
    priority = 2

    mock_cursor.rowcount = 1

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.update_task_priority(priority, task_info_id, cursor=mock_cursor)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_priority, (priority, task_info_id)
        )


def test_update_task_date_success(mock_cursor):
    """
    Tester la méthode update_task_date dans un scénario réussi
    """
    task_info_id = 1
    date = datetime.datetime(2024, 12, 31)

    mock_cursor.rowcount = 1

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.update_task_date(date, task_info_id, cursor=mock_cursor)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_date, (date, task_info_id)
        )


def test_get_task_infoID_by_taskID_success(mock_cursor):
    """
    Tester la méthode get_task_infoID_by_taskID dans un scénario réussi
    """
    task_id = 1
    expected_task_info_id = 42

    mock_cursor.fetchone.return_value = expected_task_info_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_task_infoID_by_taskID(task_id, cursor=mock_cursor)

        assert result == expected_task_info_id
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_task_infoID_by_taskID, (task_id,)
        )


def test_get_task_infoID_by_taskID_not_found(mock_cursor):
    """
    Tester la méthode get_task_infoID_by_taskID lorsqu'aucune information de tâche n'est trouvée
    """
    task_id = 9999

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_task_infoID_by_taskID(task_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_task_infoID_by_taskID, (task_id,)
        )


def test_delete_user_status_success(mock_cursor):
    """
    Tester la méthode delete_user_status avec un scénario réussi
    """
    user_id = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_user_status(user_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.delete_user_status, (user_id,))


def test_delete_user_status_exception(mock_cursor):
    """
    Tester la méthode delete_user_status lorsqu'une exception se produit
    """
    user_id = 1

    mock_cursor.execute.side_effect = Exception("Database error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_user_status(user_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Database error"


def test_get_tasks_by_project_id_empty(mock_cursor):
    """
    Tester la méthode get_tasks_by_project_id lorsqu'aucune tâche n'est trouvée
    """
    project_id = 1

    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_tasks_by_project_id(project_id, cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_tasks_by_project_id, (project_id,)
        )


def test_get_subtasks_by_task_id_empty(mock_cursor):
    """
    Tester la méthode get_subtasks_by_task_id lorsqu'aucune sous-tâche n'est trouvée
    """
    task_id = 1

    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_subtasks_by_task_id(task_id, cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(_Requests.get_subtasks_by_task_id, (task_id,))


def test_get_users_in_project_by_project_id_empty(mock_cursor):
    """
    Tester la méthode get_users_in_project_by_project_id lorsqu'aucun utilisateur n'est trouvé
    """
    project_id = 1

    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_users_in_project_by_project_id(project_id, cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_users_in_project_by_project_id, (project_id,)
        )


def test_get_email_success(mock_cursor):
    """
    Tester la méthode get_email dans un scénario réussi
    """
    email = "miaw@redgally.xyz"
    expected_email = ("miaw@redgally.xyz",)

    mock_cursor.fetchone.return_value = expected_email

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_email(email, cursor=mock_cursor)

        assert result == expected_email
        mock_cursor.execute.assert_called_once_with(_Requests.get_email, (email,))


def test_get_email_not_found(mock_cursor):
    """
    Tester la méthode get_email lorsqu'aucun email n'est trouvé
    """
    email = "random_email@test.com"

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_email(email, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.get_email, (email,))


def test_get_user_success(mock_cursor):
    """
    Tester la méthode get_user dans un scénario réussi
    """
    username = "miaw"
    expected_user = (1, "miaw", "miaw@redgally.xyz")

    mock_cursor.fetchone.return_value = expected_user

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_user(username, cursor=mock_cursor)

        assert result == expected_user
        mock_cursor.execute.assert_called_once_with(_Requests.get_user, (username,))


def test_get_user_not_found(mock_cursor):
    """
    Tester la méthode get_user lorsqu'aucun utilisateur n'est trouvé
    """
    username = "random_username"

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_user(username, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.get_user, (username,))


def test_get_userID_by_email_success(mock_cursor):
    """
    Tester la méthode get_userID_by_email dans un scénario réussi
    """
    email = "user1@example.com"
    expected_user_id = (1,)

    mock_cursor.fetchone.return_value = expected_user_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_userID_by_email(email, cursor=mock_cursor)

        assert result == expected_user_id
        mock_cursor.execute.assert_called_once_with(_Requests.get_userID_by_email, (email,))


def test_get_userID_by_email_not_found(mock_cursor):
    """
    Tester la méthode get_userID_by_email lorsqu'aucun utilisateur n'est trouvé
    """
    email = "user1@example.com"

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_userID_by_email(email, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.get_userID_by_email, (email,))


def test_add_user_status_success(mock_cursor):
    """
    Tester la méthode add_user_status dans un scénario réussi
    """
    user_id = 1
    status = 0
    expected_status_id = 123

    mock_cursor.lastrowid = expected_status_id

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_user_status(user_id, status, cursor=mock_cursor)

        assert result == expected_status_id
        mock_cursor.execute.assert_called_once_with(_Requests.add_user_status, (user_id, status))


def test_add_user_status_exception(mock_cursor):
    """
    Tester la méthode add_user_status lorsqu'une exception se produit
    """
    user_id = 1
    status = 0

    mock_cursor.execute.side_effect = Exception("Erreur d'insertion")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_user_status(user_id, status, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Erreur d'insertion"


def test_set_invites_status_success(mock_cursor):
    """
    Test the set_invites_status method in a successful scenario
    """
    project_id = 1
    user_id = 1
    joined = True

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_invites_status(joined, project_id, user_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.set_invites_status, (joined, project_id, user_id)
        )


def test_set_invites_status_exception(mock_cursor):
    """
    Test the set_invites_status method when an exception occurs
    """
    project_id = 1
    user_id = 1
    joined = True

    mock_cursor.execute.side_effect = Exception("Update error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_invites_status(joined, project_id, user_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Update error"


def test_set_user_permission_success(mock_cursor):
    """
    Test the set_user_permission method in a successful scenario
    """
    project_id = 1
    user_id = 1
    permission = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_user_permission(project_id, user_id, permission, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_user_perm, (project_id, user_id, permission)
        )


def test_set_user_permission_exception(mock_cursor):
    """
    Test the set_user_permission method when an exception occurs
    """
    project_id = 1
    user_id = 1
    permission = 1

    mock_cursor.execute.side_effect = Exception("Update error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_user_permission(project_id, user_id, permission, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Update error"


def test_set_user_status_success(mock_cursor):
    """
    Test the set_user_status method in a successful scenario
    """
    user_id = 1
    status = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_user_status(user_id, status, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_user_status, (status, user_id)
        )


def test_set_user_status_exception(mock_cursor):
    """
    Test the set_user_status method when an exception occurs
    """
    user_id = 1
    status = 1

    mock_cursor.execute.side_effect = Exception("Update error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_user_status(user_id, status, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Update error"


def test_get_totp_secret_success(mock_cursor):
    """
    Test the get_totp_secret method in a successful scenario
    """
    email = "user@example.com"
    expected_secret = "secret"

    mock_cursor.fetchone.return_value = (expected_secret,)

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_totp_secret(email, cursor=mock_cursor)

        assert result == expected_secret
        mock_cursor.execute.assert_called_once_with(_Requests.get_totp_secret, (email,))


def test_get_totp_secret_not_found(mock_cursor):
    """
    Test the get_totp_secret method when no secret is found
    """
    email = "user@example.com"

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_totp_secret(email, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.get_totp_secret, (email,))


def test_get_user_permission_success(mock_cursor):
    """
    Test the get_user_permission method in a successful scenario
    """
    project_id = 1
    user_id = 1
    expected_permission = "read"

    mock_cursor.fetchone.return_value = expected_permission

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_user_permission(project_id, user_id, cursor=mock_cursor)

        assert result == expected_permission
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_user_permission, (project_id, user_id)
        )


def test_get_user_permission_not_found(mock_cursor):
    """
    Test the get_user_permission method when no permission is found
    """
    project_id = 1
    user_id = 1

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_user_permission(project_id, user_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_user_permission, (project_id, user_id)
        )


def test_set_totp_secret_success(mock_cursor):
    """
    Test the set_totp_secret method in a successful scenario
    """
    email = "user@example.com"
    secret = "new_secret"

    mock_cursor.execute.return_value = True

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_totp_secret(email, secret, cursor=mock_cursor)

        assert result is True
        mock_cursor.execute.assert_called_once_with(_Requests.set_totp_secret, (secret, email))


def test_set_totp_secret_exception(mock_cursor):
    """
    Test the set_totp_secret method when an exception occurs
    """
    email = "user@example.com"
    secret = "new_secret"

    mock_cursor.execute.side_effect = Exception("Update error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.set_totp_secret(secret, email, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Update error"


def test_delete_project_success(mock_cursor):
    """
    Test the delete_project method in a successful scenario
    """
    project_id = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_project(project_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.delete_project, (project_id,))


def test_delete_project_exception(mock_cursor):
    """
    Test the delete_project method when an exception occurs
    """
    project_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_project(project_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_get_task_info_by_task_id_success(mock_cursor):
    """
    Test the get_task_info_by_task_id method in a successful scenario
    """
    task_id = 1
    expected_info = ("Task Title", "Description", "Open", "High", "No", "User 1", "2024-12-31")

    mock_cursor.fetchall.return_value = expected_info

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_task_info_by_task_id(task_id, cursor=mock_cursor)

        assert result == expected_info
        mock_cursor.execute.assert_called_once_with(_Requests.get_task_info_by_task_id, (task_id,))


def test_get_task_info_by_task_id_not_found(mock_cursor):
    """
    Test the get_task_info_by_task_id method when no task info is found
    """
    task_id = 1

    mock_cursor.fetchall.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_task_info_by_task_id(task_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.get_task_info_by_task_id, (task_id,))


def test_get_subtask_info_by_subtask_id_success(mock_cursor):
    """
    Test the get_subtask_info_by_subtask_id method in a successful scenario
    """
    subtask_id = 1
    expected_info = ("Subtask Title", "Description", "Open", "High", "No", "User 1", "2024-12-31")

    mock_cursor.fetchall.return_value = expected_info

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_subtask_info_by_subtask_id(subtask_id, cursor=mock_cursor)

        assert result == expected_info
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_subtask_info_by_subtask_id, (subtask_id,)
        )


def test_get_subtask_info_by_subtask_id_not_found(mock_cursor):
    """
    Test the get_subtask_info_by_subtask_id method when no subtask info is found
    """
    subtask_id = 1

    mock_cursor.fetchall.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_subtask_info_by_subtask_id(subtask_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_subtask_info_by_subtask_id, (subtask_id,)
        )


def test_delete_user_group_success(mock_cursor):
    """
    Test the delete_user_group method in a successful scenario
    """
    user_group_id = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_user_group(user_group_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.delete_users_groups, (user_group_id,)
        )


def test_delete_user_group_exception(mock_cursor):
    """
    Test the delete_user_group method when an exception occurs
    """
    user_group_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_user_group(user_group_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_delete_tasks_groups_success(mock_cursor):
    """
    Test the delete_tasks_groups method in a successful scenario
    """
    task_group_id = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_tasks_groups(task_group_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.delete_tasks_groups, (task_group_id,)
        )


def test_delete_tasks_groups_exception(mock_cursor):
    """
    Test the delete_tasks_groups method when an exception occurs
    """
    task_group_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_tasks_groups(task_group_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_delete_tasks_infos_success(mock_cursor):
    """
    Test the delete_tasks_infos method in a successful scenario
    """
    task_info_id = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_tasks_infos(task_info_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.delete_tasks_infos, (task_info_id,))


def test_delete_tasks_infos_exception(mock_cursor):
    """
    Test the delete_tasks_infos method when an exception occurs
    """
    task_info_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_tasks_infos(task_info_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_delete_tasks_success(mock_cursor):
    """
    Test the delete_tasks method in a successful scenario
    """
    task_id = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_tasks(task_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(_Requests.delete_tasks, (task_id,))


def test_delete_tasks_exception(mock_cursor):
    """
    Test the delete_tasks method when an exception occurs
    """
    task_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_tasks(task_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_check_projects_success(mock_cursor):
    """
    Test the check_projects method in a successful scenario
    """
    project_name = "Project Gamma"
    expected_result = True

    mock_cursor.fetchone.return_value = (expected_result,)

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.check_projects(project_name, cursor=mock_cursor)

        assert result == expected_result
        mock_cursor.execute.assert_called_once_with(_Requests.check_projects, (project_name,))


def test_check_projects_not_found(mock_cursor):
    """
    Test the check_projects method when no project is found
    """
    project_name = "Project Gamma"

    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.check_projects(project_name, cursor=mock_cursor)

        assert result is False
        mock_cursor.execute.assert_called_once_with(_Requests.check_projects, (project_name,))


def test_delete_users_from_users_tasks_groups_success(mock_cursor):
    """
    Test the delete_users_from_users_tasks_groups method in a successful scenario
    """
    task_group_id = 1

    mock_cursor.execute.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_users_from_users_tasks_groups(task_group_id, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.delete_users_from_users_tasks_groups,
            (task_group_id,),
        )


def test_delete_users_from_users_tasks_groups_exception(mock_cursor):
    """
    Test the delete_users_from_users_tasks_groups method when an exception occurs
    """
    task_group_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_users_from_users_tasks_groups(task_group_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_update_task_status_success(mock_cursor):
    """
    Test the update_task_status method in a successful scenario
    """
    task_id = 1
    status = 1

    mock_cursor.execute.return_value = None
    mock_cursor.rowcount = 1

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.update_task_status(task_id, status, cursor=mock_cursor)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_status,
            (
                status,
                task_id,
            ),
        )


def test_update_task_status_exception(mock_cursor):
    """
    Test the update_task_status method when an exception occurs
    """
    task_id = 1
    status = 1

    mock_cursor.execute.side_effect = Exception("Update error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.update_task_status(task_id, status, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Update error"


def test_update_task_title_failure(mock_cursor):
    """
    Test the update_task_title method when the update fails
    """
    task_info_id = 1
    title = "New Title"

    mock_cursor.rowcount = 0

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.update_task_title(title, task_info_id, cursor=mock_cursor)

        assert result is False
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_title,
            (
                title,
                task_info_id,
            ),
        )


def test_update_task_description_failure(mock_cursor):
    """
    Test the update_task_description method when the update fails
    """
    task_info_id = 1
    description = "New Description"

    mock_cursor.rowcount = 0

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.update_task_description(description, task_info_id, cursor=mock_cursor)

        assert result is False
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_description,
            (
                description,
                task_info_id,
            ),
        )


def test_update_task_priority_failure(mock_cursor):
    """
    Test the update_task_priority method when the update fails
    """
    task_info_id = 1
    priority = 2

    mock_cursor.rowcount = 0

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.update_task_priority(priority, task_info_id, cursor=mock_cursor)

        assert result is False
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_priority,
            (
                priority,
                task_info_id,
            ),
        )


def test_update_task_date_failure(mock_cursor):
    """
    Test the update_task_date method when the update fails
    """
    task_info_id = 1
    date = datetime.datetime(2024, 12, 31)

    mock_cursor.rowcount = 0

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.update_task_date(date, task_info_id, cursor=mock_cursor)

        assert result is False
        mock_cursor.execute.assert_called_once_with(
            _Requests.update_task_date,
            (
                date,
                task_info_id,
            ),
        )


def test_delete_task_exception(mock_cursor):
    """
    Test the delete_task method when an exception occurs
    """
    task_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_task(task_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_delete_user_exception(mock_cursor):
    """
    Test the delete_user method when an exception occurs
    """
    user_id = 1

    mock_cursor.execute.side_effect = Exception("Delete error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.delete_user(user_id, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Delete error"


def test_add_task_group_exception(mock_cursor):
    """
    Test the add_task_group method when an exception occurs
    """
    mock_cursor.execute.side_effect = Exception("Insert error")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func), patch(
        "backend.db_helper.cm_conn", return_value=lambda func: func
    ):
        result = DB_API.add_task_group(cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Insert error"


def test_get_project_in_users_groups_userid_success(mock_cursor):
    """
    Test the get_project_in_users_groups_userid method in a successful scenario
    """
    user_id = 1
    expected_projects = [
        (1, "Project 1", "read", True),
        (2, "Project 2", "write", False),
    ]

    mock_cursor.fetchall.return_value = expected_projects

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_project_in_users_groups_userid(user_id, cursor=mock_cursor)

        assert result == expected_projects
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_project_in_users_groups, (user_id,)
        )


def test_get_project_in_users_groups_userid_empty(mock_cursor):
    """
    Test the get_project_in_users_groups_userid method when no projects are found
    """
    user_id = 1

    mock_cursor.fetchall.return_value = []

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_project_in_users_groups_userid(user_id, cursor=mock_cursor)

        assert result == []
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_project_in_users_groups, (user_id,)
        )


def test_get_all_infos_from_email_success(mock_cursor):
    """
    Teste la méthode get_all_infos_from_email dans un scénario de succès.
    """
    email = "test@example.com"
    expected_result = (1, "testuser", "test@example.com", "hashed_password")

    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = expected_result

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_infos_from_email(email, cursor=mock_cursor)

        assert result == expected_result
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_all_infos_from_email,
            (email,),
        )


def test_get_all_infos_from_email_no_result(mock_cursor):
    """
    Teste la méthode get_all_infos_from_email lorsqu'aucun résultat n'est trouvé.
    """
    email = "nonexistent@example.com"

    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_infos_from_email(email, cursor=mock_cursor)

        assert result is None
        mock_cursor.execute.assert_called_once_with(
            _Requests.get_all_infos_from_email,
            (email,),
        )


def test_get_all_infos_from_email_exception(mock_cursor):
    """
    Teste la méthode get_all_infos_from_email lorsqu'une exception se produit.
    """
    email = "test@example.com"

    mock_cursor.execute.side_effect = Exception("Erreur de requête")

    with patch("backend.db_helper.cm_cursor", return_value=lambda func: func):
        result = DB_API.get_all_infos_from_email(email, cursor=mock_cursor)

        assert isinstance(result, Exception)
        assert str(result) == "Erreur de requête"
