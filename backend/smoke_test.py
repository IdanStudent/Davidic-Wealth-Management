import os
import sys
import time
import base64
import random
import string
import requests
import subprocess
import socket


S = requests.Session()


def rnd_email():
    # Use a valid reserved domain for examples
    return f"smoke+{int(time.time())}{random.randint(1000,9999)}@example.com"


def ensure_ok(resp: requests.Response):
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print('Request failed:', resp.status_code, resp.text)
        raise


def main():
    # Always start a fresh backend on a free port so we test the latest code
    root = os.path.dirname(os.path.dirname(__file__))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        _, port = s.getsockname()
    base = f"http://127.0.0.1:{port}"
    print('Starting local backend on', base)
    cmd = [sys.executable, '-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '127.0.0.1', '--port', str(port)]
    proc = subprocess.Popen(cmd, cwd=root)
    # wait up to 20s
    for _ in range(40):
        try:
            r = S.get(f"{base}/", timeout=1.5)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.5)
    else:
        print('Backend failed to start at', base)
        try:
            proc.terminate()
        except Exception:
            pass
        sys.exit(1)
    email = rnd_email()
    password = 'Passw0rd!123'

    # Register
    r = S.post(f"{base}/api/auth/register", json={
        'email': email,
        'password': password,
        'full_name': 'Smoke Test'
    })
    ensure_ok(r)

    # Login
    r = S.post(f"{base}/api/auth/login", json={'email': email, 'password': password})
    ensure_ok(r)
    token = r.json().get('access_token')
    if not token:
        print('Missing token in login response:', r.text)
        sys.exit(2)
    print('Token length:', len(token))
    S.headers.update({'Authorization': f'Bearer {token}'})

    # Create account
    r = S.post(f"{base}/api/accounts/", json={
        'name': 'Checking', 'type': 'Cash', 'opening_balance': 1000, 'is_liability': False
    })
    ensure_ok(r)
    acc = r.json()
    acc_id = acc.get('id')
    print('Account ID:', acc_id)

    # Categories and pick an expense
    r = S.get(f"{base}/api/categories/")
    ensure_ok(r)
    cats = r.json()
    exp = next((c for c in cats if c.get('type') == 'expense'), None)
    if not exp:
        print('No expense category found')
        sys.exit(3)
    print('Expense cat:', exp.get('id'))

    # Create transaction
    today = time.strftime('%Y-%m-%d')
    r = S.post(f"{base}/api/transactions/", json={
        'account_id': acc_id,
        'category_id': exp.get('id'),
        'date': today,
        'amount': 25.5,
        'note': 'Smoke expense'
    })
    ensure_ok(r)
    tx = r.json()
    print('Tx ID:', tx.get('id'))

    # Create budget for current month
    month = time.strftime('%Y-%m')
    r = S.post(f"{base}/api/budgets/", json={
        'month': month,
        'items': [ {'category_id': exp.get('id'), 'limit': 500} ]
    })
    ensure_ok(r)
    bud = r.json()
    print('Budget ID:', bud.get('id'))

    # Monthly report
    y = int(time.strftime('%Y'))
    m = int(time.strftime('%m'))
    r = S.get(f"{base}/api/reports/monthly", params={'year': y, 'month': m})
    ensure_ok(r)
    rep = r.json()
    print(f"Report income={rep.get('income')} expenses={rep.get('expenses')} savings={rep.get('savings')}")

    # Export CSV
    r = S.get(f"{base}/api/reports/export/csv", params={'year': y, 'month': m})
    ensure_ok(r)
    content = r.json().get('content', '')
    print('CSV bytes:', len(content))

    # Export PDF
    r = S.get(f"{base}/api/reports/export/pdf", params={'year': y, 'month': m})
    ensure_ok(r)
    b64 = r.json().get('content_b64', '')
    # quick decode check
    try:
        _ = base64.b64decode(b64, validate=True)
    except Exception:
        print('Invalid PDF base64')
        sys.exit(4)
    print('PDF b64 len:', len(b64))

    print('SMOKE TEST: PASS')

    # Cleanup if we started the server
    try:
        proc.terminate()
    except Exception:
        pass


if __name__ == '__main__':
    main()
