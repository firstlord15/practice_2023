import sys
from config import db_config_main, NAME_PROGRAMM
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, \
    QComboBox, QPushButton
from PySide6.QtGui import QColor, QIcon, QPalette, Qt
from PySide6.QtCore import Qt
import psycopg2
from api_view import start_program_api

data_cache = {}  # Словарь для кэширования данных


def check():
    conn = psycopg2.connect(**db_config_main)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM access_logs")
    result = cursor.fetchone()
    record_count = result[0]  # Количество записей в таблице

    cursor.close()
    conn.close()

    if record_count == 0:
        # Если база данных пуста, показываем сообщение
        print('База данных пуста. Открытие приложения невозможно.')
        sys.exit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NAME_PROGRAMM)

        # Настройка иконки формы
        icon = QIcon("src/files/Hyper_Alt.png")
        self.setWindowIcon(icon)

        # Подключение к базе данных
        conn = psycopg2.connect(**db_config_main)
        cursor = conn.cursor()

        # Выполнение запроса для извлечения данных из таблицы
        query = "SELECT * FROM access_logs"
        result = self.execute_query(query)

        cursor.execute(query)
        # Получение списка названий столбцов

        column_names = [desc[0] for desc in cursor.description]

        # Получение списка уникальных IP-адресов
        unique_ips = set(row[2] for row in result)

        # Закрытие соединения с базой данных
        cursor.close()
        conn.close()

        # Создание таблицы
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(result))
        self.table_widget.setColumnCount(len(result[0]))
        self.table_widget.setHorizontalHeaderLabels(column_names)

        self.table_widget.setStyleSheet(
            "QHeaderView::section { background-color: #444444; color: #ffffff; }"
            "QHeaderView { background-color: #444444; }"
        )

        for i, row in enumerate(result):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(i, j, item)

        # Создание флажков (checkbox) для сортировки
        self.sort_ip_button = QPushButton("Сортировать по IP")
        self.sort_date_button = QPushButton("Сортировать по дате")

        # Создание выпадающего списка (combobox) для выбора IP
        self.ip_combobox = QComboBox()
        self.ip_combobox.addItems(['None'] + sorted(unique_ips))
        self.ip_combobox.setStyleSheet("QComboBox { color: black; }")

        # Создание кнопки фильтрации
        self.filter_button = QPushButton("Применить фильтр")
        self.filter_button.clicked.connect(self.apply_filter)
        self.api_button = QPushButton("Сохранить в json файле")
        self.api_button.clicked.connect(self.api)

        # Обработчики событий для флажков
        self.sort_ip_button.clicked.connect(self.sort_table_ip)
        self.sort_date_button.clicked.connect(self.sort_table_date)

        # Создание виджета, содержащего таблицу, флажки и элементы фильтрации
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.sort_ip_button)
        layout.addWidget(self.sort_date_button)
        layout.addWidget(self.ip_combobox)
        layout.addWidget(self.filter_button)
        layout.addWidget(self.api_button)
        widget.setLayout(layout)

        # Установка виджета в главное окно
        self.setCentralWidget(widget)

        self.table_widget.setSortingEnabled(True)

    @staticmethod
    def execute_query(query):
        if query in data_cache:  # Проверка наличия результата запроса в кэше
            return data_cache[query]
        else:
            # Подключение к базе данных
            conn = psycopg2.connect(**db_config_main)
            cursor = conn.cursor()

            try:
                # Выполнение запроса
                cursor.execute(query)
                result = cursor.fetchall()

                # Закрытие соединения с базой данных
                cursor.close()
                conn.close()

                data_cache[query] = result  # Сохранение результата запроса в кэше
                return result
            except Exception as e:
                print(f"Ошибка выполнения запроса: {e}")
                return []

    def refresh_data(self):
        query = "SELECT * FROM access_logs"
        result = self.execute_query(query)

        self.table_widget.clearContents()
        self.table_widget.setRowCount(len(result))
        self.table_widget.setColumnCount(len(result[0]))

        for i, row in enumerate(result):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(i, j, item)

    def sort_table_ip(self):
        ip_column_index = 2  # Индекс столбца IP
        self.table_widget.sortItems(ip_column_index, Qt.SortOrder.AscendingOrder)

    def sort_table_date(self):
        date_column_index = 3  # Индекс столбца даты
        self.table_widget.sortItems(date_column_index, Qt.SortOrder.AscendingOrder)

    @staticmethod
    def api():
        start_program_api()
        sys.exit()

    def apply_filter(self):
        selected_ip = self.ip_combobox.currentText()

        # Если выбранный IP-адрес равен None, отображаем все строки
        if selected_ip == 'None':
            for row in range(self.table_widget.rowCount()):
                self.table_widget.setRowHidden(row, False)
            return

        # Перебор всех строк таблицы и скрытие тех, которые не соответствуют выбранному IP
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 2)  # Получение ячейки с IP (индекс столбца 2)
            self.table_widget.setRowHidden(row, item.text() != selected_ip)


def start_program_parser_view():
    app = QApplication(sys.argv)
    # Установка темного фона

    palette = QApplication.palette()
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    QApplication.setPalette(palette)

    window = MainWindow()
    window.setMinimumSize(1000, 600)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    check()
    start_program_parser_view()