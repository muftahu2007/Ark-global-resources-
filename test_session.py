import requests

session = requests.Session()

# 1. Access the catalog page first (this doesn't create a session)
response1 = session.get('http://127.0.0.1:8000/')
print("Initial cookies:", session.cookies.get_dict())

# 2. Simulate AJAX POST to toggle selection (adding product 1)
# Note: we need to get CSRF token or disable it for testing, but let's try just getting the page to get the CSRF token
csrf_token = session.cookies.get('csrftoken')
headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json',
    'X-CSRFToken': csrf_token,
    'Referer': 'http://127.0.0.1:8000/'
}
response2 = session.post('http://127.0.0.1:8000/toggle-selection/1/', data={'action': 'add'}, headers=headers)
print("AJAX Response:", response2.status_code, response2.text)
print("Cookies after AJAX:", session.cookies.get_dict())

# 3. Access the vault page
response3 = session.get('http://127.0.0.1:8000/inquiry/')
print("Vault page status:", response3.status_code)
# We expect the selection to be 1
if b'The vault is currently empty' in response3.content:
    print("Test failed: Vault is empty!")
else:
    print("Test passed: Vault is not empty!")
