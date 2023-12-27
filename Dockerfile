# Используем образ Ubuntu 20.04
FROM ubuntu:20.04

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Создание и переход в рабочую директорию
WORKDIR /app

# Копирование исходного кода в контейнер
COPY . /app

# Установка зависимостей Python
RUN pip3 install -r requirements.txt

# Команда для запуска бота
CMD ["python3", "naimibot.py"]
