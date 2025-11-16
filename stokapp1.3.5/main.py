from PyQt5.QtWidgets import QApplication
import sys
from login import LoginForm

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load FHJ
#with open("style.qss", "r") as f:
    #qss = f.read()
    #app.setStyleSheet(qss)
    
    login_window = LoginForm()
    login_window.show()
    sys.exit(app.exec_())
