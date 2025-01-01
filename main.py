import fastapi
import uvicorn
import traceback
import random
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI
from fastapi import status, Depends, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from routes.userRoute import get_admin_user, get_current_user, userR
from routes.productRoute import productR
from routes.vendorRoute import vendorR
from starlette.middleware.cors import CORSMiddleware
# from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.include_router(router=userR)
app.include_router(router=productR)
app.include_router(router=vendorR)
# app.add_middleware(SessionMiddleware, secret_key="akash")
allowed_origins = [
    "http://localhost",
    "http://localhost:5174",
    "http://localhost:5173",
    "http://127.0.0.1",
    "https://localhost",
    "https://127.0.0.1",
    "https://kitchen-murex-nine.vercel.app",
    "http://kitchen-murex-nine.vercel.app"
]
# Add wildcard subdomains for *.angelone.in
# allowed_origins.extend(
# [f"https://{sub}.angelone.in" for sub in ["*", "www", "api"]])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def inde(request: Request, status_code=status.HTTP_200_OK):
    return RedirectResponse('/docs', status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get("/protected-route")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user['sub']}!"}


@app.get("/protected-route-admin")
def protected_route(current_user: dict = Depends(get_admin_user)):
    return {"message": f"Welcome, {current_user['sub']}!"}


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    #     # gunicorn.run("main:app", host="0.0.0.0", port=8087, reload=True)
    #     #     #     # uvicorn main:app --reload --port 8080 --host 0.0.0.0 --ssl-keyfile "/home/akash.kansal/documents/github/dp-core-automation/certkey.pem" --ssl-certfile "/home/akash.kansal/documents/github/dp-core-automation/cert.pem"
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True,
                # ssl_keyfile="./certkey.pem",
                # ssl_certfile="./cert.pem"
                )  # , workers=4)
