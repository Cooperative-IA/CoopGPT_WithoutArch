import json
import random
import numpy as np


NAMES = [
    'Yesid',
    'Sofía',
    'Mateo',
    'Valentina',
    'Santiago',
    'María',
    'Sebastián',
    'Camila',
    'Juan',
    'Nicanor'
    'Isabella',
    'Samuel',
    'Mariana',
    'Manuel',
    'Miguel',
    'Nicole',
    'Gabriela',
    'Daniel',
    'Daniela',
    'Nicolás',
    'Sara',
    'Luis Felipe',
    'Valeria',
    'Carlos',
    'Alejandra',
    'Joaquín',
    'Luciana',
    'Andrés',
    'Ana',
    'Felipe',
    'Fernanda',
    'David',
    'Carolina'
]

SURNAMES = [
    'García',
    'Rodríguez',
    'González',
    'Martínez',
    'López',
    'Hernández',
    'Pérez',
    'Ramírez',
    'Torres',
    'Flores',
    'Gómez',
    'Díaz',
    'Mendoza',
    'Cruz',
    'Castro',
    'Ruiz',
    'Álvarez',
    'Romero',
    'Ortiz',
    'Vargas',
    'Guerrero',
    'Moreno',
    'Jiménez',
    'Rojas',
    'Soto',
    'Rivas',
    'Navarro',
    'Salazar',
    'Acosta',
    'Fonseca',
    'Rios',
    'Giraldo',
    'Quijano'
]


def generate_name():
    full_name = f"{random.choice(NAMES)}_{random.choice(SURNAMES)}"
    return full_name


def load_config():
    with open("config/config.json") as json_file:
        config_file = json.load(json_file)
    return config_file


def parse_string_to_matrix(input_string):
    rows = input_string.strip().split('\n')
    matrix = np.array([list(row) for row in rows])
    return matrix


def matrix_to_string(matrix):
    rows = [''.join(row) for row in matrix]
    return '\n'.join(rows)
