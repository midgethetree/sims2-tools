#!/bin/python

from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
import os, xml.etree.ElementTree, sys, logging
from getpass import getuser
from binascii import hexlify, unhexlify
from codecs import encode


def dbpf_decompress(n, limit):
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
            if len(x) >= limit:
                break
            x += bytes({n[index]})
            index += 1
            numplaintext -= 1
        if numplaintext != 0:
            break
        while numtocopy > 0:
            if len(x) >= limit:
                break
            x += bytes({x[-copyoffset]})
            numtocopy -= 1
        if numtocopy != 0:
            break
    return x


class Resource:
    def __init__(self, name, rtype, group, instance, classtype, filename, resource):
        try:
            self.name = name.decode("utf-8")
        except:
            self.name = None
        try:
            self.type = types2name[rtype]
        except:
            self.type = rtype
        self.group = group
        self.instance = instance
        self.classtype = classtype
        self.files = [filename]
        self.versions = [resource]

    def print(self):
        if self.name:
            search_results.insert(END, "%s\n" % self.name)
        search_results.insert(END, "File Type: %s\n" % self.type[::-1].decode("utf-8"))
        search_results.insert(
            END, "Group ID: 0x%s\n" % str(hexlify(self.group[::-1]))[2:-1]
        )
        search_results.insert(
            END, "Instance ID: 0x%s\n" % str(hexlify(self.instance[::-1]))[2:-1]
        )

    def print_files(self):
        search_results.insert(END, "Packages Using This Procedure:\n")
        for i in self.files:
            search_results.insert(END, "\t%s\n" % i)

    def print_files_alt(self):
        for i in self.files:
            search_results.insert(END, "%s\n" % i)

    def print_versions(self):
        if len(self.versions) < 2:
            search_results.insert(END, "No differences found.")
            return
        if len(self.versions[0]) > len(self.versions[1]):
            size = len(self.versions[1])
        else:
            size = len(self.versions[0])
        if self.type == b"NOCB":
            index = 66
        else:
            index = 64

        search_results.insert(END, "Changed Lines:\n")
        for i in range(index, size, 2):
            x = int.from_bytes(self.versions[0][i : i + 2], byteorder="little")
            if x > 32767:
                x -= 65536
            y = int.from_bytes(self.versions[1][i : i + 2], byteorder="little")
            if y > 32767:
                y -= 65536
            if x != y:
                search_results.insert(
                    END, "Line:\t%d\tValue:\t%d\t->\t%d\n" % ((i - index) // 2, y, x)
                )


def clear():
    button_clear["state"] = DISABLED
    global search_results
    global scrollbar
    try:
        search_results.destroy()
        scrollbar.destroy()
    except:
        pass


def search_package(
    filename,
    filter_group=None,
    filter_instance=None,
    target=None,
    nametest=None,
    limit=float("inf"),
    unique=True,
):
    global resources

    file = open(filename, "rb")
    content = file.read()
    file.close()

    filename = os.path.normpath(filename)
    print(filename)
    filename = filename.split("Downloads")[-1]
    filename = filename.split("Objects")[-1]
    filename = filename.split("Neighborhoods")[-1]
    filename = filename.lstrip("/\\")

    if int.from_bytes(content[36:40], byteorder="little") == 0:
        logging.error("empty file\n%s" % filename)
        return

    start = int.from_bytes(content[40:44], byteorder="little")
    stop = start + int.from_bytes(content[44:48], byteorder="little")
    step = int((stop - start) / int.from_bytes(content[36:40], byteorder="little"))
    for i in range(start, stop, step):
        rtype = content[i : i + 4]
        if not rtype in resources:
            continue
        group = content[i + 4 : i + 8]
        if filter_group:
            if filter_group == 127:
                if group[-1] != 127:
                    continue
            elif group != filter_group:
                continue
        instance = content[i + 8 : i + 12]
        if filter_instance:
            if instance != filter_instance:
                continue
        if step > 20:
            classid = content[i + 12 : i + 16]
        else:
            classid = 0
        index = int.from_bytes(content[i + step - 8 : i + step - 4], byteorder="little")
        length = int.from_bytes(content[i + step - 4 : i + step], byteorder="little")
        if limit == 0:
            resource = content[index : index + 74]
            name = b""
        else:
            if limit == 64:
                resource = content[index : index + 74]
            else:
                resource = content[index : index + length]
            if int.from_bytes(resource[:4], byteorder="little") == length:
                resource = dbpf_decompress(resource, limit)
            name = resource[:64].split(b"\x00")[0]
        if target:
            if rtype == b"#RTS" or rtype == b"SSTC" or rtype == b"sATT":
                if not target in resource.lower():
                    continue
            else:
                if not target in resource:
                    continue
        if nametest:
            if not nametest in name.lower():
                continue
        if not group in resources[rtype]:
            resources[rtype][group] = {}
        if not classid in resources[rtype][group]:
            resources[rtype][group][classid] = {}
        if instance in resources[rtype][group][classid]:
            if filename not in resources[rtype][group][classid][instance].files:
                resources[rtype][group][classid][instance].files.append(filename)
                resources[rtype][group][classid][instance].versions.append(resource)
            else:
                break
        elif unique:
            resources[rtype][group][classid][instance] = Resource(
                name, rtype, group, instance, classid, filename, resource
            )


def search_strs(filename):
    global resources

    file = open(filename, "rb")
    content = file.read()
    file.close()

    filename = os.path.normpath(filename)
    filename = filename.split("Downloads")[-1]
    filename = filename.split("Objects")[-1]
    filename = filename.split("Neighborhoods")[-1]
    filename = filename.lstrip("/\\")

    if int.from_bytes(content[36:40], byteorder="little") == 0:
        logging.error("empty file\n%s" % filename)
        return

    start = int.from_bytes(content[40:44], byteorder="little")
    stop = start + int.from_bytes(content[44:48], byteorder="little")
    step = int((stop - start) / int.from_bytes(content[36:40], byteorder="little"))
    for i in range(start, stop, step):
        rtype = content[i : i + 4]
        if not rtype in resources:
            continue
        group = content[i + 4 : i + 8]
        instance = content[i + 8 : i + 12]
        if step > 20:
            classid = content[i + 12 : i + 16]
        else:
            classid = 0
        index = int.from_bytes(content[i + step - 8 : i + step - 4], byteorder="little")
        length = int.from_bytes(content[i + step - 4 : i + step], byteorder="little")
        resource = content[index : index + length]
        if int.from_bytes(resource[:4], byteorder="little") == length:
            resource = dbpf_decompress(resource, float("inf"))
        name = resource[:64].split(b"\x00")[0]
        num = int.from_bytes(resource[66:68], byteorder="little")
        strings = resource[68:].split(b"\x00\x01")
        if strings[-1][-2:] == b"\x00\x00":
            strings[-1] = strings[-1][:-2]
        lengths = [len(string) for string in strings]
        if (
            num == 0
            or len(strings) != num
            or max(lengths) <= 1
            or (rtype == b"SSTC" and len(lengths) < 2)
        ):
            if not group in resources[rtype]:
                resources[rtype][group] = {}
            if not classid in resources[rtype][group]:
                resources[rtype][group][classid] = {}
            if instance in resources[rtype][group][classid]:
                resources[rtype][group][classid][instance].files.append(filename)
                resources[rtype][group][classid][instance].versions.append(resource)
            else:
                resources[rtype][group][classid][instance] = Resource(
                    name, rtype, group, instance, classid, filename, resource
                )


def print_resources(
    min_files=1,
    max_files=float("inf"),
    min_versions=1,
    max_versions=float("inf"),
    printfiles=True,
):
    button_clear["state"] = NORMAL
    global search_results
    global scrollbar
    scrollbar = Scrollbar()
    scrollbar.pack(side=RIGHT, fill=Y)
    search_results = Text(root, yscrollcommand=scrollbar.set)
    count = 0
    for i in resources:
        for j in resources[i]:
            for k in resources[i][j]:
                for l in resources[i][j][k]:
                    if (
                        len(resources[i][j][k][l].files) >= min_files
                        and len(resources[i][j][k][l].files) <= max_files
                        and len(set(resources[i][j][k][l].versions)) >= min_versions
                        and len(set(resources[i][j][k][l].versions)) <= max_versions
                    ):
                        resources[i][j][k][l].print()
                        if printfiles:
                            resources[i][j][k][l].print_files()
                        search_results.insert(END, "\n")
                        count += 1
    search_results.insert(END, f"{count} results found.")
    search_results.pack()
    scrollbar.config(command=search_results.yview)


def find_conflicts():
    clear()

    global resources
    resources = {
        b"NOCB": {},
        b"VAHB": {},
        b"SPZG": {},
        b"BATT": {},
        b"sATT": {},
        b"#RTS": {},
        b"DJBO": {},
        b"fJBO": {},
    }

    for dirpath, dirnames, filenames in os.walk(folder_dl, topdown=False):
        for file in (i for i in filenames if i[-8:].lower() == ".package"):
            search_package(os.path.join(dirpath, file), filter_group=127, limit=64)

    print_resources(min_files=2)


def find_conflicts_file():
    clear()

    global resources
    resources = {
        b"NOCB": {},
        b"VAHB": {},
        b"BATT": {},
        b"sATT": {},
        b"#RTS": {},
        b"DJBO": {},
        b"fJBO": {},
    }

    mod = askopenfilename(filetypes=[("TS2 packages", "*.package")])
    if not mod:
        return

    search_package(mod, filter_group=127, limit=64)
    for dirpath, dirnames, filenames in os.walk(folder_dl, topdown=False):
        for file in (i for i in filenames if i[-8:].lower() == ".package"):
            print(file)
            search_package(
                os.path.join(dirpath, file), filter_group=127, limit=64, unique=False
            )

    print_resources(min_files=2)


def find_conflicts_folder():
    clear()

    global resources
    resources = {
        b"NOCB": {},
        b"VAHB": {},
        b"BATT": {},
        b"sATT": {},
        b"#RTS": {},
        b"DJBO": {},
        b"fJBO": {},
    }

    folder = askdirectory()
    for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
        for file in (i for i in filenames if i[-8:].lower() == ".package"):
            search_package(os.path.join(dirpath, file), filter_group=127, limit=64)

    print_resources(min_files=2)


def find_dup_meshes():
    clear()

    global resources
    resources = {b"\x87\x86\x4f\xac": {}}

    for dirpath, dirnames, filenames in os.walk(folder_dl, topdown=False):
        for file in (i for i in filenames if i[-8:].lower() == ".package"):
            search_package(
                os.path.join(dirpath, file), filter_group=b"\x00\x00\x05\x1c", limit=0
            )

    print_resources(min_files=2)


def find_translations():
    clear()

    global resources
    resources = {b"SSTC": {}, b"sATT": {}, b"#RTS": {}}

    for dirpath, dirnames, filenames in os.walk(folder_dl, topdown=False):
        for file in (i for i in filenames if i[-8:].lower() == ".package"):
            search_strs(os.path.join(dirpath, file))

    print_resources()


def compare_packages(
    limit=float("inf"),
    min_files=1,
    max_files=float("inf"),
    min_versions=1,
    max_versions=float("inf"),
):
    clear()

    global resources
    resources = {b"NOCB": {}, b"VAHB": {}, b"\x76\x9a\x7e\x0c": {}}

    files = askopenfilenames(filetypes=[("TS2 packages", "*.package")])
    if len(files) < 2:
        return
    for file in files:
        search_package(file, limit=limit)
    print_resources(
        min_files=min_files,
        max_files=max_files,
        min_versions=min_versions,
        max_versions=max_versions,
    )


def compare_resources():
    clear()

    global resources
    file = askopenfilename(filetypes=[("Extracted resources", "*.simpe.xml")])
    if not file:
        return
    xmlroot = xml.etree.ElementTree.parse(file).getroot()
    rtype = bytes.fromhex(
        format(int(xmlroot.findall("./packedfile/type/number")[0].text), "08x")
    )[::-1]
    resources = {rtype: {}}
    classid = bytes.fromhex(
        format(int(xmlroot.findall("./packedfile/classid")[0].text), "08x")
    )[::-1]
    group = bytes.fromhex(
        format(int(xmlroot.findall("./packedfile/group")[0].text), "08x")
    )[::-1]
    instance = bytes.fromhex(
        format(int(xmlroot.findall("./packedfile/instance")[0].text), "08x")
    )[::-1]

    dirpath = os.path.dirname(os.path.realpath(file))
    file = xmlroot.findall("./packedfile")[0].attrib["name"]
    filename = os.path.join(dirpath, file)
    file = open(filename, "rb")
    resource = file.read()
    file.close()

    resources[rtype][group] = {}
    resources[rtype][group][classid] = {}
    resources[rtype][group][classid][instance] = Resource(
        resource[:64], rtype, group, instance, classid, "", resource
    )

    search_package(objects, group, instance)

    button_clear["state"] = NORMAL
    global search_results
    global scrollbar
    scrollbar = Scrollbar()
    scrollbar.pack(side=RIGHT, fill=Y)
    search_results = Text(root, yscrollcommand=scrollbar.set)
    resources[rtype][group][classid][instance].print_versions()
    search_results.insert(END, "\nSearch complete.")
    search_results.pack()
    scrollbar.config(command=search_results.yview)


def verify_filters(*args):
    if (
        search_type.get() == "Any"
        and len(search_group.get().split("x")[-1]) != 8
        and not len(search_instance.get().split("x")[-1]) in [4, 8]
    ):
        button_search["state"] = DISABLED
    else:
        button_search["state"] = NORMAL


def search():
    clear()

    global resources
    filter_type = search_type.get()
    if filter_type == "Any":
        filter_type = ""
        resources = {
            b"NOCB": {},
            b"VAHB": {},
            b"SSTC": {},
            b"DJBO": {},
            b"BATT": {},
            b"sATT": {},
            b"#RTS": {},
        }
    else:
        filter_type = filter_type.encode("utf-8")[::-1]
        try:
            filter_type = names2type[filter_type]
        except:
            pass
        resources = {filter_type: {}}

    target = search_target.get()
    if not target:
        pass
    elif filter_type == b"#RTS" or filter_type == b"SSTC" or filter_type == b"sATT":
        target = target.lower().encode("utf-8")
    elif len(target) % 2 != 0:
        target = ""
        search_target.set("")
    else:
        target = unhexlify(target)

    name = search_name.get()
    if not name:
        pass
    else:
        name = name.lower().encode("utf-8")

    filter_group = search_group.get().lower().split("x")[-1]
    if len(filter_group) == 8:
        filter_group = unhexlify(filter_group)[::-1]
    else:
        filter_group = ""
        search_group.set("")

    filter_instance = search_instance.get().lower().split("x")[-1]
    if len(filter_instance) == 4:
        filter_instance = "".join(["0000", filter_instance])
        search_instance.set(filter_instance)
        filter_instance = unhexlify(filter_instance)[::-1]
    elif len(filter_instance) == 8:
        filter_instance = unhexlify(filter_instance)[::-1]
    else:
        filter_instance = ""
        search_instance.set("")

    if var_file.get() == 4:
        folder = askdirectory()
        if not folder:
            return
        for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
            for file in (i for i in filenames if i[-8:].lower() == ".package"):
                search_package(
                    os.path.join(dirpath, file),
                    filter_group,
                    filter_instance,
                    target,
                    name,
                )

        print_resources()
    elif var_file.get() == 2:
        for dirpath, dirnames, filenames in os.walk(folder_dl, topdown=False):
            for file in (i for i in filenames if i[-8:].lower() == ".package"):
                search_package(
                    os.path.join(dirpath, file),
                    filter_group,
                    filter_instance,
                    target,
                    name,
                )

        print_resources()
    elif var_file.get() == 3:
        files = askopenfilenames()
        if len(files) == 0:
            return
        for file in files:
            search_package(file, filter_group, filter_instance, target, name)

        if len(files) > 1:
            print_resources()
        else:
            print_resources(printfiles=False)
    else:
        filename = objects
        search_package(filename, filter_group, filter_instance, target, name)

        print_resources(printfiles=False)


def get_config():
    file = os.path.join(os.path.dirname(__file__), "locations.txt")
    try:
        file = open(file, "r")
        contents = file.readlines()
        file.close()

        global objects
        global folder_dl

        objects = contents[0].rstrip("\n")
        folder_dl = contents[1].rstrip("\n")
    except:
        file = open(file, "w+")
        file.write("%s\n" % objects)
        file.write(folder_dl)
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

objects = os.path.join(
    "C:/Program Files (x86)/Origin Games/The Sims 2 Ultimate Collection/Fun with Pets/SP9/TSData/Res/Objects/",
    "objects.package",
)
folder_dl = os.path.join(
    "C:/Users/",
    "%s/" % getuser(),
    "Documents/EA Games/The Sims™ 2 Ultimate Collection/Downloads/",
)
get_config()
types2name = {
    b"dgP\xac": b"RDI3",
    b"\x87\x86\x4f\xac": b"CDMG",
    b"\x27\x3e\xcf\xeb": b"SPZG",
    b"\xb5\x80\x15\x8c": b"NTHX",
    b"\x42\xe3\xfe\xeb": b"SREV",
    b"\x76\x9a\x7e\x0c": b"GPJ",
}
names2type = dict()
for i in types2name:
    names2type[types2name[i]] = i

root = Tk()
root.geometry("640x480")
root.title("SiMidge")
menubar = Menu()
root["menu"] = menubar
menufind = Menu(menubar, tearoff=False)
menubar.add_cascade(label="Find", menu=menufind)
menuconflicts = Menu(menufind, tearoff=False)
menufind.add_cascade(label="Conflicts", menu=menuconflicts)
menuconflicts.add_command(label="All", command=find_conflicts)
menuconflicts.add_command(label="With File", command=find_conflicts_file)
menuconflicts.add_command(label="In Folder", command=find_conflicts_folder)
menufind.add_command(label="Duplicate Meshes", command=find_dup_meshes)
menufind.add_command(label="Translated / Empty Strings", command=find_translations)
menucompare = Menu(menubar, tearoff=False)
menubar.add_cascade(label="Compare", menu=menucompare)
menucompare.add_command(
    label="Packages (changed)", command=lambda: compare_packages(min_versions=2)
)
menucompare.add_command(
    label="Packages (unchanged)",
    command=lambda: compare_packages(max_versions=1, min_files=2),
)
menucompare.add_command(
    label="Packages (added/removed)",
    command=lambda: compare_packages(limit=64, max_files=1),
)
menucompare.add_command(label="Resources", command=compare_resources)

frame_top = Frame()
frame_left = Frame(frame_top)
frame_right = Frame(frame_top)

Label(frame_left, text="Type:").pack()
Label(frame_left, text="Group:").pack()
Label(frame_left, text="Instance:").pack()
Label(frame_left, text="Name:").pack()
Label(frame_left, text="Target:").pack()

search_type = StringVar()
search_type.set("Any")
search_type.trace("w", verify_filters)
OptionMenu(
    frame_right,
    search_type,
    "Any",
    "3IDR",
    "BCON",
    "BHAV",
    "CTSS",
    "GZPS",
    "JPG",
    "OBJD",
    "TREE",
    "TPRP",
    "TRCN",
    "TTAB",
    "TTAs",
    "STR#",
    "VERS",
    "XHTN",
).pack()

search_group = StringVar()
search_group.trace("w", verify_filters)
Entry(frame_right, textvariable=search_group, width=13).pack()

search_instance = StringVar()
search_instance.trace("w", verify_filters)
Entry(frame_right, textvariable=search_instance, width=13).pack()

search_name = StringVar()
Entry(frame_right, textvariable=search_name, width=13).pack()

search_target = StringVar()
Entry(frame_right, textvariable=search_target, width=13).pack()

frame_left.pack(side=LEFT)
frame_right.pack(side=LEFT)
frame_top.pack()

frame_radio = Frame()
var_file = IntVar()
var_file.set(1)
Radiobutton(frame_radio, text="Objects", variable=var_file, value=1).pack(side=LEFT)
Radiobutton(frame_radio, text="Downloads", variable=var_file, value=2).pack(side=LEFT)
Radiobutton(frame_radio, text="Other File(s)", variable=var_file, value=3).pack(
    side=LEFT
)
Radiobutton(frame_radio, text="Other Folder", variable=var_file, value=4).pack(
    side=LEFT
)
frame_radio.pack()

frame_bottom = Frame()
button_search = Button(frame_bottom, text="Search", command=search, state=DISABLED)
button_search.pack(side=LEFT)
button_clear = Button(frame_bottom, text="Clear Results", command=clear, state=DISABLED)
button_clear.pack(side=LEFT)
frame_bottom.pack()

root.mainloop()
