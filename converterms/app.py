import pika
import time
from datetime import datetime

sleepTime = 10
print(' [*] Sleeping for ', sleepTime, ' seconds.')
time.sleep(30)

print(' [*] Connecting to server ...')
queue_name = 'task_queue'
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue=queue_name, durable=True)

print(' [*] Waiting for messages.')

def callback(ch, method, properties, body):
    identifier = body.decode()

    f = open('log'+queue_name+'.txt', "a")
    f.write("{0} -- {1}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M"), identifier))
    f.close()

    print(" [x] Ok")

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=callback)
channel.start_consuming()