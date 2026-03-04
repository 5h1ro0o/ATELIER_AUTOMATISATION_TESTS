from .client import APIClient

def create_tests(client):
    tests = []
    
    def test_latest_status():
        resp, latency, error = client.get('/latest')
        if error:
            return False, latency, f"Erreur: {error}"
        if resp.status_code != 200:
            return False, latency, f"Status {resp.status_code} au lieu de 200"
        return True, latency, "OK"
    
    tests.append({"name": "GET /latest - Status 200", "category": "Contrat", "func": test_latest_status})
    
    def test_content_type_json():
        resp, latency, error = client.get('/latest')
        if error:
            return False, latency, f"Erreur: {error}"
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            return False, latency, f"Content-Type: {content_type}"
        return True, latency, "application/json"
    
    tests.append({"name": "Content-Type JSON", "category": "Contrat", "func": test_content_type_json})
    
    def test_required_fields():
        resp, latency, error = client.get('/latest')
        if error:
            return False, latency, f"Erreur: {error}"
        try:
            data = resp.json()
            required = ['amount', 'base', 'date', 'rates']
            missing = [f for f in required if f not in data]
            if missing:
                return False, latency, f"Champs manquants: {missing}"
            return True, latency, "Tous les champs présents"
        except Exception as e:
            return False, latency, f"JSON invalide: {e}"
    
    tests.append({"name": "Champs obligatoires présents", "category": "Contrat", "func": test_required_fields})
    
    def test_field_types():
        resp, latency, error = client.get('/latest')
        if error:
            return False, latency, f"Erreur: {error}"
        try:
            data = resp.json()
            errors = []
            if not isinstance(data.get('base'), str):
                errors.append("base n'est pas string")
            if not isinstance(data.get('amount'), (int, float)):
                errors.append("amount n'est pas number")
            if not isinstance(data.get('rates'), dict):
                errors.append("rates n'est pas object")
            if not isinstance(data.get('date'), str):
                errors.append("date n'est pas string")
            if errors:
                return False, latency, "; ".join(errors)
            return True, latency, "Types corrects"
        except Exception as e:
            return False, latency, f"Erreur: {e}"
    
    tests.append({"name": "Types des champs corrects", "category": "Contrat", "func": test_field_types})
    
    def test_from_param():
        resp, latency, error = client.get('/latest?from=EUR')
        if error:
            return False, latency, f"Erreur: {error}"
        try:
            data = resp.json()
            if data.get('base') != 'EUR':
                return False, latency, f"Base={data.get('base')} au lieu de EUR"
            return True, latency, "base=EUR"
        except Exception as e:
            return False, latency, f"Erreur: {e}"
    
    tests.append({"name": "GET /latest?from=EUR", "category": "Contrat", "func": test_from_param})
    
    def test_to_param():
        resp, latency, error = client.get('/latest?from=EUR&to=USD')
        if error:
            return False, latency, f"Erreur: {error}"
        try:
            data = resp.json()
            rates = data.get('rates', {})
            if 'USD' not in rates:
                return False, latency, "USD absent des rates"
            if len(rates) != 1:
                return False, latency, f"{len(rates)} devises au lieu de 1"
            return True, latency, f"USD={rates['USD']}"
        except Exception as e:
            return False, latency, f"Erreur: {e}"
    
    tests.append({"name": "GET /latest?to=USD filtre", "category": "Contrat", "func": test_to_param})
    
    def test_currencies_endpoint():
        resp, latency, error = client.get('/currencies')
        if error:
            return False, latency, f"Erreur: {error}"
        if resp.status_code != 200:
            return False, latency, f"Status {resp.status_code}"
        try:
            data = resp.json()
            if not isinstance(data, dict):
                return False, latency, "Pas un object"
            if len(data) < 10:
                return False, latency, f"Seulement {len(data)} devises"
            return True, latency, f"{len(data)} devises"
        except Exception as e:
            return False, latency, f"Erreur: {e}"
    
    tests.append({"name": "GET /currencies", "category": "Contrat", "func": test_currencies_endpoint})
    
    def test_historical_date():
        resp, latency, error = client.get('/2024-01-15')
        if error:
            return False, latency, f"Erreur: {error}"
        if resp.status_code != 200:
            return False, latency, f"Status {resp.status_code}"
        try:
            data = resp.json()
            if data.get('date') != '2024-01-15':
                return False, latency, f"Date={data.get('date')}"
            return True, latency, "Date historique OK"
        except Exception as e:
            return False, latency, f"Erreur: {e}"
    
    tests.append({"name": "GET /2024-01-15 (historique)", "category": "Contrat", "func": test_historical_date})
    
    def test_invalid_currency():
        resp, latency, error = client.get('/latest?from=INVALID')
        if error:
            return False, latency, f"Erreur réseau: {error}"
        if resp.status_code == 404:
            return True, latency, "404 Not Found (attendu)"
        if resp.status_code == 400:
            return True, latency, "400 Bad Request (attendu)"
        return False, latency, f"Status {resp.status_code} inattendu"
    
    tests.append({"name": "Devise invalide - erreur", "category": "Robustesse", "func": test_invalid_currency})
    
    def test_future_date():
        resp, latency, error = client.get('/2099-12-31')
        if error:
            return False, latency, f"Erreur réseau: {error}"
        if resp.status_code == 200:
            return True, latency, "200 OK (dernier taux)"
        return True, latency, f"Status {resp.status_code}"
    
    tests.append({"name": "Date future gérée", "category": "Robustesse", "func": test_future_date})
    
    return tests

def run_test(test):
    try:
        passed, latency, details = test['func']()
        return {
            "name": test['name'],
            "category": test['category'],
            "status": "PASS" if passed else "FAIL",
            "latency_ms": round(latency, 2),
            "details": details
        }
    except Exception as e:
        return {
            "name": test['name'],
            "category": test['category'],
            "status": "ERROR",
            "latency_ms": 0,
            "details": str(e)
        }