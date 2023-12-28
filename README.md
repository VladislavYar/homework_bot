# homework_bot

Проект представляет из себя телеграмм бота, который по средствам взаимодествия с
API сервиса Практикум.Домашка, отправляет в личный чат пользователя актуальную информацию
о домашнем задании (в случае изменения статуса), а так же информацию о случившихся ошибках.

## Шаблон наполнения env-файла
- PRACTICUM_TOKEN=TOKEN_1 # получить по адрессу https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a
- TELEGRAM_TOKEN=TOKEN_2 # получить у телеграмм бота @BotFather (https://t.me/BotFather)
- TELEGRAM_CHAT_ID=ID # Ваш ID можно узнать через телеграмм бота @userinfobot (https://t.me/userinfobot)

## Как запустить проект:

В терминале, перейдите в каталог, в который будет загружаться приложение:
```
cd 
```
Клонируйте репозиторий:
```
git clone git@github.com:VladislavYar/homework_bot.git
```
### На данном этапе создайте env-файл по шаблону из раздела выше

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Запуск проект:
```
python homework.py
```

## Cтек проекта
Python v3.9, python-telegram-bot
