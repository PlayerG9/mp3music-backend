# websocket communication protocol
```json
{
  "info": "message",
  "warning": "message",
  "error": "description",
  "error_class": "class",
  "json": {
    "uid": "hex",
    "filename": "string"
  }
}
```
- info
  - a message that can be displayed to the user
- warning
  - a message that can be displayed to the user
- error
  - error description
- error_class
  - always together with error
- json
  - uid
    - uid for the `/api/mp3file/{uid}` endpoint
  - filename
    - recommended filename (for `/api/mp3file/{uid}`)
