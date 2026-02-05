from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
import uuid, json

def _random_email(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"

user_data = {"name":"Admin","email":_random_email('admin'),"password":"adminpass","role":"admin"}
reg = client.post('/users/register', json=user_data)
print('register status:', reg.status_code)
print('register body:', reg.json() if reg.text else reg.text)
login = client.post('/users/login', data={'username':user_data['email'],'password':user_data['password']})
print('login status:', login.status_code)
print('login body:', login.json() if login.text else login.text)
if login.status_code==200:
    token = login.json().get('access_token')
else:
    token=None
print('token:', token)
headers={'Authorization':f'Bearer {token}'}
course_data={'title':'Intro','code':'PY101','capacity':30}
resp = client.post('/courses/', json=course_data, headers=headers)
print('create course status:', resp.status_code)
try:
    print('create course body:', resp.json())
except Exception as e:
    print('create course text:', resp.text)
