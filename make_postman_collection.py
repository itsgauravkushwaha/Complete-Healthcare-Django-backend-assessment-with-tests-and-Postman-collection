"""Build a beginner-friendly Postman v2.1 collection with saved ID/token scripts.
This optional one-time helper uses only Python's standard library.
"""
import json
from pathlib import Path


def item(label, method, path, body=None, save=None, no_auth=False):
    parts = path.lstrip('/').split('/')
    r = {
        'method': method,
        'header': ([{'key': 'Content-Type', 'value': 'application/json'}] if body else []),
        'url': {'raw': '{{base_url}}' + path, 'host': ['{{base_url}}'], 'path': parts},
    }
    if body is not None:
        r['body'] = {'mode':'raw', 'raw':json.dumps(body, indent=2), 'options': {'raw': {'language': 'json'}}}
    if no_auth:
        r['auth'] = {'type': 'noauth'}
    result = {'name': label, 'request': r}
    if save:
        script = [f'pm.collectionVariables.set("{var}", pm.response.json().{field});' for var, field in save.items()]
        result['event'] = [{'listen':'test','script': {'type':'text/javascript', 'exec':script}}]
    return result

collection = {
    'info': {'name': 'Healthcare Django Assignment', '_postman_id': 'healthcare-assessment-demo',
             'description': 'Run requests in order. Collection saves token and entity IDs automatically.',
             'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},
    'auth': {'type':'bearer', 'bearer': [{'key':'token','value':'{{access_token}}','type':'string'}]},
    'variable': [{'key':v,'value':value} for v,value in [
        ('base_url','http://127.0.0.1:8000'),('access_token',''),('refresh_token',''),
        ('patient_id',''),('doctor_id',''),('mapping_id','')]],
    'item': [
        item('01 Register', 'POST', '/api/auth/register/',
             {'name':'Demo User','email':'demo@example.com','password':'StrongPass!2026'}, no_auth=True),
        item('02 Login (saves JWT)', 'POST','/api/auth/login/',
             {'email':'demo@example.com','password':'StrongPass!2026'},
             {'access_token':'access','refresh_token':'refresh'}, no_auth=True),
        item('03 Create patient (saves ID)','POST','/api/patients/',
             {'name':'Demo Patient','age':30,'gender':'female','phone':'+919876543210'}, {'patient_id':'id'}),
        item('04 Get my patients','GET','/api/patients/'),
        item('05 Get one patient','GET','/api/patients/{{patient_id}}/'),
        item('06 Update patient','PUT','/api/patients/{{patient_id}}/',
             {'name':'Demo Patient Updated','age':31,'gender':'female','phone':''}),
        item('07 Create doctor (saves ID)','POST','/api/doctors/',
             {'name':'Dr. Meera Sharma','specialization':'Cardiology','email':'meera@example.com'}, {'doctor_id':'id'}),
        item('08 Get all doctors','GET','/api/doctors/'),
        item('09 Get one doctor','GET','/api/doctors/{{doctor_id}}/'),
        item('10 Update doctor','PUT','/api/doctors/{{doctor_id}}/',
             {'name':'Dr. Meera Sharma','specialization':'General Medicine','email':'meera@example.com','phone':''}),
        item('11 Assign doctor (saves mapping ID)','POST','/api/mappings/',
             {'patient':'{{patient_id}}','doctor':'{{doctor_id}}'}, {'mapping_id':'id'}),
        item('12 My patient-doctor mappings','GET','/api/mappings/'),
        item('13 Doctors for selected patient','GET','/api/mappings/{{patient_id}}/'),
        item('14 Remove assignment','DELETE','/api/mappings/{{mapping_id}}/'),
        item('15 Delete doctor','DELETE','/api/doctors/{{doctor_id}}/'),
        item('16 Delete patient','DELETE','/api/patients/{{patient_id}}/'),
        item('17 Refresh JWT','POST','/api/auth/refresh/',
             {'refresh':'{{refresh_token}}'}, {'access_token':'access'}, no_auth=True),
    ]
}
# Postman JSON raw body handles {{variables}} placeholders: remove quotes from numeric IDs.
for i in [10]:
    entry = collection['item'][i]
    entry['request']['body']['raw'] = '{\n  "patient": {{patient_id}},\n  "doctor": {{doctor_id}}\n}'

out=Path(__file__).parent/'Healthcare_Assignment.postman_collection.json'
out.write_text(json.dumps(collection,indent=2),encoding='utf8')
print(out.name)
