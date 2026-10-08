import random
from locust import HttpUser, task, between


class GatewayUser(HttpUser):
    wait_time = between(0.5, 1)
    token = None

    def on_start(self):
        username = f"user{random.randint(1, 200)}"

        response = self.client.post(
            f"/login?username={username}&password=pass123"
        )

        if response.status_code != 200 or not response.text:
            raise RuntimeError(
                f"Login failed — status={response.status_code}, "
                f"body={response.text!r}. "
                "Check that `docker compose ps` shows the gateway running."
            )

        self.token = response.json().get("access_token")

    @task
    def get_orders(self):
        with self.client.get(
            "/api/orders/",
            headers={
                "Authorization": f"Bearer {self.token}"
            },
            catch_response=True,
        ) as response:

            if response.status_code == 429:
                response.success()

            elif response.status_code != 200:
                response.failure(
                    f"unexpected status {response.status_code}"
                )