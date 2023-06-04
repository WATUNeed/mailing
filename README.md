# Сервис автоматической рассылки

_с использованием внешнего API сервиса_

---

## Стек

* fastapi
* uvicorn
* pydantic
* sqlalchemy
* alembic
* sqlalchemy[asyncio]
* asyncpg
* aiohttp
* celery

---

<a id='requests'></a>
## Устройство API

### Роутер /customer

* #### POST /create

Ожидает на вход _CustomerCreate_ с полями: __phone, code, time_zone__.

> _Атрибут phone должно состоять только из 11 цифр._

> _Атрибут code должно состоять только из 3 цифр (это код оператора)._

Создаёт, сохраняет и выводит _ShowCustomer_ с полями покупателя: __(id, phone, code, time_zone)__.

* #### GET /list

Получате список покупателей из бд и выводит _ShowCustomers_ с полем: 
```
customers [
    id, 
    phone, 
    code, 
    time_zone
]
```

* #### PUT /edit

Ожидает на вход _CustomerEdit_ с полями: __id, phone, code, time_zone__.

> _Если покупателя нет в бд, выводит 404 ошибку._

Изменяет, сохраняет и выводит _ShowCustomer_ с полями покупателя: __(id, phone, code, time_zone)__.

* #### DELETE /delete

Ожидает на вход поле: __customer_id__.

> _Если покупателя нет в бд, выводит 404 ошибку._

Удаляет из бд покупателя и выводит _ShowCustomer_ с полями покупателя: __(id, phone, code, time_zone)__.

### Роутер /mailing

* #### POST /create

Ожидает на вход _MailingCreate_ с полями: __start_date, message, filters, expiry_date__.

> _Значение времени атрибут start_date должено быть новее, чем expiry_date._

> _Атрибут filters должно состоять только из 3 цифр (это код оператора)._

Создаёт, сохраняет и выводит _ShowMailing_ с полями рассылки: __(id, start_date, message, filters, expiry_date)__.

* #### PUT /edit

Ожидает на вход _MailingEdit_ с полями: __id, start_date, message, filters, expiry_date__.

> _Если рассылки нет в бд, выводит 404 ошибку._

Изменяет, сохраняет и выводит _ShowMailing_ с полями рассылки: __(id, start_date, message, filters, expiry_date)__.

* #### DELETE /delete

Ожидает на вход поле: __mailing_id__.

> _Если рассылки нет в бд, выводит 404 ошибку._

Удаляет из бд рассылку и выводит _ShowMailing_ с полями рассылки: __(id, start_date, message, filters, expiry_date)__.

* #### POST /send

Ожидает на вход поле: __mailing_id__.

> _Изменяет атрибуты рассылки __start_date__ и __expiry_date__ на текущую дату и текущую дату + смещение, соответственно. Смещение задаётся в __settings.py__ (settings.MAILING_OFFSET_SEC)._

> _В результате работы рассылки создаются записи в сущности [message](#message_scheme)._

Запускает рассылку и выводит _ShowMailingAPIResponse_ с полями: __(code, message)__.

__Все созданные или изменённые рассылки запускаются автоматически с помощью очереди фоновых задач Celery и Redis.__

### Роутер /message

* #### POST /create

Ожидает на вход _CreateMessage_ с полями: __sending_date, status, mailing_id, customer_id__.

> _Значение атрибута __status__ может быть только значение из models.db.MessageStates(Enum)._

Создаёт, сохраняет и выводит _ShowMessage_ с полями сообщения: __(id, sending_date, status, mailing_id, customer_id)__.

* #### GET /list

Получает из бд список сообщений и выводит _ShowMessages_ с полем: 
```
messages [
    id, 
    sending_date, 
    status, 
    mailing_id, 
    customer_id
]
```

### Роутер /mailing/statistics

* #### GET /by_id

Ожидает на вход поле: __mailing_id__.

> _Подсчёт количества сообщений и распределение по статусам происходит на стороне сервера, а не бд. Т.к. результат запроса в любом случае нужно перебирать в цикле для внесения в output pydantic схему. Сделано с целью не повторять перебор и на стороне сервере и на стороне бд._

Собирает статистику из бд и выводит _ShowStatisticsByMailing_ с полями:
```
start_date, 
message, 
filters, 
expiry_date
id, 
delivered_count, 
undelivered_count, 
delivered_messages [
    start_date, 
    message, 
    filters, 
    expiry_date
    id, 
], 
undelivered_messages [
    start_date, 
    message, 
    filters, 
    expiry_date
    id, 
]
```

* #### GET /all

> _Подсчёт количества рассылок и распределение по состоянию их завершению происходит на стороне сервера, а не бд. Т.к. результат запроса в любом случае нужно перебирать в цикле для внесения в output pydantic схему. Сделано с целью не повторять перебор и на стороне сервере и на стороне бд._

Собирает статистику из бд и выводит _ShowStatisticsMailings_ с полями:
```
completed_mailings_count, 
uncompleted_mailings_count, 
total_delivered_messages, 
total_undelivered_messages, 
mailings [
    start_date, 
    message, 
    filters, 
    expiry_date
    id, 
    delivered_count, 
    undelivered_count, 
    delivered_messages [
        start_date, 
        message, 
        filters, 
        expiry_date
        id, 
    ], 
    undelivered_messages [
        start_date, 
        message, 
        filters, 
        expiry_date
        id, 
    ]
]
```

---

## <a id='schemes'>__Структура базы данных__</a>

#### Схема сущности <a id='customer_scheme'>customer</a>:

id | phone | code | time_zone 
:--|:------|:-----|:---------
UUID | BigInteger | Integer | String 
 ... | ... | ... | ... | ...

#### Схема сущности <a id='mailing_scheme'>mailing</a>:

id | start_date | message | filters | expiry_date
:--|:-----------|:--------|:--------|:-----------
UUID | DateTime | str | Integer | DateTime
 ... | ... | ... | ... | ...

>_Сущности [customer](#customer_scheme) и [mailing](#mailing_scheme) связаны по сущности [message](#message_scheme) и атрибутам __mailing_id__ и __customer_id__ (многие ко многим)._

#### Схема сущности <a id='message_scheme'>message</a>:

id | sending_date | status | mailing_id | customer_id
:--|:-------------|:-------|:-----------|:-----------
UUID | DateTime | String | UUID | UUID
 ... | ... | ... | ... | ...

---

## Как выполнять запросы

1) Запустить API через [docker](#docker).
2) Перейти по ссылке __http:\/\/host:port\/docs\/__.
3) Выполнить нужные [запросы](#requests).

_или через CURL запросы в консоли._

---

## Особенности

> _Подлючен и настроен __Docker__. Используется __docker-compose.yaml__ файл, и __docker_entrypoint.sh__ для автоматической миграции моделей через Alembic._

> _Все сессии подключения к бд происходят через декоратор __utils.decorators.request()__ -> автоматический откат при ошибке, сокращенье повторения кода._

> _Бизнес логика содержится в модуле __servises.py__ и не зависит от FastAPI._

> _Асинхронный ход в Postgres._

> _Обновление очереди рассылок происходит только при изменение в бд -> минимальное  количество запросов к бд._

> _*Узнал о фрейморке для фоновых задач celery только в конце выполнения задания. Планирую реализовать очередь рассылки через фоновые задачи. Возможно уже реализовал._

---

## Инструкции

<a id="docker"></a>
##### Запуск через Docker

1) Выполнить команду:
    ```
    docker-compose up --build
    ```

##### Настройка переменных окружения

1) Создать файл __.env__:
    ```
    # .env
    DB_USER=...
    DB_PASS=...
    DB_NAME=...
    DB_DRIVER=...
    ...
    ```

---
