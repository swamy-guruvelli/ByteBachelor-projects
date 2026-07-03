from locust import HttpUser, between, task


class TaskApiReader(HttpUser):
    wait_time = between(0.05, 0.2)

    @task(4)
    def first_cursor_page(self):
        self.client.get("/api/v1/tasks?limit=50", name="/api/v1/tasks cursor")

    @task
    def deep_offset_page(self):
        self.client.get("/api/v1/tasks?limit=50&offset=10000", name="/api/v1/tasks offset")

    @task
    def readiness(self):
        self.client.get("/health/ready")

