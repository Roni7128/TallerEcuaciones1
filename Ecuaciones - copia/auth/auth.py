# auth/auth.py
import json

USUARIOS_FILE_PATH = 'usuarios.json'

def cargar_usuarios():
    try:
        with open(USUARIOS_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE_PATH, 'w') as file:
        json.dump(usuarios, file)

usuarios = cargar_usuarios()

def autenticar(usuario, contrasena):
    return usuarios.get(usuario) == contrasena

def registrar(usuario, contrasena):
    if usuario not in usuarios:
        usuarios[usuario] = contrasena
        guardar_usuarios(usuarios)
        return True
    return False
