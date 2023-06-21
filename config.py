import json
import psycopg2

CONFIG_FILE_PATH = 'config.json'


# Загрузка конфигурационного файла
def load_config():
    with open(CONFIG_FILE_PATH) as config_file:
        return json.load(config_file)


# Сохранение конфигурационного файла
def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(config, config_file, indent=4)


# Редактирование данных в конфигурационном файле
def edit_config():
    config = load_config()
    print("Доступные разделы для редактирования:")
    for section in config["user_editable_fields"]:
        print(f"- {section}")

    section = input("Выберите раздел для редактирования: ")

    if section in config["user_editable_fields"]:
        # Редактирование значений в выбранном разделе
        print(f"Редактирование раздела '{section}':")
        for key, value in config[section].items():
            new_value = input(f"Введите новое значение для '{key}' (текущее значение: {value}): ")
            config[section][key] = new_value

        # Проверка подключения к базе данных после изменения данных
        if section == "postgres":
            check_postgres_connection(config)

        # Сохранение изменений в конфигурационном файле
        save_config(config)
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
            config = load_config()
            check_postgres_connection(config["postgres"])
        elif choice == "3":
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
