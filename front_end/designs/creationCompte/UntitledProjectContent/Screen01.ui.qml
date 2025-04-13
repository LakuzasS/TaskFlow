

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
    id: rectangle
    width: Constants.width
    height: Constants.height

    Image {
        id: image
        x: -20
        y: -112
        width: 1953
        height: 1290
        source: "../../../../../../../../../swann project/logiciel/colorkit(3).png"
        fillMode: Image.PreserveAspectFit
    }

    Rectangle {
        id: rectangle1
        x: 658
        y: 143
        width: 604
        height: 794
        color: "#b25c5c5c"
        radius: 13
        border.color: "#fc9840"
        border.width: 0
    }

    Text {
        id: _text
        x: 830
        y: 191
        width: 263
        height: 41
        color: "#ffffff"
        text: "Creér un compte"
        font.pixelSize: 31
        horizontalAlignment: Text.AlignHCenter
        font.styleName: "Gras"
        font.family: "Tahoma"

        Text {
            id: _text2
            x: -115
            y: 110
            width: 77
            height: 29
            color: "#ffffff"
            text: "E-mail"
            font.pixelSize: 21
            horizontalAlignment: Text.AlignHCenter
            font.styleName: "Gras"
            font.family: "Tahoma"

            Rectangle {
                id: rectangle5
                x: 0
                y: 28
                width: 490
                height: 70
                color: "#5c5c5c"
                radius: 5

                TextInput {
                    id: textInput
                    x: 15
                    y: 12
                    width: 460
                    height: 50
                    color: "#ffffff"
                    font.pixelSize: 17
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    echoMode: TextInput.Normal
                    layer.enabled: true
                    maximumLength: 255
                    readOnly: false
                    property int newName: 0
                }

                TextInput {
                    id: textInput1
                    x: 15
                    y: 12
                    width: 460
                    height: 50
                    color: "#ffffff"
                    font.pixelSize: 17
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    readOnly: false
                    property int newName: 0
                    maximumLength: 255
                    layer.enabled: true
                    font.bold: true
                    echoMode: TextInput.Normal
                }
            }
        }

        Text {
            id: _text3
            x: -115
            y: 227
            width: 156
            height: 31
            color: "#ffffff"
            text: "Nom d'affichage "
            font.pixelSize: 21
            horizontalAlignment: Text.AlignHCenter
            font.styleName: "Gras"
            font.family: "Tahoma"

            Rectangle {
                id: rectangle6
                x: -1
                y: 29
                width: 490
                height: 70
                color: "#5c5c5c"
                radius: 5
            }

            TextInput {
                id: textInput2
                x: 8
                y: 39
                width: 460
                height: 50
                color: "#ffffff"
                font.pixelSize: 17
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                readOnly: false
                property int newName: 0
                maximumLength: 255
                layer.enabled: true
                font.bold: true
                echoMode: TextInput.Normal
            }
        }

        Text {
            id: _text4
            x: -118
            y: 347
            width: 125
            height: 31
            color: "#ffffff"
            text: "Mot de passe"
            font.pixelSize: 21
            horizontalAlignment: Text.AlignHCenter
            font.styleName: "Gras"
            font.family: "Tahoma"

            Rectangle {
                id: rectangle7
                x: 0
                y: 29
                width: 490
                height: 70
                color: "#5c5c5c"
                radius: 5
            }

            TextInput {
                id: textInput3
                x: 15
                y: 39
                width: 460
                height: 50
                color: "#ffffff"
                font.pixelSize: 17
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                readOnly: false
                property int newName: 0
                maximumLength: 255
                layer.enabled: true
                font.bold: true
                echoMode: TextInput.Password
            }
        }

        Text {
            id: _text5
            x: -118
            y: 465
            width: 154
            height: 31
            color: "#ffffff"
            text: "Mot de passe x2"
            font.pixelSize: 21
            horizontalAlignment: Text.AlignHCenter
            font.styleName: "Gras"
            font.family: "Tahoma"

            Rectangle {
                id: rectangle9
                x: 0
                y: 29
                width: 490
                height: 70
                color: "#5c5c5c"
                radius: 5
            }

            TextInput {
                id: textInput4
                x: 15
                y: 39
                width: 460
                height: 50
                color: "#ffffff"
                font.pixelSize: 17
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                readOnly: false
                property int newName: 0
                maximumLength: 255
                layer.enabled: true
                font.bold: true
                echoMode: TextInput.Password
            }
        }

        Rectangle {
            id: rectangle8
            x: 22
            y: 623
            width: 211
            height: 74
            color: "#5c5c5c"
            radius: 5

            Button {
                id: button
                x: 24
                y: 11
                width: 164
                height: 51
                text: qsTr("Valider")
                z: 0
                scale: 1.106
                highlighted: false
                spacing: 5
                font.pointSize: 10
                font.bold: true
                font.family: "Tahoma"
                autoRepeat: true
                autoExclusive: true
                checkable: true
                checked: true
                display: AbstractButton.TextOnly
                font.weight: Font.Normal
            }
        }
    }

    DesignEffect {
        effects: [
            DesignDropShadow {}
        ]
    }

    states: [
        State {
            name: "clicked"
        }
    ]
}

/*##^##
Designer {
    D{i:0}D{i:1;locked:true}D{i:2;locked:true}D{i:4}D{i:7}D{i:8}D{i:10}D{i:11}D{i:13}
D{i:14}D{i:16}D{i:17}
}
##^##*/

