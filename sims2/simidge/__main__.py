import xml.etree.ElementTree as ET
from binascii import unhexlify
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tkinter import (
    DISABLED,
    END,
    LEFT,
    NORMAL,
    RIGHT,
    Button,
    Entry,
    Frame,
    IntVar,
    Label,
    Menu,
    OptionMenu,
    Radiobutton,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    Y,
)
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames
from typing import Any

from sims2.common.logging import config_logging, handle_exception
from sims2.dbpf import LIMIT_FOR_CONFLICT, ResourceHeader
from sims2.simidge.config import config
from sims2.simidge.search import (
    GROUP_PREFIX,
    PrintResource,
    ResourceSearch,
)

INSTANCE_LENGTH: int = 8
INSTANCE_LENGTH_SHORT: int = 4


@dataclass
class SearchFilter:
    rtype: StringVar
    group: StringVar
    instance: StringVar
    name: StringVar
    target: StringVar


class SearchType(Enum):
    OBJECTS = 1
    DOWNLOADS = 2
    FILES = 3
    FOLDER = 4


class MainApp(Frame):
    def __init__(self, master: Tk) -> None:
        master.geometry("640x480")
        master.title("SiMidge")

        super().__init__(master)

        self._add_menubar(master)

        self.filter: SearchFilter = self._add_search_filter()
        self.var_file: IntVar = self._add_searchtype_radio()

        frame_bottom: Frame = Frame(self)
        self.button_search: Button = Button(
            frame_bottom,
            text="Search",
            command=self.search,
            state=DISABLED,
        )
        self.button_search.pack(side=LEFT)
        self.button_clear: Button = Button(
            frame_bottom,
            text="Clear Results",
            command=self.clear,
            state=DISABLED,
        )
        self.button_clear.pack(side=LEFT)
        frame_bottom.pack()

        scrollbar: Scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.search_results: Text = Text(
            self,
            yscrollcommand=scrollbar.set,
            state=DISABLED,
        )
        self.search_results.pack()
        scrollbar.config(command=self.search_results.yview)

        self.pack()

    def _add_menubar(self, master: Tk) -> None:
        menubar: Menu = Menu()
        master["menu"] = menubar
        menufind: Menu = Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Find", menu=menufind)
        menuconflicts: Menu = Menu(menufind, tearoff=False)
        menufind.add_cascade(label="Conflicts", menu=menuconflicts)
        menuconflicts.add_command(label="All", command=self.find_conflicts)
        menuconflicts.add_command(label="With File", command=self.find_conflicts_file)
        menuconflicts.add_command(label="In Folder", command=self.find_conflicts_folder)
        menufind.add_command(label="Duplicate Meshes", command=self.find_dup_meshes)
        menufind.add_command(
            label="Translated / Empty Strings",
            command=self.find_translations,
        )
        menucompare: Menu = Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Compare", menu=menucompare)
        menucompare.add_command(
            label="Packages (changed)",
            command=lambda: self.compare_packages(min_versions=2),
        )
        menucompare.add_command(
            label="Packages (unchanged)",
            command=lambda: self.compare_packages(max_versions=1, min_files=2),
        )
        menucompare.add_command(
            label="Packages (added/removed)",
            command=lambda: self.compare_packages(
                limit=LIMIT_FOR_CONFLICT,
                max_files=1,
            ),
        )
        menucompare.add_command(label="Resources", command=self.compare_resources)

    def _add_search_filter(
        self,
    ) -> SearchFilter:
        frame_top: Frame = Frame(self)
        frame_left: Frame = Frame(frame_top)
        frame_right: Frame = Frame(frame_top)

        Label(frame_left, text="Type:").pack()
        Label(frame_left, text="Group:").pack()
        Label(frame_left, text="Instance:").pack()
        Label(frame_left, text="Name:").pack()
        Label(frame_left, text="Target:").pack()

        search_type: StringVar = StringVar()
        search_type.set("Any")
        search_type.trace("w", self._verify_filters)
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

        search_group: StringVar = StringVar()
        search_group.trace("w", self._verify_filters)
        Entry(frame_right, textvariable=search_group, width=13).pack()

        search_instance: StringVar = StringVar()
        search_instance.trace("w", self._verify_filters)
        Entry(frame_right, textvariable=search_instance, width=13).pack()

        search_name: StringVar = StringVar()
        Entry(frame_right, textvariable=search_name, width=13).pack()

        search_target: StringVar = StringVar()
        Entry(frame_right, textvariable=search_target, width=13).pack()

        frame_left.pack(side=LEFT)
        frame_right.pack(side=LEFT)
        frame_top.pack()

        return SearchFilter(
            search_type,
            search_group,
            search_instance,
            search_name,
            search_target,
        )

    def _add_searchtype_radio(self) -> IntVar:
        frame_radio: Frame = Frame(self)
        var_file: IntVar = IntVar()
        var_file.set(SearchType.OBJECTS.value)
        Radiobutton(
            frame_radio,
            text="Objects",
            variable=var_file,
            value=SearchType.OBJECTS.value,
        ).pack(side=LEFT)
        Radiobutton(
            frame_radio,
            text="Downloads",
            variable=var_file,
            value=SearchType.DOWNLOADS.value,
        ).pack(side=LEFT)
        Radiobutton(
            frame_radio,
            text="Other File(s)",
            variable=var_file,
            value=SearchType.FILES.value,
        ).pack(side=LEFT)
        Radiobutton(
            frame_radio,
            text="Other Folder",
            variable=var_file,
            value=SearchType.FOLDER.value,
        ).pack(side=LEFT)
        frame_radio.pack()

        return var_file

    def clear(self) -> None:
        self.button_clear["state"] = DISABLED
        self.search_results["state"] = NORMAL
        self.search_results.delete("1.0", END)

    def print_search_results(self, chars: str) -> None:
        self.button_clear["state"] = NORMAL
        self.search_results["state"] = NORMAL
        self.search_results.insert(END, chars)
        self.search_results["state"] = DISABLED

    def find_conflicts(self) -> None:
        self.clear()

        resources: ResourceSearch = ResourceSearch(
            [b"NOCB", b"VAHB", b"SPZG", b"BATT", b"sATT", b"#RTS", b"DJBO", b"fJBO"],
            filter_group=GROUP_PREFIX,
        )
        resources.search_folder(
            config.get("paths", "downloads"),
            limit=LIMIT_FOR_CONFLICT,
        )

        self.print_search_results(resources.print_resources(min_files=2))

    def find_conflicts_file(self) -> None:
        self.clear()

        mod = askopenfilename(
            initialdir=config.get("paths", "downloads"),
            filetypes=[("TS2 packages", "*.package")],
        )
        if not mod:
            return

        resources: ResourceSearch = ResourceSearch(
            [b"NOCB", b"VAHB", b"BATT", b"sATT", b"#RTS", b"DJBO", b"fJBO"],
            filter_group=GROUP_PREFIX,
        )
        resources.search_folder(
            config.get("paths", "downloads"),
            limit=LIMIT_FOR_CONFLICT,
            unique=False,
        )

        self.print_search_results(resources.print_resources(min_files=2))

    def find_conflicts_folder(self) -> None:
        self.clear()

        resources: ResourceSearch = ResourceSearch(
            [b"NOCB", b"VAHB", b"BATT", b"sATT", b"#RTS", b"DJBO", b"fJBO"],
            filter_group=GROUP_PREFIX,
        )
        resources.search_folder(
            askdirectory(initialdir=config.get("paths", "downloads")),
            limit=LIMIT_FOR_CONFLICT,
        )

        self.print_search_results(resources.print_resources(min_files=2))

    def find_dup_meshes(self) -> None:
        self.clear()

        resources: ResourceSearch = ResourceSearch(
            [b"CDMG"],
            filter_group=b"\x00\x00\x05\x1c",
        )
        resources.search_folder(config.get("paths", "downloads"), limit=0)

        self.print_search_results(resources.print_resources(min_files=2))

    def find_translations(self) -> None:
        self.clear()

        resources: ResourceSearch = ResourceSearch(
            [b"SSTC", b"sATT", b"#RTS"],
            filter_name=["Lua Scripts", "Lua Script", "More Lua Scripts"],
        )

        rootdir: Path
        _dirs: list[str]
        files: list[str]
        for rootdir, _dirs, files in Path(config.get("paths", "downloads")).walk(
            top_down=False,
        ):
            file: str
            for file in (i for i in files if i[-8:].lower() == ".package"):
                resources.search_strs(rootdir / file)

        self.print_search_results(resources.print_resources())

    def compare_packages(
        self,
        *,
        limit: float = float("inf"),
        min_files: int = 1,
        max_files: float = float("inf"),
        min_versions: int = 1,
        max_versions: float = float("inf"),
    ) -> None:
        self.clear()

        resources: ResourceSearch = ResourceSearch([b"NOCB", b"VAHB", b"GPJ"])

        files = askopenfilenames(
            initialdir=config.get("paths", "downloads"),
            filetypes=[("TS2 packages", "*.package")],
        )
        if len(files) <= 1:
            return
        file: str
        for file in files:
            resources.search_package(file, limit=limit)

        self.print_search_results(
            resources.print_resources(
                min_files=min_files,
                max_files=max_files,
                min_versions=min_versions,
                max_versions=max_versions,
            ),
        )

    def compare_resources(self) -> None:
        self.clear()

        filename: str = askopenfilename(
            initialdir=config.get("paths", "downloads"),
            filetypes=[("Extracted resources", "*.simpe.xml")],
        )
        if not filename:
            return
        xmlroot: ET.Element = ET.parse(filename).getroot()

        def get_bytes_from_xml(path: str) -> bytes | None:
            xmltxt: str | None = xmlroot.findall(f"./packedfile/{path}")[0].text
            if xmltxt is None:
                return None
            return bytes.fromhex(format(int(xmltxt), "08x"))[::-1]

        rtype: bytes | None = get_bytes_from_xml("type/number")
        if rtype is None:
            return
        classid: bytes | None = get_bytes_from_xml("classid")
        if classid is None:
            return
        group: bytes | None = get_bytes_from_xml("group")
        if group is None:
            return
        instance: bytes | None = get_bytes_from_xml("instance")
        if instance is None:
            return

        path: Path = (
            Path(filename).parent / xmlroot.findall("./packedfile")[0].attrib["name"]
        )
        with path.open("rb") as file:
            resource: bytes = file.read()

        resources: ResourceSearch = ResourceSearch(
            [rtype],
            filter_group=group,
            filter_instance=instance,
        )
        resources.append(
            PrintResource(
                resource,
                ResourceHeader(
                    b"".join(
                        [
                            rtype,
                            group,
                            instance,
                            classid,
                            int().to_bytes(4, "little"),
                            len(resource).to_bytes(4, "little"),
                        ],
                    ),
                ),
            ),
            "",
            resource,
        )

        resources.search_package(config.get("paths", "objects"))

        self.print_search_results(
            resources.print_resource(rtype, group, classid, instance),
        )

    def _verify_filters(self, *_args: Any) -> None:
        if (
            self.filter.rtype.get() == "Any"
            and len(self.filter.group.get().split("x")[-1]) != INSTANCE_LENGTH
            and len(self.filter.instance.get().split("x")[-1])
            not in {INSTANCE_LENGTH, INSTANCE_LENGTH_SHORT}
        ):
            self.button_search["state"] = DISABLED
        else:
            self.button_search["state"] = NORMAL

    def _get_search_type(self) -> tuple[bytes, list[bytes]]:
        stype: str = self.filter.rtype.get()
        if stype == "Any":
            return b"", [
                b"NOCB",
                b"VAHB",
                b"SSTC",
                b"DJBO",
                b"BATT",
                b"sATT",
                b"#RTS",
            ]
        rtype = stype.encode("utf-8")[::-1]
        filter_type = [rtype]
        return rtype, filter_type

    def _get_search_target(self, rtype: bytes) -> bytes | None:
        target: str = self.filter.target.get()
        if not target:
            return None
        if rtype in {b"#RTS", b"SSTC", b"sATT"}:
            return target.lower().encode("utf-8")
        if len(target) % 2 != 0:
            self.filter.target.set("")
            return None
        return unhexlify(target)

    def _get_search_name(self) -> str | None:
        name: str = self.filter.name.get()
        if name:
            return name.lower()
        return None

    def _get_search_group(self) -> bytes | None:
        filter_group: str = self.filter.group.get().lower().split("x")[-1]
        if len(filter_group) == INSTANCE_LENGTH:
            return unhexlify(filter_group)[::-1]
        self.filter.group.set("")
        return None

    def _get_search_instance(self) -> bytes | None:
        filter_instance: str = self.filter.instance.get().lower().split("x")[-1]
        if len(filter_instance) == INSTANCE_LENGTH_SHORT:
            filter_instance = f"0000{filter_instance}"
            self.filter.instance.set(filter_instance)
            return unhexlify(filter_instance)[::-1]
        if len(filter_instance) == INSTANCE_LENGTH:
            return unhexlify(filter_instance)[::-1]
        self.filter.instance.set("")
        return None

    def search(self) -> None:
        self.clear()

        rtype: bytes
        filter_type: list[bytes]
        rtype, filter_type = self._get_search_type()
        target: bytes | None = self._get_search_target(rtype)
        filter_name: str | None = self._get_search_name()
        filter_group: bytes | None = self._get_search_group()
        filter_instance: bytes | None = self._get_search_instance()

        resources: ResourceSearch = ResourceSearch(
            filter_type,
            filter_group=filter_group,
            filter_instance=filter_instance,
            filter_name=filter_name,
            target=target,
        )

        if self.var_file.get() == SearchType.FOLDER.value:
            folder: str = askdirectory()
            if not folder:
                return
            resources.search_folder(folder)
            self.print_search_results(resources.print_resources())
        elif self.var_file.get() == SearchType.DOWNLOADS.value:
            resources.search_folder(config.get("paths", "downloads"))
            self.print_search_results(resources.print_resources())
        elif self.var_file.get() == SearchType.FILES.value:
            files = askopenfilenames(initialdir=config.get("paths", "downloads"))
            if len(files) == 0:
                return

            file: str
            for file in files:
                resources.search_package(file)

            if len(files) > 1:
                self.print_search_results(resources.print_resources())
            else:
                self.print_search_results(resources.print_resources(printfiles=False))
        else:
            resources.search_package(config.get("paths", "objects"))
            self.print_search_results(resources.print_resources(printfiles=False))


def main() -> None:
    config_logging()

    root: Tk = Tk()
    _app: MainApp = MainApp(root)

    root.report_callback_exception = handle_exception

    root.mainloop()
