import json
import os
import threading
from datetime import datetime
from time import perf_counter
import traceback
from log_config import create_log, log_storage_config

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None


class Logger:
    """
    A logger class for tracking developer interactions with the system, including method calls,
    database transactions, and model interactions. This class also supports asynchronous
    logging, access control for authorized developers, and detailed error handling.
    """

    authorized_developers = {"dev_001", "dev_002"}  # Replace with actual authorized developer IDs

    def __init__(self):
        self.storage_type = log_storage_config["storage_type"]
        self.filename = log_storage_config["filename"]

        # Initialize Elasticsearch client if storage type is Elasticsearch
        if self.storage_type == "elasticsearch" and Elasticsearch:
            es_config = log_storage_config["elasticsearch"]
            self.es_client = Elasticsearch([es_config["host"]])
            self.index = es_config["index"]
        elif self.storage_type == "elasticsearch" and not Elasticsearch:
            raise ImportError("Elasticsearch library is not installed.")

    def is_authorized(self, developer_id):
        """Check if the developer is authorized to log actions."""
        return developer_id in self.authorized_developers

    def log_action(self, developer_id, action, model, method, result, error=None):
        if not self.is_authorized(developer_id):
            print(f"Developer {developer_id} is not authorized to log actions.")
            return

        start_time = datetime.now()
        start_perf = perf_counter()

        if isinstance(error, Exception):
            error = self.format_error(error)

        log_entry = create_log(developer_id, action, model, method, result, error)
        end_perf = perf_counter()
        elapsed_time = end_perf - start_perf

        log_entry["start_time"] = start_time.isoformat()
        log_entry["duration"] = elapsed_time

        if self.storage_type == "json_file":
            self._save_to_json_file(log_entry)
        elif self.storage_type == "elasticsearch":
            self._save_to_elasticsearch(log_entry)
        else:
            print("Storage type not implemented")

    def log_action_async(self, developer_id, action, model, method, result, error=None):
        thread = threading.Thread(target=self.log_action, args=(developer_id, action, model, method, result, error))
        thread.start()

    def _save_to_json_file(self, log_entry):
        try:
            with open(self.filename, "r+") as file:
                logs = json.load(file)
                logs.append(log_entry)
                file.seek(0)
                json.dump(logs, file, indent=4)
            print("Log saved to JSON file.")
        except Exception as e:
            print(f"Error saving log: {e}")

    def _save_to_elasticsearch(self, log_entry):
        try:
            if Elasticsearch:
                self.es_client.index(index=self.index, document=log_entry)
                print("Log saved to Elasticsearch.")
            else:
                print("Elasticsearch client not available.")
        except Exception as e:
            print(f"Error saving log to Elasticsearch: {e}")

    def read_logs(self):
        if self.storage_type == "json_file":
            logs = []
            try:
                with open(self.filename, "r") as file:
                    logs = json.load(file)
                print("Logs read successfully.")
            except FileNotFoundError:
                print("Log file not found.")
            except Exception as e:
                print(f"Error reading log file: {e}")
            return logs
        elif self.storage_type == "elasticsearch":
            try:
                response = self.es_client.search(index=self.index, body={"query": {"match_all": {}}})
                return [hit["_source"] for hit in response["hits"]["hits"]]
            except Exception as e:
                print(f"Error reading logs from Elasticsearch: {e}")
                return []

    def format_error(self, exception):
        return {
            "type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exc()
        }

    def log_method_call(self, developer_id, model, method, result, error=None, async_logging=True):
        try:
            if async_logging:
                self.log_action_async(developer_id, "Method call", model, method, result, error)
            else:
                self.log_action(developer_id, "Method call", model, method, result, error)
        except Exception as e:
            error_details = self.format_error(e)
            if async_logging:
                self.log_action_async(developer_id, "Method call", model, method, "error", error=error_details)
            else:
                self.log_action(developer_id, "Method call", model, method, "error", error=error_details)

    def log_database_transaction(self, developer_id, model, method, result, error=None):
        try:
            self.log_action_async(developer_id, "Database transaction", model, method, result, error)
        except Exception as e:
            error_details = self.format_error(e)
            self.log_action_async(developer_id, "Database transaction", model, method, "error", error=error_details)

    def log_model_interaction(self, developer_id, model, method, result, error=None):
        try:
            self.log_action_async(developer_id, "Model interaction", model, method, result, error)
        except Exception as e:
            error_details = self.format_error(e)
            self.log_action_async(developer_id, "Model interaction", model, method, "error", error=error_details)

    def filter_logs_by_action(self, action_type):
        return [log for log in self.read_logs() if log["action"] == action_type]

    def filter_logs_by_model(self, model_name):
        return [log for log in self.read_logs() if log["model"] == model_name]

    def filter_logs_by_developer(self, developer_id):
        return [log for log in self.read_logs() if log["developer_id"] == developer_id]
