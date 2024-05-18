import time
import threading
from plyer import notification
import tkinter as tk
from tkinter import messagebox
import sqlite3
import json
import os

# Конфигурации и инициализация базы данных
config_path = 'config.json'
default_configurations = {
    "eye_break": 20,
    "physical_exercise": 60,
    "drink_water": 30,
    "full_rest": 120,
}

# Загрузка конфигураций из файла или использование настроек по умолчанию
def load_configurations():
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    else:
        return default_configurations

configurations = load_configurations()

# Подключение и создание таблицы в базе данных
conn = sqlite3.connect('health_tracker.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS progress (
    date TEXT,
    eye_breaks INTEGER,
    physical_exercises INTEGER,
    water_intakes INTEGER,
    full_rests INTEGER
)
''')
conn.commit()

# Функции для уведомлений
def notify(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

def eye_break_notification():
    notify("Перерыв для глаз", "Посмотрите на объект, находящийся на расстоянии 6 метров в течение 20 секунд.")

def physical_exercise_notification():
    notify("Зарядка для тела", "Сделайте растяжку, вращение плеч и приседания.")

def drink_water_notification():
    notify("Пить воду", "Не забудьте выпить стакан воды.")

def full_rest_notification():
    notify("Полный отдых", "Отойдите от компьютера на 15 минут, прогуляйтесь или расслабьтесь.")

# Проверка уведомлений и учет времени для каждой задачи
def check_notifications():
    last_notify_times = {
        "eye_break": time.time(),
        "physical_exercise": time.time(),
        "drink_water": time.time(),
        "full_rest": time.time()
    }

    count = {
        "eye_break": 0,
        "physical_exercise": 0,
        "drink_water": 0,
        "full_rest": 0
    }

    while True:
        current_time = time.time()

        for key in count.keys():
            if (current_time - last_notify_times[key]) >= configurations[key] * 60:
                globals()[f'{key}_notification']()
                count[key] += 1
                last_notify_times[key] = current_time

        # Сохранение данных в конце рабочего дня
        localtime = time.localtime()
        if localtime.tm_hour == 23 and localtime.tm_min == 59:
            cursor.execute('''
                INSERT INTO progress (date, eye_breaks, physical_exercises, water_intakes, full_rests)
                VALUES (?, ?, ?, ?, ?)''',
                (time.strftime('%Y-%m-%d'), count['eye_break'], count['physical_exercise'], count['drink_water'], count['full_rest'])
            )
            conn.commit()

        time.sleep(1)

# Запуск функции проверки уведомлений в отдельном потоке
notification_thread = threading.Thread(target=check_notifications)
notification_thread.daemon = True
notification_thread.start()

# Создание GUI для настройки
root = tk.Tk()
root.title("Здоровый Кодер")

# Добавление элементов GUI для настройки
tk.Label(root, text="Настройки напоминаний:").pack(pady=10)

eye_break_interval = tk.IntVar(value=configurations["eye_break"])
tk.Label(root, text="Перерыв для глаз (минуты)").pack()
tk.Entry(root, textvariable=eye_break_interval).pack()

physical_exercise_interval = tk.IntVar(value=configurations["physical_exercise"])
tk.Label(root, text="Зарядка (минуты)").pack()
tk.Entry(root, textvariable=physical_exercise_interval).pack()

drink_water_interval = tk.IntVar(value=configurations["drink_water"])
tk.Label(root, text="Пить воду (минуты)").pack()
tk.Entry(root, textvariable=drink_water_interval).pack()

full_rest_interval = tk.IntVar(value=configurations["full_rest"])
tk.Label(root, text="Полный отдых (минуты)").pack()
tk.Entry(root, textvariable=full_rest_interval).pack()

# Сохранение текущих конфигураций в файл
def save_configurations():
    configurations["eye_break"] = eye_break_interval.get()
    configurations["physical_exercise"] = physical_exercise_interval.get()
    configurations["drink_water"] = drink_water_interval.get()
    configurations["full_rest"] = full_rest_interval.get()

    with open(config_path, 'w') as config_file:
        json.dump(configurations, config_file)

    messagebox.showinfo("Настройки", "Настройки сохранены успешно!")

tk.Button(root, text="Сохранить настройки", command=save_configurations).pack(pady=10)

root.mainloop()

# Закрытие базы данных при выходе из программы
conn.close()
