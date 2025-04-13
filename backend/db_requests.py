class _Requests:
    get_all_users = """
        SELECT userID, username, email, is_google_user
        FROM users;
    """

    get_all_infos_from_email = """SELECT * FROM users WHERE email = %s;"""

    get_password_from_email = """SELECT password FROM users WHERE email = %s;"""

    update_user_password = """UPDATE users SET password = %s WHERE email = %s;"""

    get_project_id_by_project_name = """
        SELECT projectID
        FROM projects
        WHERE projects.name = %s;
    """

    get_projects_by_user_id = """
        SELECT p.projectID, p.name, ug.joined
        FROM projects p
        JOIN users_groups ug ON p.projectID = ug.projectID
        WHERE ug.userID = %s;
    """

    get_project_in_users_groups = """
        SELECT ug.projectID, p.name, ug.permission, ug.joined
        FROM users_groups ug
        JOIN projects p ON p.projectID = ug.projectID
        WHERE userID = %s;
    """

    get_tasks_by_project_id = """
        SELECT t.taskID, ti.title, ti.description, ti.status,
               ti.priority, ti.covered, ti.assign, ti.dead_line
        FROM tasks t
        JOIN tasks_infos ti ON t.task_infoID = ti.task_infoID
        WHERE t.projectID = %s;
    """

    get_subtasks_by_task_id = """
        SELECT st.subtaskID, ti.title, ti.description, ti.status,
               ti.priority, ti.covered, ti.assign, ti.dead_line
        FROM subtasks st
        JOIN tasks_infos ti ON st.task_infoID = ti.task_infoID
        WHERE st.taskID = %s;
    """

    get_users_in_project_by_project_id = """
        SELECT u.userID, u.username, ug.permission
        FROM users u
        JOIN users_groups ug ON u.userID = ug.userID
        WHERE ug.projectID = %s;
    """

    get_users_in_tasks_group_by_group_id = """
        SELECT u.userID, u.username, utg.task_projectID
        FROM users u
        JOIN users_tasks_groups utg ON u.userID = utg.userID
        WHERE utg.task_projectID = %s;
    """

    get_userID_by_username = """
        SELECT userID
        FROM users
        WHERE username = %s;
    """

    get_all_status = """
        SELECT userID, status
        FROM status;
    """

    get_all_projects = """
        SELECT projectID, name
        FROM projects;
    """

    get_all_tasks = """
        SELECT t.taskID, ti.title, ti.description, ti.status,
               ti.priority, ti.covered, ti.assign, ti.dead_line
        FROM tasks t
        JOIN tasks_infos ti ON t.task_infoID = ti.task_infoID;
    """

    get_user_email = """
        SELECT email
        FROM users
        WHERE userID = %s;
    """

    get_email = """
        SELECT email
        FROM users
        WHERE email = %s;
    """

    get_user = """
        SELECT username
        FROM users
        WHERE username = %s;
    """

    get_userID_by_email = """
        SELECT userID
        FROM users
        WHERE email = %s;
    """

    add_user = """
        INSERT INTO users (username, password, email, is_google_user)
        VALUES (%s, %s, %s, %s);
    """

    add_project = """
        INSERT INTO projects (name)
        VALUES (%s);
    """

    add_user_to_group = """
        INSERT INTO users_groups (projectID, userID, permission, joined)
        VALUES (%s, %s, %s, %s);
    """

    add_task_info = """
        INSERT INTO tasks_infos (status, priority, title, description,
                                 dead_line, covered, assign)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    set_invites_status = """
        UPDATE users_groups
        SET joined = %s
        WHERE projectID = %s
          AND userID = %s;
    """

    add_task = """
        INSERT INTO tasks (projectID, task_infoID, userID)
        VALUES (%s, %s, %s);
    """

    add_subtask = """
        INSERT INTO subtasks (taskID, task_infoID)
        VALUES (%s, %s);
    """

    add_user_to_task_group = """
        INSERT INTO users_tasks_groups (task_projectID, userID)
        VALUES (%s, %s);
    """

    add_task_group = "INSERT INTO tasks_groups () VALUES ();"

    delete_user = "DELETE FROM users WHERE userID = %s;"

    delete_task = "DELETE FROM tasks WHERE taskID = %s;"

    get_user_permission = (
        "SELECT permission FROM users_groups WHERE projectID = %s AND userID = %s;"
    )

    delete_project = "DELETE FROM projects WHERE projectID = %s;"

    get_task_info_by_task_id = (
        "SELECT ti.title, ti.description, ti.status, ti.priority, ti.covered,"
        "ti.assign, ti.dead_line "
        "FROM tasks t "
        "JOIN tasks_infos ti ON t.task_infoID = ti.task_infoID "
        "WHERE t.taskID = %s;"
    )

    get_subtask_info_by_subtask_id = (
        "SELECT ti.title, ti.description, ti.status, ti.priority, ti.covered,"
        "ti.assign, ti.dead_line "
        "FROM subtasks s "
        "JOIN tasks_infos ti ON s.task_infoID = ti.task_infoID "
        "WHERE s.subtaskID = %s;"
    )

    delete_users_groups = "DELETE FROM users_groups WHERE projectID = %s;"

    delete_tasks_groups = (
        "DELETE tg FROM tasks_groups tg INNER JOIN tasks t ON t.assign = tg.task_projectID WHERE "
        "t.projectID = %s;"
    )

    delete_tasks_infos = (
        "DELETE ti FROM tasks_infos ti INNER JOIN tasks t ON "
        "t.task_infoID = ti.task_infoID WHERE t.projectID = %s;"
    )

    delete_tasks = "DELETE FROM tasks where projectID = %s;"

    check_projects = "SELECT COUNT(*) AS project_count FROM projects WHERE name = %s;"

    delete_users_from_users_tasks_groups = (
        "DELETE FROM users_tasks_groups WHERE task_projectID = %s;"
    )

    update_task_status = "UPDATE tasks_infos SET status = %s WHERE task_infoID = %s;"

    update_task_title = "UPDATE tasks_infos SET title = %s WHERE task_infoID = %s;"

    get_task_infoID_by_taskID = "SELECT task_infoID FROM tasks WHERE taskID = %s;"

    get_task_infoID_by_subtaskID = "SELECT task_infoID FROM subtasks WHERE subtaskID = %s;"

    update_task_description = "UPDATE tasks_infos SET description = %s WHERE task_infoID = %s;"

    update_task_priority = "UPDATE tasks_infos SET priority = %s WHERE task_infoID = %s;"

    update_task_date = "UPDATE tasks_infos SET dead_line = %s WHERE task_infoID = %s;"

    get_totp_secret = "SELECT totp_secret FROM users WHERE email = %s;"

    set_totp_secret = "UPDATE users SET totp_secret = %s WHERE email = %s;"

    update_user_status = "UPDATE status SET status = %s WHERE userID = %s;"

    update_user_perm = """
        UPDATE users_groups
        SET permission = %s
        WHERE projectID = %s
          AND userID = %s;
    """

    add_user_status = "INSERT INTO status (userID, status) VALUES (%s, %s);"

    delete_user_status = "DELETE * FROM status WHERE userID = %s;"
