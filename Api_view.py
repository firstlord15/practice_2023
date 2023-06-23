from PySide6.QtWidgets import QApplication, QDialog, QLabel, QComboBox, QVBoxLayout, QPushButton
import sys


class MyForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Форма с фильтрами")

        # Создание элементов формы
        label_earliest_date = QLabel(f"Самая ранняя дата: {find_earliest_date()}")
        label_latest_date = QLabel(f"Самая поздняя дата: {find_latest_date()}")
        label_all_ips = QLabel(f"Все виды IP: {find_unique_ips()}")

        combo_box_ip = QComboBox()
        # Здесь можно добавить значения в комбинированный список IP

        button_filter = QPushButton("Применить фильтр")
        button_filter.clicked.connect(self.apply_filter)

        # Создание компоновщика вертикального размещения
        layout = QVBoxLayout()
        layout.addWidget(label_earliest_date)
        layout.addWidget(label_latest_date)
        layout.addWidget(label_all_ips)
        layout.addWidget(combo_box_ip)
        layout.addWidget(button_filter)

        self.setLayout(layout)

    def apply_filter(self):
        selected_ip = combo_box_ip.currentText()
        # Здесь можно обработать выбранный IP и выполнить соответствующие действия

        # Закрытие текущей формы
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    form = MyForm()
    form.show()

    sys.exit(app.exec())
