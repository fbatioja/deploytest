import time
from celery import Celery
from celery.utils.log import get_task_logger
import requests
from pydub import AudioSegment
import ffmpeg

logger = get_task_logger(__name__)

app = Celery('tasks',
             broker='amqp://admin:mypass@rabbitmq:5672',
             backend='rpc://')


@app.task()
def convert_task(filename, newFormat, userId):
    logger.info(f'Got Request - Starting work {filename}, {newFormat}')
    convert_validation(filename, newFormat, userId)
    logger.info('Work Finished ')

    #requests.post('http://gestor-tareas:5000/updateTask',json={'nombre': "prueba"})
    return "ok"

def convert_validation(filename, newFormat, userId):
    filenameSplit = filename.split(".")
    extencion = filenameSplit[len(filenameSplit) - 1]
    if extencion in ['mp3', 'aac', 'wac', 'wma', 'ogg']:
        audio_convert(filename, newFormat, userId)
    else: 
        logger.info(f'El archivo con extención {extencion} no es soportado')

def audio_convert(filename, newFormat, userId):

    source_path = f"./Files/{userId}/{filename}"
    destination_path = f"./Files/{userId}/"+filename[:-3]+newFormat
    AudioSegment.from_file(source_path).export(destination_path, format=newFormat)
    return True