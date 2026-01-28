# Shelly Gen2+ API Reference for Scripts and Configuration

## Core endpoints

### 1. Get device info
```
GET {device_url}/rpc/Shelly.GetDeviceInfo
```

Response:
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

### 2. List scripts
```
GET {device_url}/rpc/Script.List
```

Response:
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

### 3. Get script code
```
GET {device_url}/rpc/Script.GetCode?id={script_id}
```

Response:
```json
{
  "data": "let CONFIG = {\n  humidity_threshold: 70,\n  fan_switch_id: 0\n};\n\n// Script code here..."
}
```

### 4. Upload script code
```
POST {device_url}/rpc/Script.PutCode
Content-Type: application/json

{
  "id": 1,
  "code": "let CONFIG = {...};\n// Your script code",
  "append": false
}
```

Response:
```json
{
  "len": 1234
}
```

### 5. Create a new script
```
POST {device_url}/rpc/Script.Create
Content-Type: application/json

{
  "name": "new_script"
}
```

Response:
```json
{
  "id": 3
}
```

### 6. Delete a script
```
POST {device_url}/rpc/Script.Delete
Content-Type: application/json

{
  "id": 3
}
```

### 7. Enable/disable a script
```
POST {device_url}/rpc/Script.SetConfig
Content-Type: application/json

{
  "id": 1,
  "config": {
    "enable": true
  }
}
```

### 8. Start/stop a script
```
POST {device_url}/rpc/Script.Start
Content-Type: application/json

{
  "id": 1
}
```

```
POST {device_url}/rpc/Script.Stop
Content-Type: application/json

{
  "id": 1
}
```

### 9. Get script status
```
GET {device_url}/rpc/Script.GetStatus?id={script_id}
```

Response:
```json
{
  "running": true,
  "mem_used": 1024,
  "mem_peak": 2048,
  "mem_free": 30720,
  "errors": []
}
```

### 10. Get device configuration
```
GET {device_url}/rpc/Shelly.GetConfig
```

### 11. Set device configuration
```
POST {device_url}/rpc/Shelly.SetConfig
Content-Type: application/json

{ /* full or partial config */ }
```

## Limits

- **Maximum number of scripts**: 10 per device
- **Maximum script size**: 16 KB
- **Maximum memory usage**: ~30 KB per script

## Usage examples

### Python
```python
import requests

device_url = "http://192.168.1.100"

# Get script list
response = requests.get(f"{device_url}/rpc/Script.List")
scripts = response.json()["scripts"]

# Save script code
for script in scripts:
    response = requests.get(
        f"{device_url}/rpc/Script.GetCode",
        params={"id": script["id"]}
    )
    code = response.json()["data"]

    with open(f"script_{script['id']}.js", "w") as f:
        f.write(code)

# Upload script code
with open("script_1.js", "r") as f:
    code = f.read()

requests.post(
    f"{device_url}/rpc/Script.PutCode",
    json={"id": 1, "code": code}
)

# Get configuration
config = requests.get(f"{device_url}/rpc/Shelly.GetConfig").json()

# Set configuration
requests.post(f"{device_url}/rpc/Shelly.SetConfig", json=config)
```

### cURL
```bash
# Get script list
curl http://192.168.1.100/rpc/Script.List

# Get script code
curl "http://192.168.1.100/rpc/Script.GetCode?id=1"

# Upload script code
curl -X POST http://192.168.1.100/rpc/Script.PutCode \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "code": "let x = 1;"}'

# Get configuration
curl http://192.168.1.100/rpc/Shelly.GetConfig
```

## Authentication

If authentication is enabled on the device:

```python
import requests
from requests.auth import HTTPDigestAuth

auth = HTTPDigestAuth('admin', 'password')
response = requests.get(
    f"{device_url}/rpc/Script.List",
    auth=auth
)
```

## Error handling

Possible error codes:

- **-103**: Invalid argument
- **-104**: Timeout
- **-105**: Out of memory
- **-114**: Resource exhausted (too many scripts)
- **-115**: Not allowed
- **401**: Unauthorized (authentication required)

Example error response:
```json
{
  "code": -103,
  "message": "Invalid argument"
}
```

## WebSocket API (advanced)

Shelly Gen2+ also supports WebSocket for real-time events:

```javascript
const ws = new WebSocket('ws://192.168.1.100/rpc');

ws.onmessage = (event) => {
  console.log('Message:', JSON.parse(event.data));
};

// Subscribe to script events
ws.send(JSON.stringify({
  "id": 1,
  "method": "Script.GetStatus",
  "params": {"id": 1}
}));
```

## Useful links

- [Official Shelly API documentation](https://shelly-api-docs.shelly.cloud/)
- [Shelly script examples](https://github.com/ALLTERCO/shelly-script-examples)
- [Shelly community forum](https://community.shelly.cloud/)
