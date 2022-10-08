import pika

# connect 
credentials = pika.PlainCredentials('{USERNAME}', '{PASSWORD}')
parameters = pika.ConnectionParameters(host='{Address of RabbitMQ server}', credentials=credentials) 
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='{Name of the queue to use}')

# producer
channel.basic_publish(exchange='', routing_key='{Name of the queue to use}', body='{Message to publish}')
# _______________________________________________________________________________________________________

# consumer
def callback(ch, method, properties, body):
    # TODO: Process message here 
    print(" [x] Received %r" % body)
channel.basic_consume(queue='{Name of the queue to use}', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
# _______________________________________________________________________________________________________

connection.close()







