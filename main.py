from db import check_func  # импорт функции для проверки всех настроек ДБ
from parser import main_func_parser  # импорт парсера
from parser_view import start_program  # импорт запуска таблицы


if __name__ == "__main__":
    # Проверка и создания ДБ, Таблиц и функций если их нет.
    check_func()
    input('\nДля продалжения нажмите на ENTER...\n')

    main_func_parser()
    input('\nДля продалжения нажмите на ENTER...\n')

    start_program()



