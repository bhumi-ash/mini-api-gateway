from locust import HttpUser, task, between


class GatewayUser(HttpUser):
    wait_time = between(0.1, 0.5)
    token = None

    def on_start(self):
        response = self.client.post(
            "/login?username=asha&password=pass123"
        )
        self.token = response.json().get("access_token")

    @task
    def get_orders(self):
        self.client.get(
            "/api/orders",
            headers={
                "Authorization": f"Bearer {self.token}"
            },
        )