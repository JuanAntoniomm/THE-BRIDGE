import numpy as np
import random
def crea_tablero(lado = 10): # Puede que este influyendo en como se pinta en los tableros
    tablero = np.full((lado,lado)," ")
    return tablero
def crear_barco(eslora):
    fila = (int(input(f"Introduce la fila inicial del barco de eslora {eslora}: ")) -1)
    columna = (int(input(f"Introduce la columna inicial del barco de eslora {eslora}: ")) -1)
    orientacion = input("Introduce la orientación del barco H para horizontal, V para vertical: ").upper()
    if orientacion == "H":
        barco = [(fila, columna + x) for x in range(eslora)]
    elif orientacion == "V":
        barco = [(fila + x, columna) for x in range(eslora)]
    else:
        print("Orientación no válida")
        return None

    return barco
def coloca_barco(tablero_trabajo_personal, barco):
    num_max_filas = tablero_trabajo_personal.shape[0]
    num_max_columnas = tablero_trabajo_personal.shape[1]
    for pieza in barco:
        fila = pieza[0]
        columna = pieza[1]
        if fila < 0  or fila >= num_max_filas:
            print(f"No puedo poner la pieza {pieza} porque se sale del tablero")
            return False
        if columna <0 or columna>= num_max_columnas:
            print(f"No puedo poner la pieza {pieza} porque se sale del tablero")
            return False
        if tablero_trabajo_personal[pieza] == "O" or tablero_trabajo_personal[pieza] == "X":
            print(f"No puedo poner la pieza {pieza} porque hay otro barco")
            return False
    for pieza in barco:
        tablero_trabajo_personal[pieza] = "O"
    return True
def colocar_todos_mis_barcos(tablero_trabajo_personal):
    lista_mis_barcos = [2, 2, 2, 3, 3, 4]

    for eslora in lista_mis_barcos:
        colocado = False
        while colocado == False:
            barco = crear_barco(eslora)
            resultado = coloca_barco(tablero_trabajo_personal, barco)

            if resultado is not False:
                colocado = True
def barco_aleatorio_pc(eslora):
    orientacion = random.choice(["H", "V"])
    if orientacion == "H":
        fila = random.randint(0, 9)
        columna = random.randint(0, 10 - eslora)
        barco = [(fila, columna + x) for x in range(eslora)]
    else:
        fila = random.randint(0, 10 - eslora)
        columna = random.randint(0, 9)
        barco = [(fila + x, columna) for x in range(eslora)]
    
    return barco

def coloca_todos_los_barcos_pc(tablero_trabajo_pc): # Se superponen
    lista_barcos_pc = [2, 2, 2, 3, 3, 4]
    for eslora in lista_barcos_pc:
        colocado = False
        while colocado == False:
            barco = barco_aleatorio_pc(eslora)
            colocado = coloca_barco(tablero_trabajo_pc, barco)
    return tablero_trabajo_pc
def disparar(tablero_trabajo_pc, tablero_trabajo_personal2, coordenada): # Disparo yo
    if tablero_trabajo_personal2[coordenada] == "X":
        print("Agonia, deja de perder el tiempo, dispara a otro sitio")
    elif tablero_trabajo_personal2[coordenada] == "-":
        print("Agonia, deja de perder el tiempo, dispara a otro sitio")
    elif tablero_trabajo_pc[coordenada] == "O":
        tablero_trabajo_personal2[coordenada] = "X"
        print("Tocado")
        tablero_trabajo_pc[coordenada] = "X"
    elif tablero_trabajo_pc[coordenada] == " ":
        tablero_trabajo_personal2[coordenada] = "-"
        print("Agua")
def crear_coordenada_disparoPC():
    fila = np.random.randint(0,10)
    columna = np.random.randint(0,10)
    return fila, columna
def disparar_pc(tablero_trabajo_personal, tablero_trabajo_pc2):
    coordenada_pc = crear_coordenada_disparoPC()
    while tablero_trabajo_pc2[coordenada_pc] == "X" or tablero_trabajo_pc2[coordenada_pc] == "-":
        coordenada_pc = crear_coordenada_disparoPC()
        
    if tablero_trabajo_personal[coordenada_pc] == "O":
        tablero_trabajo_pc2[coordenada_pc] = "X"
        print("Tocado")
        tablero_trabajo_personal[coordenada_pc] = "X"
    elif tablero_trabajo_personal[coordenada_pc] == " ":
        tablero_trabajo_pc2[coordenada_pc] = "-"
        print("Agua")
def mostrar_tableros(arg, tablero_trabajo_personal, tablero_trabajo_personal2, tablero_trabajo_pc):
    if arg == "d":
        print(tablero_trabajo_personal2)
    elif arg == "f":
        print(tablero_trabajo_personal)
    elif arg == "z":
        print(tablero_trabajo_pc)
    
def turno_jugador(tablero_trabajo_pc, tablero_trabajo_personal2):
        fila = (int(input("Introduce una coordenada en la fila del 1 al 10: ")) -1)
        columna = (int(input("Introduce una coordenada del 1 al 10 para la columna: ")) -1)
        return disparar(tablero_trabajo_pc, tablero_trabajo_personal2, (fila, columna))

def turno_pc(tablero_trabajo_personal, tablero_trabajo_pc2):
        return disparar_pc(tablero_trabajo_personal, tablero_trabajo_pc2)

def comprobar_vic(tablero_trabajo_personal, tablero_trabajo_pc):
       if "O" not in tablero_trabajo_personal:
              print("Vaya has perdido, más suerte la próxima")
              return True
       elif "O" not in tablero_trabajo_pc:
              print("Enhorabuena has ganado")
              return True
       else:
              return False