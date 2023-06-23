from config import load_config
from db import check_func

# Проверка и создания ДБ, Таблиц и функций если их нет.
check_func()

config = load_config()

