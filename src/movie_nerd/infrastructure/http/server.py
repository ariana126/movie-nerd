from fastapi import FastAPI, Response
from pydm import ServiceContainer

from movie_nerd.infrastructure.bootstrap.app import App

App.boot()
service_container = ServiceContainer.get_instance()

app = FastAPI()

@app.get('/health')
def start_chat():
    return Response(status_code=204)
