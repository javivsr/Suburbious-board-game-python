"""
Javier Vaca Sánchez
Enrique Quiñones Ureta

Hemos utilizado el código solución de la primera práctica del Campus Virtual, con las siguientes
modificaciones:

 - Cambiamos el "__init__" de la clase Juego añadiendo parámetros para el número de filas y columnas
 - Hemos juntado los métodos originales "lee_fichero_tablero" y "lee_fichero_secuencia" en uno
   solo, lee_fichero, que actualiza las propiedades "tab" y "sec"
 - Hemos añadido parámetros para el número de filas y columnas en "crea_tablero_azar"
 - Hemos cambiado el parámetro "mov" de tipo string de los métodos "jugada_correcta" y "jugar" por dos
   enteros que nos dicen la fila y columna de la jugada.
 - Se ha añadido un método "jugar_azar" que escoge un movimiento correcto al azar y hace una jugada
 - Se han añadido callbacks a los métodos "jugar" y "jugar_azar" para que se puedan ejecutar las
   animaciones
"""

from enum import IntEnum
from random import choice


def letra(i):
    """ Devuelve la letra i-esima a partir de la A
    :param i: indice 0-based
    :return: letra i-ésima
    """
    return chr(ord('A') + i)


class TipoElem(IntEnum):
    """ Tipos de elementos """
    VACIO = 0
    TIENDA = 1
    CASA = 2
    MANSION = 3
    EDIFICIO = 4
    HOSPITAL = 5
    BIGFOOT = 6
    BEBE = 7
    ESCUELA = 8
    UNIVERSIDAD = 9
    WICK = 10
    ESCOMBRO = 11


class InfoElem(object):
    """ Representa la información sobre un tipo de elemento """

    def __init__(self, car, ftab, fjue, ptos, colap):
        self.car = car
        self.ftab = ftab
        self.fjue = fjue
        self.ptos = ptos
        self.colap = colap


class Elem(object):
    """ Representa un elemento de una celda """
    # Tabla de información sobre los elementos
    TABLA = {TipoElem.VACIO: InfoElem('.', 45, 0, 0, None),
             TipoElem.TIENDA: InfoElem('a', 18, 60, 1, TipoElem.CASA),
             TipoElem.CASA: InfoElem('b', 4, 10, 5, TipoElem.MANSION),
             TipoElem.MANSION: InfoElem('c', 3, 2, 25, TipoElem.EDIFICIO),
             TipoElem.EDIFICIO: InfoElem('d', 0, 0, 125, TipoElem.HOSPITAL),
             TipoElem.HOSPITAL: InfoElem('e', 0, 0, 625, None),
             TipoElem.BIGFOOT: InfoElem('1', 2, 12, -25, None),
             TipoElem.BEBE: InfoElem('2', 0, 0, -5, TipoElem.ESCUELA),
             TipoElem.ESCUELA: InfoElem('3', 0, 0, 50, TipoElem.UNIVERSIDAD),
             TipoElem.UNIVERSIDAD: InfoElem('4', 0, 0, 500, None),
             TipoElem.WICK: InfoElem('W', 0, 1, 0, None),
             TipoElem.ESCOMBRO: InfoElem('X', 0, 0, -50, None)}

    def __init__(self, tipo, edad=0):
        self.tipo = tipo
        self.edad = edad

    def inc_edad(self):
        """ Incrementa la edad del elemento """
        self.edad += 1

    @property
    def car(self):
        """ Devuelve el carácter asociado a éste elemento
        :return: El carácter asociado a éste elemento
        """
        return Elem.TABLA[self.tipo].car

    @property
    def ptos(self):
        """ Devuelve la puntuación de éste elemento
        :return: Los puntos de éste elemento
        """
        return Elem.TABLA[self.tipo].ptos


class Juego(object):
    """ Representa el estado del juego """

    # --- CONSTANTES DEL JUEGO ---
    NUMFIL = 6  # Número de filas del tablero (para tableros creados al azar)
    NUMCOL = 6  # Número de columnas del tablero (para tableros creados al azar)
    TAM_COLAPSO = 3  # Número de elementos para que se produzca un colapso
    EDAD_ESCOMBROS = 10  # Edad a partir de la cual depositan escombros los bigfoots
    VECINAS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Desplazamiento (desp. fil, desp. col) para acceder a celdas vecinas

    # Cambiamos el constructor añadiendo parámetros para el número de filas y columnas
    def __init__(self, fich=None, nfil=6, ncol=6):
        # Creamos los vectores para elegir elementos al azar
        self.azar_tab = [t for tipo in TipoElem for t in [tipo] * Elem.TABLA[tipo].ftab]
        self.azar_sec = [t for tipo in TipoElem for t in [tipo] * Elem.TABLA[tipo].fjue]
        # La matriz que almacena los elementos del tablero
        self.tab = None
        self.sec = []
        if fich:
            self.lee_fichero(fich)
            # El número de filas y columnas ahora puede ser variable
            self.nfil = len(self.tab)
            self.ncol = len(self.tab[0])
        else:
            self.crea_tablero_azar(nfil, ncol)
            self.nfil = nfil
            self.ncol = ncol
        # Elementos restantes del estado del juego
        self.turno = 1
        self.puntos = self.calcula_puntos()
        self.almacen = Elem(TipoElem.VACIO)
        self.actual = self.elige_actual()

    def __getitem__(self, pos):
        """ Para poder acceder al tablero con notación matricial: self[i,j] """
        return self.tab[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self.tab[pos[0]][pos[1]] = value

    @property
    def bigfoots(self):
        """ Recorre los bigfoots del tablero, devolviendo una tupla con su fila, columna y elemento """
        nfil, ncol = len(self.tab), len(self.tab[0])
        for i in range(nfil):
            for j in range(ncol):
                if self.tab[i][j].tipo == TipoElem.BIGFOOT:
                    yield i, j, self.tab[i][j]

    # Unimos los métodos lee_fichero_tablero y lee_fichero_secuencia en uno solo
    def lee_fichero(self, nomfich):
        """ Lee el tablero y la secuencia de un fichero. El fichero se supone correcto.
        :param nomfich: Ruta del fichero
        """
        # Diccionario caracter -> tipo de elemento
        car_tipo = dict((Elem.TABLA[tipo].car, tipo) for tipo in TipoElem)
        with open(nomfich) as fich:
            lins = fich.read().splitlines()
            self.sec = [car_tipo[car] for car in lins[0].strip()]
            self.tab = [[Elem(car_tipo[car]) for car in lin.strip()] for lin in lins[1:]]

    # Añadimos los parámetros de número de filas y de columnas
    def crea_tablero_azar(self, nfil, ncol):
        """ Crea un tablero al azar """
        self.tab = [[Elem(choice(self.azar_tab)) for _ in range(ncol)] for _ in range(nfil)]

    def elige_actual(self):
        """ Elige el elemento actual, a partir de la secuencia o al azar (si está vacía)
        :return: El elemento elegido
        """
        if self.sec:
            # Se actualiza la secuencia de forma circular
            self.sec = self.sec[1:] + [self.sec[0]]
            return Elem(self.sec[-1])
        else:
            # Se elige al azar
            return Elem(choice(self.azar_sec))

    def calcula_puntos(self):
        """ Devuelve la puntuación del tablero
        :return La puntuación del tablero
        """
        return sum(elem.ptos for fil in self.tab for elem in fil)

    def __repr__(self):
        ncol = len(self.tab[0])
        sepf = f"  ├{'───┼' * (ncol - 1)}───┤\n"
        return f"   {' '.join(f' {i + 1} ' for i in range(ncol))}\n" + \
               f"  ┌{'───┬' * (ncol - 1)}───┐\n" + \
               sepf.join(f"{letra(i)} │ {' │ '.join(e.car for e in lin)} │\n" for i, lin in enumerate(self.tab)) + \
               f"  └{'───┴' * (ncol - 1)}───┘\n"

    def __str__(self):
        return f"\n{repr(self)}  Turno: {self.turno} Puntos: {self.puntos}\n" + \
               f"  Almacen: [{self.almacen.car}] Actual: [{self.actual.car}]\n"

    def en_rango(self, fil, col):
        """ Comprueba si las coordenadas estan en rango
        :param fil: fila del tablero (0-based)
        :param col: columna del tablero (0-based)
        :return: True si están en el rango correcto
        """
        return 0 <= fil < len(self.tab) and 0 <= col < len(self.tab[0])

    # La jugada ahora viene dada por fila y columna, no por un string
    def jugada_correcta(self, fil, col):
        """ Comprueba si la jugada es correcta
        :param fil: Fila de destino
        :param col: Columna de destino
        :return: True si es correcta, False caso contrario
        """
        # Comprobación de rango
        if not self.en_rango(fil, col):
            return False
        # Comprobación de destino vacío (salvo WICK)
        if self.actual.tipo == TipoElem.WICK:
            return self[fil, col].tipo != TipoElem.VACIO
        else:
            return self[fil, col].tipo == TipoElem.VACIO

    def cambio_almacen(self):
        """ Intercambio almacén <-> elemento actual """
        self.actual, self.almacen = self.almacen, self.actual
        # Detectamos si el almacén estaba vacío
        if self.actual.tipo == TipoElem.VACIO:
            self.actual = self.elige_actual()

    # La jugada ahora viene dada por fila y columna, no por un string
    # Añadimos callbacks para los eventos relevantes
    def jugar(self, fil, col, on_kill, on_colapso, on_bebes, on_movimiento):
        """ Realiza una jugada y actualiza el tablero
        :param mov: jugada (se supone correcta)
        :return True si se ha terminado la partida
        """
        # Etapa 2.3.1
        if self.actual.tipo == TipoElem.WICK:
            on_kill(fil, col)  # Evento de matar elemento en celda
            # Vaciar celda
            self[fil, col] = Elem(TipoElem.VACIO)
        else:
            # Insertar elemento
            self[fil, col] = self.actual
            # Etapa 2.3.2
            while self.colapso(fil, col, on_colapso):
                pass
        # Etapa 2.3.3
        self.inc_edad_bigfoots()
        # Etapa 2.3.4
        bebes = self.encierro_bigfoots()
        if len(bebes) > 0:
            on_bebes(bebes)  # Evento de transformación en bebés
            # Etapa 2.3.5
            self.colapso_bebes(bebes, on_colapso)
        # Etapa 2.3.6
        self.mueve_bigfoots(on_movimiento)
        # Incrementamos el turno
        self.turno += 1
        # Elegimos el siguiente elemento actual
        self.actual = self.elige_actual()
        # Actualizamos la puntuación
        self.puntos = self.calcula_puntos()
        # Detectamos si es fin de partida
        return all(e.tipo != TipoElem.VACIO for fil in self.tab for e in fil)

    # Añadimos un callback que se llamará si se produce un colapso
    def colapso(self, fil, col, on_colapso):
        """ Comprueba si hay un grupo para el elemento situado en (fil, col)
            con tamaño superior a 3 y si es así lo colapsa
        :param fil: fila de la celda
        :param col: columna de la celda
        :return: True si se ha producido un colapso
        """
        elem = self[fil, col]
        tipo_colap = Elem.TABLA[elem.tipo].colap  # Tipo del elemento al que colapsa
        if tipo_colap is None:
            # Elemento no colapsable
            return False
        # Se obtiene el conjunto de coordenadas de elementos del grupo
        grupo = self.calc_grupo(fil, col, lambda e: e.tipo == elem.tipo)
        # Se comprueba si hay elementos suficientes para colapsar
        if len(grupo) >= Juego.TAM_COLAPSO:
            # Evento de colapso: Pasamos la posición de colapso y el conjunto de posiciones de los elem. que colapsan
            on_colapso(fil, col, grupo)
            # Se vacían las celdas
            for i, j in grupo:
                self[i, j] = Elem(TipoElem.VACIO)
            # Se coloca el nuevo elemento en la posición de colapso
            self[fil, col] = Elem(tipo_colap)
            return True
        else:
            return False

    def inc_edad_bigfoots(self):
        """ Incrementa la edad de los bigfoots (sección 2.2.3)
        """
        for _, _, e in self.bigfoots:
            e.inc_edad()

    def encierro_bigfoots(self):
        """ Detecta los bigfoots encerrados y los convierte en bebés (sección 2.2.4)
        :return: el conjunto de posiciones de los nuevos bebés
        """
        bebes = set()
        for fil, col, elem in self.bigfoots:
            region = self.calc_grupo(fil, col, lambda e: e.tipo == TipoElem.VACIO or e.tipo == TipoElem.BIGFOOT)
            # Comprobar si no hay ningín elemento vacío en la región
            if all(self[i, j].tipo != TipoElem.VACIO for i, j in region):
                # Los bigfoots de esa región están encerrados, convertirles en bebes
                bebes |= region
                for pos in region:
                    self[pos] = Elem(TipoElem.BEBE, self[pos].edad)  # Los bebes mantienen la edad de los bigfoots
        return bebes

    # Añadimos un callback porque lo necesita la llamada a "colapso"
    def colapso_bebes(self, bebes, on_colapso):
        """ Comprueba si los nuevos bebes colapsan y realiza el colapso
        :param bebes: conjunto de posiciones (tupla de fila y columna) de los bebes
        """
        while len(bebes) > 0:
            # En cada iteración se colapsa (o no) un grupo de bebes
            # Cogemos uno cualquiera
            fil, col = bebes.pop()
            grupo = self.calc_grupo(fil, col, lambda e: e.tipo == TipoElem.BEBE)
            # Quitamos los de su grupo (diferencia de conjuntos)
            bebes -= grupo
            if len(grupo) >= Juego.TAM_COLAPSO:
                # Encontrar el de más edad del grupo
                _, fil, col = max(((self[i, j].edad, i, j) for i, j in grupo), key=lambda t: t[0])
                # Colapsar
                while self.colapso(fil, col, on_colapso):
                    pass

    # Añadimos un callback para animar el movimiento de los bigfoots
    def mueve_bigfoots(self, on_movimiento=None):
        """ Se mueven los bigfoots, actualizando las matrices de tablero y edad """
        # Obtenemos la lista de bigfoots ordenada de mayor a menor edad
        bigfoots = sorted(list(self.bigfoots), key=lambda t: t[2].edad, reverse=True)
        # Nuevo: Creamos una lista de posiciones anteriores y actuales, para la animación
        lis_mov = []
        # Recorremos los bigfoots
        for i, j, elem in bigfoots:
            # Buscamos primera posición vecina vacía y movemos el bigfoot
            for di, dj in Juego.VECINAS:
                mi, mj = i+di, j+dj
                if self.en_rango(mi, mj) and self[mi, mj].tipo == TipoElem.VACIO:
                    self[mi, mj] = elem
                    self[i, j] = Elem(TipoElem.VACIO if elem.edad <= Juego.EDAD_ESCOMBROS else TipoElem.ESCOMBRO)
                    lis_mov.append((i, j, mi, mj))
                    break
        # Llamamos al callback con la lista de posiciones anteriores y actuales de los elementos que se mueven
        if len(lis_mov) > 0:
            on_movimiento(lis_mov)

    def calc_grupo(self, fil, col, cond):
        """ Calcula el conjunto de celdas de un grupo o de una región.
         El resultado se devuelve como un conjunto de coordenadas (tuplas de fila y columna)
         Se comprueba si la celda (fil,col) está en el tablero y cumple la condicion 'cond', entonces se añade al
         conjunto esa celda y los grupos/regiones de las celdas vecinas.
         Para evitar recursión infinita se comprueba si la posición actual ya estaba en el conjunto.
        :param fil: fila de la celda que se comprueba
        :param col: columna de la celda que se comprueba
        :param cond: función que recibe un elemento y devuelve un valor lógico
        :return  El conjunto de posiciones de las celdas del grupo o región
        """
        grupo = set()
        self.calc_grupo_rec(fil, col, cond, grupo)
        return grupo

    def calc_grupo_rec(self, fil, col, cond, grupo):
        """ Función de ayuda de calc_grupo """
        if self.en_rango(fil, col) and cond(self[fil, col]) and (fil, col) not in grupo:
            grupo.add((fil, col))
            for dfil, dcol in Juego.VECINAS:
                self.calc_grupo_rec(fil+dfil, col+dcol, cond, grupo)

    # Nuevo método: Jugar eligiendo posición al azar
    def jugar_azar(self, on_kill, on_colapso, on_bebes, on_movimiento):
        # Creamos la lista de posiciones válidas
        validas = []
        for fil in range(self.nfil):
            for col in range(self.ncol):
                if self.jugada_correcta(fil, col):
                    validas.append((fil,col))
        # Elegimos una al azar usando choice
        pos = choice(validas)
        return self.jugar(pos[0], pos[1], on_kill, on_colapso, on_bebes, on_movimiento)

# Quitamos el main, ya no es necesario