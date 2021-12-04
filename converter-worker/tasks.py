import time
from celery import Celery
from celery.utils.log import get_task_logger
import requests
from pydub import AudioSegment
import os
from .util import FileManager

logger = get_task_logger(__name__)


gestor_tareas_host = os.environ.get("GESTOR_TAREAS_HOST")
queue_url = os.environ.get("QUEUE_URL")
queue_name = os.environ.get("SQS_QUEUE_NAME")
rabbit_user = os.environ.get("RABBITMQ_DEFAULT_USER")
rabbit_password = os.environ.get("RABBITMQ_DEFAULT_PASS")
rabbit_hostname = os.environ.get("RABBITMQ_HOSTNAME")
gestor_tareas_host = os.environ.get("GESTOR_TAREAS_HOST")
log_host = os.environ.get("LOG_HOST")

app = Celery('tasks',
             broker=f"{queue_url}")

fileManager = FileManager.get_instance()


@app.task(name='convert_task')
def convert_task(filename, newFormat, userId, taskId, timecreated):
    timestart = round(time.time())
    diff = timestart - timecreated
    logger.info(f'Solicitud de conversión - {filename} a {newFormat}')
    resp = convert_validation(filename, newFormat, userId)
    timeend = round(time.time())
    requests.post(f"{log_host}/logTransaction", json={"taskId": taskId,"timecreated": timecreated,"timestart": timestart,"diff": diff,"timeend": timeend})
    if resp:
        logger.info(f"Conversión de archvio {filename} a {newFormat}")
        requests.post(f"{gestor_tareas_host}/updateTask",
                      json={"taskId": taskId})


def convert_validation(filename, newFormat, userId):
    filenameSplit = filename.split(".")
    extencion = filenameSplit[len(filenameSplit) - 1]
    if extencion in ['mp3', 'aac', 'wav', 'wma', 'ogg']:
        logger.info(f'pre audio convert')
        return audio_convert(filename, newFormat, userId)
    else:
        logger.info(f'El archivo con extención {extencion} no es soportado')
        return False


def audio_convert(filename, newFormat, userId):
    filenameSplit = filename.split(".")
    extencion = filenameSplit[len(filenameSplit) - 1]
    # f"./Files/{userId}/{filename}"
    source_path = fileManager.get_file(filename, userId)

    target_name = filename[:-3] + newFormat
    destination_path = f"./Files/{userId}/" + target_name
    try:
        if extencion == "mp3":
            AudioSegment.from_mp3(source_path).export(
                destination_path, format=newFormat)
        elif extencion == "ogg":
            logger.info(f'pre audio ogg')
            AudioSegment.from_ogg(source_path).export(
                destination_path, format=newFormat)
        elif extencion == "wav":
            AudioSegment.from_wav(source_path).export(
                destination_path, format=newFormat)
        else:
            AudioSegment.from_file(source_path).export(
                destination_path, format=newFormat)
    except:
        fileManager.clean_local_files(userId)
        return False

    logger.info(f'send file')
    fileManager.send_file(destination_path, target_name, userId)
    return True
