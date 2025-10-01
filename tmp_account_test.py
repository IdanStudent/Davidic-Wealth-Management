import requests, datetime
base='http://localhost:8000'
email='balancetest@example.com'
pw='Secret123!'
# register
r=requests.post(base+'/api/auth/register', json={'email':email,'password':pw,'full_name':'Balance Test'})
print('register',r.status_code)
# login
r=requests.post(base+'/api/auth/login', data={'username':email,'password':pw})
print('login',r.status_code, r.text[:200])
if r.status_code!=200:
    raise SystemExit('login failed')
token=r.json().get('access_token')
headers={'Authorization':f'Bearer {token}'}
# create account with opening balance
r=requests.post(base+'/api/accounts/', json={'name':'StartAcc','type':'Cash','opening_balance':100.0,'is_liability':False}, headers=headers)
print('create account', r.status_code, r.text[:300])
# list accounts
r=requests.get(base+'/api/accounts/', headers=headers)
print('list', r.status_code, r.text[:400])
# create another account without opening balance
r=requests.post(base+'/api/accounts/', json={'name':'NoOpen','type':'Cash','opening_balance':0.0,'is_liability':False}, headers=headers)
print('create noopen', r.status_code)
r=requests.get(base+'/api/accounts/', headers=headers)
print('list after', r.status_code, r.text[:400])
