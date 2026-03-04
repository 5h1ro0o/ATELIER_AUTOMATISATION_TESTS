import requests
import time

class APIClient:
    def __init__(self, base_url, timeout=3.0, max_retries=1):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
    
    def get(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)
        
        last_error = None
        latency_ms = 0
        
        for attempt in range(self.max_retries + 1):
            start_time = time.time()
            try:
                response = requests.get(url, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 2))
                    if attempt < self.max_retries:
                        time.sleep(min(retry_after, 5))
                        continue
                    return response, latency_ms, "Rate limited (429)"
                
                return response, latency_ms, None
                
            except requests.Timeout:
                latency_ms = (time.time() - start_time) * 1000
                last_error = f"Timeout après {self.timeout}s"
                if attempt < self.max_retries:
                    time.sleep(1)
                    continue
                    
            except requests.RequestException as e:
                latency_ms = (time.time() - start_time) * 1000
                last_error = str(e)
                if attempt < self.max_retries:
                    time.sleep(1)
                    continue
        
        return None, latency_ms, last_error