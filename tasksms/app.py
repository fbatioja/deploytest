from flask import Flask
import pika
import uuid

app = Flask(__name__)

@app.route('/tasks', methods = ['GET'])
def add():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    
    channel.queue_declare(queue='task_queue', durable=True)
    uuidOne = uuid.uuid1()
    mensaje = str(uuidOne)
    
    channel.basic_publish(
        exchange = '',
        routing_key = 'task_queue',
        body = mensaje,
        properties = pika.BasicProperties(
            delivery_mode = 2,  # make message persistent
        ))
    connection.close()
    return " [x] Sent: " + mensaje

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')