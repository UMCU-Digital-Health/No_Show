import uvicorn

from noshow.api.app import app

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8013)