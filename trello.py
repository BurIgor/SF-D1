import sys
import requests

# Данные авторизации в API Trello
auth_params = {
    'key': "Ваш key",
    'token': "Ваш token",
}

# Адрес, на котором расположен API Trello, # Именно туда мы будем отправлять HTTP запросы.
base_url = "https://api.trello.com/1/{}"

# Идентификатор доски
board_id = "Ваш board_id"


def read():
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print('[' + str(len(task_data)) + '] ' + column['name'])
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['id'] + ' : ' + '\t' + task['name'])


def create(name, column_name):
    # Получим данные всех колонок на доске
    columns = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in columns:
        # Создадим задачу с именем _name_ в найденной колонке
        if column['name'] == column_name:
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            break


def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Среди всех колонок нужно собрать задачи, с заданным именем и получить их id
    tasks = {}
    task_id = None
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                tasks[len(tasks)] = task['id']
                print('\t№ ' + str(len(tasks) - 1) + ' : \t' + task['name'] +
                      '\t колонка: "' + column['name'] +
                      '"\t id: ' + task['id'])

    if not len(tasks):
        print('Такой задачи нет.')
        return

    if len(tasks) == 1:
        task_number = 0
    else:
        task_number = int(input('Укажите номер карточки для перемещения: '))

    if task_number < 0 or task_number >= len(tasks):
        print('Указан несуществующий номер карточки.')
        return

    task_id = tasks[task_number]

    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                         data={'value': column['id'], **auth_params})
            print('Карточка перемещена.')
            break


def add_column(column_name):
    # Проверяем существование колонки с заданным именем
    # Получим данные всех колонок на доске
    columns = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках
    for column in columns:
        # Проверяем совпадение названия колонки
        if column['name'] == column_name:
            print('Колонка с таким именем уже существует.  Дубликат колонки не создан.')
            return

    # Создаем колонку с заданным именем
    requests.post(base_url.format('boards/' + board_id + '/lists'),
                  data={'name': column_name, 'idBoard': board_id, **auth_params})

    # Выводим данные, чтобы убедиться в том, что новая колонка создана
    read()


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'add_column':
        add_column(sys.argv[2])
