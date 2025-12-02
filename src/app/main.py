from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "PR Review Assistant API is running 🚀"}
