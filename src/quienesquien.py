import pytest
import random
from pyswip import Prolog
import numpy as np

def print_characters(prolog, board):
    i = 1
    print_board = '|'
    for name in board:
        print_board += name + '| '
        chars = list(prolog.query(f"obtener_caracteristicas({name}, Caracteristicas)."))[0]['Caracteristicas']
        for char in chars:
            print_board += char
            if char != chars[-1]:
                print_board += ' - '
        print_board += ' |\n|'
    print(print_board[:-2])

def check_characteristic(prolog, board, characteristic, status):
    new_board = []
    for name in board:
        check = bool(list(prolog.query(f"tiene_caracteristica({name}, {characteristic}).")))
        if check == status:
            new_board.append(name)
    return new_board

def computer_action(prolog, character_names, unique_characteristics):
    character_dict = {}
    for char in character_names:
        character_dict[char] = list(prolog.query(f"obtener_caracteristicas({char}, Caracteristicas)."))[0]['Caracteristicas']

def main():
    prolog = Prolog()
    prolog.consult('do_quienesquien/src/quienesquien_modified.pl')
    character_names = list(prolog.query("obtener_nombres(Nombres)."))[0]['Nombres']
    unique_characteristics = list(prolog.query("caracteristicas_unicas(CaracteristicasUnicas)."))[0]['CaracteristicasUnicas']
    computer_action(prolog, character_names, unique_characteristics)
    
    status = 'starting'
    while status != 'finished':
        if status == 'starting':
            player_character = input(f"Seleccióna un personaje entre los diponibles -> {character_names}\n(Si desea obtener las caracteristicas de algun personaje escriba el caracter \"¡\" delante del nombre.) \n").strip().lower()

            if '¡' in player_character and player_character.replace('¡', '') in character_names:
                chars = list(prolog.query(f"obtener_caracteristicas({player_character.replace('¡', '')}, Caracteristicas)."))
                print(chars)
                continue
            elif player_character not in character_names:
                print("El personaje selecciónado no existe.")
                continue

            computer_character = random.choice(character_names)
            computer_characteristics = list(prolog.query(f"obtener_caracteristicas({computer_character}, Caracteristicas)."))[0]['Caracteristicas']
            player_board = character_names
            computer_board = character_names
            status = 'playing'
            round = 1
            turn = 'player'
            print('¡Recuerda que la primera pregunta no puede ser si el personaje es hombre o mujer!')

        if status == 'playing':
            if turn == 'player':
                print_characters(prolog, player_board)
                selection = input('Seleccióna una característica o un personaje entre los disponibles\n').replace(' ', '_')
                if round == 1 and (selection == 'hombre' or selection == 'mujer'):
                    print('¡La primera pregunta no puede ser si el personaje es hombre o mujer!')

                elif selection in unique_characteristics:
                    if selection not in computer_characteristics:
                        print(f"El personaje NO tiene la caracteristica --> {selection}")
                        player_board = check_characteristic(prolog, player_board, selection, False)
                    else:
                        print(f"El personaje tiene la caracteristica --> {selection}")
                        player_board = check_characteristic(prolog, player_board, selection, True)
                    round += 1
                    turn = 'computer'
                
                elif selection in character_names:
                    if selection != computer_character:
                        print(f"El personaje NO es --> {selection}")
                        round += 1
                        turn = 'computer'
                    else:
                        print("¡FELICIDADES HAS ACERTADO!")
                        while selection != 'si' or selection != 'no':
                            selection = input('¿Deseas empezar una nueva partida? (si|no)').strip().lower()
                            if selection == 'si':
                                status = 'starting'
                            elif selection == 'no':
                                status = 'finished'
            if turn == 'computer':
                pass

if __name__ == "__main__":
    main()