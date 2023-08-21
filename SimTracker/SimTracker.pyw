#!/bin/python

from tkinter import *
from tkinter.ttk import *
import os, xml.etree.ElementTree, sys, logging
from getpass import getuser
from math import log


def dbpf_decompress(n):
    x = b""
    index = 9
    while index < len(n):
        if n[index] == 252:
            break
        elif n[index] < 128:
            command = n[index : index + 2]
            numplaintext = command[0] & 3
            numtocopy = ((command[0] & 28) >> 2) + 3
            copyoffset = ((command[0] & 96) << 3) + command[1] + 1
            index += 2
        elif n[index] < 192:
            command = n[index : index + 3]
            numplaintext = ((command[1] & 192) >> 6) & 3
            numtocopy = (command[0] & 63) + 4
            copyoffset = ((command[1] & 63) << 8) + command[2] + 1
            index += 3
        elif n[index] < 224:
            command = n[index : index + 4]
            numplaintext = command[0] & 3
            numtocopy = ((command[0] & 12) << 6) + command[3] + 5
            copyoffset = ((command[0] & 16) << 12) + (command[1] << 8) + command[2] + 1
            index += 4
        elif n[index] < 252:
            command = n[index]
            numplaintext = ((command & 31) + 1) << 2
            numtocopy = 0
            copyoffset = 0
            index += 1
        else:
            command = n[index]
            numplaintext = command & 3
            numtocopy = 0
            copyoffset = 0
            index += 1
        while numplaintext > 0:
            x += bytes({n[index]})
            index += 1
            numplaintext -= 1
        while numtocopy > 0:
            x += bytes({x[-copyoffset]})
            numtocopy -= 1
    return x


class Sim:
    def __init__(self, resource):
        self.firstname, self.lastname = "Unknown", "Unknown"
        self.bio = ""
        self.skin1, self.skin2, self.skin3, self.skin4 = "", "", "", ""
        self.hair1, self.hair2, self.hair, self.eyes1, self.eyes2 = "", "", "", "", ""
        self.p_nice = int.from_bytes(resource[16:18], byteorder="little") // 100
        self.p_active = int.from_bytes(resource[18:20], byteorder="little") // 100
        self.p_playful = int.from_bytes(resource[22:24], byteorder="little") // 100
        self.p_outgoing = int.from_bytes(resource[24:26], byteorder="little") // 100
        self.p_neat = int.from_bytes(resource[26:28], byteorder="little") // 100
        self.s_cleaning = int.from_bytes(resource[30:32], byteorder="little") // 100
        self.s_cooking = int.from_bytes(resource[32:34], byteorder="little") // 100
        self.s_charisma = int.from_bytes(resource[34:36], byteorder="little") // 100
        self.s_mechanical = int.from_bytes(resource[36:38], byteorder="little") // 100
        self.s_creativity = int.from_bytes(resource[42:44], byteorder="little") // 100
        self.s_body = int.from_bytes(resource[46:48], byteorder="little") // 100
        self.s_logic = int.from_bytes(resource[48:50], byteorder="little") // 100
        m = int.from_bytes(resource[56:58], byteorder="little")
        if m > 32767:
            m = -65535 + m
        f = int.from_bytes(resource[58:60], byteorder="little")
        if f > 32767:
            f = -65536 + f
        if m > 0:
            if f > 0:
                self.sexuality = "Bi"
            else:
                self.sexuality = "M"
        elif f > 0:
            self.sexuality = "F"
        else:
            self.sexuality = ""

        self.asp1, self.asp2, self.ltw = (
            int.from_bytes(resource[104:106], byteorder="little"),
            "",
            "",
        )
        self.fam = resource[134:136]
        pflags1 = int.from_bytes(resource[180:182], byteorder="little")
        (
            self.spn_ghost,
            self.spn_servo,
            self.spn_zombie,
            self.spn_vampire,
            self.spn_werewolf,
            self.spn_plantsim,
            self.spn_witch,
            self.spn_mermaid,
            self.spn_genie,
            self.spn_fairy,
        ) = ("", "", "", "", "", "", "", "", "", "")
        if resource[322:324] == b"\x28\x00":
            self.spn_servo = True
        if pflags1 & 1:
            self.spn_zombie = True
        if pflags1 & 4:
            self.spn_vampire = True
        if pflags1 & 32:
            self.spn_werewolf = True
        if pflags1 & 256:
            self.spn_plantsim = True
        if pflags1 & 1024:
            self.spn_witch = True
        self.species = resource[384:386]
        self.career = careers[resource[190:194]]
        if self.career and self.species == b"\x00\x00":
            self.level = int.from_bytes(resource[126:128], byteorder="little")
            if self.level > 10:
                self.level = 10
            elif self.level < 0:
                self.level = 1
            try:
                self.job = jobs[resource[190:194]][self.level - 1]
            except:
                self.job = "Custom"
        elif self.fam == b"\xff\x7f":
            self.level = ""
            self.job = npcs[int.from_bytes(resource[322:324], byteorder="little") - 1]
        else:
            self.level = ""
            self.job = ""
        self.daysleft = int.from_bytes(resource[194:196], byteorder="little")
        self.age = int.from_bytes(
            resource[196:198], byteorder="little"
        ) + int.from_bytes(resource[324:326], byteorder="little")
        if self.species != b"\x00\x00":
            age = resource[128:130]
            if age > b"\x13\x00":
                self.age += 2
            elif age == b"\x13\x00":
                self.age += 1
        if self.daysleft > self.age:
            self.age += 1
        else:
            self.age -= self.daysleft
        if (
            int.from_bytes(resource[128:130], byteorder="little") == 2
            and int.from_bytes(resource[196:198], byteorder="little") == 0
        ):
            self.age += 2
        if self.age >= 54:
            if self.daysleft > self.age:
                self.daysleft = self.age
            else:
                self.daysleft += self.age + 1
        else:
            self.daysleft = ""
        self.i_politics = int.from_bytes(resource[260:262], byteorder="little") // 100
        self.i_money = int.from_bytes(resource[262:264], byteorder="little") // 100
        self.i_environment = (
            int.from_bytes(resource[264:266], byteorder="little") // 100
        )
        self.i_crime = int.from_bytes(resource[266:268], byteorder="little") // 100
        self.i_entertainment = (
            int.from_bytes(resource[268:270], byteorder="little") // 100
        )
        self.i_culture = int.from_bytes(resource[270:272], byteorder="little") // 100
        self.i_food = int.from_bytes(resource[272:274], byteorder="little") // 100
        self.i_health = int.from_bytes(resource[274:276], byteorder="little") // 100
        self.i_fashion = int.from_bytes(resource[276:278], byteorder="little") // 100
        self.i_sports = int.from_bytes(resource[278:280], byteorder="little") // 100
        self.i_paranormal = int.from_bytes(resource[280:282], byteorder="little") // 100
        self.i_travel = int.from_bytes(resource[282:284], byteorder="little") // 100
        self.i_work = int.from_bytes(resource[284:286], byteorder="little") // 100
        self.i_weather = int.from_bytes(resource[286:288], byteorder="little") // 100
        self.i_animals = int.from_bytes(resource[288:290], byteorder="little") // 100
        self.i_school = int.from_bytes(resource[290:292], byteorder="little") // 100
        self.i_toys = int.from_bytes(resource[292:294], byteorder="little") // 100
        self.i_scifi = int.from_bytes(resource[294:296], byteorder="little") // 100
        if self.age >= 18:
            self.major = majors[resource[352:356]]
        else:
            self.major = ""
        self.kep1 = int.from_bytes(resource[358:360], byteorder="little")
        tos = int.from_bytes(resource[372:374], byteorder="little")
        self.to_grad = tos & 1
        self.to_ungrad = tos & 2
        self.to_fat = tos & 4
        self.to_fit = tos & 8
        self.to_mermaid = tos & 16 == 16
        self.to_genie = tos & 32 == 32
        self.to_ghost = tos & 64 == 64
        self.to_vampire = tos & 128 == 128
        self.to_beard = tos & 256
        self.to_glasses = tos & 512
        self.to_makeup = tos & 1024
        self.to_fullface = tos & 2048
        self.to_hat = tos & 4096
        self.to_jewelry = tos & 8192
        tos = int.from_bytes(resource[374:376], byteorder="little")
        self.to_blond = tos & 1
        self.to_red = tos & 2
        self.to_brown = tos & 4
        self.to_black = tos & 8
        self.to_custom = tos & 16
        self.to_grey = tos & 32
        self.to_hardworker = tos & 64
        self.to_unemployed = tos & 128
        self.to_logic = tos & 256
        self.to_charisma = tos & 512
        self.to_cooking = tos & 1024
        self.to_mechanical = tos & 2048
        self.to_creativity = tos & 4096
        self.to_body = tos & 8192
        self.to_cleaning = tos & 16384
        self.to_zombie = tos & 32768 == 32768
        tos = int.from_bytes(resource[418:420], byteorder="little")
        self.to_servo = tos & 1 == 1
        self.to_plantsim = tos & 2 == 2
        self.to_werewolf = tos & 4 == 4
        self.to_witch = tos & 8 == 8
        self.tos = []
        tos = int.from_bytes(resource[376:378], byteorder="little")
        if tos & 1:
            self.tos.append("Educated")
        if tos & 2:
            self.tos.append("Uneducated")
        if tos & 4:
            self.tos.append("Fatness")
        if tos & 8:
            self.tos.append("Fitness")
        if tos & 16:
            self.tos.append("Mermaidism")
        if tos & 32:
            self.tos.append("Geniism")
        if tos & 64:
            self.tos.append("Ghostism")
        if tos & 128:
            self.tos.append("Vampirism")
        if tos & 256:
            self.tos.append("Beard")
        if tos & 512:
            self.tos.append("Glasses")
        if tos & 1024:
            self.tos.append("Makeup")
        if tos & 2048:
            self.tos.append("Full-Face")
        if tos & 4096:
            self.tos.append("Hats")
        if tos & 8192:
            self.tos.append("Jewelry")
        tos = int.from_bytes(resource[378:380], byteorder="little")
        if tos & 1:
            self.tos.append("Blonde")
        if tos & 2:
            self.tos.append("Red Hair")
        if tos & 4:
            self.tos.append("Brown Hair")
        if tos & 8:
            self.tos.append("Black Hair")
        if tos & 16:
            self.tos.append("Custom Hair")
        if tos & 32:
            self.tos.append("Grey Hair")
        if tos & 64:
            self.tos.append("Hardworker")
        if tos & 128:
            self.tos.append("Unemployed")
        if tos & 256:
            self.tos.append("Logical")
        if tos & 512:
            self.tos.append("Charismatic")
        if tos & 1024:
            self.tos.append("Good Cook")
        if tos & 2048:
            self.tos.append("Handy")
        if tos & 4096:
            self.tos.append("Creativity")
        if tos & 8192:
            self.tos.append("Athletic")
        if tos & 16384:
            self.tos.append("Good At Cleaning")
        if tos & 32768:
            self.tos.append("Zombiism")
        tos = int.from_bytes(resource[414:416], byteorder="little")
        if tos & 1:
            self.tos.append("Robots")
        if tos & 2:
            self.tos.append("Plantsimism")
        if tos & 4:
            self.tos.append("Lycanthropy")
        if tos & 8:
            self.tos.append("Witchiness")
        for i in range(len(self.tos), 2):
            self.tos.append("")
        self.to = ""
        tos = int.from_bytes(resource[380:382], byteorder="little")
        if tos & 1:
            self.to = "Educated"
        elif tos & 2:
            self.to = "Uneducated"
        elif tos & 4:
            self.to = "Fatness"
        elif tos & 8:
            self.to = "Fitness"
        elif tos & 16:
            self.to = "Mermaidism"
        elif tos & 32:
            self.to = "Geniism"
        elif tos & 64:
            self.to = "Ghostism"
        elif tos & 128:
            self.to = "Vampirism"
        elif tos & 256:
            self.to = "Beard"
        elif tos & 512:
            self.to = "Glasses"
        elif tos & 1024:
            self.to = "Makeup"
        elif tos & 2048:
            self.to = "Full-Face"
        elif tos & 4096:
            self.to = "Hats"
        elif tos & 8192:
            self.to = "Jewelry"
        tos = int.from_bytes(resource[382:384], byteorder="little")
        if tos & 1:
            self.to = "Blonde"
        elif tos & 2:
            self.to = "Red Hair"
        elif tos & 4:
            self.to = "Brown Hair"
        elif tos & 8:
            self.to = "Black Hair"
        elif tos & 16:
            self.to = "Custom Hair"
        elif tos & 32:
            self.to = "Grey Hair"
        elif tos & 64:
            self.to = "Hardworker"
        elif tos & 128:
            self.to = "Unemployed"
        elif tos & 256:
            self.to = "Logical"
        elif tos & 512:
            self.to = "Charismatic"
        elif tos & 1024:
            self.to = "Good Cook"
        elif tos & 2048:
            self.to = "Handy"
        elif tos & 4096:
            self.to = "Creativity"
        elif tos & 8192:
            self.to = "Athletic"
        elif tos & 16384:
            self.to = "Good At Cleaning"
        elif tos & 32768:
            self.to = "Zombiism"
        tos = int.from_bytes(resource[416:418], byteorder="little")
        if tos & 1:
            self.to = "Robots"
        elif tos & 2:
            self.to = "Plantsimism"
        elif tos & 4:
            self.to = "Lycanthropy"
        elif tos & 8:
            self.to = "Witchiness"
        self.h_cuisine = int.from_bytes(resource[420:422], byteorder="little") // 100
        self.h_art = int.from_bytes(resource[422:424], byteorder="little") // 100
        self.h_lit = int.from_bytes(resource[424:426], byteorder="little") // 100
        self.h_sports = int.from_bytes(resource[426:428], byteorder="little") // 100
        self.h_games = int.from_bytes(resource[428:430], byteorder="little") // 100
        self.h_nature = int.from_bytes(resource[430:432], byteorder="little") // 100
        self.h_tinkering = int.from_bytes(resource[432:434], byteorder="little") // 100
        self.h_fitness = int.from_bytes(resource[434:436], byteorder="little") // 100
        self.h_science = int.from_bytes(resource[436:438], byteorder="little") // 100
        self.h_music = int.from_bytes(resource[438:440], byteorder="little") // 100
        try:
            self.oth = hobbies[resource[442:444]]
        except:
            self.oth = "Custom"
        self.lta = int.from_bytes(resource[444:446], byteorder="little")
        self.lta_benefits = int.from_bytes(
            resource[446:448], byteorder="little"
        ) - int.from_bytes(resource[448:450], byteorder="little")
        self.trait1, self.trait2, self.trait3, self.trait4, self.trait5 = (
            "",
            "",
            "",
            "",
            "",
        )
        self.renuyu = 0


class Family:
    def __init__(self, lot):
        self.lot = lot
        self.day = ""
        self.time = ""
        self.season = ""
        self.ssnlngth = ""
        self.name = ""
        self.desc = ""

    def str(self, name, desc):
        self.name = name
        self.desc = desc


class SimsTree(Treeview):
    def __init__(self, master, columns, widths, yscrollcommand):
        Treeview.__init__(self, master, columns=columns, yscrollcommand=yscrollcommand)
        self.column("#0", width=150, stretch=FALSE)
        self.heading("#0", text="Name", command=lambda: self.sort_column("#0", False))
        for i, j in enumerate(self["columns"]):
            self.column(j, width=widths[i], stretch=FALSE)
            self.heading(
                j, text=j, command=lambda column=j: self.sort_column(column, False)
            )
        self.bind("<Button-3>", self.right_click)
        self.bind("<Button-2>", self.unsort)

        global tabs
        tabs.append(self)

    def unsort(self, event):
        for tab in tabs:
            l = [i for i in tab.get_children()]
            l.sort()
            for j, k in enumerate(l):
                tab.move(k, "", j)

    def sort_column(self, column, reverse):
        if column == "#0":
            l = [(self.item(i)["text"], i) for i in self.get_children()]
        else:
            try:
                l = [(int(self.set(i, column)), i) for i in self.get_children()]
            except:
                l = [(self.set(i, column), i) for i in self.get_children()]
        l.sort(reverse=reverse, key=lambda i: i[0])

        for tab in tabs:
            for i, (j, k) in enumerate(l):
                tab.move(k, "", i)

    def right_click(self, event):
        if self.identify("region", event.x, event.y) == "heading":
            column = self.identify_column(event.x)
            self.sort_column(column, True)

    def pack(self):
        Treeview.pack(self, expand=True, fill=BOTH)


class PetsTree(SimsTree):
    def __init__(self, master, columns, widths, yscrollcommand):
        Treeview.__init__(self, master, columns=columns, yscrollcommand=yscrollcommand)
        self.column("#0", width=150, stretch=FALSE)
        self.heading("#0", text="Name", command=lambda: self.sort_column("#0", False))
        for i, j in enumerate(self["columns"]):
            self.column(j, width=widths[i], stretch=FALSE)
            self.heading(
                j, text=j, command=lambda column=j: self.sort_column(column, False)
            )
        self.bind("<Button-3>", self.right_click)
        self.bind("<Button-2>", self.unsort)

    def unsort(self, event):
        l = [i for i in self.get_children()]
        l.sort()
        for j, k in enumerate(l):
            self.move(k, "", j)

    def sort_column(self, column, reverse):
        if column == "#0":
            l = [(self.item(i)["text"], i) for i in self.get_children()]
        else:
            try:
                l = [(int(self.set(i, column)), i) for i in self.get_children()]
            except:
                l = [(self.set(i, column), i) for i in self.get_children()]
        l.sort(reverse=reverse, key=lambda i: i[0])

        for i, (j, k) in enumerate(l):
            self.move(k, "", i)


def clear():
    global tab_parent
    try:
        tab_parent.destroy()
    except:
        pass
    global nhoods
    try:
        nhoods.destroy()
    except:
        pass


def select_neighborhood():
    clear()

    global nhoods
    nhoods = Frame()
    nhoods.pack()

    folders = []
    for i in folders_nhoods:
        for j in os.listdir(i):
            if os.path.isdir(os.path.join(i, j)) and len(j) == 4:
                folders.append((j, i))

    if len(folders) > 0:
        for i, j in enumerate(folders):
            image = PhotoImage(
                file="%s%s/%s_Neighborhood.png" % (j[1], j[0], j[0]),
                width=300,
                height=225,
            )
            button = Button(
                nhoods,
                text=j[0],
                image=image,
                compound="top",
                command=lambda nhood=j: search_neighborhood(nhood),
            )
            button.image = image
            button.grid(row=i // 3, column=i % 3)


def search_neighborhood(nhood):
    directory = os.path.join(nhood[1], "%s/" % (nhood[0]))
    filename = os.path.join(directory, "%s_Neighborhood.package" % (nhood[0]))
    nhood = nhood[0]

    clear()

    global sims
    global families

    sims = {}
    families = {}
    guid2nid = {}
    nids = []

    file = open(filename, "rb")
    content = file.read()
    file.close()

    ngbh = 0

    start = int.from_bytes(content[40:44], byteorder="little")
    stop = start + int.from_bytes(content[44:48], byteorder="little")
    step = int((stop - start) / int.from_bytes(content[36:40], byteorder="little"))
    for i in range(start, stop, step):
        rtype = content[i : i + 4]
        if rtype == b"HBGN":
            ngbh = i
        elif rtype == b"\xfb\x2e\xce\xaa":
            index = int.from_bytes(
                content[i + step - 8 : i + step - 4], byteorder="little"
            )
            length = int.from_bytes(
                content[i + step - 4 : i + step], byteorder="little"
            )
            resource = content[index : index + length]
            if int.from_bytes(resource[:4], byteorder="little") == length:
                resource = dbpf_decompress(resource)
            if int.from_bytes(resource[134:136], byteorder="little") > 0 or (
                nhood != "N001"
                and int.from_bytes(resource[148:150], byteorder="little") > 0
            ):
                sims[resource[474:476]] = Sim(resource)
                guid2nid[resource[476:480]] = resource[474:476]
                nids.append(resource[474:476])
        elif rtype == b"IMAF":
            index = int.from_bytes(
                content[i + step - 8 : i + step - 4], byteorder="little"
            )
            length = int.from_bytes(
                content[i + step - 4 : i + step], byteorder="little"
            )
            resource = content[index : index + length]
            if int.from_bytes(resource[:4], byteorder="little") == length:
                resource = dbpf_decompress(resource)
            families[content[i + 8 : i + 10]] = Family(
                int.from_bytes(resource[12:16], byteorder="little")
            )

    index = int.from_bytes(content[ngbh + 16 : ngbh + 20], byteorder="little")
    length = int.from_bytes(content[ngbh + 20 : ngbh + 24], byteorder="little")
    resource = content[index : index + length]
    if int.from_bytes(resource[:4], byteorder="little") == length:
        resource = dbpf_decompress(resource)
    try:
        resource = resource[resource.index(b"\xff\x7f\x00\x00\xbe\x00\x00\x00") :]
    except:
        pass
    resource = resource.split(b"\x00\x00\xbe\x00\x00\x00")
    nid = nids[0]
    for i in range(2, len(resource)):
        if nids.index(nid) < len(nids) - 1:
            if resource[i - 1][-2:] == nids[nids.index(nid) + 1]:
                nid = resource[i - 1][-2:]
        if sims[nid].species != b"\x00\x00":
            continue
        if b"\x89\x89\xd0\x53" in resource[i]:
            sims[nid].asp2 = int.from_bytes(
                resource[i][
                    resource[i].index(b"\x89\x89\xd0\x53")
                    + 18 : resource[i].index(b"\x89\x89\xd0\x53")
                    + 20
                ],
                byteorder="little",
            )
        inventory = resource[i].split(b"\xbb\x87\x00")
        if len(inventory) > 1:
            sims[nid].trait1 = traits[inventory[0][-1:]]
            if len(inventory) > 2:
                sims[nid].trait2 = traits[inventory[1][-1:]]
                if len(inventory) > 3:
                    sims[nid].trait3 = traits[inventory[2][-1:]]
                    if len(inventory) > 4:
                        sims[nid].trait4 = traits[inventory[3][-1:]]
                        if len(inventory) > 5:
                            sims[nid].trait5 = traits[inventory[4][-1:]]
            inventory = resource[i].split(b"\xc0\x55\xe3\x33")
            if len(inventory) >= 2:
                sims[nid].lta_benefits = (
                    int.from_bytes(inventory[1][20:22], byteorder="little")
                    + int.from_bytes(inventory[1][22:24], byteorder="little")
                    + int.from_bytes(inventory[1][24:26], byteorder="little")
                    + int.from_bytes(inventory[1][26:28], byteorder="little")
                )
            inventory = resource[i].split(b"\x55\x20\x04\x8e")
            if len(inventory) >= 2:
                print("%s:\tsim loaded" % (int.from_bytes(nid, byteorder="little")))
            inventory = resource[i].split(b"\x08\x64\x93\x00")
            sims[nid].renuyu = len(resource[i].split(b"\x9c\x94\xa8\xaf")) - 1
        inventory = resource[i].split(b"\xbb\x8e\x00")
        for i in inventory:
            if i[-1:] == b"\x8b\x27":
                sims[nid].spn_mermaid = True
            elif i[-1:] == b"\x75\x27":
                sims[nid].spn_genie = True
            elif i[-1:] == b"\x76\x27":
                sims[nid].spn_fairy = True
            elif i[-1:] == b"\x9b\x27":
                sims[nid].spn_ghost = True

    for i in range(start, stop, step):
        rtype = content[i : i + 4]
        if rtype == b"#RTS":
            if content[i + 8 : i + 10] in families:
                index = int.from_bytes(
                    content[i + step - 8 : i + step - 4], byteorder="little"
                )
                length = int.from_bytes(
                    content[i + step - 4 : i + step], byteorder="little"
                )
                resource = content[index : index + length]
                if int.from_bytes(resource[:4], byteorder="little") == length:
                    resource = dbpf_decompress(resource)
                name = resource[68:].split(b"\x01")
                if len(name) > 2:
                    families[content[i + 8 : i + 10]].str(
                        name[1].decode("utf-8"), name[2].decode("utf-8")
                    )
                else:
                    families[content[i + 8 : i + 10]].str(name[1].decode("utf-8"), "")
        elif rtype == b"\xe7\x99\xf9\x0b":
            index = int.from_bytes(
                content[i + step - 8 : i + step - 4], byteorder="little"
            )
            length = int.from_bytes(
                content[i + step - 4 : i + step], byteorder="little"
            )
            resource = content[index : index + length]
            if int.from_bytes(resource[:4], byteorder="little") == length:
                resource = dbpf_decompress(resource)
            nid = resource[-25:-23]
            if nid != b"\x00\x00":
                if nid in sims:
                    if not sims[nid].career:
                        sims[nid].career = "Owned Business"
                        sims[nid].job = "Owner"
                        sims[nid].level = 3
        else:
            nid = content[i + 8 : i + 10]
            if nid not in sims or sims[nid].species != b"\x00\x00":
                continue
            if rtype == b"\x3f\xe3\xfe\xeb":
                index = int.from_bytes(
                    content[i + step - 8 : i + step - 4], byteorder="little"
                )
                length = int.from_bytes(
                    content[i + step - 4 : i + step], byteorder="little"
                )
                resource = content[index : index + length]
                if int.from_bytes(resource[:4], byteorder="little") == length:
                    resource = dbpf_decompress(resource)
                if resource[:4] == b"\xe0\x50\xe7\xcb":
                    try:
                        sims[nid].skin1 = skins[
                            resource.split(b"6$\x00\x00\x00")[1][:36].decode("utf-8")
                        ]
                    except:
                        sims[nid].skin1 = "Custom"
                    try:
                        sims[nid].skin2 = skins[
                            resource.split(b"268435462$\x00\x00\x00")[1][:36].decode(
                                "utf-8"
                            )
                        ]
                    except:
                        sims[nid].skin2 = "Custom"
                    try:
                        sims[nid].skin3 = skins[
                            resource.split(b"2$\x00\x00\x00")[1][:36].decode("utf-8")
                        ]
                    except:
                        sims[nid].skin3 = "Custom"
                    try:
                        sims[nid].skin4 = skins[
                            resource.split(b"268435458$\x00\x00\x00")[1][:36].decode(
                                "utf-8"
                            )
                        ]
                    except:
                        sims[nid].skin4 = "Custom"
                    try:
                        sims[nid].hair1 = hairs[
                            resource.split(b"1$\x00\x00\x00")[1][:36].decode("utf-8")
                        ]
                    except:
                        sims[nid].hair1 = "Custom"
                    try:
                        sims[nid].hair2 = hairs[
                            resource.split(b"268435457$\x00\x00\x00")[1][:36].decode(
                                "utf-8"
                            )
                        ]
                    except:
                        sims[nid].hair2 = "Custom"
                    try:
                        sims[nid].eyes1 = eyes[
                            resource.split(b"3$\x00\x00\x00")[1][:36].decode("utf-8")
                        ]
                    except:
                        sims[nid].eyes1 = "Custom"
                    try:
                        sims[nid].eyes2 = eyes[
                            resource.split(b"268435459$\x00\x00\x00")[1][:36].decode(
                                "utf-8"
                            )
                        ]
                    except:
                        sims[nid].eyes2 = "Custom"
                else:
                    resource = resource.decode("utf-8")
                    xmlroot = xml.etree.ElementTree.fromstring(resource)
                    try:
                        sims[nid].skin1 = skins[
                            xmlroot.find("./AnyString[@key='6']").text
                        ]
                    except:
                        sims[nid].skin1 = "Custom"
                    try:
                        sims[nid].skin2 = skins[
                            xmlroot.find("./AnyString[@key='268435462']").text
                        ]
                    except:
                        sims[nid].skin2 = "Custom"
                    try:
                        sims[nid].skin3 = skins[
                            xmlroot.find("./AnyString[@key='2']").text
                        ]
                    except:
                        sims[nid].skin3 = "Custom"
                    try:
                        sims[nid].skin4 = skins[
                            xmlroot.find("./AnyString[@key='268435458']").text
                        ]
                    except:
                        sims[nid].skin4 = "Custom"
                    try:
                        sims[nid].hair1 = hairs[
                            xmlroot.find("./AnyString[@key='1']").text
                        ]
                    except:
                        sims[nid].hair1 = "Custom"
                    try:
                        sims[nid].hair2 = hairs[
                            xmlroot.find("./AnyString[@key='268435457']").text
                        ]
                    except:
                        sims[nid].hair2 = "Custom"
                    try:
                        sims[nid].eyes1 = eyes[
                            xmlroot.find("./AnyString[@key='3']").text
                        ]
                    except:
                        sims[nid].eyes1 = "Custom"
                    try:
                        sims[nid].eyes2 = eyes[
                            xmlroot.find("./AnyString[@key='268435459']").text
                        ]
                    except:
                        sims[nid].eyes2 = "Custom"
            elif rtype == b"\x8e\x54\x95\xcd":
                if sims[nid].age < 13:
                    continue
                index = int.from_bytes(
                    content[i + step - 8 : i + step - 4], byteorder="little"
                )
                length = int.from_bytes(
                    content[i + step - 4 : i + step], byteorder="little"
                )
                resource = content[index : index + length]
                if int.from_bytes(resource[:4], byteorder="little") == length:
                    resource = dbpf_decompress(resource)
                if resource[14:18] in ltws:
                    sims[nid].ltw = ltws[resource[14:18]]

    for i in sims:
        asp2 = sims[i].asp2
        if sims[i].asp2:
            sims[i].asp2 = aspirations[int(log(asp2, 2))]
            sims[i].asp1 = aspirations[
                int(log(sims[i].asp1 ^ (asp2 & sims[i].asp1), 2))
            ]
        elif sims[i].asp1 > 0:
            sims[i].asp1 = aspirations[int(log(sims[i].asp1, 2))]

    folder = os.path.join(directory, "Characters/")
    for filename in os.listdir(folder):
        file = open(os.path.join(folder, filename), "rb")
        content = file.read()
        file.close()

        name = ""
        guid = b""
        hair = ""

        start = int.from_bytes(content[40:44], byteorder="little")
        stop = start + int.from_bytes(content[44:48], byteorder="little")
        step = int((stop - start) / int.from_bytes(content[36:40], byteorder="little"))
        for i in range(start, stop, step):
            rtype = content[i : i + 4]
            if not rtype in [b"SSTC", b"DJBO", b"\xac\x8e\x59\xac"]:
                continue
            index = int.from_bytes(
                content[i + step - 8 : i + step - 4], byteorder="little"
            )
            length = int.from_bytes(
                content[i + step - 4 : i + step], byteorder="little"
            )
            resource = content[index : index + length]
            if int.from_bytes(resource[:4], byteorder="little") == length:
                resource = dbpf_decompress(resource)
            if rtype == b"DJBO":
                guid = resource[92:96]
            elif rtype == b"SSTC":
                name = resource[68:].split(b"\x01")
            elif rtype == b"\xac\x8e\x59\xac":
                if resource[:4] == b"\xe0\x50\xe7\xcb":
                    try:
                        hair = hairs[
                            resource.split(b"haircolor$\x00\x00\x00")[1][:36].decode(
                                "utf-8"
                            )
                        ]
                    except:
                        hair = "Custom"
                else:
                    resource = resource.decode("utf-8")
                    xmlroot = xml.etree.ElementTree.fromstring(resource)
                    try:
                        hair = hairs[xmlroot.find("./AnyString[@key='haircolor']").text]
                    except:
                        hair = "Custom"

        if not guid in guid2nid:
            continue
        guid = guid2nid[guid]
        sims[guid].firstname = name[1].split(b"\x00")[0].decode("utf-8")
        if sims[guid].firstname[:6] == "Prof. ":
            sims[guid].firstname = sims[guid].firstname[6:]
        sims[guid].bio = name[2].split(b"\x00")[0].decode("utf-8")
        sims[guid].lastname = name[3].split(b"\x00")[0].decode("utf-8")
        sims[guid].hair = hair

    folder = os.path.join(directory, "Lots/")
    for family in families:
        lot = families[family].lot
        if lot > 0:
            file = open(os.path.join(folder, "%s_Lot%s.package" % (nhood, lot)), "rb")
            content = file.read()
            file.close()

            start = int.from_bytes(content[40:44], byteorder="little")
            stop = start + int.from_bytes(content[44:48], byteorder="little")
            step = int(
                (stop - start) / int.from_bytes(content[36:40], byteorder="little")
            )
            for i in range(start, stop, step):
                rtype = content[i : i + 4]
                if rtype == b"IMIS":
                    index = int.from_bytes(
                        content[i + step - 8 : i + step - 4], byteorder="little"
                    )
                    length = int.from_bytes(
                        content[i + step - 4 : i + step], byteorder="little"
                    )
                    resource = content[index : index + length]
                    if int.from_bytes(resource[:4], byteorder="little") == length:
                        resource = dbpf_decompress(resource)
                    families[family].time = "%s:%02d" % (
                        int.from_bytes(resource[76:78], byteorder="little"),
                        int.from_bytes(resource[86:88], byteorder="little"),
                    )
                    families[family].day = int.from_bytes(
                        resource[132:134], byteorder="little"
                    )
                elif rtype == b"\x8b\xe2\x1b\xb2":
                    index = int.from_bytes(
                        content[i + step - 8 : i + step - 4], byteorder="little"
                    )
                    length = int.from_bytes(
                        content[i + step - 4 : i + step], byteorder="little"
                    )
                    resource = content[index : index + length]
                    if int.from_bytes(resource[:4], byteorder="little") == length:
                        resource = dbpf_decompress(resource)
                    index = int.from_bytes(resource[4:8], byteorder="little")
                    families[family].season = int.from_bytes(
                        resource[index + 12 : index + 16], byteorder="little"
                    )
                    families[family].ssnlngth = int.from_bytes(
                        resource[index + 16 : index + 20], byteorder="little"
                    )

    global tab_parent

    tab_parent = Notebook()
    tab_sims = Frame(tab_parent)
    tab_traits = Frame(tab_parent)
    tab_interests = Frame(tab_parent)
    tab_hobbies = Frame(tab_parent)
    tab_jobs = Frame(tab_parent)
    tab_tos = Frame(tab_parent)
    tab_tos2 = Frame(tab_parent)
    tab_genetics = Frame(tab_parent)
    tab_supernatural = Frame(tab_parent)
    tab_bios = Frame(tab_parent)
    tab_pets = Frame(tab_parent)
    tab_families = Frame(tab_parent)
    tab_parent.add(tab_sims, text="Sims")
    tab_parent.add(tab_traits, text="Traits")
    tab_parent.add(tab_interests, text="Interests")
    tab_parent.add(tab_hobbies, text="Hobbies")
    tab_parent.add(tab_jobs, text="Jobs")
    tab_parent.add(tab_tos, text="Attraction")
    tab_parent.add(tab_genetics, text="Genetics")
    tab_parent.add(tab_supernatural, text="Supernatural")
    tab_parent.add(tab_bios, text="Bios")
    tab_parent.add(tab_pets, text="Pets")
    tab_parent.add(tab_families, text="Families")
    tab_parent.pack(expand=True, fill=BOTH)

    global tabs
    tabs = []

    scrollbar_sims = Scrollbar(tab_sims)
    scrollbar_sims.pack(side=RIGHT, fill=Y)
    tree_sims = SimsTree(
        tab_sims,
        [
            "Family",
            "Age",
            "D-Day",
            "Neat",
            "Outgoing",
            "Active",
            "Playful",
            "Nice",
            "Asp 1",
            "Asp 2",
            "LTW",
            "LTA",
            "Pts",
        ],
        [100, 50, 50, 50, 50, 50, 50, 50, 50, 50, 125, 50, 50],
        scrollbar_sims.set,
    )
    tree_sims.pack()
    scrollbar_sims.config(command=tree_sims.yview)

    scrollbar_traits = Scrollbar(tab_traits)
    scrollbar_traits.pack(side=RIGHT, fill=Y)
    tree_traits = SimsTree(
        tab_traits,
        ["Trait 1", "Trait 2", "Trait 3", "Trait 4", "Trait 5"],
        [150 for i in range(5)],
        scrollbar_traits.set,
    )
    tree_traits.pack()
    scrollbar_traits.config(command=tree_traits.yview)

    scrollbar_interests = Scrollbar(tab_interests)
    scrollbar_interests.pack(side=RIGHT, fill=Y)
    tree_interests = SimsTree(
        tab_interests,
        [
            "Environment",
            "Food",
            "Weather",
            "Culture",
            "Money",
            "Politics",
            "Paranormal",
            "Health",
            "Fashion",
            "Travel",
            "Crime",
            "Sports",
            "Entertainment",
            "Animals",
            "Work",
            "School",
            "Toys",
            "Sci-Fi",
        ],
        [43 for i in range(18)],
        scrollbar_interests.set,
    )
    tree_interests.pack()
    scrollbar_interests.config(command=tree_interests.yview)

    scrollbar_hobbies = Scrollbar(tab_hobbies)
    scrollbar_hobbies.pack(side=RIGHT, fill=Y)
    tree_hobbies = SimsTree(
        tab_hobbies,
        [
            "OTH",
            "Cuisine",
            "Art",
            "Lit",
            "Sports",
            "Games",
            "Nature",
            "Tinkering",
            "Fitness",
            "Science",
            "Music",
        ],
        [75, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50],
        scrollbar_hobbies.set,
    )
    tree_hobbies.pack()
    scrollbar_hobbies.config(command=tree_hobbies.yview)

    scrollbar_jobs = Scrollbar(tab_jobs)
    scrollbar_jobs.pack(side=RIGHT, fill=Y)
    tree_jobs = SimsTree(
        tab_jobs,
        [
            "Cooking",
            "Mechanical",
            "Charisma",
            "Body",
            "Logic",
            "Creativity",
            "Cleaning",
            "Major",
            "Career",
            "Job",
            "Level",
        ],
        [50, 50, 50, 50, 50, 50, 50, 100, 100, 150, 50],
        scrollbar_jobs.set,
    )
    tree_jobs.pack()
    scrollbar_jobs.config(command=tree_jobs.yview)

    scrollbar_tos = Scrollbar(tab_tos)
    scrollbar_tos.pack(side=RIGHT, fill=Y)
    tree_tos = SimsTree(
        tab_tos,
        [
            "Sexuality",
            "Fat",
            "Fit",
            "Beard",
            "Glasses",
            "Makeup",
            "Full-Face",
            "Hat",
            "Jewelry",
            "Turn On 1",
            "Turn On 2",
            "Turn Off",
        ],
        [50, 50, 50, 50, 50, 50, 50, 50, 50, 105, 105, 105],
        scrollbar_tos.set,
    )
    tree_tos.pack()
    scrollbar_tos.config(command=tree_tos.yview)

    scrollbar_genetics = Scrollbar(tab_genetics)
    scrollbar_genetics.pack(side=RIGHT, fill=Y)
    tree_genetics = SimsTree(
        tab_genetics,
        [
            "Skin (D)",
            "Skin (r)",
            "Skin Range (1)",
            "Skin Range (2)",
            "Hair (D)",
            "Hair (r)",
            "Eyes (D)",
            "Eyes (r)",
        ],
        [75 for i in range(8)],
        scrollbar_genetics.set,
    )
    tree_genetics.pack()
    scrollbar_genetics.config(command=tree_genetics.yview)

    scrollbar_supernatural = Scrollbar(tab_supernatural)
    scrollbar_supernatural.pack(side=RIGHT, fill=Y)
    tree_supernatural = SimsTree(
        tab_supernatural,
        [
            "Ghost",
            "Zombie",
            "Vampire",
            "Servo",
            "Werewolf",
            "Plantsim",
            "Genie",
            "Witch",
            "Mermaid",
            "Fairy",
        ],
        [75 for i in range(10)],
        scrollbar_supernatural.set,
    )
    tree_supernatural.pack()
    scrollbar_supernatural.config(command=tree_supernatural.yview)

    Style().configure("Bio.Treeview", rowheight=50)
    scrollbar_bios = Scrollbar(tab_bios)
    scrollbar_bios.pack(side=RIGHT, fill=Y)
    tree_bios = Treeview(
        tab_bios,
        style="Bio.Treeview",
        columns=["Bio"],
        yscrollcommand=scrollbar_bios.set,
    )
    tree_bios.column("#0", width=150, stretch=FALSE)
    tree_bios.heading("#0", text="Name")
    tree_bios.heading("Bio", text="Bio")
    tree_bios.pack(expand=True, fill=BOTH)
    scrollbar_bios.config(command=tree_bios.yview)

    scrollbar_pets = Scrollbar(tab_pets)
    scrollbar_pets.pack(side=RIGHT, fill=Y)
    tree_pets = PetsTree(tab_pets, ["Family", "Age"], [100, 50], scrollbar_pets.set)
    tree_pets.pack()
    scrollbar_pets.config(command=tree_pets.yview)

    scrollbar_families = Scrollbar(tab_families)
    scrollbar_families.pack(side=RIGHT, fill=Y)
    tree_families = PetsTree(
        tab_families,
        ["Day", "Time", "Season", "SSN Length"],
        [50, 50, 50, 50],
        scrollbar_families.set,
    )
    tree_families.pack()
    scrollbar_families.config(command=tree_families.yview)

    for i in sims:
        if sims[i].species != b"\x00\x00":
            tree_pets.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[families[sims[i].fam].name, sims[i].age],
            )
        else:
            if sims[i].firstname in [
                "Unknown",
                "Social Bunny",
                "Social Worker",
                "Repo Man",
                "Unsavory Charlatan",
                "Tour Guide",
                "Local Chef",
                "Fire Dancer",
                "Pirate Captain Edward Dregg",
                "Ninja",
                "Food Judge",
                "Break Dancer",
                "Human Statue",
                "Hot Dog Chef",
            ]:
                continue
            tree_sims.insert(
                "",
                END,
                text="%s %s (%s)"
                % (
                    sims[i].firstname,
                    sims[i].lastname,
                    int.from_bytes(i, byteorder="little"),
                ),
                values=[
                    families[sims[i].fam].name,
                    sims[i].age,
                    sims[i].daysleft,
                    sims[i].p_neat,
                    sims[i].p_outgoing,
                    sims[i].p_active,
                    sims[i].p_playful,
                    sims[i].p_nice,
                    sims[i].asp1,
                    sims[i].asp2,
                    sims[i].ltw,
                    sims[i].lta,
                    sims[i].lta_benefits,
                ],
            )
            tree_traits.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[
                    sims[i].trait1,
                    sims[i].trait2,
                    sims[i].trait3,
                    sims[i].trait4,
                    sims[i].trait5,
                ],
            )
            tree_interests.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[
                    sims[i].i_environment,
                    sims[i].i_food,
                    sims[i].i_weather,
                    sims[i].i_culture,
                    sims[i].i_money,
                    sims[i].i_politics,
                    sims[i].i_paranormal,
                    sims[i].i_health,
                    sims[i].i_fashion,
                    sims[i].i_travel,
                    sims[i].i_crime,
                    sims[i].i_sports,
                    sims[i].i_entertainment,
                    sims[i].i_animals,
                    sims[i].i_work,
                    sims[i].i_school,
                    sims[i].i_toys,
                    sims[i].i_scifi,
                ],
            )
            tree_hobbies.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[
                    sims[i].oth,
                    sims[i].h_cuisine,
                    sims[i].h_art,
                    sims[i].h_lit,
                    sims[i].h_sports,
                    sims[i].h_games,
                    sims[i].h_nature,
                    sims[i].h_tinkering,
                    sims[i].h_fitness,
                    sims[i].h_science,
                    sims[i].h_music,
                ],
            )
            tree_jobs.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[
                    sims[i].s_cooking,
                    sims[i].s_mechanical,
                    sims[i].s_charisma,
                    sims[i].s_body,
                    sims[i].s_logic,
                    sims[i].s_creativity,
                    sims[i].s_cleaning,
                    sims[i].major,
                    sims[i].career,
                    sims[i].job,
                    sims[i].level,
                ],
            )
            tree_tos.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[
                    sims[i].sexuality,
                    sims[i].to_fat,
                    sims[i].to_fit,
                    sims[i].to_beard,
                    sims[i].to_glasses,
                    sims[i].to_makeup,
                    sims[i].to_fullface,
                    sims[i].to_hat,
                    sims[i].to_jewelry,
                    sims[i].tos[0],
                    sims[i].tos[1],
                    sims[i].to,
                ],
            )
            tree_genetics.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[
                    sims[i].skin1,
                    sims[i].skin2,
                    sims[i].skin3,
                    sims[i].skin4,
                    sims[i].hair1,
                    sims[i].hair2,
                    sims[i].eyes1,
                    sims[i].eyes2,
                ],
            )
            tree_supernatural.insert(
                "",
                END,
                text="%s %s" % (sims[i].firstname, sims[i].lastname),
                values=[
                    sims[i].spn_ghost,
                    sims[i].spn_zombie,
                    sims[i].spn_vampire,
                    sims[i].spn_servo,
                    sims[i].spn_werewolf,
                    sims[i].spn_plantsim,
                    sims[i].spn_genie,
                    sims[i].spn_witch,
                    sims[i].spn_mermaid,
                    sims[i].spn_fairy,
                ],
            )
            if sims[i].bio:
                tree_bios.insert(
                    "",
                    END,
                    text="%s %s" % (sims[i].firstname, sims[i].lastname),
                    values=[sims[i].bio],
                )

    for i in families:
        if i == b"\x00\x00" or int.from_bytes(i, byteorder="little") >= 32000:
            continue
        tree_families.insert(
            "",
            END,
            text="%s" % families[i].name,
            values=[
                families[i].day,
                families[i].time,
                families[i].season,
                families[i].ssnlngth,
            ],
        )


def get_config():
    file = os.path.join(os.path.dirname(__file__), "locations.txt")
    try:
        file = open(file, "r")
        contents = file.readlines()
        file.close()

        global folders_nhoods

        folders_nhoods = []
        for i in contents:
            folders_nhoods.append(i.rstrip("\n"))
    except:
        file = open(file, "w+")
        for i in folders_nhoods:
            file.write("%s\n" % i)
        file.close()


def handle_exception(type, value, tb):
    if issubclass(type, KeyboardInterrupt):
        sys.__excepthook__(type, value, tb)
        return

    logger.error("Uncaught exception", exc_info=(type, value, tb))


logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "error.log"),
    format="%(asctime)s %(levelname)s %(message)s\n",
)
logger = logging.getLogger("SiMidge")
sys.excepthook = handle_exception

folders_nhoods = [
    os.path.join(
        os.path.join(
            "C:/Users/",
            "%s/" % getuser(),
            "Documents/EA Games/The Sims™ 2 Ultimate Collection/",
        ),
        "Neighborhoods/",
    )
]
get_config()

hobbies = {
    b"\x00\x00": "",
    b"\xcc\x00": "Cuisine",
    b"\xcd\x00": "Art",
    b"\xce\x00": "Literature",
    b"\xcf\x00": "Sports",
    b"\xd0\x00": "Games",
    b"\xd1\x00": "Nature",
    b"\xd2\x00": "Tinkering",
    b"\xd3\x00": "Fitness",
    b"\xd4\x00": "Science",
    b"\xd5\x00": "Music",
}
traits = {
    b"\x04": "Absent-Minded",
    b"\x05": "Adventerous",
    b"\x06": "Ambitious",
    b"\x07": "Angler",
    b"\x08": "Animal Lover",
    b"\x09": "Artistic",
    b"\x0a": "Athletic",
    b"\x0b": "Avant Garde",
    b"\x0c": "Bookworm",
    b"\x0d": "Born Salesperson",
    b"\x0e": "Bot Fan",
    b"\x0f": "Brave",
    b"\x10": "Brooding",
    b"\x11": "Can't Stand Art",
    b"\x12": "Cat Person",
    b"\x13": "Charismatic",
    b"\x14": "Childish",
    b"\x15": "Clumsy",
    b"\x16": "Commitment Issues",
    b"\x17": "Computer Whiz",
    b"\x18": "Couch Potato",
    b"\x19": "Coward",
    b"\x1a": "Daredevil",
    b"\x1b": "Disciplined",
    b"\x1c": "Dislikes Children",
    b"\x1d": "Diva",
    b"\x1e": "Dog Person",
    b"\x1f": "Dramatic",
    b"\x20": "Easily Impressed",
    b"\x21": "Eccentric",
    b"\x22": "Eco-Friendly",
    b"\x23": "Equestrian",
    b"\x24": "Evil",
    b"\x25": "Excitable",
    b"\x26": "Family-Oriented",
    b"\x27": "Flirty",
    b"\x28": "Friendly",
    b"\x29": "Frugal",
    b"\x2a": "Gatherer",
    b"\x2b": "Genius",
    b"\x2c": "Good",
    b"\x2d": "Good Sense of Humor",
    b"\x2e": "Great Kisser",
    b"\x2f": "Green Thumb",
    b"\x30": "Grumpy",
    b"\x31": "Handy",
    b"\x32": "Hates the Outdoors",
    b"\x33": "Heavy Sleeper",
    b"\x34": "Hopeless Romantic",
    b"\x35": "Hot-Headed",
    b"\x36": "Hydrophobic",
    b"\x37": "Inappropriate",
    b"\x38": "Erratic",
    b"\x39": "Irresistible",
    b"\x3a": "Swiper",
    b"\x3b": "Light Sleeper",
    b"\x3c": "Loner",
    b"\x3d": "Loser",
    b"\x3e": "Loves the Cold",
    b"\x3f": "Loves the Heat",
    b"\x40": "Loves the Outdoors",
    b"\x41": "Loves to Swim",
    b"\x42": "Lucky",
    b"\x43": "Mean Spirited",
    b"\x44": "Mooch",
    b"\x45": "Natural Born Performer",
    b"\x46": "Natural Cook",
    b"\x47": "Neat",
    b"\x48": "Neurotic",
    b"\x49": "Never Nude",
    b"\x4a": "Night Owl",
    b"\x4b": "No Sense of Humor",
    b"\x4c": "Nurturing",
    b"\x4d": "Over-Emotional",
    b"\x4e": "Party Animal",
    b"\x4f": "Perceptive",
    b"\x50": "Perfectionist",
    b"\x51": "Photographer's Eyes",
    b"\x52": "Proper",
    b"\x53": "Rebellious",
    b"\x54": "Sailor",
    b"\x55": "Savvy Sculptor",
    b"\x56": "Schmoozer",
    b"\x57": "Shy",
    b"\x58": "Slob",
    b"\x59": "Snob",
    b"\x5a": "Social Butterfly",
    b"\x5b": "Socially Awkward",
    b"\x5c": "Star Quality",
    b"\x5d": "Supernatural Fan",
    b"\x5e": "Supernatural Skeptic",
    b"\x5f": "Technophobe",
    b"\x60": "Unflirty",
    b"\x61": "Unlucky",
    b"\x62": "Unstable",
    b"\x63": "Vegetarian",
    b"\x64": "Vehicle Enthusiast",
    b"\x65": "Virtuoso",
    b"\x66": "Workaholic",
}
aspirations = ["Rom", "Fam", "For", "Power", "Pop", "Kno", "", "Ple", "Chs"]
ltws = {
    b"\xce\x5f\x95\xee": "Celebrity Chef",
    b"\x2d\x60\x95\x4e": "General",
    b"\x3d\x60\x95\x4e": "Hall of Famer",
    b"\x3b\xc4\xb8\x0e": "Superhero",
    b"\xa9\x60\x95\x4e": "Supervillain",
    b"\xe7\x5f\x95\xae": "Party Guest",
    b"\x54\x60\x95\x8e": "Chief of Staff",
    b"\x63\xc4\xb8\x6e": "Mad Scientist",
    b"\x95\x60\x95\x6e": "Mayor",
    b"\xbc\x60\x95\xee": "Business Tycoon",
    b"\xa4\xef\x4c\xb2": "Game Studio Head",
    b"\x5f\xf0\x4c\xd2": "Media Magnate",
    b"\x2f\xf1\x4c\x92": "Rock God",
    b"\x01\xf0\x4c\x32": "Space Pirate",
    b"\x63\xf2\x4c\x32": "Education Minister",
    b"\x27\xf0\x4c\xd2": "The Law",
    b"\xfd\xd4\x2c\x74": "City Planner",
    b"\x30\xd4\x2c\xf4": "Prestidigitator",
    b"\x59\xd2\x2c\x34": "Ballet Dancer",
    b"\xb9\xd4\x2c\x54": "Hand of Poseidon",
    b"\x6d\xd4\x2c\xf4": "Head of SCIA",
    b"\xd8\x60\x95\x8e": "Visionary",
    b"\x19\x60\x95\xae": "Ecologocial Guru",
    b"\x81\x60\x95\x0e": "Icon",
    b"\xff\x5f\x95\x4e": "Cult Leader",
    b"\xeb\x60\x95\x8e": "Earn $100K",
    b"\x61\x61\x95\xce": "Graduate 3 Kids",
    b"\x2b\x61\x95\x6e": "6 Grandkids",
    b"\x06\x62\x95\x2e": "20 Best Friends",
    b"\x4e\x62\x95\x4e": "20 Lovers",
    b"\x96\x62\x95\xee": "Marry Off 6 Kids",
    b"\x64\x62\x95\xee": "Max Skills",
    b"\xb5\x62\x95\xae": "Golden Anniversary",
    b"\xda\x62\x95\x8e": "Woohoo 20 Sims",
    b"\x36\x8d\x97\x8f": "Eat Grilled Cheese",
    b"\xb9\x8c\x97\xcf": "50 First Dates",
    b"\x5d\x8d\x97\xaf": "50 Dream Dates",
    b"\xb5\x1c\x7d\x10": "5 Top Businesses",
    b"\x6c\x24\xb0\x31": "6 Pets Top Careers",
    b"\x45\x23\xb0\x91": "20 Pet Best Friends",
    b"\x06\x24\xb0\x31": "Raise 20 Pets",
}
majors = {
    b"\x00\x00\x00\x00": "",
    b"\x63\xf0\x9c\xae": "Physics",
    b"\x85\xf0\x9c\xce": "Literature",
    b"\x07\xf0\x9c\x2e": "Art",
    b"\x44\xf0\x9c\xee": "Economics",
    b"\x6d\xf0\x9c\x4e": "Political Science",
    b"\x8d\xf0\x9c\xee": "Mathematics",
    b"\x57\xf0\x9c\x2e": "Philosophy",
    b"\x2b\xf0\x9c\x4e": "Biology",
    b"\x74\xf0\x9c\x2e": "History",
    b"\x7c\xf0\x9c\xce": "Psychology",
    b"\x1d\xbf\x97\x8e": "Undeclared",
    b"\x4d\xf0\x9c\x4e": "Drama",
}
careers = {
    b"\x00\x00\x00\x00": "",
    b"\xe3\xbc\x9e\xac": "Social Work",
    b"\xd2\xbb\x43\xb2": "Music",
    b"\xfd\x61\x77\x0c": "Medicine",
    b"\x06\xc3\x40\xf2": "Game Development",
    b"\x55\x65\x19\x45": "Business",
    b"\xb0\x7b\xa0\xec": "Science",
    b"\x14\x5b\x94\x2c": "Politics",
    b"\x62\xc9\x40\x12": "Game Development",
    b"\x0c\x8b\x42\xb2": "Music",
    b"\xbc\xff\x6f\x4e": "Artist",
    b"\x0b\x62\x77\xec": "Slacker",
    b"\x94\x94\xe0\x53": "Entertainment",
    b"\x39\x7b\xa0\x6c": "Social Work",
    b"\x30\x8b\x42\x72": "Education",
    b"\xa5\x94\xe0\xd3": "Dance",
    b"\xb0\xff\x6f\xae": "Show Business",
    b"\xc0\x94\xe0\x93": "Intelligence",
    b"\xc1\xa4\x88\xb1": "Service",
    b"\xdc\x7b\xa0\x6c": "Slacker",
    b"\x01\xc3\xe1\xf3": "Construction",
    b"\x32\xbd\x9e\x6c": "Military",
    b"\x0a\x40\x8f\xd0": "Owned Business",
    b"\x43\x94\xe0\x13": "Oceanography",
    b"\x0e\xbd\x9e\x6c": "Criminal",
    b"\x1c\x00\x70\xee": "Natural Scientist",
    b"\x22\x94\xe0\xd3": "Dance",
    b"\x2d\xcc\x75\xd1": "Show Business",
    b"\x0c\x7b\xa0\x4c": "Culinary",
    b"\x47\xbd\x9e\x0c": "Science",
    b"\x8d\x7b\xa0\xcc": "Politics",
    b"\x19\x8b\x42\x12": "Law",
    b"\x77\x05\x1e\x4c": "Business",
    b"\x12\xe2\x40\x52": "Journalism",
    b"\x18\xe9\x89\xac": "Medicine",
    b"\xec\xbb\x43\xd2": "Education",
    b"\x04\x94\xe0\x73": "Oceanography",
    b"\x87\xff\x6f\x2e": "Paranormal",
    b"\x1f\xd9\x6b\x31": "Owned Business",
    b"\xa5\xcb\x40\x32": "Adventurer",
    b"\x0e\x94\xe0\x33": "Intelligence",
    b"\x0f\xc3\xe1\x53": "Construction",
    b"\x47\xe9\x89\xac": "Athletics",
    b"\x5f\xe9\x89\x2c": "Athletics",
    b"\x44\xd9\x40\x72": "Journalism",
    b"\xcd\x7a\xa0\xac": "Criminal",
    b"\x17\x94\xe0\xb3": "Entertainment",
    b"\x66\x7b\xa0\xcc": "Military",
    b"\x00\xa4\x88\xd1": "Security",
    b"\x35\xd2\x40\xf2": "Adventurer",
    b"\xde\xbb\x43\x12": "Law",
    b"\x5f\xbd\x9e\xec": "Culinary",
    b"\x12\xa6\x68\x00": "Artist",
    b"\x0f\xa6\x68\x00": "Natural Scientist",
    b"\x10\xa6\x68\x00": "Paranormal",
    b"\x13\xa6\x68\x00": "Show Business",
}
jobs = {
    b"\xe3\xbc\x9e\xac": [
        "Social Worker Trainee",
        "Nursing Home Caseworker",
        "Adoption Caseworker",
        "Domestic Violence Counselor",
        "Health Care Caseworker",
        "Mental Health Caseworker",
        "C.P.S. Caseworker",
        "Caseload Supervisor",
        "Secretary of D.H.S.S.",
        "Captain Hero",
    ],
    b"\xd2\xbb\x43\xb2": [
        "Record Store Clerk",
        "Piano Tuner",
        "Coffee Shop Sound Engineer",
    ],
    b"\xfd\x61\x77\x0c": [
        "Emergency Medical Technician",
        "Paramedic",
        "Nurse",
        "Intern",
        "Resident",
        "General Practitioner",
        "Specialist",
        "Surgeon",
        "Medical Researcher",
        "Chief of Staff",
    ],
    b"\x06\xc3\x40\xf2": [
        "Game Tester",
        "Lead Tester",
        "Testing Manager",
        "Associate Designer",
        "Designer",
        "Lead Designer",
        "Producer",
        "Director",
        "Executive Vice President",
        "Game Studio Head",
    ],
    b"\x55\x65\x19\x45": [
        "Mailroom Technician",
        "Executive Assistant",
        "Field Sales Representative",
        "Junior Executive",
        "Executive",
        "Senior Manager",
        "Vice President",
        "President",
        "CEO",
        "Business Tycoon",
    ],
    b"\xb0\x7b\xa0\xec": ["Lab Glass Scrubber", "Test Subject", "Lab Assistant"],
    b"\x14\x5b\x94\x2c": [
        "Campaign Worker",
        "Intern",
        "Lobbyist",
        "Campaign Manager",
        "City Council Member",
        "State Assemblyperson",
        "Congressperson",
        "Judge",
        "Senator",
        "Mayor",
    ],
    b"\x62\xc9\x40\x12": ["Noob", "Button Masher", "Trash Talker"],
    b"\x0c\x8b\x42\xb2": [
        "Record Store Clerk",
        "Piano Tuner",
        "Coffee Shop Sound Engineer",
        "Summer Camp Music Teacher",
        "Battle of the Bands Judge",
        "Roadie",
        "Studio Musician",
        "Concert Pianist",
        "Symphony Conductor",
        "Rock God",
    ],
    b"\xbc\xff\x6f\x4e": [
        "Canvas Stretcher",
        "Street Caricaturist",
        "Souvenir Whittler",
        "Comic Book Penciller",
        "Wedding Photographer",
        "Art Forget",
        "Fashion Photographer",
        "Acclaimed Muralist",
        "Conceptual Artist",
        "Visionary",
    ],
    b"\x0b\x62\x77\xec": [
        "Golf Caddy",
        "Gas Station Attendant",
        "Convenience Store Clerk",
        "Record Store Clerk",
        "Party DJ",
        "Projectionist",
        "Home Video Editor",
        "Freelance Photographer",
        "Freelance Web Designer",
        "Professional Party Guest",
    ],
    b"\x94\x94\xe0\x53": ["Stand Up Comedian", "Birthday Party Mascot", "Mime"],
    b"\x39\x7b\xa0\x6c": ["Peer Mediator", "Shelter Worker", "Help-Line Worker"],
    b"\x30\x8b\x42\x72": [
        "Playground Monitor",
        "Teacher's Aide",
        "Substitute Teacher",
        "Elementary School Teacher",
        "High School Teacher",
        "University Guest Lecturer",
        "High School Principal",
        "College Senior Professor",
        "College Dean of Students",
        "Education Minister",
    ],
    b"\xa5\x94\xe0\xd3": [
        "Aerobics Instructor",
        "Backup Dancer",
        "Jazzercise Instructor",
    ],
    b"\xb0\xff\x6f\xae": [
        "Screen Test Stand-in",
        "Body Double",
        "Bit Player",
        "Commercial Actor",
        "Cartoon Voice",
        "Supporting Player",
        "Broadway Star",
        "Leading Star",
        "Blockbuster Director",
        "Icon",
    ],
    b"\xc0\x94\xe0\x93": ["Gumshow", "Private Eye", "Crime Scene Investigator"],
    b"\xdc\x7b\xa0\x6c": [
        "Golf Caddy",
        "Gas Station Attendant",
        "Convenience Store Clerk",
    ],
    b"\x01\xc3\xe1\xf3": [
        "Cement Mixer",
        "Brick Layer",
        "Foreman",
        "Head of Construction Company",
        "Architect's Apprentice",
        "Draftsman",
        "Architect",
        "Architectural Partner",
        "Master Architect",
        "City Planner",
    ],
    b"\x32\xbd\x9e\x6c": [
        "Recruit",
        "Elite Forces",
        "Drill Instructor",
        "Junior Officer",
        "Counter Intelligence",
        "Flight Officer",
        "Senior Officer",
        "Commander",
        "Astronaut",
        "General",
    ],
    b"\x0a\x40\x8f\xd0": ["Employee", "Manager"],
    b"\x43\x94\xe0\x13": [
        "Fish Chummer",
        "Dolphin Tank Cleaner",
        "Sea Lice Research Assistant",
    ],
    b"\x0e\xbd\x9e\x6c": [
        "Pickpocket",
        "Bagman",
        "Bookie",
        "Con Artist",
        "Getaway Driver",
        "Bank Robber",
        "Cat Burglar",
        "Counterfeiter",
        "Smuggler",
        "Criminal Mastermind",
    ],
    b"\x1c\x00\x70\xee": [
        "Ratkeeper",
        "Algae Hunter",
        "Clam Wrangler",
        "Scatmaster",
        "Soil Identifier",
        "Rogue Botanist",
        "Animal Linguist",
        "Unnatural Crossbreeder",
        "Dinosaur Cloner",
        "Ecological Guru",
    ],
    b"\x22\x94\xe0\xd3": [
        "Aerobics Instructor",
        "Backup Dancer",
        "Jazzercise Instructor",
        "Pop 'n Lock Performer",
        "Dance Video Star",
        "Interpretive Dancer",
        "Tap Dancer",
        "Ballroom Dancer",
        "Flamenco Master",
        "World Class Ballet Dancer",
    ],
    b"\x0c\x7b\xa0\x4c": [
        "Dishwasher",
        "Drive Through Clerk",
        "Fast Food Shift Manager",
    ],
    b"\x47\xbd\x9e\x0c": [
        "Test Subject",
        "Lab Assistant",
        "Field Researcher",
        "Science Teacher",
        "Project Leader",
        "Inventor",
        "Scholar",
        "Top Secret Researcher",
        "Theorist",
        "Mad Scientist",
    ],
    b"\x8d\x7b\xa0\xcc": ["Door to Door Poller", "Campaign Worker", "Intern"],
    b"\x19\x8b\x42\x12": [
        "File Clerk",
        "Law Firm Receptionist",
        "Legal Secretary",
        "Legal Biller",
        "Paralegal",
        "Personal Injury Attorney",
        "Family Law Attorney",
        "International Corporate Lawyer",
        "Entertainment Attorney",
        "The Law",
    ],
    b"\x77\x05\x1e\x4c": ["Gofer", "Mailroom Technician", "Executive Assistant"],
    b"\x12\xe2\x40\x52": [
        "Yearbook Club Supervisor",
        "Blog Writer",
        "Internet Movie Critic",
    ],
    b"\x18\xe9\x89\xac": [
        "Nursing Home Attendant",
        "Orderly",
        "Emergency Medical Technician",
    ],
    b"\xec\xbb\x43\xd2": ["Playground Monitor", "Teacher's Aide", "Substitute Teacher"],
    b"\x04\x94\xe0\x73": [
        "Fish Chummer",
        "Dolphin Tank Cleaner",
        "Sea Lice Research Assistant",
        "Dive Master",
        "Underwater Demolitionist",
        "Marine Biologist",
        "Whale Tracker",
        "Deep Sea Fisherman",
        "Protector of Whales",
        "Hand of Poseidon",
    ],
    b"\x87\xff\x6f\x2e": [
        "Psychic Phone Friend",
        "Conspiracy Theorist",
        "Tarot Card Reader",
        "Hypnotist",
        "Medium",
        "Dowser",
        "Police Psychic",
        "UFO Investigator",
        "Exorcist",
        "Cult Leader",
    ],
    b"\x1f\xd9\x6b\x31": ["Employee", "Manager"],
    b"\xa5\xcb\x40\x32": [
        "Ambassador's Intern",
        "Spelunker",
        "Multiregional Sim of Some Question",
        "Deep Sea Excavator",
        "Relic Liberator",
        "Dread Pirate",
        "Warhead Disarmer",
        "Hostage Negotiator",
        "International Sim of Mystery",
        "Space Pirate",
    ],
    b"\x0e\x94\xe0\x33": [
        "Gumshow",
        "Private Eye",
        "Crime Scene Investigator",
        "Surveillance Operator",
        "Reconnaissance Communicator",
        "Rookie Field Agent",
        "Field Agent",
        "Double Agent",
        "Elite Operative",
        "Head of SCIA",
    ],
    b"\x0f\xc3\xe1\x53": ["Cement Mixer", "Brick Layer", "Foreman"],
    b"\x47\xe9\x89\xac": ["Waterperson", "Locker Room Attendant", "Team Mascot"],
    b"\x5f\xe9\x89\x2c": [
        "Team Mascot",
        "Minor Leaguer",
        "Rookie",
        "Starter",
        "All Star",
        "MVP",
        "Superstar",
        "Assistant Coach",
        "Coach",
        "Hall of Famer",
    ],
    b"\x44\xd9\x40\x72": [
        "Yearbook Club Supervisor",
        "Blog Writer",
        "Internet Movie Critic",
        "Fact Checker",
        "Obituary Writer",
        "Horoscope Writer",
        "Sports Columnist",
        "Investigatory Journalist",
        "Magazine Editor",
        "Media Magnate",
    ],
    b"\xcd\x7a\xa0\xac": ["Street Hawker", "Numbers Runner", "Pickpocket"],
    b"\x17\x94\xe0\xb3": [
        "Stand Up Comedian",
        "Birthday Party Mascot",
        "Mime",
        "Lounge Singer",
        "Ventriloquist",
        "Round Table Knight",
        "Juggler",
        "Master of Ceremonies",
        "Headliner",
        "Pretidigitator",
    ],
    b"\x66\x7b\xa0\xcc": ["Paintball Attendant", "Recruit Training Corps", "Recruit"],
    b"\x35\xd2\x40\xf2": [
        "Ambassador's Intern",
        "Spelunker",
        "Multiregional Sim of Some Question",
    ],
    b"\xde\xbb\x43\x12": ["File Clerk", "Law Firm Receptionist", "Legal Secretary"],
    b"\x5f\xbd\x9e\xec": [
        "Dishwasher",
        "Barista",
        "Bartender",
        "Host",
        "Waiter",
        "Prep Cook",
        "Sous Chef",
        "Executive Chef",
        "Restauranteur",
        "Celebrity Chef",
    ],
    b"\x12\xa6\x68\x00": [
        "Paint Pot Washer",
        "Canvas Stretcher",
        "Street Caricaturist",
    ],
    b"\x0f\xa6\x68\x00": ["Plant Watcher", "Ratkeeper", "Algae Hunter"],
    b"\x10\xa6\x68\x00": [
        "Psychic Phone Friend",
        "Conspiracy Theorist",
        "Tarot Card Reader",
    ],
    b"\x13\xa6\x68\x00": ["Talent Show Entrant", "Set Runner", "Screen Test Stand-in"],
}
npcs = [
    "Bartender",
    "Bartender",
    "Boss",
    "Burglar",
    "Driver",
    "Streaker",
    "Coach",
    "Cook",
    "Cop",
    "Delivery Person",
    "Exterminator",
    "Firefighter",
    "Gardener",
    "Barista",
    "Reaper",
    "Handyperson",
    "Headmaster",
    "Matchmaker",
    "Maid",
    "Mail Carrier",
    "Nanny",
    "Newspaper Delivery Person",
    "Pizza Delivery Person",
    "Professor",
    "Cow Mascot",
    "Repo Man",
    "Cheerleader",
    "Llama Mascot",
    "Imaginary Friend",
    "Social Worker",
    "Clerk",
    "Therapist",
    "Chinese Delivery Person",
    "Host",
    "Waiter",
    "Chef",
    "DJ",
    "Crumplebottom",
    "Vampire",
    "Servo",
    "Reporter",
    "Stylist",
    "Stray",
    "Wolf",
    "Skunk",
    "Animal Control Officer",
    "Obedience Trainer",
    "Masseuse",
    "Bellhop",
    "Villain",
    "Tour Guide",
    "Hermit",
    "Ninja",
    "Bigfoot",
    "Housekeeper",
    "Food Stand Chef",
    "Fire Dancer",
    "Shaman",
    "Ghost Pirate Captain",
    "Food Judge",
    "Genie",
    "DJ",
    "Matchmaker",
    "Head Witch",
    "Break Dancer",
    "Familiar",
    "Human Statue",
    "Landlord",
    "Butler",
    "Hot Dog Chef",
]
skins = {
    "00000001-0000-0000-0000-000000000000": "S1",
    "00000002-0000-0000-0000-000000000000": "S2",
    "00000003-0000-0000-0000-000000000000": "S3",
    "00000004-0000-0000-0000-000000000000": "S4",
    "6baf064a-85ad-4e37-8d81-a987e9f8da46": "Alien",
    "b9a94827-7544-450c-a8f4-6f643ae89a71": "Mannequin",
}
hairs = {
    "00000001-0000-0000-0000-000000000000": "Black",
    "00000002-0000-0000-0000-000000000000": "Brown",
    "00000003-0000-0000-0000-000000000000": "Blond",
    "00000004-0000-0000-0000-000000000000": "Red",
    "00000005-0000-0000-0000-000000000000": "Gray",
}
eyes = {
    "51c4a750-c9f4-4cfe-801c-898efc360cb7": "Green",
    "0758508c-7111-40f9-b33b-706464626ac9": "Gray",
    "e43f3360-3a08-4755-8b83-a0d37a6c424b": "Light Blue",
    "2d6839c5-0b7c-48a1-9c55-4bd9cc873b0f": "Dark Blue",
    "32dee745-b6ce-419f-9e86-ae93802d2682": "Brown",
    "12d4f3e1-fdbe-4fe7-ace3-46dd9ff52b51": "Alien",
}
root = Tk()
root.geometry("960x1080")
root.title("SimTracker")
menubar = Menu()
menubar.add_command(label="Neighborhoods", command=select_neighborhood)
root["menu"] = menubar

select_neighborhood()

root.mainloop()
