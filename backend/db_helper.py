import logging
from functools import partial
from typing import Callable, Optional, List, Union, TypeAlias, Any

import mysql.connector
from mysql.connector import errorcode
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

from backend.config import DB_HOST, DB_USER, DB_DATABASE, DB_PASSWORD

ResultType: TypeAlias = Union[List[RowType], Optional[RowType], str, Exception]

_log = logging.getLogger(__name__)


def cm_cursor() -> Callable:
    """
    Ce décorateur créer un curseur depuis une connexion vers une bdd.

    Ce décorateur est utilsé pour chaque requête SQL vers la base de données.
    Il crée automatiquement le curseur, puis le close une fois la fonction terminée.
    Utilisé en tant que "context manager".
    :return: Le résultat de la fonction enfante ou une Exception en cas d'erreur
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> ResultType:
            global conn
            if not isinstance(conn, MySQLConnectionAbstract):
                _conn = _create_conn()
                assert _conn
                assert _conn.is_connected(), "La db est injoinable"
                conn = _conn

            # Créer un curseur tamponné
            cursor = kwargs.get("cursor", None)
            if cursor:
                kwargs.pop("cursor")
            else:
                # Notez l'argument buffered=True
                cursor = conn.cursor(buffered=True)

            try:
                res = func(cursor=cursor, *args, **kwargs)
            except Exception as e:
                res = e
            finally:
                cursor.close()
            return res

        return wrapper

    return decorator


def create_conn(
    host: str, user: str, password: str, database: str
) -> Optional[Union[MySQLConnectionAbstract, PooledMySQLConnection]]:
    """
    Cette fonction est utilisée pour créer la connexion vers la base de données.

    :param host: Ip ou le nom du server MYSQL
    :param user: Utilisateur se connectant au server MYSQL
    :param password: Password de l'utilisateur
    :param database: La base de donnée cible
    :return: La connexion sinon None en cas d'echec
    """
    global conn
    try:
        _log.debug(f"Création de la connexion vers la bdd {host=} {user=} {database=}")
        connexion = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        _log.debug("Connexion effectuée avec succes")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            _log.error(
                "Accès refusé. Vérifiez votre nom d'utilisateur ou votre mot de passe."
            )  # Ne doit pas apparaitre sauf si mal config coté server
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            _log.error("La base de données spécifiée n'existe pas.")
        elif err.errno == errorcode.CR_CONN_HOST_ERROR:
            _log.error("Impossible de se connecter au serveur mysql (mauvaise ip ?).")
        elif err.errno == errorcode.CR_CONNECTION_ERROR:
            _log.error("Erreur de connexion à la base de données.")
        elif err.errno == errorcode.CR_SERVER_LOST:
            _log.error("La connexion au serveur MySQL a été perdue.")
        else:
            _log.error(f"Erreur MySQL: {err}")
        connexion = None
    conn = connexion
    return conn


_create_conn = partial(
    create_conn, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE
)  # Evite de réecrire a chaque fois l'host, l'user, le password et la database ...
conn: Optional[Union[MySQLConnectionAbstract, PooledMySQLConnection]] = _create_conn()


def cm_conn() -> Callable:
    """
    Ce décorateur est utilisé pour les rollback ou les commits sur la DB.

    Utilisé seulement pour les ajouts dans la base de données,
    les modifications et les suppressions, en tant que "context manager".
    :return: True si commit, Exception si rollback
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Union[Any, Exception]:
            global conn
            if not isinstance(conn, MySQLConnectionAbstract):
                _conn: Optional[Union[MySQLConnectionAbstract, PooledMySQLConnection]] = (
                    _create_conn()
                )
                if _conn is None or not _conn.is_connected():
                    return False
                conn = _conn

            res = func(*args, **kwargs)
            if isinstance(res, Exception):
                conn.rollback()
                _log.debug("Rollback effectué")
            else:
                conn.commit()
                _log.debug("Commit effectué")
            return res

        return wrapper

    return decorator


if __name__ == "__main__":
    _create_conn()
