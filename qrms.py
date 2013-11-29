#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import psutil
import sys
import re

MENSAJES = {
    ('notepad.exe', "bloc de notas", "No puede ser", "Esta usted ejecutando el bloc de notas. ¿No sabe que existen mejores editores como vim o emacs que haran su vida mas sencilla?"),
    ('iexplore.exe', "Microsoft Internet Explorer", "Vaya vaya", "El navegador que utiliza no es software libre. ¿Sabe que existen navegadores libres como Firefox o Chrome, y que al usarlos está contribuyendo a su desarrollo? Pruebelo."),
}

SECONDS=10

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        menu = QtGui.QMenu(parent)
        exitAction = menu.addAction("E&xit")
        QtCore.QObject.connect(exitAction, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("quit()"))
        self.setContextMenu(menu)

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.invoca)

        self.ya_avisado = set()

        if self.supportsMessages():
            self.timer.start(1 * 1000)
        else:
            self.setToolTip("RMS: No tengo soporte para presentar mensajes")

    def invoca(self):
        self.timer.start(SECONDS * 1000)
        busca = lambda pat, s: re.search("\\b%s\\b" % pat, s) is not None

        print("Rastreando procesos")
        software_malo = set()
        # FIXME usar p.username para que avise solo de procesos tuyos
        cmdlines = [" ".join(p.cmdline) for p in psutil.process_iter()]
        # print(cmdlines)
        for command, nombre, titulo, mensaje in MENSAJES:
            encontro = False
            for cmdline in cmdlines:
                if busca(command, cmdline):
                    encontro = True
                    break
            if encontro:
                software_malo.add(command)
                if not command in self.ya_avisado:
                    print("tiene abierto %s !!" % command)
                    self.showMessage(titulo, mensaje)
                    self.ya_avisado.add(command)
                    break
            else:
                if command in self.ya_avisado:
                    print("cerro %s :-)" % command)
                    self.showMessage("Gracias", "Gracias por cerrar %s, me daba grima" % nombre)
                    self.ya_avisado.remove(command)
                    break
        if len(software_malo) > 0:
            self.setToolTip("RMS: Tienes %d software privativo. No toi feliz." % len(software_malo))
            self.setIcon(QtGui.QIcon("tux_sad.lite.png"))
        else:
            self.setToolTip("RMS: Perfecto. Soy feliz.")
            self.setIcon(QtGui.QIcon("tux_happy.lite.png"))
        print("Finalizado")


def main():
    app = QtGui.QApplication(sys.argv)

    style = app.style()
    icon = QtGui.QIcon(style.standardPixmap(QtGui.QStyle.SP_FileIcon))
    trayIcon = SystemTrayIcon(icon)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
