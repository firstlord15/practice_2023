import json
import psycopg2

CONFIG_FILE_PATH = 'config/config.json'


# Загрузка конфигурационного файла
def load_config():
    with open(CONFIG_FILE_PATH) as config_file:
        return json.load(config_file)


# Загатавливаю данны
config_data = load_config()
RESULT_PATH = config_data["result_files_path"]
LOGS_PATH = config_data["log_file_path"]

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


# Редактирование данных в конфигурационном файле
def edit_config():
    print("Доступные разделы для редактирования:")
    for section in config_data["user_editable_fields"]:
        print(f"- {section}")

    section = input("Выберите раздел для редактирования: ")

    if section in config_data["user_editable_fields"]:
        # Редактирование значений в выбранном разделе
        print(f"Редактирование раздела '{section}':")
        for key, value in config_data[section].items():
            new_value = input(f"Введите новое значение для '{key}' (текущее значение: {value}): ")
            config_data[section][key] = new_value

        # Проверка подключения к базе данных после изменения данных
        if section == "postgres":
            check_postgres_connection(config_data)

        # Сохранение изменений в конфигурационном файле
        save_config(config_data)
        print("Конфигурационный файл успешно обновлен.")
    else:
        print("Неверный раздел для редактирования.")


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


# Главная функция программы
def main():
    while True:
        print("Меню:")
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
