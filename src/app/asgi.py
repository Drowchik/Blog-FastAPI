from src.app.main import get_app
from src.app.services.elasticsearch import es

app = get_app()

@app.on_event("startup")
async def startup_event():
    try:
        await es.create_index()
    except Exception as e:
        print(f"Ошибка при создании индекса: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await es.close()