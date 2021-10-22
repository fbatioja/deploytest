import time
from celery import Celery
from celery.utils.log import get_task_logger
import requests

logger = get_task_logger(__name__)

app = Celery('tasks',
             broker='amqp://admin:mypass@rabbitmq:5672',
             backend='rpc://')


@app.task()
def convert_task(x):
    logger.info('Got Request - Starting work ')
    time.sleep(4)
    logger.info('Work Finished ')
    requests.post('http://gestor-tareas:5000/updateTask',json={'nombre': "prueba"})
    return x
