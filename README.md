# Overview
This is a toy SQS consumer written in python, its purpose it to help explore different async options and try different 
concurrency scenarios (messages with fast vs slow processing times).

Started with a non-async consumer and then grew it into an async example.

Using localstack SQS for the queue and wiremock for the consumer to execute an HTTP call against.

The tests are very basic.

# Important Commands

Docker compose should be able to standup wiremock and localstack with the initial required configuration.
* Wiremock - with a basic (and delayed) response
* localstack - with the queue setup you need for testing (which is done via the `init-localstack.sh` script that runs as part of docker compose).

## Manual commands
```
# Create a queue
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name my-queue2 --region us-east-1

# List the queues
aws --endpoint-url=http://localhost:4566 sqs list-queues

# Run the service
poetry run python sqs_consumer_project/sqs_consumer.py

# Send a message
aws --endpoint-url=http://localhost:4566 sqs send-message --queue-url http://localhost:4566/000000000000/my-queue2 --message-body '{"name": "Anthony", "age":2, "ignored":"new-fields"}'

# Get queue attributes
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/my-queue2 --attribute-names All

# Purge Queue
aws --endpoint-url=http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/test-my-queue2
```

# Guide if you wanted to use Mamba
These are the exact steps I used on a Ubuntu 23.10 install.

```
mamba create -n python-async -c conda-forge  python=3.12

mamba activate python-async

pip install poetry

poetry env info         

poetry install

poetry config --list
```