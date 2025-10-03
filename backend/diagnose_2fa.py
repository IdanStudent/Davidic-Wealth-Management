import time, requests, pyotp, random

base='http://127.0.0.1:8000'
s=requests.Session()
email=f'diag+{int(time.time())}{random.randint(1000,9999)}@example.com'
password='Passw0rd!123'

print('Base:', base)
# Register
r=s.post(base+'/api/auth/register', json={'email':email,'password':password,'full_name':'Diag'})
print('register', r.status_code, r.text[:120])
# Login
r=s.post(base+'/api/auth/login', json={'email':email,'password':password})
print('login', r.status_code, r.text[:120])
if r.status_code!=200:
    raise SystemExit('Login failed')

# Enable 2FA step1
r=s.post(base+'/api/utils/2fa', json={'enable': True})
print('enable-step1', r.status_code)
print('resp:', r.text[:200])
js=r.json()
secret=js.get('secret')
if not secret:
    raise SystemExit('No secret returned')

# Compute OTP and confirm
otp=pyotp.TOTP(secret).now()
print('computed otp', otp)
r=s.post(base+'/api/utils/2fa', json={'enable': True, 'code': otp})
print('enable-step2', r.status_code, r.text)

# Verify status
r=s.get(base+'/api/utils/2fa')
print('status', r.status_code, r.text)

# Test login with otp enforcement
# First logout: use a bad token header to simulate missing auth
s.headers.pop('Authorization', None)
# Attempt login without OTP -> should return 401 with detail '2FA required'
r=s.post(base+'/api/auth/login', json={'email':email,'password':password})
print('login-no-otp', r.status_code, r.text)
# Try with OTP
now=pyotp.TOTP(secret).now()
r=s.post(base+'/api/auth/login', json={'email':email,'password':password,'otp':now})
print('login-with-otp', r.status_code, r.text[:200])
