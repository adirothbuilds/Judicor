from fastapi import FastAPI

app = FastAPI(title="Judicor Control Plane")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Judicor control plane placeholder"}
