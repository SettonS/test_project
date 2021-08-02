ТЕСТОВОЕ ЗАДАНИЕ на позицию 
Junior Backend разработчик

## Docker
   для запуска контейнера требуется скачать docker-compose.yaml
   и выполнить команду docker-compose up
    

## Установка:
    pip install -r requirements.txt

## Запуск:
    run command: gunicorn -w 1 --threads 4 project.wsgi:application

## Эндпоинты
    /:
        GET:
            В ответе содержится поле “response” со списком из 5 клиентов, 
            потративших наибольшую сумму за весь период.

            Каждый клиент описывается следующими полями:
                username - логин клиента;
                spent_money - сумма потраченных средств за весь период;
                gems - список из названий камней, которые купили
                как минимум двое из списка "5 клиентов, потративших
                наибольшую сумму за весь период", и данный клиент является
                одним из этих покупателей.

        POST:
            Аргументы:
                deals: файл, содержащий историю сделок, файл должен иметь имя
                deals.csv

            Ответ:
                • Status: OK - файл был обработан без критических ошибок;
                • Status: Error, Desc: <Описание ошибки>
