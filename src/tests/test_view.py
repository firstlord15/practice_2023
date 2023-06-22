import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QCheckBox, QComboBox, QPushButton, QLineEdit
from PySide6.QtGui import QColor, QPalette, Qt
import psycopg2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Приложение с таблицей")

        # Подключение к базе данных
        conn = psycopg2.connect(dbname='Practice', user='postgres', password='0909', host='localhost')
        cursor = conn.cursor()

        # Выполнение запроса для извлечения данных из таблицы
        query = "SELECT * FROM access_logs"
        cursor.execute(query)
        result = cursor.fetchall()

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

        self.table_widget.setStyleSheet("QHeaderView::section { background-color: #444444; color: #ffffff; }"
                                        "QHeaderView { background-color: #444444; }")

        for i, row in enumerate(result):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(i, j, item)

        # Создание флажков (checkbox) для сортировки
        self.checkbox_ip = QCheckBox("Сортировать по IP")
        self.checkbox_date = QCheckBox("Сортировать по дате")

        # Создание выпадающего списка (combobox) для выбора IP
        self.ip_combobox = QComboBox()
        self.ip_combobox.setFixedWidth(300)
        self.ip_combobox.addItems(sorted(unique_ips))
        self.ip_combobox.setStyleSheet("QComboBox { color: black; }")

        # Создание кнопки фильтрации
        self.filter_button = QPushButton("Применить фильтр")
        self.filter_button.setFixedWidth(150)
        self.filter_button.clicked.connect(self.apply_filter)

        # Обработчики событий для флажков
        self.checkbox_ip.stateChanged.connect(self.sort_table)
        self.checkbox_date.stateChanged.connect(self.sort_table)

        # Создание виджета, содержащего таблицу, флажки и элементы фильтрации
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.checkbox_ip)
        layout.addWidget(self.checkbox_date)
        layout.addWidget(self.ip_combobox)
        layout.addWidget(self.filter_button)
        widget.setLayout(layout)

        # Установка виджета в главное окно
        self.setCentralWidget(widget)

        self.table_widget.setSortingEnabled(True)

    def sort_table(self):
        # Получение состояния флажков
        sort_by_ip = self.checkbox_ip.isChecked()
        sort_by_date = self.checkbox_date.isChecked()

        # Определение индексов столбцов для сортировки
        id_colum_index = 0  # Индекс столбца ID
        ip_column_index = 1  # Индекс столбца IP
        date_column_index = 2  # Индекс столбца даты

        # Сортировка таблицы в зависимости от состояния флажков
        if sort_by_ip and sort_by_date:
            self.table_widget.sortItems(ip_column_index, Qt.SortOrder.AscendingOrder)
            self.table_widget.sortItems(date_column_index, Qt.SortOrder.AscendingOrder)
        elif sort_by_ip:
            self.table_widget.sortItems(ip_column_index, Qt.SortOrder.AscendingOrder)
        elif sort_by_date:
            self.table_widget.sortItems(date_column_index, Qt.SortOrder.AscendingOrder)
        else:
            # Сортировка отключена, восстанавливаем исходный порядок
            self.table_widget.sortItems(id_colum_index, Qt.SortOrder.AscendingOrder)

    def apply_filter(self):
        selected_ip = self.ip_combobox.currentText()

        # Перебор всех строк таблицы и скрытие тех, которые не соответствуют выбранному IP
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 2)  # Получение ячейки с IP (индекс столбца 1)
            if item.text() != selected_ip:
                self.table_widget.setRowHidden(row, True)
            else:
                self.table_widget.setRowHidden(row, False)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Установка темного фона
    palette = QApplication.palette()
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    QApplication.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
