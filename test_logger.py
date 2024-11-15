import unittest
from logger import Logger
from log_config import log_storage_config
from datetime import datetime
import json
import os
import io
import sys
import contextlib


class TestLogger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up any necessary files or configurations for testing."""
        cls.logger = Logger()
        # Monkey-patch log_action_async to call log_action directly
        cls.logger.log_action_async = cls.logger.log_action

    def setUp(self):
        """Set up before each test."""
        self.developer_id = "dev_001"
        self.action = "Method call"
        self.model = "UserModel"
        self.method = "update_user"
        self.result = "success"
        self.error = None

        # Clear JSON log file if it's being used for testing
        if log_storage_config["storage_type"] == "json_file":
            with open(log_storage_config["filename"], "w") as file:
                json.dump([], file)

    def test_authorized_developer_logging(self):
        """Test that an authorized developer's log is saved correctly."""
        self.logger.log_action(
            developer_id=self.developer_id,
            action=self.action,
            model=self.model,
            method=self.method,
            result=self.result,
            error=self.error
        )

        if log_storage_config["storage_type"] == "json_file":
            with open(log_storage_config["filename"], "r") as file:
                logs = json.load(file)
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[-1]["developer_id"], self.developer_id)
        elif log_storage_config["storage_type"] == "elasticsearch":
            logs = self.logger.read_logs()
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[-1]["developer_id"], self.developer_id)

    def test_unauthorized_developer_logging(self):
        """Test that an unauthorized developer's log is not saved."""
        unauthorized_developer_id = "unauthorized_dev"

        # Capture stdout to suppress print statements
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            # Attempt to log an action with an unauthorized developer ID
            self.logger.log_action(
                developer_id=unauthorized_developer_id,
                action=self.action,
                model=self.model,
                method=self.method,
                result=self.result,
                error=self.error
            )
        # stdout is restored here

        # Read the logs
        logs = self.logger.read_logs()

        # Assert that no logs have the unauthorized developer ID
        unauthorized_logs = [log for log in logs if log["developer_id"] == unauthorized_developer_id]
        self.assertEqual(len(unauthorized_logs), 0, "Unauthorized developer's log should not be saved.")

    def test_log_error_handling(self):
        """Test logging of an action with an error."""
        try:
            1 / 0  # Intentional error
        except Exception as e:
            error_details = self.logger.format_error(e)  # Format the error
            self.logger.log_method_call(
                developer_id=self.developer_id,
                model=self.model,
                method=self.method,
                result="failure",
                error=error_details,
                async_logging=False  # Ensure synchronous logging
            )

        logs = self.logger.read_logs()
        self.assertGreater(len(logs), 0)
        self.assertIn("error", logs[-1])
        self.assertIn("traceback", logs[-1]["error"])

    def test_filter_logs_by_action(self):
        """Test filtering logs by action type."""
        self.logger.log_action(
            developer_id=self.developer_id,
            action="Database transaction",
            model=self.model,
            method=self.method,
            result=self.result,
            error=self.error
        )
        filtered_logs = self.logger.filter_logs_by_action("Database transaction")
        self.assertGreater(len(filtered_logs), 0)
        self.assertTrue(all(log["action"] == "Database transaction" for log in filtered_logs))

    def test_filter_logs_by_model(self):
        """Test filtering logs by model name."""
        self.logger.log_action(
            developer_id=self.developer_id,
            action=self.action,
            model="TestModel",
            method=self.method,
            result=self.result,
            error=self.error
        )
        filtered_logs = self.logger.filter_logs_by_model("TestModel")
        self.assertGreater(len(filtered_logs), 0)
        self.assertTrue(all(log["model"] == "TestModel" for log in filtered_logs))

    def test_filter_logs_by_developer(self):
        """Test filtering logs by developer ID."""
        self.logger.log_action(
            developer_id="dev_002",
            action=self.action,
            model=self.model,
            method=self.method,
            result=self.result,
            error=self.error
        )
        filtered_logs = self.logger.filter_logs_by_developer("dev_002")
        self.assertGreater(len(filtered_logs), 0)
        self.assertTrue(all(log["developer_id"] == "dev_002" for log in filtered_logs))

    def tearDown(self):
        """Clean up any resources after each test."""
        if log_storage_config["storage_type"] == "json_file" and os.path.exists(log_storage_config["filename"]):
            os.remove(log_storage_config["filename"])


if __name__ == "__main__":
    unittest.main()
