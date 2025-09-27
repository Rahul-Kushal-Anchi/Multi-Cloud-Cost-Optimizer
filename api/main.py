from fastapi import FastAPI

app = FastAPI(title="Multi-Cloud Cost Optimizer API")

@app.get("/healthz")
def healthz():
    return {"ok": True}
