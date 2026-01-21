from fastapi import FastAPI

app = FastAPI(title="Ticketing Service")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
