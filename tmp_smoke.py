import requests, datetime
base='http://localhost:8000'
u={'email':'testuser@example.com','password':'Secret123!','full_name':'Test User'}
try:
    r=requests.post(base+'/api/auth/register', json=u)
    print('register', r.status_code, r.text[:200])
except Exception as e:
    print('register err', e)
try:
    r=requests.post(base+'/api/auth/login', data={'username':u['email'],'password':u['password']})
    print('login', r.status_code, r.text[:200])
    token=r.json().get('access_token')
except Exception as e:
    print('login err', e); token=None
headers={'Authorization':f'Bearer {token}'} if token else {}
acc={'name':'Checking','type':'Cash','opening_balance':100.0,'is_liability':False}
try:
    r=requests.post(base+'/api/accounts/', json=acc, headers=headers)
    print('create account', r.status_code, r.text[:300])
except Exception as e:
    print('create account err', e)
cat={'name':'Income','type':'income','icon':'coin'}
try:
    r=requests.post(base+'/api/categories/', json=cat, headers=headers)
    print('create cat', r.status_code, r.text[:200])
    cat_id=r.json().get('id')
except Exception as e:
    print('create cat err', e); cat_id=None
try:
    r=requests.get(base+'/api/accounts/', headers=headers)
    print('list acc', r.status_code, r.text[:300])
    if r.status_code==200 and r.json():
        a=r.json()[0]; acc_id=a['id']
    else:
        acc_id=None
except Exception as e:
    print('list acc err', e); acc_id=None
if acc_id and cat_id:
    tx={'account_id':acc_id,'category_id':cat_id,'date':datetime.date.today().isoformat(),'amount':200.0,'note':'Test Income'}
    try:
        r=requests.post(base+'/api/transactions/', json=tx, headers=headers)
        print('create tx', r.status_code, r.text[:500])
    except Exception as e:
        print('create tx err', e)
else:
    print('missing acc or cat', acc_id, cat_id)
