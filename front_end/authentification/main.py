import sys
import os
import threading
from queue import Queue
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFontDatabase, QFont

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, project_root)

from authentification import MainWindow  # noqa
from api.api_google import app as flask_app  # noqa

message_queue = Queue()
queue_lock = threading.Lock()


def load_sf_font():
    """
    Charge la police SF Pro et applique-la comme police par défaut de l'application.
    """
    font_ids = []
    font_ids.append(QFontDatabase.addApplicationFont(":/fonts/SF-Pro-Text-Regular.ttf"))
    font_ids.append(QFontDatabase.addApplicationFont(":/fonts/SF-Pro-Text-Bold.ttf"))
    font_ids.append(QFontDatabase.addApplicationFont(":/fonts/SF-Pro-Text-Italic.ttf"))

    if -1 in font_ids:
        print("[PyQt] Échec du chargement de la SF Font")
    else:
        print("[PyQt] SF Font chargée avec succès")

    app_font = QFont("SF Pro Text", 10)  # Définir "SF Pro Text" comme police par défaut
    QtWidgets.QApplication.instance().setFont(app_font)


def load_stylesheet(app):
    """
    Charge le fichier de style QSS et applique-le à l'application.
    """
    try:
        with open("style.qss", "r") as style_file:
            style = style_file.read()
            app.setStyleSheet(style)
            print("[PyQt] Fichier de style chargé avec succès.")
    except FileNotFoundError:
        print("[PyQt] Fichier style.qss introuvable. Aucun style appliqué.")
    except Exception as e:
        print(f"[PyQt] Erreur lors du chargement du fichier de style : {e}")


def run_flask():
    """
    Démarre le serveur Flask dans un thread séparé.
    """
    flask_app.config["message_queue"] = message_queue
    flask_app.config["queue_lock"] = queue_lock
    print("[Flask] Serveur démarré sur le port 5001.")
    flask_app.run(port=5001, use_reloader=False)


def main():
    """
    Point d'entrée principal de l'application.
    """
    app = QtWidgets.QApplication(sys.argv)

    # Charger la police SF Pro
    load_sf_font()

    # Charger le fichier de style QSS
    load_stylesheet(app)

    # Configurer la fenêtre principale
    win = MainWindow()
    win.show()

    # Démarrer le serveur Flask dans un thread séparé
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Fonction pour vérifier la file de messages
    def check_queue():
        try:
            with queue_lock:
                while not message_queue.empty():
                    message = message_queue.get()
                    print(f"[PyQt] Message récupéré : {message}")

                    if not isinstance(message, dict):
                        print(f"[PyQt] Message invalide dans la file : {message}")
                        continue

                    message_type = message.get("type")
                    if message_type == "google_login_success":
                        user_data = message.get("data")
                        print(f"[PyQt] Données utilisateur reçues : {user_data}")
                        if isinstance(user_data, dict):
                            win.connect_google_user(user_data)
                        else:
                            print(f"[PyQt] Données utilisateur invalides : {user_data}")
                    else:
                        print(f"[PyQt] Type de message inconnu : {message_type}")
        except Exception as e:
            print(f"[PyQt] Erreur lors de la lecture de la file : {e}")

    # Configurer un timer pour vérifier régulièrement la file de messages
    timer = QTimer()
    timer.timeout.connect(check_queue)
    timer.start(100)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
