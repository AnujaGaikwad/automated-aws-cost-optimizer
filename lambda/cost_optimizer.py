import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):

    action = event.get("action")

    if not action:
        print("No action provided.")

        return {
            "statusCode": 400,
            "message": "Action is required. Use 'start' or 'stop'."
        }

    action = action.lower()

    print(f"Cost Optimizer action: {action}")

    if action == "start":
        state = "stopped"

    elif action == "stop":
        state = "running"

    else:
        print(f"Invalid action: {action}")

        return {
            "statusCode": 400,
            "message": "Invalid action. Use 'start' or 'stop'."
        }

    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "instance-state-name",
                "Values": [state]
            },
            {
                "Name": "tag:Environment",
                "Values": ["Dev"]
            },
            {
                "Name": "tag:AutoStop",
                "Values": ["true"]
            }
        ]
    )

    affected_instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]

            print(f"Eligible instance found: {instance_id}")

            if action == "start":
                ec2.start_instances(
                    InstanceIds=[instance_id]
                )
            else:
                ec2.stop_instances(
                    InstanceIds=[instance_id]
                )

            affected_instances.append(instance_id)

            print(f"{action.upper()} action performed: {instance_id}")

    print(
        f"Total instances affected: {len(affected_instances)}"
    )

    return {
        "statusCode": 200,
        "action": action,
        "affected_instances": affected_instances,
        "count": len(affected_instances)
    }