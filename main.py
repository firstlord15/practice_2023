from db import check_func  # импорт функции для проверки всех настроек ДБ
from parser import main_func_parser  # импорт парсера
from parser_view import start_program_parser_view  # импорт запуска таблицы
from config import NAME_PROGRAMM, main
from colorama import Fore, init

init()

if __name__ == "__main__":
    print(Fore.YELLOW + f"Добро пожаловать в {NAME_PROGRAMM}\n", Fore.WHITE)

    print("Прошу вас выбрать первый пункт редактирования\nИ изменить настройки 'postgres'\n")
    print(Fore.YELLOW)
    main()  # запускается db_check
    print(Fore.WHITE)
    input('Для продалжения нажмите на ENTER...')

    # Проверка и создания ДБ, Таблиц и функций если их нет.
    print(Fore.GREEN)
    check_func()  # запускается db_check
    print(Fore.WHITE)
    input('Для продалжения нажмите на ENTER...')

    print(Fore.GREEN)
    main_func_parser()  # запускается parser
    print(Fore.WHITE)
    input('Для продалжения нажмите на ENTER...')

    start_program_parser_view()  # запускается parser_view
