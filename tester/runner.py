import statistics
from datetime import datetime, timezone, timedelta
from .client import APIClient
from .tests import create_tests, run_test

PARIS_TZ = timezone(timedelta(hours=1))

def run_all_tests(base_url="https://api.frankfurter.app"):
    client = APIClient(base_url, timeout=3.0, max_retries=1)
    tests = create_tests(client)
    
    results = []
    latencies = []
    passed = 0
    failed = 0
    errors = 0
    
    for test in tests:
        result = run_test(test)
        results.append(result)
        
        if result['latency_ms'] > 0:
            latencies.append(result['latency_ms'])
        
        if result['status'] == 'PASS':
            passed += 1
        elif result['status'] == 'FAIL':
            failed += 1
        else:
            errors += 1
    
    total = len(results)
    
    latency_avg = round(statistics.mean(latencies), 2) if latencies else 0
    latency_p95 = round(sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) >= 2 else (latencies[0] if latencies else 0), 2)
    error_rate = round((failed + errors) / total, 3) if total > 0 else 0
    availability = round(passed / total * 100, 1) if total > 0 else 0
    
    return {
        "api": "Frankfurter",
        "base_url": base_url,
        "timestamp": datetime.now(PARIS_TZ).isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "error_rate": error_rate,
            "availability_pct": availability,
            "latency_ms_avg": latency_avg,
            "latency_ms_p95": latency_p95
        },
        "tests": results
    }