# Configuration for log storage (using JSON file for simplicity)
log_storage_config = {
    "storage_type": "elasticsearch",  # Options: 'json_file' or 'elasticsearch'
    "filename": "logs.json",  # File to store logs if using 'json_file'
    "elasticsearch": {
        "host": "http://localhost:9200",  # Elasticsearch server URL
        "index": "developer_logs"  # Elasticsearch index name
    }
}


# Function to create a log entry
def create_log(developer_id, action, model, method, result, error=None):
    log_entry = {
        "developer_id": developer_id,
        "action": action,
        "model": model,
        "method": method,
        "result": result,
        "error": error
    }
    return log_entry
