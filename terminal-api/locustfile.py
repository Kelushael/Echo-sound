from locust import HttpUser, task, between
import random

commands = [
    "ls -la",
    "docker ps -a",
    "git status",
    "df -h",
    "free -m",
    "ps aux | grep python"
]

class TerminalUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def execute_command(self):
        command = random.choice(commands)
        self.client.post(
            "/execute",
            json={
                "command": command,
                "timeout": 10
            },
            headers={"X-API-Key": "test_key"}
        )

    @task(3)
    def health_check(self):
        self.client.get("/health")
