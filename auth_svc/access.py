import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        token = None
        error = ('Missing credentials', 401)
        return token, error
    
    basicAuth = (auth.username, auth.password)
    # One could use formated string and env variable AUTH_SVC_ADDRESS
    response = requests.post(
        'http://localhost:5000/login', auth = basicAuth,
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)