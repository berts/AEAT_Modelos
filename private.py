# script que cambia la visibilidad de todos los repositorios de un usuario de GitHub a privado.
import requests

# Token de acceso personal de GitHub
token = 'tu_token_de_acceso'
username = 'tu_nombre_de_usuario'

# Encabezados para la solicitud
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Obtener todos los repositorios del usuario
repos_url = f'https://api.github.com/users/{username}/repos'
response = requests.get(repos_url, headers=headers)
repos = response.json()

# Iterar sobre cada repositorio y cambiar su visibilidad a privada
for repo in repos:
    repo_name = repo['full_name']
    url = f'https://api.github.com/repos/{repo_name}'
    data = {'private': True}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f'{repo_name} ahora es privado.')
    else:
        print(f'Error al cambiar la visibilidad de {repo_name}: {response.status_code}')