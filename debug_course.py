from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
import uuid

def _random_email(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"

user_data = {"name":"Admin","email":_random_email('admin'),"password":"adminpass","role":"admin"}
reg = client.post('/users/register', json=user_data)
print('register', reg.status_code, reg.text)
login = client.post('/users/login', data={'username':user_data['email'],'password':user_data['password']})
print('login', login.status_code, login.text)
token = login.json().get('access_token')
headers={'Authorization':f'Bearer {token}'}
course_data={'title':'Intro','code':'PY101','capacity':30}
resp = client.post('/courses/', json=course_data, headers=headers)
print('create course', resp.status_code, resp.text)
