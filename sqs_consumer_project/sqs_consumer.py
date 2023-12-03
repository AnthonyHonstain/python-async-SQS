import boto3


def consume_sqs_messages(sqs_queue_url):
    # Create SQS client
    sqs = boto3.client(
        'sqs',
        endpoint_url='http://localhost:4566',
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

    # Receive messages from SQS queue
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=10,  # Adjust as needed
        WaitTimeSeconds=10,  # Adjust as needed
    )

    # Process messages
    if 'Messages' in response:
        for message in response['Messages']:
            print(f"Received message: {message['Body']}")
            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=sqs_queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
    else:
        print("No messages to process.")


# Example usage
if __name__ == "__main__":
    queue_url = "/000000000000/my-queue2"
    consume_sqs_messages(queue_url)
