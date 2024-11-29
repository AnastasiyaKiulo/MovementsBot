import sqlite3
from datetime import datetime, date

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("counter.db")
    cursor = conn.cursor()

    # Таблица для счетчиков пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counters (
            user_id INTEGER PRIMARY KEY,
            counter INTEGER DEFAULT 0,
            last_update DATE DEFAULT (DATE('now'))
        )
    """)

    # Таблица для логирования нажатий
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            time DATETIME DEFAULT (DATETIME('now'))
        )
    """)
    conn.commit()
    conn.close()

# def update_db_structure():
#     conn = sqlite3.connect("counter.db")
#     cursor = conn.cursor()

#     # Добавляем столбец last_pressed, если его ещё нет
#     cursor.execute("""
#         ALTER TABLE counters ADD COLUMN last_pressed DATETIME
#     """)
#     conn.commit()
#     conn.close()

# Очистка данных для конкретного пользователя

def add_log_entry(user_id, time):
    conn = sqlite3.connect("counter.db")
    cursor = conn.cursor()

    # Добавляем запись в таблицу log
    cursor.execute(
        "INSERT INTO log (user_id, time) VALUES (?, ?);",
        (user_id, time)
    )

    conn.commit()
    conn.close()

def clear_user_data(user_id):
    conn = sqlite3.connect("counter.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM counters WHERE user_id = ?;", (user_id,))
    cursor.execute("DELETE FROM log WHERE user_id = ?;", (user_id,))
    conn.commit()
    conn.close()

# Проверка и сброс счетчика при смене дня
def reset_if_new_day(user_id):
    conn = sqlite3.connect("counter.db")
    cursor = conn.cursor()

    # Проверяем дату последнего обновления
    cursor.execute("SELECT counter, last_update FROM counters WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    today = date.today()

    if result:
        counter, last_update = result[:2]
        last_update = datetime.strptime(last_update, "%Y-%m-%d").date()

        if last_update < today:  # Если день сменился
            cursor.execute("""
                UPDATE counters SET counter = 0, last_update = DATE('now') WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            counter = 0  # Сбрасываем локально
    else:
        # Если записи для пользователя нет, создаем новую
        cursor.execute("""
            INSERT INTO counters (user_id, counter, last_update) VALUES (?, 0, DATE('now'))
        """, (user_id,))
        conn.commit()
        counter = 0  # Начальное значение

    conn.close()
    return counter

# Увеличение счетчика и запись времени
def increment_counter(user_id):
    conn = sqlite3.connect("counter.db")
    cursor = conn.cursor()

    # Сбрасываем счетчик, если день сменился
    current_value = reset_if_new_day(user_id)

    # Увеличиваем значение счетчика
    cursor.execute("""
        UPDATE counters SET counter = counter + 1 WHERE user_id = ?
    """, (user_id,))
    conn.commit()

    # Логируем нажатие
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO log (user_id, time) VALUES (?, ?)
    """, (user_id, now))
    conn.commit()

    conn.close()
    return current_value + 1  # Возвращаем новое значение

# Получение текущего значения и всех времен
def get_counter_and_logs(user_id):
    conn = sqlite3.connect("counter.db")
    cursor = conn.cursor()

    # Получаем текущее значение счетчика
    cursor.execute("SELECT counter FROM counters WHERE user_id = ?;", (user_id,))
    counter_value = cursor.fetchone()
    counter_value = counter_value[0] if counter_value else 0

    # Получаем логи событий
    cursor.execute("SELECT time FROM log WHERE user_id = ? ORDER BY time;", (user_id,))
    logs = cursor.fetchall()

    conn.close()

    # Группируем логи по дням
    grouped_logs = {}
    for log in logs:
        timestamp = datetime.strptime(log[0], "%Y-%m-%d %H:%M:%S")
        day = timestamp.date()
        if day not in grouped_logs:
            grouped_logs[day] = []
        grouped_logs[day].append(timestamp.strftime("%H:%M"))

    # Формируем текст лога с разделением по дням
    formatted_logs = []
    for day, times in grouped_logs.items():
        formatted_logs.append(f"{day.strftime('%d.%m.%Y')}:")
        formatted_logs.append(" -> ".join(times))
        formatted_logs.append("")  # Пустая строка для разделения дней

    # Убираем последнюю пустую строку
    if formatted_logs and not formatted_logs[-1]:
        formatted_logs.pop()

    return counter_value, "\n".join(formatted_logs)
