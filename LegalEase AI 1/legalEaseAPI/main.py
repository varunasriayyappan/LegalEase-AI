from fastapi import FastAPI

from legalEaseAPI.routes import router

app = FastAPI(title="LegalEase - AI Legal Document Generator")
app.include_router(router)


@app.get("/")
def home():
    return {"message": "Welcome to LegalEase AI Legal Document Generator API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)