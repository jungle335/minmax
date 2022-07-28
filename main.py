import random
import pygame
import copy
import ctypes
import easygui
from time import time
from statistics import median

black, white, red, blue = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)
dim, offset = 800, 7
dRow, dCol = [-1, 0, 1, 0], [0, 1, 0, -1]
liber, otrava, cul = 0, 2, [1, -1]
yes, adancime_max = 6, -1


def genereaza_tabla(nr_otr, n, m):
    """

    Se creeaza doua liste, una ce contine indici generati aleator pentru linie, cealalta contine indici generati
    aleator pentru coloana. Se parcurg simultan cele doua liste si se marcheaza in matrice elementul otrava (2) pe
    pozitiile date de cei doi indici.

    Parameters
    ----------
    nr_otr: int
    n: int
    m: int

    Returns
    -------
    list[list]
    """
    ind_lin, ind_col = random.sample(range(0, n - 1), nr_otr), random.sample(range(0, m - 1), nr_otr)
    tabla = [[liber] * m for _ in range(n)]
    i, j = 0, 0
    while i < nr_otr and j < nr_otr:
        tabla[ind_lin[i]][ind_col[j]] = otrava
        i, j = i + 1, j + 1
    return tabla


def obtine_dreptunghiuri(tabla, cul_joc):
    def conexiune(matrice):
        def BFS(start):
            def valid(i, j):
                """

                Pentru o pereche de coordonate, se verifica apartenenta la matrice, valoarea din tabla sa fie o pozitie libera
                sau o pozitie otravita si sa nu fi fost accesata inainte.

                Parameters
                ----------
                i: int
                j: int

                Returns
                -------
                bool
                """
                return 0 <= i < len(matrice) and 0 <= j < len(matrice[0]) and matrice[i][j] in [0, 2] and not \
                    viz[i][j]

            """
            Fiecare nod nevizitat se adauga intr-o coada impreuna cu vecinii lui (daca acestia reprezinta o mutare 
            valida). Se elimina nodul expandat, algoritmul continuand cu vecinii acestuia.
            
            Parameters
            ----------
            start: tuple[int, int]
                
            Returns
            -------
            list
            
            """

            viz = [[0] * len(tabla[0]) for _ in range(len(tabla))]
            q, all = [(start[0], start[1])], []
            while len(q) > 0:
                cell = q.pop(0)
                x, y = cell[0], cell[1]
                viz[x][y] = 1
                all.append(cell)
                for i in range(4):
                    adjx, adjy = x + dRow[i], y + dCol[i]
                    if valid(adjx, adjy):
                        q.append((adjx, adjy))
                        viz[adjx][adjy] = 1
            return all

        """
        
        Se creeaza o lista cu toate perechille de coordonate care reprezinta pozitii libere sau otravite.
        Se aplica BFS din primul punct din aceasta lista si se verifica daca se poate ajunge la celelalte.
        
        Parameters
        ----------
        matrice: list[list]
        
        Returns
        -------
        bool
        """

        to_check = [(i, j) for i in range(len(matrice)) for j in range(len(matrice[0])) if
                    matrice[i][j] in [liber, otrava]]
        rez = BFS(to_check[0])
        for elem in to_check:
            if elem not in rez:
                return False
        return True

    """
    
    Se creeaza o lista cu toate pozitiile libere din tabla de joc. Se parcurg coordonatele si se creeaza dreptunghiurile 
    care contin pozitiile libere pornind din fiecare coordonata. Se coloreaza dreptunghiul si se adauga in lista mutarilor 
    posibile (Orice dreptunghi este descris prin coltul din stanga sus si coltul din dreapta jos).
    
    Parameters
    ----------
    tabla: list[list]
    cul_joc: int
    
    Returns
    -------
    dict
    """

    mutari, mat = {}, [(i, j) for i in range(len(tabla)) for j in range(len(tabla[0])) if tabla[i][j] == 0]
    for i in range(len(mat)):
        xx, xy = mat[i][0], mat[i][1]
        for j in range(i, len(mat)):
            yy, yz = mat[j][0], mat[j][1]
            if {tabla[ii][jj] for ii in range(xx, yy + 1) for jj in range(xy, yz + 1)} == {0}:
                copie_joc = copy.deepcopy(tabla)
                for z in range(xx, yy + 1):
                    copie_joc[z][xy:(yz + 1)] = [cul_joc] * len(copie_joc[z][xy:(yz + 1)])
                if conexiune(copie_joc):
                    mutari[(xx, xy, yy, yz)] = Joc(copie_joc)
    return mutari


def estimeaza_scor(tabla, jucator):
    """
        Se verifica cate pozitii libere exista. Pentru jucatorul MAX, se returneaza valoarea ca atare,
        iar pentru jucatorul MIN se returneaza valoarea opusa.

        Parameters
        ----------
        tabla: list[list]
        jucator: int

        Returns
        -------
        int
        """
    eval = len([tabla[i][j] for i in range(len(tabla)) for j in range(len(tabla[0])) if tabla[i][j] != liber])
    if jucator == -1:
        return eval5
    return -eval


def estimeaza_scor1(tabla, jucator):
    """
    Se verifica cate dreptunghiuri diferite poate forma jucatorul curent. Pentru jucatorul MAX, se returneaza valoarea ca atare,
    iar pentru jucatorul MIN se returneaza valoarea opusa.

    Parameters
    ----------
    tabla: list[list]
    jucator: int

    Returns
    -------
    int
    """
    eval = len(obtine_dreptunghiuri(tabla, jucator).values())
    if jucator == -1:
        return eval
    return -eval


def calculeaza(lst, keyword):
    print("Informatii despre mutarile calculatorului")
    print(f"{keyword} minim: ", min(lst))
    print(f"{keyword} maxim: ", max(lst))
    print(f"{keyword} mediu: ", sum(lst) / len(lst))
    print("Mediana: ", median(lst))
    print()


class Joc:
    def __init__(self, tabla):
        """
        Primeste configuratia initiala a jocului sub forma de matrice

        Parameters
        ----------
        tabla: list[list]
        """
        self.matrice = tabla

    def initiaza(self, user_flag):
        """
        
        User_flag reprezinta decizia jucatorului in ceea ce priveste algoritmul pe care sa-l aplice calculatorul
        (minmax sau alpha-beta).
        
        Parameters
        ----------
        user_flag: bool
        """

        def deseneaza_tabla(tabla):
            """
            
            Se foloseste culoarea negru pentru fundal. Se parcurge tabla de joc si se coloreaza in functie de valoarea
            elementelor din matrice. Daca elementul este 1 (simbolul jucatorului), se alege culoarea rosu. Daca elementul
            este -1 (simbolul calculatorului), se alege albastru, iar daca elementul este 2 (simbolul otravei), se alege
            negru. Programul ruleaza la infinit verificand doua evenimente (de inchidere a programului si cel de miscare
            al cursorului). La miscarea cursorului, se verifica daca mutarea jucatorului este valida. Calculatorul aplica
            unul dintre algoritmi (minmax / alpha-beta) pentru a-si realiza mutarea. Starea finala se verifica prin faptul
            ca unul dintre jucatori ramane fara mutari (lungimea dictionarului ce contine mutarile posibile este 0). De
            asemenea, tabla de joc are o dimensiune diferita in functie de configuratie.
            
            Parameters
            ----------
            tabla: list[list]
            """
            win.fill(black)
            for i in range(len(tabla[0])):
                for j in range(len(tabla)):
                    if tabla[j][i] == 1:
                        pygame.draw.rect(win, red, (i * unit + offset, j * unit + offset, unit - offset, unit - offset))
                    elif tabla[j][i] == -1:
                        pygame.draw.rect(win, blue,
                                         (i * unit + offset, j * unit + offset, unit - offset, unit - offset))
                    elif tabla[j][i] == otrava:
                        pygame.draw.rect(win, black,
                                         (i * unit + offset, j * unit + offset, unit - offset, unit - offset))
                    else:
                        pygame.draw.rect(win, white,
                                         (i * unit + offset, j * unit + offset, unit - offset, unit - offset))

        pygame.display.set_caption('Tudose Mihai-Cristian Hap! (Chomp!)')
        unit = dim // max(len(self.matrice), len(self.matrice[0]))
        win = pygame.display.set_mode((unit * len(self.matrice[0]) + offset, unit * len(self.matrice) + offset))
        joc, juc_curent, choice, start, final = self.matrice, 1, (-1, -1), int(round(time() * 1000)), 0
        print("Mutarea jucatorului")
        mutari, nr_mut_j, nr_mut_c, noduri, timpi = obtine_dreptunghiuri(joc, juc_curent), 0, 0, [], []
        deseneaza_tabla(joc)
        pygame.display.update()

        while True:
            ctypes.windll.user32.MessageBoxW(1, "Ce algoritm doriti sa utilizati?", "Message", 1)

            if not mutari:
                ctypes.windll.user32.MessageBoxW(0,
                                                 f"Jocul s-a terminat. A castigat {'Rosu' if juc_curent == -1 else 'Albastru'}",
                                                 "Message", 0)
                final = int(round(time() * 1000))
                print("\nProgramul a rulat ", final - start, " milisecunde")
                print("Jucatorul a mutat de", nr_mut_j, "ori\nCalculatorul a mutat de", nr_mut_c, "ori")
                print()
                calculeaza(timpi, "Timp")
                calculeaza(noduri, "Numarul")
                pygame.quit()
                exit()
            if juc_curent == -1:
                t_inainte = int(round(time() * 1000))
                if user_flag:
                    joc, nrn = minmax_parinte(joc.matrice, adancime_max, juc_curent)
                else:
                    joc, nrn = alpha_beta_parinte(joc.matrice, adancime_max, float("-inf"), float("inf"), juc_curent)

                noduri.append(nrn)
                if joc[1] is None:
                    ctypes.windll.user32.MessageBoxW(0,
                                                     f"Jocul s-a terminat. A castigat {'Rosu' if juc_curent == -1 else 'Albastru'}",
                                                     "Message", 0)
                    final = int(round(time() * 1000))
                    print("Programul a rulat ", final - start, " milisecunde")
                    print("Jucatorul a mutat de", nr_mut_j, "ori\nCalculatorul a mutat de", nr_mut_c, "ori")
                    print()
                    calculeaza(timpi, "Timp")
                    calculeaza(noduri, "Numarul")
                    pygame.quit()
                    exit()

                print("Estimarea nodului radacina este", joc[0])
                print(Joc(joc[1]))
                juc_curent = 1
                mutari = obtine_dreptunghiuri(joc[1], juc_curent)
                deseneaza_tabla(joc[1])
                pygame.display.update()
                t_dupa, nr_mut_c = int(round(time() * 1000)), nr_mut_c + 1
                rulare = t_dupa - t_inainte
                timpi.append(rulare)
                print("Mutarea calculatorului a durat " + str(rulare) + " milisecunde")
                print("Mutarea jucatorului")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    final = int(round(time() * 1000))
                    print("\nProgramul a rulat ", final - start, " milisecunde")
                    print("Jucatorul a mutat de", nr_mut_j, "ori\nCalculatorul a mutat de", nr_mut_c, "ori")
                    print()
                    calculeaza(timpi, "Timp")
                    calculeaza(noduri, "Numarul")
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    t_inainte = int(round(time() * 1000))
                    pos = pygame.mouse.get_pos()
                    cursor = (pos[1] // unit, pos[0] // unit)
                    if tuple([*choice, *cursor]) in mutari or tuple([*cursor, *choice]) in mutari:
                        if choice[0] > cursor[0] or choice[1] > cursor[1]:
                            choice, cursor = cursor, choice
                        joc = mutari[(choice[0], choice[1], cursor[0], cursor[1])]
                        juc_curent = -1
                        if joc is None:
                            ctypes.windll.user32.MessageBoxW(0,
                                                             f"Jocul s-a terminat. A castigat {'Rosu' if juc_curent == -1 else 'Albastru'}",
                                                             "Message", 0)
                            final = int(round(time() * 1000))
                            print("\nProgramul a rulat ", final - start, " milisecunde")
                            print("Jucatorul a mutat de", nr_mut_j, "ori\nCalculatorul a mutat de", nr_mut_c, "ori")
                            print()
                            calculeaza(timpi, "Timp")
                            calculeaza(noduri, "Numarul")
                            pygame.quit()
                            exit()

                        print(joc)
                        mutari, choice = obtine_dreptunghiuri(joc.matrice, juc_curent), (-1, -1)
                        deseneaza_tabla(joc.matrice)
                        pygame.display.update()
                        t_dupa, nr_mut_j = int(round(time() * 1000)), nr_mut_j + 1
                        rulare = t_dupa - t_inainte
                        timpi.append(rulare)
                        print("Mutarea jucatorului a durat " + str(rulare) + " milisecunde")
                        print("Mutarea calculatorului")
                    else:
                        choice = cursor

    def __str__(self):
        """
        Se parcurge matricea si se stocheaza intr-un string. Cu ajutorul unui dictionar, se memoreaza simbolurile
        jocului (-1 -> calculator, 1 -> jucator, . -> pozitie libera, 2 -> b).

        Returns
        -------
        str
        """
        sir, cul = "", {-1: '\033[94ma\033[0m', 0: '.', 1: '\033[91mr\033[0m', 2: 'b'}
        for i in range(len(self.matrice)):
            for j in range(len(self.matrice[0])):
                sir += cul[self.matrice[i][j]] + ' '
            sir += '\n'
        return sir


def minmax_parinte(tabla, adancime, jucator):
    def minmax(tabla, adancime, jucator):
        if adancime == 0:
            return estimeaza_scor(tabla, jucator), None

        nonlocal nr_noduri
        nr_noduri += 1
        best_move, configuratii = None, obtine_dreptunghiuri(tabla, jucator).values()
        if jucator == -1:
            maxim = float("-inf")
            for conf in configuratii:
                eval = minmax(conf.matrice, adancime - 1, -jucator)[0]
                if eval > maxim:
                    best_move, maxim = conf.matrice, eval

            return maxim, best_move

        minim = float("inf")
        for conf in configuratii:
            eval = minmax(conf.matrice, adancime - 1, -jucator)[0]
            if eval < minim:
                best_move, minim = conf.matrice, eval

        return minim, best_move

    nr_noduri = 0
    return minmax(tabla, adancime, jucator), nr_noduri


def alpha_beta_parinte(tabla, adancime, alfa, beta, jucator):
    def alpha_beta(tabla, adancime, alfa, beta, jucator):
        if adancime == 0:
            return estimeaza_scor(tabla, jucator), None

        nonlocal nr_noduri
        nr_noduri += 1
        best_move, configuratii = None, obtine_dreptunghiuri(tabla, jucator).values()
        if jucator == -1:
            maxim = float("-inf")
            for conf in configuratii:
                eval = alpha_beta(conf.matrice, adancime - 1, alfa, beta, -jucator)[0]
                if eval > maxim:
                    best_move, maxim = conf.matrice, eval
                alfa = max(alfa, maxim)
                if alfa >= beta:
                    break
            return maxim, best_move

        minim = float("inf")
        for conf in configuratii:
            eval = alpha_beta(conf.matrice, adancime - 1, alfa, beta, -jucator)[0]
            if eval < minim:
                best_move, minim = conf.matrice, eval
            beta = min(beta, minim)
            if alfa >= beta:
                break

        return minim, best_move

    nr_noduri = 0
    return alpha_beta(tabla, adancime, alfa, beta, jucator), nr_noduri


if __name__ == '__main__':
    while True:
        ctypes.windll.user32.MessageBoxW(0, "Introduceti dimensiunile tablei", "Message")
        nrl, nrc = int(easygui.enterbox("Numarul de linii")), int(easygui.enterbox("Numarul de coloane"))
        nr_otr = int(easygui.enterbox("Numarul de patrate otravite"))
        ctypes.windll.user32.MessageBoxW(0, "Introduceti nivelul de dificultate al jocului: usor, mediu sau greu",
                                         "Message")
        rez = easygui.enterbox("Nivelul de dificultate")
        if rez == "usor":
            adancime_max = 2
        elif rez == "mediu":
            adancime_max = 3
        elif rez == "greu":
            adancime_max = 4
        else:
            ctypes.windll.user32.MessageBoxW(0, "Va rugam sa setati nivelul jocului!!!", "Message")
            continue
        rezM = ctypes.windll.user32.MessageBoxW(0, "Doriti sa utilizati algoritmul MinMax?", "Message", 4)
        if rezM == yes:
            Joc(genereaza_tabla(nr_otr, nrl, nrc)).initiaza(True)
        else:
            rezAB = ctypes.windll.user32.MessageBoxW(0, "Doriti sa utilizati algoritmul Alpha-Beta?", "Message", 4)
            if rezAB == yes:
                Joc(genereaza_tabla(nr_otr, nrl, nrc)).initiaza(False)
            else:
                ctypes.windll.user32.MessageBoxW(0, "Trebuie sa alegi un algoritm!!!", "Message")
