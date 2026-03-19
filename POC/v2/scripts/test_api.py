import httpx


def run_health_check(base_url: str = "http://localhost:8000") -> None:
    response = httpx.get(f"{base_url}/health", timeout=10.0)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    run_health_check()
