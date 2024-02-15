# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 20:56:02 2022

@author: Victor Laügt
"""
from pathlib import Path
from tkinter import Tk, Canvas, Frame, Radiobutton, Button, Entry, Label, IntVar,\
    ALL, LEFT
import argparse

# from MyTools.debug import DebugSpace
# dbg = DebugSpace()


class SpeedControl(Frame):
    """Zone pour contrôler le temps d'attente entre le calcul de chaque étape
    de l'animation
    """
    def __init__(self, master, univers, pad):
        super().__init__(master)
        # attribut
        self.univers = univers
        self.entry = Entry(self)

        # pack items
        pack_align(
            [Label(self, text="Temps d'attente minumum (ms):"),
             self.entry,
             Button(self, text='Valider', command=self.set_speed)],
            side = LEFT,
            padx = pad
            )

    def set_speed(self):
        """Change le temps d'attente entre chaque étape de la simulation"""
        new_time = int(self.entry.get())
        if new_time > 0:
            self.univers.time = new_time



class Editor(Frame):
    """Barre d'outils qui contient des boutons permettant de sélectionner un
    outil d'édition à utiliser pour modifier l'univers actuel
    """
    def __init__(self, master, univers, pad):
        super().__init__(master)

        # attributs
        self.edit_tool = self.tools[0]
        self.selected = IntVar(value=0)
        self.univers = univers

        # pack items
        pack_align(
            [Label(self, text='Editeur:'),
             Radiobutton(self, text='Inverser cellule', variable=self.selected,
                         value=0, command=self.select_tool, indicatoron=0),
             Radiobutton(self, text='Planeur', variable=self.selected,
                         value=1, command=self.select_tool, indicatoron=0),
             Radiobutton(self, text='Canon à planeurs', variable=self.selected,
                         value=2, command=self.select_tool, indicatoron=0),
             Radiobutton(self, text="Feu d'articfice", variable=self.selected,
                         value=3, command=self.select_tool, indicatoron=0),
             Button(self, text='Effacer tout', command=self.univers.clear_all)],
            side=LEFT, padx=pad, pady=pad/2)


    def select_tool(self):
        """Sélectionne un outil d'édition"""
        self.edit_tool = self.tools[self.selected.get()]


    def use(self, i, j):
        """Utilise l'outil d'édition selectionné"""
        self.edit_tool(self, i, j)


    def draw(self, i, j, config):
        """Construit la configuration de cellules config à la position (i, j)"""
        n, p = self.univers.n, self.univers.p
        for k, l in config:
            self.univers.birth(((k+i)%n)*p + (l+j)%p)


    # --- editor tools
    def switch_cell(self, i, j):
        """Inverse l'état de la cellule à la position (i, j)"""
        t = i*(self.univers.p) + j
        if self.univers.alive[t]:
            self.univers.death(t)
        else:
            self.univers.birth(t)

    def plane(self, i, j):
        """Construit un planeur à la position (i, j)"""
        self.draw(i, j, self.plane_config)

    def canon(self, i, j):
        """Construit un canon à planeurs à la position (i, j)"""
        self.draw(i, j, self.canon_config)

    def firework(self, i, j):
        """Contsruit un feu d'artifice à la position (i, j)"""
        self.draw(i, j, self.firework_config)

    tools = [switch_cell, plane, canon, firework]

    plane_config = ((0, 2), (1, 0), (1, 2), (2, 1), (2, 2))

    canon_config = (
        (0, 4), (0, 5), (1, 4), (1, 5), (10, 4), (10, 5), (10, 6), (11, 3),
        (11, 7), (12, 2), (12, 8), (13, 2), (13, 8), (14, 5), (15, 3), (15, 7),
        (16, 4), (16, 5), (16, 6), (17, 5), (20, 2), (20, 3), (20, 4), (21, 2),
        (21, 3), (21, 4), (22, 1), (22, 5), (24, 0), (24, 1), (24, 5), (24, 6),
        (34, 2), (34, 3), (35, 2), (35, 3)
        )

    firework_config = (
        (0, 2), (1, 0), (1, 1), (1, 3), (1, 4), (2, 1), (2, 3), (3, 0), (3, 1),
        (3, 3), (3, 4)
        )



class SimulControl(Frame):
    """Barre d'outils qui contient les boutons:
        Simuler/Pause:
            Met en pause ou de reprend la simulation
        Sauvegarder:
            Sauvegarde l'état actuel de l'univers dans un fichier .txt
        Charger:
            Ecrase l'univers actuerl en restaurant la sauvegarde
    """
    def __init__(self, master, univers, save_file_path, pad):
        super().__init__(master)

        # attributs
        self.pause_button = Radiobutton(
            self,
            variable=IntVar(),
            value=0,
            indicatoron=0,
            command=self.switch_play,
            text='Simuler/Pause'
            )
        self.load_save_button = Button(
            self,
            text='Charger',
            command=self.load
            )
        self.univers = univers
        self.save_file_path = save_file_path

        # pack items
        pack_align(
            [Label(self, text='Simulation:'),
             self.pause_button,
             Button(self, text='Sauvegarder', command=self.save),
             self.load_save_button],
            side=LEFT,
            padx=pad
            )

        # init attributes
        self.pause_button.deselect()
        if not self.saved_data():
            self.load_save_button.config(state='disabled')


    def switch_play(self):
        """Démarre ou met en pause la simulation"""
        self.univers.play = not self.univers.play
        if self.univers.play:
            # reprise de la simulation
            self.pause_button.deselect()
            self.univers.init_display()
            self.univers.evolve()
        else:
            # mise en pause
            self.pause_button.select()
            self.univers.show_cell_edges()


    # --- gestion des sauvegardes
    def save(self):
        """Ecrase le fichier GameOfLifeSave.txt et écrit dedans l'état actuel
        de l'univers
        """
        n, p, size = self.univers.n, self.univers.p, self.univers.size
        with self.save_file_path.open(mode='w') as file:
            file.write(f'{n} {p} '+' '.join(str(t) for t in range(size)
                                            if self.univers.alive[t]))
        self.load_save_button.config(state='normal')


    def saved_data(self):
        """Renvoi l'univers contenu dans le fichier de sauvegarde s'il est de
        la même taille et forme que l'univers actuel de la simulation, sinon
        renvoi None
        """
        if self.save_file_path.is_file():
            with self.save_file_path.open(mode='r') as file:
                data = file.read().split()
                if len(data) >= 3:
                    n, p, *saved_univers = data
                    if (int(n), int(p)) == (self.univers.n, self.univers.p):
                        return saved_univers


    def load(self):
        """Charge la sauvegarde contenue dans le fichier GameOfLife.txt"""
        saved_univers = self.saved_data()
        if saved_univers:
            self.univers.clear_all()
            for t in saved_univers:
                self.univers.birth(int(t))



class BoundaryConditionsControl(Frame):
    """Zone pour choisir les conditions aux limites de l'univers"""
    def __init__(self, master, univers, pad):
        super().__init__(master)
        self.univers = univers
        self.boundary_type = IntVar(value=0)
        self.neighborhood_builder = [self.univers.periodic_univers_neighborhood,
                                     self.univers.finite_univers_neighborhood]

        pack_align(
            [Label(self, text='Conditions aux limites:'),
             Radiobutton(self,
                         variable=self.boundary_type,
                         value=0,
                         indicatoron=0,
                         command=self.switch_boundary_type,
                         text='univers periodique'),
             Radiobutton(self,
                         variable=self.boundary_type,
                         value=1,
                         indicatoron=0,
                         command=self.switch_boundary_type,
                         text='univers fini')],
            side=LEFT, padx=pad)


    def switch_boundary_type(self):
        """Change les conditions aux limites de l'univers"""
        boundary_type = self.boundary_type.get()
        self.univers.init_neighborhoods(self.neighborhood_builder[boundary_type])


class Univers(Canvas):
    """Implémente l'univers de la simulation

    Attributs
    =================
    n:
        nombre de lignes dans l'univers
    p:
        nombres de colonnes dans l'univers
    size:
        nombres de cellules dans l'univers
    ----------
    alive:
        alive[t] == True -> La cellule d'indice t est vivante
        alive[t] == False -> La cellule d'indice t est morte
    neighborhood:
        neighborhood[t] == indices des cellules voisines de la cellule
        d'indice t
    alive_neighbors:
        alive_neighbors[t] == nombre de voisins vivants de la cellule
        d'indice t
    cells_repr:
        liste qui contient les identifiants des carrés représentant chacune des
        cellules de l'univers
    time:
        nombre de millisecondes entre l'affichage de deux étapes successives de
        la simulation
    play:
        play == True -> Simulation en cours
        play == False -> Simulation en pause
    ----------
    c:
        longueur d'un côté d'une cellule
    h:
        hauteur de la représentation graphique de l'univers
    w:
        largeur de la représentation graphique de l'univers
    ALIVE_COLOR:
        couleur des cellules vivantes
    DEAD_COLOR:
        couleur des cellules mortes
    """
    def __init__(self, master, n, p, c):
        # dimensionnement de l'univers
        self.n = n
        self.p = n
        self.size = n*p

        # paramètres graphiques
        self.c = c
        self.h = n*c
        self.w = p*c
        self.ALIVE_COLOR = 'white'
        self.DEAD_COLOR = 'black'
        super().__init__(width=self.w, height=self.h, bg=self.DEAD_COLOR)

        # variables de la simulation
        self.alive = [False]*(p*n)
        self.init_neighborhoods(self.periodic_univers_neighborhood)
        self.alive_neighbors = [0]*(p*n)
        self.cells_repr = [None]*(p*n)
        self.time = 1
        self.play = False

        # action du clique gauche de l'utilisateur
        self.bind('<Button-1>', self.click)


    def init_neighborhoods(self, neighborhood_builder):
        self.neighborhood = [neighborhood_builder(i, j) for i in range(self.n)
                                                        for j in range(self.p)]

    def init_display(self):
        """Efface entièrement la grille de cellules puis la reconstruit pour
        qu'elle représente l'état actuel de la simulation
        """
        n, p, c = self.n, self.p, self.c
        self.delete(ALL)
        y1, y2 = 0, c
        for i in range(n):
            x1, x2 = 0, c
            for j in range(p):
                t = i*p + j
                if self.alive[t]:
                    cell = self.create_rectangle(x1, y1, x2, y2,
                                                 fill=self.ALIVE_COLOR)
                else:
                    cell = self.create_rectangle(x1, y1, x2, y2,
                                                 fill=self.DEAD_COLOR)
                self.cells_repr[t] = cell
                x1, x2 = x2, x2+c
            y1, y2 = y2, y2+c


    def click(self, event):
        c = self.c
        self.master.editor.use((event.y-(event.y%c)) // c,
                               (event.x-(event.x%c)) // c)


    def periodic_univers_neighborhood(self, i:int, j:int):
        """Renvoie les indices des 8 cellules voisines de la cellule (i, j)
        dans l'univers si celui-ci est infini et periodique.
        """
        n, p = self.n, self.p
        up = (i-1)%n
        down = (i+1)%n
        left = (j-1)%p
        right = (j+1)%p
        return ((up*p + left)  , (up*p + j)  , (up*p + right),
                (i*p + left)   ,               (i*p + right),
                (down*p + left), (down*p + j), (down*p + right))


    def finite_univers_neighborhood(self, i:int, j:int):
        """Renvoie les indices des 8 cellules voisines de la cellule (i, j)
        dans l'univers si celui-ci est fini.
        """
        n, p = self.n, self.p
        up = i-1
        down = i+1
        left = j-1
        right = j+1
        result = []
        if up >= 0:
            result.append(up*p + j)
            if left >= 0:
                result.append(up*p + left)
            if right < n:
                result.append(up*p + right)
        if left >= 0:
            result.append(i*p + left)
        if right < n:
            result.append(i*p + right)
        if down < n:
            result.append(down*p + j)
            if left >= 0:
                result.append(down*p + left)
            if right < n:
                result.append(down*p + right)
        return result


    def show_cell_edges(self):
        """Dessine les bordures des cases de la grille de cellules"""
        # bordures horizontales
        y = 0
        for i in range(self.n):
            self.create_line(0, y, self.w, y, width=1, fill=self.ALIVE_COLOR)
            y += self.c
        # bordures verticales
        x = 0
        for i in range(self.p):
            self.create_line(x, 0, x, self.h, width=1, fill=self.ALIVE_COLOR)
            x += self.c


    def clear_all(self):
        """Rend morte toute les cellules de l'univers"""
        n, p = self.n, self.p
        for i in range(n):
            for j in range(p):
                t = i*p + j
                self.alive[t] = False
                self.alive_neighbors[t] = 0
                self.itemconfig(self.cells_repr[t], fill=self.DEAD_COLOR)


    def birth(self, t:int):
        """Rend (ou laisse) vivante la cellule d'indice t dans l'univers et affiche
        sa représentation graphique
        """
        alive, alive_neighbors = self.alive, self.alive_neighbors
        if not alive[t]:
            alive[t] = True
            for u in self.neighborhood[t]:
                alive_neighbors[u] += 1
            self.itemconfig(self.cells_repr[t], fill=self.ALIVE_COLOR)


    def death(self, t:int):
        """Rend (ou laisse) morte la cellule d'indice t dans l'univers et efface sa
        représentation graphique
        """
        alive, alive_neighbors = self.alive, self.alive_neighbors
        if alive[t]:
            alive[t] = False
            for u in self.neighborhood[t]:
                alive_neighbors[u] -= 1
            self.itemconfig(self.cells_repr[t], fill=self.DEAD_COLOR)


    def evolve(self):
        """Fait évoluer (in place) l'univers de la simulation selon les règles du
        jeu de la vie:
        - Une cellule vivante meurt si elle possède 1, 4, 5, 6, 7, ou 8 voisins
        vivants.
        - Une cellule vivante survie si elle est entourée de 2 ou 3 cellules
        vivantes.
        - Une cellule morte devient vivante si elle est entourée d'exactement
        3 cellules vivantes.

        Implémentation:
        2 voisins vivants => pas de changement d'état de la cellule
        3 voisins vivants => naissance de la cellule
        autre situation   => mort de la cellule
        """
        alive_neighbors = self.alive_neighbors

        # calcule les naissances et les morts pour passer à l'étape suivante
        birth_list, death_list = [], []
        for t in range(self.size):
            count = alive_neighbors[t]
            if count == 3:
                birth_list.append(t)
            elif count == 2:
                pass
            else:
                death_list.append(t)

        # passe à l'étape suivante en effectuant les naissances et morts calculées
        for t in birth_list:
            self.birth(t)
        for t in death_list:
            self.death(t)

        # planifie la prochaine évolution
        if self.play:
            window.after(self.time, self.evolve)



class MainWindow(Tk):
    """Fenêtre principale de l'application"""
    def __init__(self, n, p, c, pad):
        super().__init__()

        # zone où l'univers de la simulation s'affiche
        self.univers = Univers(self, n, p, c)

        # zone pour changer la vitesse de l'animation
        self.speed_control = SpeedControl(self, self.univers, pad)

        # zone pour contrôler la simulation
        self.simul_control = SimulControl(self,
                                          self.univers,
                                          Path('GameOfLifeSave.txt'),
                                          pad)

        # zone pour éditer l'univers
        self.editor = Editor(self, self.univers, pad)

        # zone pour controler les conditions aux limites
        self.boundary_control = BoundaryConditionsControl(self, self.univers, pad)

        # pack items
        self.speed_control.grid(row=0, column=0, pady=pad, sticky='W')
        self.univers.grid(row=1, column=0, padx=pad, pady=pad, sticky='W')
        self.simul_control.grid(row=2, column=0, pady=pad, sticky='W')
        self.editor.grid(row=3, column=0, pady=pad, sticky='W')
        self.boundary_control.grid(row=4, column=0, pady=pad, sticky='W')

        # Contrôles au clavier
        self.bind('<KeyPress-q>', lambda _: self.destroy())
        self.bind('<Return>', lambda _: self.simul_control.switch_play())

        self.univers.init_display()
        self.univers.show_cell_edges()



def pack_align(items, *, side, **kwargs):
    for can in items:
        can.pack(side=side, **kwargs)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('height', type=int, default=80, nargs='?',
                        help="Nombre de lignes de l'univers (80 par défaut)")
    parser.add_argument('width', type=int, default=80, nargs='?',
                        help="Nombre de colonnes de l'univers (80 par défaut)")
    parser.add_argument('-c', '--cell-size', type=int, default=10,
                        help=("Longueur du côté d'une cellule de l'univers "
                              "(10 par défaut, à adapter selon le système d'"
                              "affichage)"))
    args = parser.parse_args()

    window = MainWindow(args.height, args.width, args.cell_size, args.cell_size/3)
    window.mainloop()
