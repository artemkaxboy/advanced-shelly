# Shelly Gen2+ API Reference для работы со скриптами

## Основные endpoint'ы

### 1. Получение информации об устройстве
```
GET http://{device_ip}/rpc/Shelly.GetDeviceInfo
```

Ответ:
```json
{
  "name": "My Shelly Plus 1PM",
  "id": "shellyplus1pm-a8032ab12345",
  "mac": "A8032AB12345",
  "model": "SNSW-001P16EU",
  "gen": 2,
  "fw_id": "20230913-114450/v1.14.0-gcb84623",
  "ver": "1.14.0",
  "app": "Plus1PM",
  "auth_en": false,
  "auth_domain": null
}
```

### 2. Получение списка скриптов
```
GET http://{device_ip}/rpc/Script.List
```

Ответ:
```json
{
  "scripts": [
    {
      "id": 1,
      "name": "my_automation",
      "enable": true,
      "running": true
    },
    {
      "id": 2,
      "name": "humidity_control",
      "enable": false,
      "running": false
    }
  ]
}
```

### 3. Получение кода скрипта
```
GET http://{device_ip}/rpc/Script.GetCode?id={script_id}
```

Ответ:
```json
{
  "data": "let CONFIG = {\n  humidity_threshold: 70,\n  fan_switch_id: 0\n};\n\n// Script code here..."
}
```

### 4. Загрузка кода скрипта
```
POST http://{device_ip}/rpc/Script.PutCode
Content-Type: application/json

{
  "id": 1,
  "code": "let CONFIG = {...};\n// Your script code",
  "append": false
}
```

Ответ:
```json
{
  "len": 1234
}
```

### 5. Создание нового скрипта
```
POST http://{device_ip}/rpc/Script.Create
Content-Type: application/json

{
  "name": "new_script"
}
```

Ответ:
```json
{
  "id": 3
}
```

### 6. Удаление скрипта
```
POST http://{device_ip}/rpc/Script.Delete
Content-Type: application/json

{
  "id": 3
}
```

### 7. Включение/выключение скрипта
```
POST http://{device_ip}/rpc/Script.SetConfig
Content-Type: application/json

{
  "id": 1,
  "config": {
    "enable": true
  }
}
```

### 8. Запуск/остановка скрипта
```
POST http://{device_ip}/rpc/Script.Start
Content-Type: application/json

{
  "id": 1
}
```

```
POST http://{device_ip}/rpc/Script.Stop
Content-Type: application/json

{
  "id": 1
}
```

### 9. Получение статуса скрипта
```
GET http://{device_ip}/rpc/Script.GetStatus?id={script_id}
```

Ответ:
```json
{
  "running": true,
  "mem_used": 1024,
  "mem_peak": 2048,
  "mem_free": 30720,
  "errors": []
}
```

## Ограничения

- **Максимальное количество скриптов**: 10 на устройство
- **Максимальный размер скрипта**: 16 KB
- **Максимальное использование памяти**: ~30 KB на скрипт

## Примеры использования

### Python
```python
import requests
import json

device_ip = "192.168.1.100"

# Получить список скриптов
response = requests.get(f"http://{device_ip}/rpc/Script.List")
scripts = response.json()["scripts"]

# Сохранить код скрипта
for script in scripts:
    response = requests.get(
        f"http://{device_ip}/rpc/Script.GetCode",
        params={"id": script["id"]}
    )
    code = response.json()["data"]
    
    with open(f"script_{script['id']}.js", "w") as f:
        f.write(code)

# Загрузить код скрипта
with open("script_1.js", "r") as f:
    code = f.read()

response = requests.post(
    f"http://{device_ip}/rpc/Script.PutCode",
    json={"id": 1, "code": code}
)
```

### cURL
```bash
# Получить список скриптов
curl http://192.168.1.100/rpc/Script.List

# Получить код скрипта
curl "http://192.168.1.100/rpc/Script.GetCode?id=1"

# Загрузить код скрипта
curl -X POST http://192.168.1.100/rpc/Script.PutCode \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "code": "let x = 1;"}'
```

## Аутентификация

Если на устройстве включена аутентификация:

```python
import requests
from requests.auth import HTTPDigestAuth

auth = HTTPDigestAuth('admin', 'password')
response = requests.get(
    f"http://{device_ip}/rpc/Script.List",
    auth=auth
)
```

## Обработка ошибок

Возможные коды ошибок:

- **-103**: Invalid argument
- **-104**: Timeout
- **-105**: Out of memory
- **-114**: Resource exhausted (too many scripts)
- **-115**: Not allowed
- **401**: Unauthorized (требуется аутентификация)

Пример ответа с ошибкой:
```json
{
  "code": -103,
  "message": "Invalid argument"
}
```

## WebSocket API (для продвинутых случаев)

Shelly Gen2+ также поддерживает WebSocket для получения событий в реальном времени:

```javascript
const ws = new WebSocket('ws://192.168.1.100/rpc');

ws.onmessage = (event) => {
  console.log('Message:', JSON.parse(event.data));
};

// Подписка на события скриптов
ws.send(JSON.stringify({
  "id": 1,
  "method": "Script.GetStatus",
  "params": {"id": 1}
}));
```

## Полезные ссылки

- [Официальная документация Shelly API](https://shelly-api-docs.shelly.cloud/)
- [Примеры скриптов для Shelly](https://github.com/ALLTERCO/shelly-script-examples)
- [Форум сообщества Shelly](https://community.shelly.cloud/)
