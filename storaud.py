from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from datetime import datetime, timedelta

# Authenticate using the default credential
credential = DefaultAzureCredential()

# Instantiate a Subscription client
subscription_client = SubscriptionClient(credential)

# List all subscriptions and iterate over them
for subscription in subscription_client.subscriptions.list():
    
    # Instantiate clients for the specific subscription
    storage_client = StorageManagementClient(credential, subscription.subscription_id)
    monitor_client = MonitorManagementClient(credential, subscription.subscription_id)

    # List all storage accounts in the current subscription
    for storage_account in storage_client.storage_accounts.list():
        
        # Fetch metrics for the most recent hour
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)

        metrics_data = monitor_client.metrics.list(
            resource_uri=storage_account.id,
            timespan=f"{start_time}/{end_time}",
            interval='PT1H',  # Represents 1 hour
            metricnames='UsedCapacity',
            aggregation='Total'
        )

        used_capacity = 0.0  # Initialize the used capacity for this storage account
        
        for metric in metrics_data.value:
            for timeseries in metric.timeseries:
                for data in timeseries.data:
                    used_capacity += data.total / (1024 ** 3)  # Convert bytes to GB and accumulate

        # Print the used capacity for this storage account in the desired format
        print(f"{subscription.display_name}_{storage_account.name}_Used Capacity {used_capacity:.2f}GB")
