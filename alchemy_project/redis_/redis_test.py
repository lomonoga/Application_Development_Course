import redis

# Подключение к локальному Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Проверка подключения
try:
    client.ping()
    print("Успешное подключение к Redis")
except redis.ConnectionError:
    print("Ошибка подключения к Redis")
    exit(1)

# Установка и получение значения
client.set("user:name", "Иван")
name = client.get("user:name")
print(f"Имя: {name}")

# Установка с TTL
client.setex("session:123", 3600, "active")
print("Установлена сессия с TTL 3600 сек")

# Работа с числами
client.set("counter", 0)
client.incr("counter")
client.incrby("counter", 5)
client.decr("counter")
print(f"Счетчик: {client.get('counter')}")

# Установка полей
client.hset("user:1000", mapping={
    "name": "Иван",
    "age": "30",
    "city": "Москва"
})
print("Создан хеш user:1000")

# Получение значений
name = client.hget("user:1000", "name")
all_data = client.hgetall("user:1000")
print(f"Имя из хеша: {name}")
print(f"Все данные: {all_data}")

# Проверка существования поля
exists = client.hexists("user:1000", "email")
print(f"Поле email существует: {exists}")

# Получение всех ключей или значений
keys = client.hkeys("user:1000")
values = client.hvals("user:1000")
print(f"Ключи: {keys}")
print(f"Значения: {values}")

# Добавление элементов
client.lpush("tasks", "task1", "task2")
client.rpush("tasks", "task3", "task4")
print("Добавлены задачи в список")

# Получение элементов
tasks = client.lrange("tasks", 0, -1)
first_task = client.lpop("tasks")
last_task = client.rpop("tasks")
print(f"Все задачи: {tasks}")
print(f"Первая задача: {first_task}")
print(f"Последняя задача: {last_task}")

# Получение длины списка
length = client.llen("tasks")
print(f"Осталось задач: {length}")

# Добавление элементов
client.sadd("tags", "python", "redis_", "database")
client.sadd("languages", "python", "java", "javascript")
print("Созданы множества tags и languages")

# Проверка принадлежности
is_member = client.sismember("tags", "python")
print(f"python в tags: {is_member}")

# Получение всех элементов
all_tags = client.smembers("tags")
print(f"Все теги: {all_tags}")

# Операции с множествами
intersection = client.sinter("tags", "languages")
union = client.sunion("tags", "languages")
difference = client.sdiff("tags", "languages")
print(f"Пересечение: {intersection}")
print(f"Объединение: {union}")
print(f"Разность (tags - languages): {difference}")

# Добавление элементов с оценкой
client.zadd("leaderboard", {
    "player1": 100,
    "player2": 200,
    "player3": 150
})
print("Создан leaderboard")

# Получение элементов по рангу
top_players = client.zrange("leaderboard", 0, 2, withscores=True)
print(f"Топ-3 игрока: {top_players}")

# Получение элементов по оценке
players_by_score = client.zrangebyscore("leaderboard", 100, 200)
print(f"Игроки с score 100-200: {players_by_score}")

# Получение ранга элемента
rank = client.zrank("leaderboard", "player1")
print(f"Ранг player1: {rank}")

print("\nВсе операции выполнены успешно!")
