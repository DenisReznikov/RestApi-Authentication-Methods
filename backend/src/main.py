from fastapi import FastAPI, Depends
# from backend.src.app.basic_auth.basic_auth import *
import uvicorn

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}


@app.get("/secure-endpoint")
def secure_endpoint(username: str = Depends(authenticate)):
    return {"message": f"Hello, {username}. You have accessed a secure endpoint."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
