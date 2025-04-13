import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_db_api():
    """Fixture pour simuler DB_API"""
    with patch('backend.db_api.DB_API') as mock_class:
        mock_instance = mock_class.return_value
        yield mock_instance


def test_deconnexion_success(mock_db_api):
    """Test d'une déconnexion réussie"""
    user_id = 1
    mock_db_api.set_user_status(user_id, 0)

    mock_db_api.set_user_status.assert_called_once_with(user_id, 0)


def test_delete_account_success(mock_db_api):
    """Test de la suppression réussie d'un compte"""
    user_id = 1
    mock_db_api.get_userID_by_email.return_value = [user_id]

    # Test suppression du statut
    mock_db_api.delete_user_status(user_id)
    mock_db_api.delete_user_status.assert_called_once_with(user_id)

    # Test suppression de l'utilisateur
    mock_db_api.delete_user(user_id)
    mock_db_api.delete_user.assert_called_once_with(user_id)


def test_add_project_new(mock_db_api):
    """Test l'ajout d'un nouveau projet"""
    project_name = "Test Project"
    user_id = 1
    project_id = 1

    mock_db_api.check_projects.return_value = False
    mock_db_api.add_project.return_value = project_id

    result = mock_db_api.check_projects(project_name)
    assert result is False
    mock_db_api.check_projects.assert_called_once_with(project_name)

    new_project_id = mock_db_api.add_project(project_name)
    assert new_project_id == project_id
    mock_db_api.add_project.assert_called_once_with(project_name)

    mock_db_api.add_user_to_group(project_id, user_id, 2, 2)
    mock_db_api.add_user_to_group.assert_called_once_with(project_id, user_id, 2, 2)


def test_add_project_existing(mock_db_api):
    """Test tentative d'ajout d'un projet existant"""
    project_name = "Existing Project"
    mock_db_api.check_projects.return_value = True

    result = mock_db_api.check_projects(project_name)
    assert result is True
    mock_db_api.check_projects.assert_called_once_with(project_name)


def test_load_projects(mock_db_api):
    """Test du chargement des projets d'un utilisateur"""
    user_id = 1
    test_projects = [(1, "Project Alpha", 2), (2, "Project Beta", 2)]

    mock_db_api.get_projects_by_user_id.return_value = test_projects
    projects = mock_db_api.get_projects_by_user_id(user_id)

    assert projects == test_projects
    mock_db_api.get_projects_by_user_id.assert_called_once_with(user_id)


def test_get_project_users(mock_db_api):
    """Test de la récupération des utilisateurs d'un projet"""
    project_id = 1
    test_users = [(1, "Jules@example.com", 2), (2, "user2@example.com", 1)]

    mock_db_api.get_users_in_project_by_project_id.return_value = test_users
    users = mock_db_api.get_users_in_project_by_project_id(project_id)

    assert users == test_users
    mock_db_api.get_users_in_project_by_project_id.assert_called_once_with(project_id)


def test_user_status_fonctions(mock_db_api):
    """Test des opérations sur le statut utilisateur"""
    status_list = [(1, True), (2, False)]

    mock_db_api.get_all_status.return_value = status_list
    result = mock_db_api.get_all_status()
    assert result == status_list
    mock_db_api.get_all_status.assert_called_once()

    user_id = 1
    status = 1
    mock_db_api.set_user_status(user_id, status)
    mock_db_api.set_user_status.assert_called_once_with(user_id, status)


def test_add_user_success(mock_db_api):
    selected_user = "Marius"
    mock_db_api.assign_user_dropdown.currentText.return_value = selected_user
    mock_db_api.is_user_already_assigned.return_value = False

    user = mock_db_api.assign_user_dropdown.currentText()
    mock_db_api.is_user_already_assigned(user)


def test_add_user_already_assigned(mock_db_api):
    """Test lorsque l'utilisateur est déjà assigné."""
    selected_user = "Hugo"

    mock_db_api.assign_user_dropdown.currentText.return_value = selected_user
    mock_db_api.is_user_already_assigned.return_value = True

    result = mock_db_api.is_user_already_assigned(selected_user)
    assert result is True
    mock_db_api.add_selected_user.assert_not_called()

    mock_db_api.is_user_already_assigned.assert_called_once_with(selected_user)
    mock_db_api.assigned_users_list.addItem.assert_not_called()


def test_remove_user_success(mock_db_api):
    """Test de suppression réussie d'un utilisateur."""
    user = "Marius"
    mock_db_api.remove_user_from_task(user)
    mock_db_api.remove_user_from_task.assert_called_once_with(user)


def test_remove_user_no_user_selected(mock_db_api):
    """Test de suppression d'un utilisateur sans utilisateur sélectionné."""
    mock_db_api.assigned_users_list.currentItem.return_value = None

    mock_db_api.remove_selected_user()

    mock_db_api.assigned_users_list.takeItem.assert_not_called()


def test_remove_user_no_user_found(mock_db_api):
    """Test de suppression d'un utilisateur non trouvé."""
    selected_user = "Marius"
    mock_db_api.assigned_users_list.currentItem.return_value = selected_user
    mock_db_api.assigned_users_list.takeItem.return_value = None

    mock_db_api.remove_selected_user()

    mock_db_api.assigned_users_list.takeItem.assert_not_called()


def test_add_task_success(mock_db_api):
    """Test d'ajout de tâche réussi."""
    project_id = 1
    task_info_id = 1
    user_id = 1
    mock_db_api.add_task_info()
    mock_db_api.add_task(project_id, task_info_id, user_id)
    mock_db_api.add_task_info.assert_called_once()
    mock_db_api.add_task.assert_called_once_with(project_id, task_info_id, user_id)


def test_add_subtask_success(mock_db_api):
    """Test d'ajout de sous-tâche réussi."""
    project_id = 1
    task_info_id = 1
    user_id = 1
    mock_db_api.add_subtask_info()
    mock_db_api.add_subtask(project_id, task_info_id, user_id)
    mock_db_api.add_subtask_info.assert_called_once()
    mock_db_api.add_subtask.assert_called_once_with(project_id, task_info_id, user_id)


def test_load_task_info(mock_db_api):
    """Test du chargement des informations de tâche."""
    task_id = 1
    task_info = ("Task 1", "Description 1", "Status 1", "Priority 1", "Covered 1", "Assign 1", "Dead Line 1")

    mock_db_api.get_task_info_by_task_id.return_value = task_info

    result = mock_db_api.get_task_info_by_task_id(task_id)
    assert result == task_info
    mock_db_api.get_task_info_by_task_id.assert_called_once_with(task_id)


def test_delete_task_success(mock_db_api):
    """Test de suppression de tâche réussie."""
    task_id = 1
    mock_db_api.delete_task(task_id)
    mock_db_api.delete_task.assert_called_once_with(task_id)


def test_delete_task_no_task_id(mock_db_api):
    """Test de suppression de tâche sans ID de tâche."""
    task_id = None

    if task_id is not None:
        mock_db_api.delete_task(task_id)

    mock_db_api.delete_task.assert_not_called()


def test_delete_project_success(mock_db_api):
    """Test de suppression de projet réussie."""
    project_id = 1

    mock_db_api.delete_project(project_id)

    mock_db_api.delete_project.assert_called_once_with(project_id)


def test_delete_project_no_project_id(mock_db_api):
    """Test de suppression de projet sans ID de projet."""
    project_id = None

    if project_id is not None:
        mock_db_api.delete_project(project_id)

    mock_db_api.delete_project.assert_not_called()


def test_mark_completed_success(mock_db_api):
    """Test de marquage de tâche comme complétée."""
    task_infoID = 1
    mock_db_api.update_task_status(task_infoID, 1)
    mock_db_api.update_task_status.assert_called_once_with(task_infoID, 1)


def test_mark_completed_no_task_infoID(mock_db_api):
    """Test de marquage de tâche sans ID d'information de tâche."""
    task_infoID = None

    if task_infoID is not None:
        mock_db_api.update_task_status(task_infoID, 1)

    mock_db_api.update_task_status.assert_not_called()


def test_accept_project_success(mock_db_api):
    """Test d'acceptation de projet réussie."""
    project_id = 1
    user_id = 1
    mock_db_api.accept_project(project_id, user_id)
    mock_db_api.accept_project.assert_called_once_with(project_id, user_id)


def test_send_invitation_success(mock_db_api):
    """Test d'envoi d'invitation réussi."""
    project_id = 1
    user_id = 1
    permission = 0
    mock_db_api.add_user_to_group(
        project_id=project_id, user_id=user_id, permission=permission, joined=False
    )
    mock_db_api.add_user_to_group.assert_called_once_with(
        project_id=project_id, user_id=user_id, permission=permission, joined=False
    )


