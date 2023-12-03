# Overview
This is a toy SQS consumer written in python, its purpose it to help explore different async options and try different 
concurrency scenarios (messages with fast vs slow processing times).

Started with a non-async consumer and then grew it into an async example.

Using localstack SQS for the queue.

There are no tests yet.

# Important Commands
```
# Create a queue
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name my-queue2 --region us-east-1

# List the queues
aws --endpoint-url=http://localhost:4566 sqs list-queues

# Run the service
poetry run python sqs_consumer_project/sqs_consumer.py

# Send a message
aws --endpoint-url=http://localhost:4566 sqs send-message --queue-url http://localhost:4566/000000000000/my-queue2 --message-body "Hello, World"

# Get queue attributes
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/my-queue2 --attribute-names All
```