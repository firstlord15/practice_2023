import os
import json
import psycopg2

CONFIG_FILE_PATH = 'config/config.json'


# Загрузка конфигурационного файла
def load_config():
    try:
        with open(CONFIG_FILE_PATH) as config_file:
            config = json.load(config_file)
            required_keys = ["name_programm", "postgres", "database", "log_file_path", "result_files_path",
                             "user_editable_fields", "log_file_mask"]
            for key in required_keys:
                if key not in config:
                    print(f"Ошибка: отсутствует обязательный ключ '{key}' в файле конфигурации '{CONFIG_FILE_PATH}'.")
                    exit(1)
            return config
    except FileNotFoundError:
        print(f"Ошибка: файл конфигурации '{CONFIG_FILE_PATH}' не найден.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: некорректный формат файла конфигурации '{CONFIG_FILE_PATH}'.")
        exit(1)


# Загатавливаю данны
config_data = load_config()
RESULT_PATH = config_data["result_files_path"]
LOGS_PATH = config_data["log_file_path"]
NAME_PROGRAMM = config_data["name_programm"]

db_config_main = {
    'dbname': config_data['database']['dbname'],
    'user': config_data['database']['username'],
    'password': config_data['database']['password'],
    'host': config_data['database']['host'],
    'port': config_data['database']['port']
}

db_config_postgres = {
    'dbname': config_data['postgres']['dbname'],
    'user': config_data['postgres']['username'],
    'password': config_data['postgres']['password'],
    'host': config_data['postgres']['host'],
    'port': config_data['postgres']['port']
}


# Сохранение конфигурационного файла
def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(config, config_file, indent=4)


def edit_config():
    print("\nДоступные разделы для редактирования:")
    for section in config_data["user_editable_fields"]:
        print(f"- {section}")

    section = input("Выберите раздел для редактирования: ")

    if section in config_data["user_editable_fields"]:
        # Редактирование значений в выбранном разделе
        print(f"\nРедактирование раздела '{section}':\n")
        try:
            while True:
                for key, value in config_data[section].items():
                    new_value = input(f"Введите новое значение для '{key}' (текущее значение: {value}, для выхода введите 'exit'): ")
                    if new_value.lower() == "exit":
                        break
                    if key == "log_file_path" and not os.path.exists(new_value):
                        while not os.path.exists(new_value):
                            print(f"Файл '{new_value}' не найден.")
                            new_value = input(f"Введите новое значение для '{key}' (для выхода введите 'exit'): ")
                            if new_value.lower() == "exit":
                                break
                    config_data[section][key] = new_value
                else:
                    break
        except AttributeError:
            if isinstance(config_data[section], str):
                new_value = input(f"Введите новое значение для '{section}' (текущее значение: {config_data[section]}, для выхода введите 'exit'): ")
                if new_value.lower() == "exit":
                    pass
                elif section == "log_file_path" and not os.path.exists(new_value):
                    while not os.path.exists(new_value):
                        print(f"Файл '{new_value}' не найден.")
                        new_value = input(f"Введите новое значение для '{section}' (для выхода введите 'exit'): ")
                        if new_value.lower() == "exit":
                            break
                else:
                    config_data[section] = new_value
            else:
                while True:
                    for value in config_data[section]:
                        new_value = input(f"Введите новое значение для '{section} -> {value}' (текущее значение: {config_data[section][value]}, для выхода введите 'exit'): ")
                        if new_value.lower() == "exit":
                            break
                        if value == "log_file_path" and not os.path.exists(new_value):
                            while not os.path.exists(new_value):
                                print(f"Файл '{new_value}' не найден.")
                                new_value = input(f"Введите новое значение для '{section} -> {value}' (для выхода введите 'exit'): ")
                                if new_value.lower() == "exit":
                                    break
                        config_data[section][value] = new_value
                    else:
                        break

        # Проверка подключения к базе данных после изменения данных
        if section == "postgres":
            check_postgres_connection(config_data)

        # Сохранение изменений в конфигурационном файле
        save_config(config_data)
        print("Конфигурационный файл успешно обновлен.\n")
    else:
        print("Неверный раздел для редактирования.\n")
        edit_config()



# Проверка подключения к базе данных PostgreSQL
def check_postgres_connection(config):
    try:
        conn = psycopg2.connect(
            dbname=config["postgres"]["dbname"],
            user=config["postgres"]["username"],
            password=config["postgres"]["password"],
            host=config["postgres"]["host"],
            port=config["postgres"]["port"]
        )
        conn.close()
        print("Успешное подключение к базе данных PostgreSQL.")
    except psycopg2.Error as e:
        print("Ошибка подключения к базе данных PostgreSQL:")
        print(e)
        exit(1)


# Главная функция программы
def main():
    while True:
        print("\nМеню:")
        print("1. Редактировать данные в конфигурационном файле")
        print("2. Проверить подключение к базе данных PostgreSQL")
        print("3. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            edit_config()
        elif choice == "2":
            check_postgres_connection(config_data)
        elif choice == "3":
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
