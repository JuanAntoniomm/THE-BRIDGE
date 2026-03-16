Hundir la Flota en Python
Descripción.

Este proyecto implementa una versión del juego clásico Hundir la flota utilizando Python.
El jugador coloca manualmente sus barcos en un tablero de 10x10 y juega contra el ordenador, que coloca sus barcos de forma aleatoria y dispara a posiciones también aleatorias, sin repetir donde ya ha disparado. Aun es una versión frágil del juego, por lo que  no seguir las instrucciones al pie de la letra puede producir su detención.

El objetivo del juego es hundir todos los barcos del rival antes de que el rival hunda los tuyos.

Ejecutar el juego.

main.py; utils.py; ReadMe, deben estar en la carpeta.
Después ejecuta el programa desde el terminal con el comando Python main.py.

Instrucciones.

Al empezar, el jugador colocará sus barcos. Los cuales se componen de tres de eslora 2, dos de eslora 3, y un último de eslora 4. Es muy importante no dar coordenadas menores de uno o mayores de diez, ya que esto hará que el juego falle. También es importante tener en cuenta la orientación, nosotros solo daremos la primera coordenada y si introducimos un h (horizontal) continuará hacia la derecha, por el lado contrario si introducimos una v (vertical) continuará hacia abajo. El ordenador lo hará automáticamente de manera aleatoria.

De la misma manera, al disparar las coordenadas deben comprenderse en un rango del uno al diez, para que no falle. También se debe tener en cuenta que si el jugador dispara a un lugar donde ya había disparado, pierde el turno, se debe estar atento. El ordenador lo hará automáticamente de manera aleatoria, sin repetir casillas donde haya disparado. El que primero hunda todos los barcos del rival, ganará la partida.

Estructura del proyecto.
Archivo principal: main.py --> ejecuta el juego y da sentido al flujo.
utils.py --> contiene todas las funciones del juego.
ReadMe --> Descripción del proyecto.

Funcionamiento general

El programa utiliza cuatro tableros:

tablero de barcos del jugador
tablero de disparos del jugador
tablero de barcos del ordenador
tablero de disparos del ordenador

Cada turno se realiza la siguiente secuencia:

Turno del jugador
Comprobación de victoria
Turno del ordenador
Nueva comprobación de victoria
El juego continúa hasta que uno de los jugadores pierde todos sus barcos.
