from utils import crea_tablero
from utils import crear_barco
from utils import coloca_barco
from utils import colocar_todos_mis_barcos
from utils import barco_aleatorio_pc
from utils import coloca_todos_los_barcos_pc
from utils import disparar
from utils import crear_coordenada_disparoPC
from utils import disparar_pc
from utils import mostrar_tableros
from utils import turno_jugador
from utils import turno_pc
from utils import comprobar_vic
tablero_trabajo_personal = crea_tablero(10)
tablero_trabajo_pc = crea_tablero(10)
tablero_trabajo_personal2 = crea_tablero(10)
tablero_trabajo_pc2 = crea_tablero(10)
print("Es el momento de colocar la flota")
colocar_todos_mis_barcos(tablero_trabajo_personal)
print("Ahora le toca a tu oponente")
coloca_todos_los_barcos_pc(tablero_trabajo_pc)
while True:
    print("\nTU TABLERO")
    mostrar_tableros("f", tablero_trabajo_personal, tablero_trabajo_personal2, tablero_trabajo_pc)

    print("\nTABLERO DE DISPAROS")
    mostrar_tableros("d", tablero_trabajo_personal, tablero_trabajo_personal2, tablero_trabajo_pc)

    print("TABLERO PC")
    mostrar_tableros("z", tablero_trabajo_personal, tablero_trabajo_personal2, tablero_trabajo_pc)

    turno_jugador(tablero_trabajo_pc, tablero_trabajo_personal2)
    if comprobar_vic(tablero_trabajo_personal, tablero_trabajo_pc):
        break
    turno_pc(tablero_trabajo_personal, tablero_trabajo_pc2)
    if comprobar_vic(tablero_trabajo_personal, tablero_trabajo_pc):
        break