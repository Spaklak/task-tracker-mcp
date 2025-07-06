import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=5252,
        reload=True,
        log_level="info"
    )
