from fastapi import FastAPI

app = FastAPI(title="HelpDesk API")


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/hello/{name}")
def hello(name: str):
    return {"message": f"Hola, {name}"}

