from PySide6.QtWidgets import QApplication, QDialog, QLabel, QComboBox, QVBoxLayout, QPushButton, QLineEdit
from api import find_earliest_date, find_latest_date, get_logs, get_result
import psycopg2
import sys

from config import load_config

config = load_config()

db_config = {
    'dbname': config['database']['dbname'],
    'user': config['database']['username'],
    'password': config['database']['password'],
    'host': config['database']['host'],
    'port': config['database']['port']
}


class MyForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Api")

        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()

        query = "SELECT * FROM access_logs"
        cursor.execute(query)
        data = cursor.fetchall()

        unique_ips = set(row[2] for row in data)

        cursor.close()
        conn.close()

        # Создание элементов формы
        self.label_earliest_date = QLabel(f"Самая ранняя дата: {find_earliest_date()}")
        self.line_edit_start_date = QLineEdit()
        self.line_edit_start_date.setPlaceholderText("Введите начальную дату (ГГГГ-ММ-ДД)")

        self.label_latest_date = QLabel(f"Самая поздняя дата: {find_latest_date()}")
        self.line_edit_end_date = QLineEdit()
        self.line_edit_end_date.setPlaceholderText("Введите конечную дату (ГГГГ-ММ-ДД)")

        self.combo_box_ip = QComboBox()
        self.combo_box_ip.addItems(['None'] + sorted(unique_ips))

        self.button_filter = QPushButton("Применить фильтр")
        self.button_filter.clicked.connect(self.apply_filter)

        layout = QVBoxLayout()
        layout.addWidget(self.label_earliest_date)
        layout.addWidget(self.label_latest_date)
        layout.addWidget(self.line_edit_start_date)
        layout.addWidget(self.line_edit_end_date)
        layout.addWidget(self.combo_box_ip)
        layout.addWidget(self.button_filter)

        self.setLayout(layout)

    def apply_filter(self):
        # Тут берем данные с текстовых полей и комбо бокса
        selected_start_date = self.line_edit_start_date.text()
        selected_end_date = self.line_edit_end_date.text()
        selected_ip = self.combo_box_ip.currentText()

        logs = get_logs(selected_start_date, selected_end_date, selected_ip)  # Форматируем, фильтруем
        get_result(logs)  # загружаем файл

        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    form = MyForm()
    form.show()

    form.setFixedSize(400, 200)

    sys.exit(app.exec())
