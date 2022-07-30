# websocket communication protocol

```json
{
  "youtubeId": "string",
  "metadata": {
    "title": "string",
    "author": "string"
  }
}
```

```json
{
  "info": "message",
  "warning": "message",
  "error": "description",
  "error_class": "class",
  "progress": {
    "has": 0,
    "max": 0
  },
  "final": {
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
- progress
  - has
    - has downloaded
  - max
    - to download
- final
  - uid
    - uid for the `/api/mp3file/{uid}` endpoint
  - filename
    - recommended filename (for `/api/mp3file/{uid}`)
