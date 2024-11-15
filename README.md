# Logging System Project

This project provides a robust **logging system** designed for tracking developer interactions with the system, such as method calls, database transactions, and model interactions. The logger supports multiple storage backends, including:

1. **JSON file** storage.
2. **Elasticsearch** for advanced logging and search capabilities.

The system includes features like:
- **Access control** for authorized developers.
- **Asynchronous logging** for improved performance.
- **Error handling** with detailed tracebacks.
- **Filtering logs** by action, model, or developer.

## Features
- **Storage Options**: Log entries can be saved in a JSON file or an Elasticsearch index.
- **Error Handling**: Automatically logs and formats exceptions.
- **Asynchronous Logging**: Non-blocking logging for better performance.
- **Access Control**: Restricts logging to authorized developers.
- **Log Filtering**: Retrieve logs based on specific criteria such as action type, model, or developer.

## Project Structure
- `logger.py`: Implements the main logging functionality.
- `log_config.py`: Contains the configuration for the logging system, including storage type and Elasticsearch details.
- `test_logger.py`: Unit tests for the logging system to ensure proper functionality.

## Requirements
- Python 3.8+
- For Elasticsearch support:
  - Elasticsearch server running locally or remotely.
  - Python Elasticsearch client (`elasticsearch` library).

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Pooria82/Logging-System-Project.git
   cd Logging-System-Project
   ```

2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. If using Elasticsearch, ensure the Elasticsearch service is running and accessible.

## Configuration
The logging configuration is defined in `log_config.py`. Modify it to suit your requirements:
- Use JSON file storage:
  ```python
  log_storage_config = {
      "storage_type": "json_file",
      "filename": "logs.json"
  }
  ```

- Use Elasticsearch:
  ```python
  log_storage_config = {
      "storage_type": "elasticsearch",
      "elasticsearch": {
          "host": "http://localhost:9200",
          "index": "developer_logs"
      }
  }
  ```

## Usage
### Example Logging
Here's a sample usage of the logger:
```python
from logger import Logger

# Initialize the logger
logger = Logger()

# Log a successful method call
logger.log_method_call(
    developer_id="dev_001",
    model="UserModel",
    method="update_user",
    result="success"
)

# Log a failed method call with an error
try:
    result = 1 / 0  # Intentional error
except Exception as e:
    logger.log_method_call(
        developer_id="dev_001",
        model="OrderModel",
        method="calculate_discount",
        result="failure",
        error=e
    )
```

### Run Tests
To verify the functionality, execute the test suite:
```bash
python -m unittest test_logger.py
```

## Troubleshooting
- If using Elasticsearch and encountering an `ImportError`:
  Install the Elasticsearch library:
  ```bash
  pip install elasticsearch
  ```

- Ensure the Elasticsearch server is running and reachable at the configured host.

## Contribution
Feel free to submit issues or pull requests to contribute to this project. Follow standard best practices for code quality and testing.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
