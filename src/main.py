# Project developed by:
# - Javier Vaca Sánchez
# - Enrique Quiñones Ureta
"""
The board state is represented by two "matrices" (lists of lists):
- tab[row][col] -> Elem (element present at that row (0..5) and column (0..5))
- edad[row][col] -> int (age of the Bigfoot at that row and column; if there is no Bigfoot, the value is ignored)

When calculating groups and regions, we work with a set of cell coordinates
belonging to the group or region. Coordinates are represented as tuples (row, col).

To move Bigfoots, we first extract a list of tuples (age, row, col) for each Bigfoot
and then sort it in descending order (tuples naturally sort by age).

Checking for trapped Bigfoots returns a set with the coordinates of Bigfoots that
turned into babies. Since they occupy the same positions, the age matrix retains 
their previous ages, which is used during baby collapse detection to find the oldest 
one determining the collapse position.
"""

from enum import IntEnum
from random import choice


class Elem(IntEnum):
    """ Types of elements """
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


# --- PROGRAM CONSTANTS ---
NUMFIL = 6  # Number of rows on the board
NUMCOL = 6  # Number of columns on the board
TAM_COLAPSO = 3  # Minimum number of adjacent matching elements required for a collapse
EDAD_ESCOMBROS = 10  # Age threshold after which Bigfoots leave debris behind
# Element lookup table data
TABLA = [('.', 45, 0, 0, None),
         ('a', 18, 60, 1, Elem.CASA),
         ('b', 4, 10, 5, Elem.MANSION),
         ('c', 3, 2, 25, Elem.EDIFICIO),
         ('d', 0, 0, 125, Elem.HOSPITAL),
         ('e', 0, 0, 625, None),
         ('1', 2, 12, -25, None),
         ('2', 0, 0, -5, Elem.ESCUELA),
         ('3', 0, 0, 50, Elem.UNIVERSIDAD),
         ('4', 0, 0, 500, None),
         ('W', 0, 1, 0, None),
         ('X', 0, 0, -50, None)]


def imprimir(tab, edad, turno, puntos, almacen, actual):
    """ Prints the game board on the screen.
    :param tab: Matrix of board elements
    :param edad: Matrix of Bigfoot ages
    :param turno: Current turn count
    :param puntos: Current score
    :param almacen: Element stored in warehouse
    :param actual: Current element to be placed
    """
    # Column header
    print("")
    print(" ", end='')
    for i in range(NUMCOL):
        print(f"   {i + 1}", end='')
    print("")
    # Row borders
    sep_pri = "  ╔" + "═══╤" * (NUMCOL - 1) + "═══╗"
    sep_int = "  ╟" + "───┼" * (NUMCOL - 1) + "───╢"
    sep_ult = "  ╚" + "═══╧" * (NUMCOL - 1) + "═══╝"
    for i in range(NUMFIL):
        print(sep_pri if i == 0 else sep_int)
        ch = chr(ord('A') + i)
        print(f"{ch} ", end='')
        for j in range(NUMCOL):
            print('║' if j == 0 else '│', end='')
            elem = tab[i][j]
            car = TABLA[elem][0]
            print(f" {car} ", end='')
        print('║')
    print(sep_ult)
    print(f"  Turn: {turno} Score: {puntos}")
    car_alm = TABLA[almacen][0]
    car_act = TABLA[actual][0]
    print(f"  Warehouse: [{car_alm}] Current: [{car_act}]")
    print("")


def busca_elem(car):
    """ Returns the element corresponding to a character (searches in lookup table).
    :param car: Character to search for
    :return: The matching Elem enum
    """
    i = 0
    for reg in TABLA:
        if reg[0] == car:
            return Elem(i)
        i += 1


def lee_fichero_tablero(nomfich):
    """ Reads board state from a file.
    :param nomfich: File path
    :return: NUMFIL x NUMCOL matrix containing elements
    """
    mat = []
    fich = open(nomfich)
    try:
        for i in range(NUMFIL):
            lin = fich.readline()
            lin = lin.strip()  # Strip newline characters

            fil = []
            for j in range(NUMCOL):
                ch = lin[j]
                fil.append(busca_elem(ch))
            mat.append(fil)
    finally:
        fich.close()
    return mat


def crea_tablero_azar(azar_tab):
    """ Generates a random board according to element frequency weights.
    :param azar_tab: Weighted selection vector for board elements
    :return: NUMFIL x NUMCOL matrix containing elements
    """
    mat = []
    for i in range(NUMFIL):
        fil = []
        for j in range(NUMCOL):
            elem = choice(azar_tab)
            fil.append(elem)
        mat.append(fil)
    return mat


def lee_fichero_secuencia(nomfich):
    """ Reads element sequence from a file.
    :param nomfich: File path
    :return: List of elements in sequence
    """
    lis = []
    fich = open(nomfich)
    try:
        lin = fich.readline()
        lin = lin.strip()
        for car in lin:
            lis.append(busca_elem(car))
    finally:
        fich.close()
    return lis


def elige_actual(secuencia, azar_sec):
    """ Chooses current element from sequence or randomly if empty.
    :param secuencia: List sequence of elements
    :param azar_sec: Weighted selection vector for sequence elements
    :return: Selected Elem
    """
    if len(secuencia) == 0:
        # Select randomly
        return choice(azar_sec)
    else:
        # Pick the first element from sequence
        elem = secuencia[0]
        # Rotate sequence circularly
        for i in range(1, len(secuencia)):
            secuencia[i - 1] = secuencia[i]
        secuencia[-1] = elem
        return elem


def calcula_puntos(tab):
    """ Calculates current total board score.
    :param tab: Matrix of board elements
    :return: Sum of scores across all cells
    """
    puntos = 0
    for i in range(NUMFIL):
        for j in range(NUMCOL):
            elem = tab[i][j]
            # Score values stored in column 3 of TABLA
            puntos += TABLA[elem][3]
    return puntos


def fin_partida(tab):
    """ Checks if game is over (no empty cells remaining).
    :param tab: Matrix of board elements
    :return: True if no empty cells remain
    """
    for i in range(NUMFIL):
        for j in range(NUMCOL):
            if tab[i][j] == Elem.VACIO:
                return False
    return True


def jugada_correcta(tab, mov, actual):
    """ Validates if player's move is allowed.
    :param tab: Matrix of board elements
    :param mov: Input move string
    :param actual: Current element being placed
    :return: True if valid, False otherwise
    """
    if mov == '*':
        return True
    if len(mov) != 2:
        return False
    fil = ord(mov[0]) - ord('A')
    col = ord(mov[1]) - ord('1')
    # Bounds check
    if fil < 0 or fil >= NUMFIL or col < 0 or col >= NUMCOL:
        return False
    # Destination cell check (must be non-empty for WICK, empty for others)
    if actual == Elem.WICK:
        return tab[fil][col] != Elem.VACIO
    else:
        return tab[fil][col] == Elem.VACIO


def jugar(tab, mov, edad, actual):
    """ Executes a move and updates board state.
    :param tab: Matrix of board elements
    :param mov: Move coordinates string
    :param edad: Matrix of Bigfoot ages
    :param actual: Element being placed
    """
    fil = ord(mov[0]) - ord('A')
    col = ord(mov[1]) - ord('1')
    if actual == Elem.WICK:
        # Clear target cell
        tab[fil][col] = Elem.VACIO
    else:
        # Place element
        tab[fil][col] = actual
        # Process chain collapses
        hay_colapso = True
        while hay_colapso:
            hay_colapso = colapso(tab, fil, col)
    # Increment Bigfoot age
    inc_edad_bigfoots(tab, edad)
    # Check for trapped Bigfoots
    bebes = encierro_bigfoots(tab)
    if len(bebes) > 0:
        # Collapse resulting Babies
        colapso_bebes(tab, edad, bebes)
    # Move Bigfoots across board
    mueve_bigfoots(tab, edad)


def grupo(tab, fil, col, elem, conj):
    """ Calculates all connected cells forming a group via Flood-Fill algorithm.
        Coordinates are accumulated as (row, col) tuples in 'conj'.
    :param tab: Matrix of board elements
    :param fil: Row coordinate
    :param col: Column coordinate
    :param elem: Target element to match
    :param conj: Set accumulating group cell coordinates
    """
    # Check board boundaries
    if fil < 0 or fil >= NUMFIL or col < 0 or col >= NUMCOL:
        return
    # Check element match
    if tab[fil][col] != elem:
        return
    # Avoid infinite recursion loop
    if (fil, col) in conj:
        return
    # Add coordinate to set
    conj.add((fil, col))
    # Recursively check adjacent cells
    grupo(tab, fil-1, col, elem, conj)
    grupo(tab, fil, col+1, elem, conj)
    grupo(tab, fil+1, col, elem, conj)
    grupo(tab, fil, col-1, elem, conj)


def region(tab, fil, col, conj):
    """ Calculates connected cells forming a region containing Bigfoots/Empty cells.
    :param tab: Matrix of board elements
    :param fil: Row coordinate
    :param col: Column coordinate
    :param conj: Set accumulating region coordinates
    :return: True if region connects to at least one empty cell
    """
    if fil < 0 or fil >= NUMFIL or col < 0 or col >= NUMCOL:
        return False
    if tab[fil][col] != Elem.BIGFOOT and tab[fil][col] != Elem.VACIO:
        return False
    if (fil, col) in conj:
        return False
    conj.add((fil, col))
    av1 = region(tab, fil-1, col, conj)
    av2 = region(tab, fil, col+1, conj)
    av3 = region(tab, fil+1, col, conj)
    av4 = region(tab, fil, col-1, conj)
    return tab[fil][col] == Elem.VACIO or av1 or av2 or av3 or av4


def colapso(tab, fil, col):
    """ Checks and collapses connected groups larger than threshold size.
    :param tab: Matrix of board elements
    :param fil: Row coordinate
    :param col: Column coordinate
    :return: True if collapse occurred
    """
    elem = tab[fil][col]
    elem_colap = TABLA[elem][4]  # Target evolved element (column 4 in TABLA)
    if elem_colap is None:
        return False
    conj = set()
    grupo(tab, fil, col, elem, conj)
    if len(conj) >= TAM_COLAPSO:
        # Clear matched group cells
        for coord in conj:
            i, j = coord[0], coord[1]
            tab[i][j] = Elem.VACIO
        # Place collapsed evolved element at placement coordinate
        tab[fil][col] = elem_colap
        return True
    else:
        return False


def inc_edad_bigfoots(tab, edad):
    """ Increments age counter for active Bigfoots.
    :param tab: Matrix of board elements
    :param edad: Matrix of Bigfoot ages
    """
    for i in range(NUMFIL):
        for j in range(NUMCOL):
            if tab[i][j] == Elem.BIGFOOT:
                edad[i][j] += 1


def encierro_bigfoots(tab):
    """ Detects enclosed Bigfoots with no escape path and turns them into Babies.
    :param tab: Matrix of board elements
    :return: Set of coordinates where new Babies were created
    """
    bebes = set()
    for i in range(NUMFIL):
        for j in range(NUMCOL):
            if tab[i][j] == Elem.BIGFOOT:
                conj = set()
                hay_vacio = region(tab, i, j, conj)
                if not hay_vacio:
                    # Bigfoots in enclosed region turn into Babies
                    for coord in conj:
                        bi, bj = coord[0], coord[1]
                        tab[bi][bj] = Elem.BEBE
                        bebes.add(coord)
    return bebes


def pos_max_edad(edad, coords):
    """ Finds position of oldest Baby/Bigfoot among given coordinates.
    :param edad: Matrix of Bigfoot ages
    :param coords: List of (row, col) coordinates
    :return: (row, col) tuple of oldest element
    """
    max_edad = -1
    max_fil, max_col = 0, 0
    for coord in coords:
        fil, col = coord[0], coord[1]
        if edad[fil][col] > max_edad:
            max_edad = edad[fil][col]
            max_fil, max_col = fil, col
    return max_fil, max_col


def colapso_bebes(tab, edad, bebes):
    """ Processes and collapses matching Baby groups.
    :param tab: Matrix of board elements
    :param edad: Matrix of Bigfoot ages
    :param bebes: Set of Baby coordinates
    """
    while len(bebes) > 0:
        bebe = bebes.pop()
        fil, col = bebe[0], bebe[1]
        conj = set()
        grupo(tab, fil, col, Elem.BEBE, conj)
        bebes = bebes - conj
        if len(conj) >= TAM_COLAPSO:
            # Determine placement cell based on oldest Baby
            fil, col = pos_max_edad(edad, list(conj))
            hay_colapso = True
            while hay_colapso:
                hay_colapso = colapso(tab, fil, col)


def mueve_bigfoots(tab, edad):
    """ Handles Bigfoot movement prioritization by age.
    :param tab: Matrix of board elements
    :param edad: Matrix of Bigfoot ages
    """
    bigfoots = []
    for i in range(NUMFIL):
        for j in range(NUMCOL):
            if tab[i][j] == Elem.BIGFOOT:
                bigfoots.append((edad[i][j], i, j))
    # Sort Bigfoots by age in descending order
    bigfoots.sort(reverse=True)
    
    for tup in bigfoots:
        e, i, j = tup[0], tup[1], tup[2]
        # Search adjacent empty cell and relocate
        if i > 0 and tab[i-1][j] == Elem.VACIO:
            tab[i-1][j] = Elem.BIGFOOT
            edad[i-1][j] = e
            tab[i][j] = Elem.VACIO if e <= EDAD_ESCOMBROS else Elem.ESCOMBRO
            edad[i][j] = 0
        elif j < NUMCOL-1 and tab[i][j+1] == Elem.VACIO:
            tab[i][j+1] = Elem.BIGFOOT
            edad[i][j+1] = e
            tab[i][j] = Elem.VACIO if e <= EDAD_ESCOMBROS else Elem.ESCOMBRO
            edad[i][j] = 0
        elif i < NUMFIL-1 and tab[i+1][j] == Elem.VACIO:
            tab[i+1][j] = Elem.BIGFOOT
            edad[i+1][j] = e
            tab[i][j] = Elem.VACIO if e <= EDAD_ESCOMBROS else Elem.ESCOMBRO
            edad[i][j] = 0
        elif j > 0 and tab[i][j-1] == Elem.VACIO:
            tab[i][j-1] = Elem.BIGFOOT
            edad[i][j-1] = e
            tab[i][j] = Elem.VACIO if e <= EDAD_ESCOMBROS else Elem.ESCOMBRO
            edad[i][j] = 0


def main():
    """ Main application entry point """
    print("SUBURBIOUS!")
    azar_tab = []
    azar_sec = []
    for elem in Elem:
        freq_tab = TABLA[elem][1]
        freq_sec = TABLA[elem][2]
        azar_tab.extend([elem] * freq_tab)
        azar_sec.extend([elem] * freq_sec)

    # Prompt file paths
    fich_tab = input("Board setup file path = ")
    if len(fich_tab) == 0:
        tab = crea_tablero_azar(azar_tab)
    else:
        tab = lee_fichero_tablero(fich_tab)
        
    fich_sec = input("Element sequence file path = ")
    if len(fich_sec) == 0:
        secuencia = []
    else:
        secuencia = lee_fichero_secuencia(fich_sec)

    # Initialize game variables
    turno = 1
    puntos = calcula_puntos(tab)
    almacen = Elem.VACIO
    actual = elige_actual(secuencia, azar_sec)
    edad = []
    for i in range(NUMFIL):
        edad.append([0]*NUMCOL)

    # Game loop
    fin = False
    while not fin:
        imprimir(tab, edad, turno, puntos, almacen, actual)
        mov = input("Move to cell (e.g. A1, * to swap warehouse): ")
        while not jugada_correcta(tab, mov, actual):
            print("\nInvalid move!\n")
            mov = input("Move to cell (e.g. A1, * to swap warehouse): ")
            
        if mov == '*':
            # Swap with warehouse
            actual, almacen = almacen, actual
            if actual == Elem.VACIO:
                actual = elige_actual(secuencia, azar_sec)
        else:
            jugar(tab, mov, edad, actual)
            turno += 1
            actual = elige_actual(secuencia, azar_sec)
            puntos = calcula_puntos(tab)
            fin = fin_partida(tab)

    # Game over
    imprimir(tab, edad, turno, puntos, almacen, actual)
    print("Game over!")


if __name__ == '__main__':
    main()