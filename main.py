import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routes import user_route, article_route, auth_route

app = FastAPI(description="",
              version="0.1")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


app.include_router(user_route, prefix="/account", tags=["users"])
app.include_router(auth_route, prefix="/auth", tags=["auth"])
app.include_router(article_route, prefix="/article", tags=["article"])

if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", reload=True)
