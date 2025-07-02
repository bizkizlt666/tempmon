import os
import sys
import subprocess
import psutil
import getpass
import fcntl
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QListWidget, QListWidgetItem, QWidget, 
    QHBoxLayout, QVBoxLayout, QApplication, QStackedLayout, QSizePolicy, QCheckBox
)


class HeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        width = 300 
        height = 50
        self.pixmap = QPixmap(width, height)
        self.pixmap.fill(Qt.transparent)  

        painter = QPainter(self.pixmap)
        color = QColor(0, 0, 0, 127)  
        painter.fillRect(0, 0, width, height, color)
        painter.end()

        self.text = "Running processes"
        self.font = QFont("Arial Black", 18)
        self.text_color = QColor("#43ff00")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)  #Háttér kirajzolása
        painter.setFont(self.font)
        painter.setPen(self.text_color)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)
        
class SideWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.setFixedHeight(500)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Header widget
        self.layout.addWidget(HeaderWidget())

        # Lista widget létrehozása és hozzáadása
        self.process_list = QListWidget()
        self.process_list.setStyleSheet("background-color: transparent; color: lime; font-size: 14px;")
        self.layout.addWidget(self.process_list)

        # Gombsor létrehozása
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()

        # Refresh gomb
        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                color: rgba(0, 248, 255);
                background-color: rgba(161, 161, 161, 200);
                border: 4px solid #3c3c3c;
                border-radius: 20px;
                font-size: 20px;
                padding: 0px;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(0, 187, 255, 200);
                color: rgba(0, 248, 255, 150);
            }
        """)
        refresh_btn.setFont(QFont("", 20))
        refresh_btn.clicked.connect(self.update_process_list)
        button_layout.addWidget(refresh_btn)

        # Elfogadás gomb
        apply_btn = QPushButton("✔")
        apply_btn.setFixedSize(40, 40)
        apply_btn.setStyleSheet("""
            QPushButton {
                color: rgba(0, 255, 0);
                background-color: rgba(161, 161, 161, 200);
                border: 4px solid #3c3c3c;
                border-radius: 20px;
                font-size: 20px;
                padding: 0px;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(151, 255, 121, 200);
                color: rgba(0, 255, 0, 200);
            }
        """)
        apply_btn.setFont(QFont("", 20))
        apply_btn.clicked.connect(self.close_side)
        apply_btn.clicked.connect(self.create_or_overwrite_killist)
        button_layout.addWidget(apply_btn)

        # Bezárás gomb
        close_btn = QPushButton("✘")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                color: rgba(255, 0, 0);
                background-color: rgba(161, 161, 161, 200);
                border: 4px solid #3c3c3c;
                border-radius: 20px;
                font-size: 20px;
                padding: 0px;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0);
                color: rgba(255, 100, 100, 200);
            }
        """)
        close_btn.clicked.connect(self.close_side)
        button_layout.addWidget(close_btn)

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # Induláskor lista frissítése
        self.update_process_list()
        
    def update_process_list(self):
        self.process_list.clear()
        current_user = getpass.getuser()
        seen_names = set()

        for proc in psutil.process_iter(['name', 'username']):
            try:
                if proc.info['username'] == current_user:
                    name = proc.info['name']
                    if name not in seen_names:
                        seen_names.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        sorted_names = sorted(seen_names)

        for name in sorted_names:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(10, 4, 10, 4)
            layout.setSpacing(5)

            label = QLabel(name)
            label.setStyleSheet("color: lime; font-size: 14px;")
            label.setMinimumHeight(32)
            label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 12px; /* 10 = 20/2, így lesz tökéletes kör */
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #3c3c3c;
                    background: rgba(161, 161, 161, 200);
                }
                QCheckBox::indicator:checked {
                    border: 2px solid rgba(161, 161, 161, 200);
                    background: lime;
                }
                QCheckBox::indicator:hover {
                    border: 2px solid rgba(161, 161, 161, 200);
                    background: rgba(0, 255, 0, 30);
                }
            """)

            checkbox.setMinimumHeight(32)

            layout.addWidget(label)
            layout.addStretch()
            layout.addWidget(checkbox)

            widget.setLayout(layout)
            widget.setMinimumHeight(36)

            item.setSizeHint(QSize(0, 42))

            self.process_list.addItem(item)
            self.process_list.setItemWidget(item, widget)

    def close_side(self):
        parent = self.parentWidget()
        if parent:
            parent.hide_side_widget()  # vagy más, amivel elrejted a SideWidget-et

    def create_or_overwrite_killist(self):
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "killist.ini")
        
        try:
            checked_names = []
            for i in range(self.process_list.count()):
                item = self.process_list.item(i)
                widget = self.process_list.itemWidget(item)
                if widget:
                    layout = widget.layout()
                    label = layout.itemAt(0).widget()
                    checkbox = layout.itemAt(layout.count() - 1).widget()
                    if checkbox.isChecked():
                        checked_names.append(label.text())
            checked_names = sorted(checked_names, key=lambda x: x.lower())
            with open(file_path, "w", encoding="utf-8") as f:
                for name in checked_names:
                    f.write(name + "\n")
            print(f"{file_path} létrehozva / felülírva {len(checked_names)} folyamattal.")
        except Exception as e:
            print(f"Hiba killist.ini létrehozásakor: {e}")

class TempMonitor(QWidget):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.bg_image_path = os.path.join(current_dir, "source", "bg02.jpg")

        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "digital-7.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            self.digital_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            self.digital_family = None

        self.setWindowTitle("Temperature Monitor")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setStyleSheet("color: lime; font-size: 16px;")


        # Fő vízszintes layout (bal oldal: stacked, jobb oldal: side widget)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(self.main_layout)
        self.stack = QStackedLayout()

        # Main widget
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.create_main_layout())
        self.stack.addWidget(self.main_widget)

        # Thin widget
        self.thin_widget = QWidget()
        self.thin_widget.setLayout(self.create_thin_layout())
        
        #self.thin_widget.setMaximumHeight(32)
        self.thin_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #self.thin_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.stack.addWidget(self.thin_widget)
        
        # Stack layout bal oldalra
        self.stack_container = QWidget()
        self.stack_container.setLayout(self.stack)
        self.main_layout.addWidget(self.stack_container)

        # Oldalsó widget (jobb oldalra), eleinte rejtve
        self.side_widget = SideWidget()
        self.side_widget.hide()
        self.main_layout.addWidget(self.side_widget)
        self.side_widget_index = self.main_layout.indexOf(self.side_widget)
        self.stack.setCurrentIndex(0)

        # Timer a hőmérséklet frissítéshez
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_temps)
        self.timer.start(1000)

        # Bal felső sarokba igazítás
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        self.move(geometry.topLeft())
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def create_main_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Fejléc widget a háttérhez
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: transparent") 

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(2, 0, 2, 0)
        header_layout.setSpacing(4)

        # Label betöltése
        self.label = QLabel("Loading...")
        self.label.setStyleSheet("background-color: transparent; font-size: 20px; padding: 0px; margin: 0px;")

        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "digital-7.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            font = QFont(family)
            font.setPointSize(20)
            self.label.setFont(font)

        header_layout.addWidget(self.label)

        # Thin mód gomb
        thin_btn = QPushButton("ー")
        thin_btn.setFixedSize(32, 32)
        thin_btn.setStyleSheet("""
            QPushButton {
                color: rgba(0, 255, 0);
                background-color: rgba(161, 161, 161, 200);
                border: 2px solid #3c3c3c;
                border-radius: 16px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(151, 255, 121, 200);
                color: rgba(0, 255, 0, 200);
            }
        """)
        thin_btn.clicked.connect(self.show_thin_layout)
        header_layout.addWidget(thin_btn)

        # Kilépés gomb
        exit_btn = QPushButton("✘")
        exit_btn.setFixedSize(32, 32)
        exit_btn.setStyleSheet("""
            QPushButton {
                color: rgba(255, 0, 0);
                background-color: rgba(161, 161, 161, 200);
                border: 2px solid #3c3c3c;
                border-radius: 16px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0);
                color: rgba(255, 100, 100, 200);
            }
        """)
        exit_btn.clicked.connect(self.close)
        header_layout.addWidget(exit_btn)
        layout.addWidget(header_widget)

        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: transparent; padding: 2;")
        layout.addWidget(self.list_widget)

        # Lista feltöltése
        items = [
            ("Process killer", "killer.sh"),
            ("Processes List", "proclist.py"),
            ("Még", "meg.sh"),
            ("Semmi", "semmi.sh"),
        ]
        self.script_map = {name: path for name, path in items}

        for name, _ in items:
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)

            lbl = QLabel(name)
            lbl.setStyleSheet("background-color: transparent; color: lime; font-size: 16px;")

            btn = QPushButton("➤")
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    color: rgba(0, 255, 0);
                    background-color: rgba(161, 161, 161, 200);
                    border: 2px solid #3c3c3c;
                    border-radius: 16px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(151, 255, 121, 200);
                    color: rgba(0, 255, 0, 200);
                }
            """)
            btn.clicked.connect(lambda _, n=name: self.list_button_clicked(n))

            item_layout.addWidget(lbl)
            item_layout.addStretch()
            item_layout.addWidget(btn)

            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

        return layout

    
    def create_thin_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.thin_label = QLabel()
        self.thin_label.setAlignment(Qt.AlignCenter)

        self.thin_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.thin_label, 1)

        # Vissza gomb
        back_btn = QPushButton(" ")
        back_btn.setFixedSize(24, 24)
        back_btn.setStyleSheet("""
            QPushButton {
                color: rgba(0, 255, 0);
                background-color: rgba(161, 161, 161, 200);
                border: 2px solid #3c3c3c;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(151, 255, 121, 200);
                color: rgba(0, 255, 0, 200);
            }
        """)
        back_btn.clicked.connect(self.show_main_layout)
        layout.addWidget(back_btn)
        layout.setAlignment(back_btn, Qt.AlignVCenter)

        return layout
    
    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(self.bg_image_path)
        painter.drawPixmap(self.rect(), pixmap)

    def resizeEvent(self, event):
        if event.size() != event.oldSize():
            self.pixmap = QPixmap(self.size())
            self.pixmap.fill(Qt.transparent)
        super().resizeEvent(event)



    def show_thin_layout(self):
        self.stack.setCurrentIndex(1)
        self.side_widget.hide()
        self.main_widget.hide()
        self.setFixedSize(250, 32)  
        self.adjustSize()  


    def show_main_layout(self):
        self.stack.setCurrentIndex(0)
        self.stack_container.updateGeometry()

        # FELOLDJUK A FIXÁLÁST
        self.setMinimumSize(0, 0)
        from PyQt5.QtWidgets import QWIDGETSIZE_MAX
        self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self.adjustSize()

    def show_side_panel(self):
        self.side_widget.show()
        self.adjustSize()  

        
    def hide_side_widget(self):
        self.side_widget.hide()
        self.adjustSize() 


    def update_temps(self):
        cpu = self.get_cpu_temp()
        gpu = self.get_gpu_temp()

        cpu_str = f"{float(cpu):4.1f}" if cpu != "--" else "--.-"
        gpu_str = f"{float(gpu):4.1f}" if gpu != "--" else "--.-"

        def temp_color(temp):
            try:
                t = float(temp)
                if t <= 65:
                    return "lime"
                elif t <= 89:
                    return "orange"
                else:
                    return "red"
            except:
                return "white"

        cpu_color = temp_color(cpu)
        gpu_color = temp_color(gpu)

        # Main label HTML-ben maradhat (színezés miatt)
        self.label.setText(f"CPU: <span style='color:{cpu_color}'>{cpu_str}°C</span> | GPU: <span style='color:{gpu_color}'>{gpu_str}°C</span>")

        # Thin label: HTML formázással színezett szöveg
        if self.digital_family:
            font = QFont(self.digital_family)
        else:
            font = QFont("DejaVu Sans Mono")
        font.setPointSize(16) 
        self.thin_label.setFont(font)

        self.thin_label.setStyleSheet("background-color: black; font-size: 20px; padding: 0px; margin: 0px;")
        self.thin_label.setText(
            f"C: <span style='color:{cpu_color}'>{cpu_str}°C</span>  "
            f"G: <span style='color:{gpu_color}'>{gpu_str}°C</span>"
        )

    def get_cpu_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.readline().strip()) / 1000
                return f"{temp:.1f}"
        except:
            return "--"

    def get_gpu_temp(self):
        try:
            output = subprocess.check_output([
                "nvidia-smi",
                "--query-gpu=temperature.gpu",
                "--format=csv,noheader,nounits"
            ])
            return output.decode("utf-8").strip()
        except:
            return "--"

    def list_button_clicked(self, name):
        if name == "Processes List":
            if self.main_layout.indexOf(self.side_widget) == -1:
                self.main_layout.addWidget(self.side_widget)
            self.side_widget.show()
        else:
            script_name = self.script_map.get(name)
            if script_name:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
                if os.path.exists(path):
                    if script_name.endswith(".sh"):
                        subprocess.Popen(["bash", path])
                    elif script_name.endswith(".py"):
                        subprocess.Popen([sys.executable, path])
                    else:
                        print("Ismeretlen kiterjesztés.")
                else:
                    print("Script nem található.")
                    
def check_single_instance():
    username = getpass.getuser()
    lockfile_path = f"/tmp/tempmonitor_{username}.lock"
    global lockfile
    lockfile = open(lockfile_path, 'w')
    try:
        fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Már fut egy példány.")
        sys.exit(0)
        
if __name__ == "__main__":
    check_single_instance()
    app = QApplication(sys.argv)
    window = TempMonitor()
    window.show()
    sys.exit(app.exec_())

