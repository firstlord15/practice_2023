from PySide6.QtWidgets import QApplication, QDialog, QLabel, QComboBox, QVBoxLayout, QPushButton, QLineEdit
from api import find_earliest_date, find_latest_date, get_logs, get_result
from config import db_config_main
import psycopg2
import sys


class MyForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Api")

        conn = psycopg2.connect(**db_config_main)
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
        # Получение данных с текстовых полей и комбо бокса
        selected_start_date = self.line_edit_start_date.text()
        selected_end_date = self.line_edit_end_date.text()
        selected_ip = self.combo_box_ip.currentText()

        # Если поле начальной даты не заполнено, используется самая ранняя дата
        if selected_start_date == '':
            selected_start_date = find_earliest_date()

        # Если поле конечной даты не заполнено, используется самая поздняя дата
        if selected_end_date == '':
            selected_end_date = find_latest_date()

        # Если выбран IP 'None', присваивается значение None
        if selected_ip == 'None':
            selected_ip = None

        # Получение отфильтрованных логов
        logs = get_logs(selected_start_date, selected_end_date, selected_ip)

        # Сохранение результата в файл
        get_result(logs)

        self.accept()


def start_program_api():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    form = MyForm()
    form.show()
    form.setFixedSize(400, 200)
    app.exec_()


if __name__ == "__main__":
    start_program_api()
