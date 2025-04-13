from PyQt5 import QtCore, QtGui, QtWidgets
from backend.db_api import DB_API
from pagePrincipale import MainWindow as MainWindowUI
import webbrowser
import pyotp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from zxcvbn import zxcvbn
from random import randint

# =====================
# Config email pour TOTP
# =====================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

accounts = [
    {"email": "taskflowreminder1@gmail.com", "password": "bgnt irxw fblu vemb"},
    {"email": "taskflowreminder2@gmail.com", "password": "lkya wtsu opzy pnse"},
    {"email": "taskflowreminder3@gmail.com", "password": "jjnw nuhq eopy azfw"},
]


def send_otp_email(recipient_email: str, otp_code: str):
    """
    Envoie l'OTP (code TOTP) par email au user.
    """
    subject = "Votre code TOTP"
    body = f"Votre code à 6 chiffres : {otp_code}\nIl est valable 30 secondes."
    message = MIMEMultipart()
    acc = accounts[randint(0, len(accounts) - 1)]
    SENDER_EMAIL = acc.get("email")
    SENDER_PASSWORD = acc.get("password")
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)


def send_totp_to_user(totp, user_email: str):
    """
    Génère le code TOTP et l'envoie par mail.
    """
    current_otp = totp.now()
    send_otp_email(user_email, current_otp)


def verify_totp_code(totp, user_input_code: str) -> bool:
    """
    Vérifie si le code TOTP entré par l'utilisateur est correct
    dans la fenêtre de code.
    """
    return totp.verify(user_input_code)  # True si code correct, False sinon.


# Identifiants Google
CLIENT_ID = "428963010703-4ehn75nf048kk43mmjpqksvva1d01qk8.apps.googleusercontent.com"
REDIRECT_URI = "http://localhost:5001/oauth2callback"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={}&redirect_uri={}&scope=email+profile+openid"


# -----------------------------------------------
# Dialog pour la saisie du code TOTP
# -----------------------------------------------
class OtpDialog(QtWidgets.QDialog):
    def __init__(self, secret_key, parent=None):
        super().__init__(parent)
        self.secret_key = secret_key
        self.setWindowTitle("Vérification du code TOTP")
        self.setModal(True)
        self.setup_ui()
        # Centrer la fenêtre
        self.setFixedSize(300, 150)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Entrez le code reçu par email :")
        font = QtGui.QFont()
        font.setPointSize(11)
        label.setFont(font)

        self.codeEdit = QtWidgets.QLineEdit()
        self.codeEdit.setPlaceholderText("Code à 6 chiffres")
        self.codeEdit.setFixedWidth(200)
        self.codeEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.codeEdit.setMaxLength(6)
        self.codeEdit.setValidator(QtGui.QIntValidator(0, 999999, self))

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self,
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(label, alignment=QtCore.Qt.AlignHCenter)
        layout.addWidget(self.codeEdit, alignment=QtCore.Qt.AlignHCenter)
        layout.addWidget(self.buttonBox, alignment=QtCore.Qt.AlignHCenter)

    def get_code(self):
        return self.codeEdit.text().strip()


class Ui_MainWindow(object):
    """
    Classe gérant l'interface utilisateur de la fenêtre d'authentification.
    Permet la connexion via email/mot de passe ou Google,
    ainsi que l'inscription de nouveaux utilisateurs.

    Exemple:
    >>> app = QtWidgets.QApplication(sys.argv)
    >>> MainWindow = QtWidgets.QMainWindow()
    >>> ui = Ui_MainWindow()
    >>> ui.setupUi(MainWindow)
    >>> MainWindow.show()
    """

    def __init__(self):
        """
        Initialise une nouvelle instance de Ui_MainWindow.
        Configure l'attribut totp à None pour une potentielle utilisation ultérieure.

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> print(ui.totp)  # None
        """
        self.totp = None

    def setupUi(self, MainWindow):
        """
        Configure l'interface utilisateur complète de la fenêtre d'authentification.
        Crée et positionne tous les widgets nécessaires.

        :param MainWindow: Instance de QMainWindow à configurer

        Le setup inclut:
        - Configuration de la fenêtre principal*
        - Chargement du fichier de style QSS
        - Création des champs de saisie (nom d'utilisateur, email, mot de passe)
        - Mise en place des boutons (connexion Google, validation)
        - Configuration des messages d'erreur
        - Mise en place du lien de création de compte

        Exemple:
        >>> window = QtWidgets.QMainWindow()
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> window.show()
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1035, 774)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("images/authentification/logo_alternatif.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        MainWindow.setWindowIcon(icon)

        # Charger le fichier QSS
        try:
            with open("authentification.qss", "r") as file:
                stylesheet = file.read()
                MainWindow.setStyleSheet(stylesheet)
        except FileNotFoundError:
            pass

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # --- Frame mire d'authentification
        self.frameMire = QtWidgets.QFrame(self.centralwidget)
        self.frameMire.setMinimumSize(QtCore.QSize(350, 500))
        self.frameMire.setMaximumSize(QtCore.QSize(350, 500))
        self.frameMire.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMire.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMire.setObjectName("frameMire")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameMire)
        self.verticalLayout.setObjectName("verticalLayout")

        # --- Titre
        self.frameTitre = QtWidgets.QFrame(self.frameMire)
        self.frameTitre.setMinimumSize(QtCore.QSize(100, 60))
        self.frameTitre.setMaximumSize(QtCore.QSize(300, 60))
        self.frameTitre.setObjectName("frameTitre")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frameTitre)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(self.frameTitre)
        self.label.setMinimumSize(QtCore.QSize(100, 60))
        self.label.setMaximumSize(QtCore.QSize(1500, 60))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(17)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("titre")
        self.verticalLayout_5.addWidget(self.label)
        self.verticalLayout.addWidget(self.frameTitre, 0, QtCore.Qt.AlignHCenter)

        # --- Frame "Nom d'utilisateur"
        self.frameUser = QtWidgets.QFrame(self.frameMire)
        self.frameUser.setObjectName("frameUser")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frameUser)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.titreUser = QtWidgets.QLabel(self.frameUser)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.titreUser.setFont(font)
        self.titreUser.setObjectName("titreUser")
        self.titreUser.setMinimumSize(QtCore.QSize(160, 30))
        self.titreUser.setMaximumSize(QtCore.QSize(160, 30))
        self.verticalLayout_7.addWidget(self.titreUser)
        self.inputUser = QtWidgets.QLineEdit(self.frameUser)
        self.inputUser.setMinimumSize(QtCore.QSize(300, 30))
        self.inputUser.setMaximumSize(QtCore.QSize(300, 30))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        self.inputUser.setFont(font)
        self.inputUser.setObjectName("inputUser")
        self.verticalLayout_7.addWidget(self.inputUser)
        self.verticalLayout.addWidget(self.frameUser, 0, QtCore.Qt.AlignHCenter)

        # --- Frame Email
        self.frameLogin = QtWidgets.QFrame(self.frameMire)
        self.frameLogin.setObjectName("frameLogin")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frameLogin)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.titreMail = QtWidgets.QLabel(self.frameLogin)
        self.titreMail.setMinimumSize(QtCore.QSize(60, 30))
        self.titreMail.setMaximumSize(QtCore.QSize(60, 30))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.titreMail.setFont(font)
        self.verticalLayout_2.addWidget(self.titreMail)
        self.inputMail = QtWidgets.QLineEdit(self.frameLogin)
        self.inputMail.setMinimumSize(QtCore.QSize(300, 30))
        self.inputMail.setMaximumSize(QtCore.QSize(300, 30))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        self.inputMail.setFont(font)
        self.inputMail.setObjectName("inputMail")
        self.verticalLayout_2.addWidget(self.inputMail)
        self.verticalLayout.addWidget(self.frameLogin, 0, QtCore.Qt.AlignHCenter)

        # --- Frame Password
        self.framePassword = QtWidgets.QFrame(self.frameMire)
        self.framePassword.setObjectName("framePassword")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.framePassword)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.titrePassword = QtWidgets.QLabel(self.framePassword)
        self.titrePassword.setMaximumSize(QtCore.QSize(120, 30))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.titrePassword.setFont(font)
        self.verticalLayout_3.addWidget(self.titrePassword)
        self.inputPassword = QtWidgets.QLineEdit(self.framePassword)
        self.inputPassword.setMinimumSize(QtCore.QSize(300, 30))
        self.inputPassword.setMaximumSize(QtCore.QSize(300, 30))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        self.inputPassword.setFont(font)
        self.inputPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.inputPassword.setObjectName("inputPassword")
        self.verticalLayout_3.addWidget(self.inputPassword)
        self.verticalLayout.addWidget(self.framePassword, 0, QtCore.Qt.AlignHCenter)

        for frame in [self.frameUser, self.frameLogin, self.framePassword]:
            frame.setMinimumSize(QtCore.QSize(350, 80))
            frame.setMaximumSize(QtCore.QSize(350, 80))

        # --- Bouton Google
        self.google_login_button = QtWidgets.QPushButton(self.frameMire)
        google_icon = QtGui.QIcon("images/authentification/logo_google.png")
        self.google_login_button.setIconSize(QtCore.QSize(50, 50))
        self.google_login_button.setIcon(google_icon)
        self.google_login_button.setMinimumSize(QtCore.QSize(50, 50))
        self.google_login_button.setMaximumSize(QtCore.QSize(50, 50))
        self.verticalLayout.addWidget(self.google_login_button, 0, QtCore.Qt.AlignHCenter)
        self.google_login_button.clicked.connect(self.login_with_google)

        # --- Label erreur
        self.frameErreur = QtWidgets.QFrame(self.frameMire)
        self.frameErreur.setMinimumSize(QtCore.QSize(350, 50))
        self.frameErreur.setMaximumSize(QtCore.QSize(350, 50))
        self.frameErreur.setObjectName("frameErreur")
        self.verticalLayoutErreur = QtWidgets.QVBoxLayout(self.frameErreur)
        self.verticalLayoutErreur.setObjectName("verticalLayoutErreur")
        self.labelErreur = QtWidgets.QLabel(self.frameErreur)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        self.labelErreur.setFont(font)
        self.labelErreur.setStyleSheet("color: red;")
        self.labelErreur.setAlignment(QtCore.Qt.AlignCenter)
        self.labelErreur.setWordWrap(True)
        self.verticalLayoutErreur.addWidget(self.labelErreur)
        self.verticalLayout.insertWidget(4, self.frameErreur, 0, QtCore.Qt.AlignHCenter)

        # --- Bouton Valider
        self.frameBouton = QtWidgets.QFrame(self.frameMire)
        self.frameBouton.setMinimumSize(QtCore.QSize(150, 80))
        self.frameBouton.setMaximumSize(QtCore.QSize(150, 80))
        self.frameBouton.setObjectName("frameBouton")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frameBouton)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.boutonValider = QtWidgets.QPushButton(self.frameBouton)
        self.boutonValider.setMaximumSize(QtCore.QSize(150, 50))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.boutonValider.setFont(font)
        self.boutonValider.setObjectName("boutonValider")
        self.verticalLayout_4.addWidget(self.boutonValider)
        self.verticalLayout.addWidget(self.frameBouton, 0, QtCore.Qt.AlignHCenter)

        # --- Lien "Créer un compte"
        self.frameCreerCompte = QtWidgets.QFrame(self.frameMire)
        self.frameCreerCompte.setMinimumSize(QtCore.QSize(100, 50))
        self.frameCreerCompte.setMaximumSize(QtCore.QSize(100, 50))
        self.frameCreerCompte.setObjectName("frameCreerCompte")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frameCreerCompte)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.boutonCreerCompte = QtWidgets.QLabel(
            "<a href='#'>Créer un compte</a>", self.frameCreerCompte
        )
        self.boutonCreerCompte.setMinimumSize(QtCore.QSize(25, 25))
        self.boutonCreerCompte.setMaximumSize(QtCore.QSize(80, 25))
        self.boutonCreerCompte.setObjectName("boutonCreerCompte")
        self.boutonCreerCompte.setAlignment(QtCore.Qt.AlignCenter)
        self.boutonCreerCompte.linkActivated.connect(self.show_signup_form)
        self.verticalLayout_6.addWidget(self.boutonCreerCompte)
        self.verticalLayout.addWidget(self.frameCreerCompte, 0, QtCore.Qt.AlignHCenter)

        self.gridLayout.addWidget(self.frameMire, 2, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(300, 140))
        self.frame.setMaximumSize(QtCore.QSize(300, 160))
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout.addWidget(self.frame_2, 3, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.is_login_form = True
        self.main_window = MainWindow
        self.update_form_state()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def show_signup_form(self):
        """
        Bascule entre le formulaire de connexion et le formulaire d'inscription.
        Met à jour l'interface en conséquence via update_form_state().

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.show_signup_form()  # Bascule vers le formulaire d'inscription
        >>> print(ui.is_login_form)  # False
        """
        self.is_login_form = not self.is_login_form
        self.update_form_state()

    def update_form_state(self):
        """
        Met à jour l'état de l'interface selon le mode actif (connexion ou inscription).
        Gère la visibilité des champs, les textes affichés et les connexions des signaux.

        Cette méthode:
        - Déconnecte les anciens signaux
        - Met à jour les textes et placeholders
        - Configure la visibilité des widgets
        - Reconnecte les nouveaux signaux appropriés

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.is_login_form = False
        >>> ui.update_form_state()  # L'interface passe en mode inscription
        """
        _translate = QtCore.QCoreApplication.translate
        try:
            self.boutonValider.clicked.disconnect()
            self.inputMail.returnPressed.disconnect()
            self.inputPassword.returnPressed.disconnect()
        except Exception:
            pass

        if self.is_login_form:
            self.google_login_button.setVisible(True)
            self.frameUser.setVisible(False)
            self.inputUser.setVisible(False)
            self.titreUser.setVisible(False)

            self.main_window.setWindowTitle(_translate("MainWindow", "TaskFlow - Login"))
            self.titreUser.setText(_translate("MainWindow", "Nom d'Utilisateur"))
            self.label.setText(_translate("MainWindow", "S'identifier"))
            self.boutonValider.setText(_translate("MainWindow", "Valider"))
            self.boutonCreerCompte.setText("<a href='#'>Créer un compte</a>")
            self.inputPassword.setPlaceholderText("")
            self.inputMail.setPlaceholderText("")

            self.boutonValider.clicked.connect(self.handle_login)
            self.inputMail.returnPressed.connect(self.handle_login)
            self.inputPassword.returnPressed.connect(self.handle_login)
        else:
            self.google_login_button.setVisible(False)
            self.frameUser.setVisible(True)
            self.inputUser.setVisible(True)
            self.titreUser.setVisible(True)

            self.main_window.setWindowTitle(_translate("MainWindow", "TaskFlow - Inscription"))
            self.label.setText(_translate("MainWindow", "Créer un compte"))
            self.boutonValider.setText(_translate("MainWindow", "S'inscrire"))
            self.boutonCreerCompte.setText("<a href='#'>Retour</a>")
            self.inputPassword.setPlaceholderText("Minimum 8 caractères")
            self.inputMail.setPlaceholderText("exemple@email.com")
            self.inputUser.setPlaceholderText("exemple")

            self.boutonValider.clicked.connect(self.handle_signup)
            self.inputMail.returnPressed.connect(self.handle_signup)
            self.inputPassword.returnPressed.connect(self.handle_signup)

    def handle_login(self):
        """
        Gère le processus de connexion utilisateur.
        Vérifie les identifiants via Argon2 puis met en place l'authentification TOTP.

        Le processus comprend:
        1. Validation des identifiants utilisateur
        2. Récupération/création de la clé secrète TOTP
        3. Envoi du code TOTP par email
        4. Vérification du code saisi
        5. Ouverture de la fenêtre principale si authentification réussie

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.inputMail.setText("user@example.com")
        >>> ui.inputPassword.setText("password123")
        >>> ui.handle_login()  # Lance le processus de connexion
        """
        self.clear_error_message()

        email = self.inputMail.text().strip()
        password = self.inputPassword.text()

        try:
            is_ok = DB_API.check_user_credentials(email, password)
            if not is_ok:
                self.show_error_message("Échec de connexion Email ou mot de passe incorrect")
                return

            # 1) Authentification OK - Récupérer ou générer la clé secrète
            secret_key = self.get_or_create_user_secret(email)
            self.totp = pyotp.TOTP(secret_key)
            if not secret_key:
                self.show_error_message("Erreur Impossible de récupérer ou de créer la clé TOTP")
                return

            # 2) Ouvrir une popup demandant le code
            otp_dialog = OtpDialog(secret_key)
            print("Affichage de la popup OTP...")

            # 3) Envoyer le code TOTP par email
            print("Envoi du code TOTP par email...")
            send_totp_to_user(self.totp, email)
            print("Code TOTP envoyé avec succès.")

            result = otp_dialog.exec_()
            print("Popup OTP fermée, résultat :", result)

            if result == QtWidgets.QDialog.Accepted:
                entered_code = otp_dialog.get_code()
                print("Code OTP saisi :", entered_code)

                if verify_totp_code(self.totp, entered_code):
                    userID = DB_API.get_userID_by_email(email)
                    DB_API.set_user_status(userID[0], 1)
                    self.show_success_message("Connexion réussie Bienvenue!")
                    self.open_main_window()
                else:
                    self.show_error_message("Erreur Code invalide ou expiré")
            else:
                self.show_error_message("OTP annulé Connexion abandonnée")

        except Exception as e:
            print(f"Erreur lors de la connexion ou de l'authentification : {e}")
            self.show_error_message("Erreur critique Une erreur est survenue : {e}")

    def login_with_google(self):
        """
        Initie le processus de connexion via Google.
        Ouvre le navigateur sur la page d'authentification Google.

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.google_login_button.click()  # ou ui.login_with_google()
        >>> # Ouvre le navigateur sur la page de connexion Google
        """
        print("Ouverture de la page de connexion Google...")
        webbrowser.open(AUTH_URL.format(CLIENT_ID, REDIRECT_URI))
        print("Navigateur ouvert. En attente du callback Google...")

    def connect_google_user(self, user_data: dict):
        """
        Finalise la connexion d'un utilisateur via Google.

        :param user_data: Dictionnaire contenant les informations de l'utilisateur Google

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> user_data = {
        >>>     "name": "John Doe",
        >>>     "email": "john.doe@gmail.com"
        >>> }
        >>> ui.connect_google_user(user_data)
        >>> # L'utilisateur est connecté et la fenêtre principale s'ouvre
        """
        if not isinstance(user_data, dict):
            print("[PyQt] Erreur : données utilisateur invalides.")
            return

        name = user_data.get("name", "Utilisateur")
        email = user_data.get("email", "Email inconnu")

        print(f"[PyQt] Bienvenue {name} ({email})")
        self.show_success_message(f"Bienvenue {name} !")
        self.open_main_window_google(email)

    def open_main_window_google(self, email: str):
        """
        Ouvre la fenêtre principale après une connexion réussie via Google.
        Configure l'utilisateur actif avec l'email Google.

        :param email: Email de l'utilisateur Google

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.open_main_window_google("user@gmail.com")
        >>> # La fenêtre principale s'ouvre avec l'utilisateur configuré
        """
        if not email:
            print("[PyQt] Erreur : email invalide.")
            self.show_error_message("Erreur : email non valide.")
            return

        print(f"[PyQt] Ouverture de la fenêtre principale avec l'utilisateur {email}.")
        self.main_window.close()
        self.main_window_ui = MainWindowUI()
        self.main_window_ui.set_current_user(
            email
        )  # Configure l'utilisateur avec l'email récupéré
        self.main_window_ui.show()

    def handle_signup(self) -> bool:
        """
        Gère le processus d'inscription d'un nouvel utilisateur.

        Effectue les validations suivantes:
        - Vérifie que l'email n'est pas une adresse Gmail
        - Valide le format de l'email
        - Vérifie la force du mot de passe via zxcvbn
        - Contrôle l'unicité de l'email et du nom d'utilisateur

        :return: True si l'inscription est réussie, False sinon

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.show_signup_form()  # Passage en mode inscription
        >>> ui.inputUser.setText("john_doe")
        >>> ui.inputMail.setText("john@example.com")
        >>> ui.inputPassword.setText("StrongP@ssw0rd")
        >>> success = ui.handle_signup()
        >>> if success:
        >>>     print("Inscription réussie!")
        """
        self.clear_error_message()
        username = self.inputUser.text().strip()
        email = self.inputMail.text().strip()
        password = self.inputPassword.text()

        # Vérifier que l'email ne termine pas par @gmail.com
        if email.lower().endswith("@gmail.com"):
            self.show_error_message(
                "Erreur d'inscription Impossible de créer un compte "
                "avec un email se terminant par '@gmail.com'",
            )
            return False

        # Validation de l'adresse email
        if not self.validate_email(email):
            self.show_error_message(
                "Erreur d'inscription Veuillez entrer une adresse email valide"
            )
            return False

        # Vérification de la force du mot de passe avec zxcvbn
        password_strength = zxcvbn(password)
        if password_strength["score"] < 3:  # Score requis : 3 ou plus
            feedback = password_strength["feedback"]
            warning = feedback.get("warning", "")
            suggestions = " ".join(feedback.get("suggestions", []))
            self.show_error_message(
                "Mot de passe faible"
                f"Votre mot de passe est trop faible. {warning} {suggestions}",
            )
            return False

        # Vérifier que le mot de passe a au moins 8 caractères
        if len(password) < 8:
            self.show_error_message(
                "Erreur d'inscription Le mot de passe doit contenir au moins 8 caractères"
            )
            return False

        # Vérification si l'email existe déjà
        existing_email = DB_API.get_email(email)
        if existing_email and not isinstance(existing_email, Exception):
            self.show_error_message("Erreur d'inscription Cette adresse email est déjà utilisée")
            return False

        # Vérification si le nom d'utilisateur existe déjà
        existing_username = DB_API.get_user(username)
        if existing_username and not isinstance(existing_username, Exception):
            self.show_error_message("Erreur d'inscription Ce nom d'utilisateur est déjà utilisé")
            return False

        # Création du compte utilisateur
        is_google_user = 0  # forcé à 0 pour les comptes non Google
        try:
            success = DB_API.add_user(username, password, email, is_google_user)
            DB_API.add_user_status(success, 0)
            if success and not isinstance(success, Exception):
                self.show_success_message(
                    "Inscription réussie Votre compte a été créé avec succès!"
                )
                self.is_login_form = True
                self.update_form_state()
                return True
            else:
                self.show_error_message(
                    "Erreur d'inscription Erreur lors de la création du compte"
                )
                return False
        except Exception:
            self.show_error_message("Erreur d'inscription Une erreur est survenue: {e!s}")
            return False

    def validate_email(self, email: str) -> bool:
        """
        Valide le format d'une adresse email.

        :param email: Adresse email à valider
        :return: True si le format est valide, False sinon

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> print(ui.validate_email("user@example.com"))  # True
        >>> print(ui.validate_email("invalid.email"))  # False
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def get_or_create_user_secret(self, email: str) -> str:
        """
        Récupère la clé secrète TOTP d'un utilisateur ou en crée une nouvelle.

        :param email: Email de l'utilisateur
        :return: Clé secrète TOTP

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> secret = ui.get_or_create_user_secret("user@example.com")
        >>> print(len(secret))  # 32 (longueur typique d'une clé TOTP)
        """
        # Exemple: On imagine que DB_API.get_totp_secret(email) renvoie la clé ou None
        existing_secret = DB_API.get_totp_secret(email)
        if existing_secret and not isinstance(existing_secret, Exception):
            return existing_secret

        # Sinon on génère
        new_secret = pyotp.random_base32()
        DB_API.set_totp_secret(email, new_secret)
        return new_secret

    def show_error_message(self, message: str):
        """
        Affiche un message d'erreur temporaire dans l'interface.

        :param message: Message d'erreur à afficher

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.show_error_message("Email invalide!")
        >>> # Le message s'affiche en rouge et disparaît après 3 secondes
        """
        self.labelErreur.setText(message)
        QtCore.QTimer.singleShot(3000, self.clear_error_message)

    def clear_error_message(self):
        """
        Efface le message d'erreur actuellement affiché dans l'interface.

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.show_error_message("Une erreur")
        >>> ui.clear_error_message()  # Le message disparaît
        """
        self.labelErreur.clear()

    def show_success_message(self, message: str):
        """
        Affiche un message de succès temporaire dans l'interface.

        :param message: Message de succès à afficher

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.show_success_message("Connexion réussie!")
        >>> # Le message s'affiche en blanc et disparaît après 3 secondes
        """
        self.labelErreur.setStyleSheet("color: white;")
        self.labelErreur.setText(message)
        QtCore.QTimer.singleShot(3000, self.clear_error_message)
        QtCore.QTimer.singleShot(3000, lambda: self.labelErreur.setStyleSheet("color: red;"))

    def open_main_window(self):
        """
        Ferme la fenêtre d'authentification et ouvre la fenêtre principale
        après une connexion réussie via email/mot de passe.
        Configure l'utilisateur actif avec l'email utilisé pour la connexion.

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> ui.setupUi(window)
        >>> ui.inputMail.setText("user@example.com")
        >>> ui.open_main_window()
        >>> # La fenêtre principale s'ouvre avec l'utilisateur configuré
        """
        self.main_window.close()
        self.main_window_ui = MainWindowUI()
        self.main_window_ui.set_current_user(self.inputMail.text())
        self.main_window_ui.show()

    def retranslateUi(self, MainWindow):
        """
        Configure les textes de l'interface utilisateur.
        Utilise QCoreApplication.translate pour la gestion des traductions.

        :param MainWindow: Instance de QMainWindow dont les textes doivent être traduits

        Cette méthode définit:
        - Le titre de la fenêtre
        - Les labels des champs de saisie
        - Le texte des boutons
        - Les autres éléments textuels de l'interface

        Exemple:
        >>> ui = Ui_MainWindow()
        >>> window = QtWidgets.QMainWindow()
        >>> ui.setupUi(window)
        >>> ui.retranslateUi(window)
        >>> print(window.windowTitle())  # "TaskFlow - Login"
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TaskFlow - Login"))
        self.titreUser.setText(_translate("MainWindow", "Nom d'Utilisateur"))
        self.label.setText(_translate("MainWindow", "S'identifier"))
        self.titreMail.setText(_translate("MainWindow", "E-Mail"))
        self.titrePassword.setText(_translate("MainWindow", "Mot de passe"))
        self.boutonValider.setText(_translate("MainWindow", "Valider"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        """
        Initialise la classe Ui_MainWindow.

        Cette méthode initialise les valeurs de l'utilisateur actuel et de l'ID utilisateur.
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

    def closeEvent(self, event):
        print("Close clicked authentif")
        event.accept()
