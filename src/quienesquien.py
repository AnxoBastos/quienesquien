import random
from pyswip import Prolog
import math

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

def calculate_entropy(group):
    total = len(group)
    if total == 0:
        return 0

    frequency = {}
    for element in group:
        if element in frequency:
            frequency[element] += 1
        else:
            frequency[element] = 1
        
    probabilities = [freq / total for freq in frequency.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy

def information_gain(character, characteristic):
    total = len(character)
    if total == 0:
        return 0

    group_with_characteristic = []
    group_without_characteristic = []
    for name, characteristics in character.items():
        if characteristic in characteristics:
            group_with_characteristic.append(name)
        else:
            group_without_characteristic.append(name)

    entropy_before = calculate_entropy(character.keys())
    entropy_after = (
        (len(group_with_characteristic) / total) * calculate_entropy(group_with_characteristic) +
        (len(group_without_characteristic) / total) * calculate_entropy(group_without_characteristic)
    )

    return entropy_before - entropy_after

def select_best_characteristic(characters, unique_characteristics):
    best_characteristic = None
    best_gain = -1

    for characteristic in unique_characteristics:
        gain = information_gain(characters, characteristic)
        if gain > best_gain:
            best_gain = gain
            best_characteristic = characteristic

    return best_characteristic

def filter_characters(characters, characteristic, value):
    if value:
        return {name: chars for name, chars in characters.items() if characteristic in chars}
    else:
        return {name: chars for name, chars in characters.items() if characteristic not in chars}

def main():
    prolog = Prolog()
    prolog.consult('quienesquien/src/quienesquien.pl')
    character_names = list(prolog.query("obtener_nombres(Nombres)."))[0]['Nombres']
    unique_characteristics = list(prolog.query("caracteristicas_unicas(CaracteristicasUnicas)."))[0]['CaracteristicasUnicas']
    
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
            characters_dict = {}
            for char in character_names:
                characters_dict[char] = list(prolog.query(f"obtener_caracteristicas({char}, Caracteristicas)."))[0]['Caracteristicas']
            player_board = character_names

            status = 'playing'
            round = 1

            print('¡Recuerda que la primera pregunta no puede ser si el personaje es hombre o mujer!')
            turn = random.choice(('player', 'computer'))
            if turn == 'computer': print('Empieza a preguntar el ordenador')
            else: print('Empiezas a preguntar tu')

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
                        print("¡Felicidades has acertado!")
                        while selection != 'si' and selection != 'no':
                            selection = input('¿Deseas empezar una nueva partida? (si|no)\n').strip().lower()
                            print(selection)
                            if selection == 'si':
                                status = 'starting'
                            elif selection == 'no':
                                status = 'finished'
            if turn == 'computer':
                if len(characters_dict) == 1:
                    name = next(iter(characters_dict))
                    win_condition = input(f"¿El personaje es {name}? (si|no)\n").strip().lower() == "si"
                    if win_condition:
                        print("¡Ha acertado el ordenador!")
                    else:
                        print("ERROR: No se pudo identificar un único personaje.")
                    while selection != 'si' and selection != 'no':
                            selection = input('¿Deseas empezar una nueva partida? (si|no)\n').strip().lower()
                            if selection == 'si':
                                status = 'starting'
                            elif selection == 'no':
                                status = 'finished'
                else:
                    best_characteristic = select_best_characteristic(characters_dict, unique_characteristics)
                    answer = input(f"¿El personaje tiene {best_characteristic}? (si|no)\n").strip().lower() == "si"
                    characters_dict = filter_characters(characters_dict, best_characteristic, answer)
                    round += 1
                    turn = 'player'

if __name__ == "__main__":
    main()