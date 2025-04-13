

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import UntitledProject
import QtQuick.Studio.DesignEffects

Rectangle {
    id: main
    width: Constants.width
    height: Constants.height

    Image {
        id: background
        x: -20
        y: -112
        width: 1953
        height: 1290
        source: "../../colorkit3.png"
        fillMode: Image.PreserveAspectFit
    }

    Rectangle {
        id: mireAuthentification
        x: 658
        y: 143
        width: 604
        height: 794
        color: "#b25c5c5c"
        radius: 13
        border.color: "#fc9840"
        border.width: 0

        Text {
            id: mainTitre
            x: 172
            y: 48
            width: 263
            height: 41
            color: "#ffffff"
            text: "S'identifier"
            font.pixelSize: 31
            horizontalAlignment: Text.AlignHCenter
            font.styleName: "Gras"
            font.family: "Tahoma"
        }

        Text {
            id: textMail
            x: 57
            y: 156
            width: 62
            height: 31
            color: "#ffffff"
            text: "E-Mail"
            font.pixelSize: 21
            horizontalAlignment: Text.AlignLeft
            font.styleName: "Gras"
            font.family: "Tahoma"
        }

        TextField {
            id: inputMail
            x: 57
            y: 193
            width: 490
            height: 68
            color: "#ffffff"
            selectedTextColor: "#5c5c5c"
            font.pointSize: 17
            selectionColor: "#b3c7c7c7"
            placeholderText: qsTr("")
            background: Rectangle {
                color: "#5c5c5c"
                radius: 5
            }
        }

        Text {
            id: textPassword
            x: 57
            y: 280
            width: 125
            height: 31
            color: "#ffffff"
            text: "Mot de passe"
            font.pixelSize: 21
            horizontalAlignment: Text.AlignHCenter
            font.styleName: "Gras"
            font.family: "Tahoma"
        }

        TextField {
            id: inputPassword
            x: 57
            y: 317
            width: 490
            height: 68
            color: "#ffffff"
            echoMode: TextInput.Password
            selectionColor: "#b3c7c7c7"
            selectedTextColor: "#5c5c5c"
            placeholderText: qsTr("")
            font.pointSize: 17
            background: Rectangle {
                color: "#5c5c5c"
                radius: 5
            }
        }

        Button {
            id: boutonValider
            x: 199
            y: 641
            width: 210
            height: 75
            text: qsTr("Valider")
            font.pointSize: 17
            hoverEnabled: true

            contentItem: Text {
                color: "#ffffff"
                text: "Valider"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.pointSize: 17
                styleColor: "#ffffff"
            }

            background: Rectangle {
                color: boutonValider.down ? "#5c5c5c" : boutonValider.hovered ? "#343434" : "#5c5c5c"
                radius: 5
                border.width: 0
            }
        }
    }

    DesignEffect {
        effects: [
            DesignDropShadow {}
        ]
    }
}
