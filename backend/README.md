# Dynamic MST Backend

FastAPI backend for dynamic MST updates powered by a Link-Cut Tree (LCT), plus a Kruskal baseline for timing comparison.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

- `GET /health`
- `POST /graph/mutate`

Example payload:

```json
{
  "operation": "insert_edge",
  "u": 1,
  "v": 2,
  "w": 7
}
```
