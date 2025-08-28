"""A tool for searching in .package files."""

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import xml.etree.ElementTree as ET
from binascii import unhexlify
from dataclasses import dataclass
from enum import Enum
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, override

from sims2.common.logging import config_logging, handle_exception
from sims2.dbpf import LIMIT_FOR_CONFLICT, ResourceHeader
from sims2.simidge._config import config, save_config
from sims2.simidge.search import (
    GROUP_PREFIX,
    CompResource,
    ResourceSearch,
)

logger: Logger = getLogger(__name__)

INSTANCE_LENGTH: int = 8
INSTANCE_LENGTH_SHORT: int = 4


@dataclass
class SearchFilter:
    """Filters to use when searching a package file.

    Attributes:
        rtype: Type of resources to search for.
        group: Group of resources to search for.
        instance: Instance of resources to search for.
        name: String to search for in resource names.
        target: String to search for in resource contents.
    """

    rtype: tk.StringVar
    group: tk.StringVar
    instance: tk.StringVar
    name: tk.StringVar
    target: tk.StringVar


class SearchType(Enum):
    """Enum describing where to search."""

    OBJECTS = 1
    DOWNLOADS = 2
    FILES = 3
    FOLDER = 4


class MainApp(tk.Frame):
    """The main GUI application."""

    def __init__(self, master: tk.Tk) -> None:
        """Initialize the main GUI application with a Tkinter root.

        Args:
            master: Tkinter widget representing window.
        """
        master.geometry("640x480")
        master.title("SiMidge")

        super().__init__(master)

        self._add_menubar(master)

        self.filter: SearchFilter = self._add_search_filter()
        self.var_file: tk.IntVar = self._add_searchtype_radio()

        frame_bottom: tk.Frame = tk.Frame(self)
        self.button_search: tk.Button = tk.Button(
            frame_bottom,
            text="Search",
            command=self.search,
            state=tk.DISABLED,
        )
        self.button_search.pack(side=tk.LEFT)
        self.button_clear: tk.Button = tk.Button(
            frame_bottom,
            text="Clear Results",
            command=self.clear_search_results,
            state=tk.DISABLED,
        )
        self.button_clear.pack(side=tk.LEFT)
        frame_bottom.pack()

        scrollbar: tk.Scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_results: tk.Text = tk.Text(
            self,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
        )
        self.search_results.pack()
        _ = scrollbar.config(command=self.search_results.yview)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]

        self.pack()

    def _add_menubar(self, master: tk.Tk) -> None:
        menubar: tk.Menu = tk.Menu()
        master["menu"] = menubar
        menufind: tk.Menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Find", menu=menufind)
        menuconflicts: tk.Menu = tk.Menu(menufind, tearoff=False)
        menufind.add_cascade(label="Conflicts", menu=menuconflicts)
        menuconflicts.add_command(label="All", command=self.find_conflicts)
        menuconflicts.add_command(label="With File", command=self.find_conflicts_file)
        menuconflicts.add_command(label="In Folder", command=self.find_conflicts_folder)
        menufind.add_command(label="Duplicate Meshes", command=self.find_dup_meshes)
        menufind.add_command(
            label="Translated / Empty Strings",
            command=self.find_translations,
        )
        menucompare: tk.Menu = tk.Menu(menubar, tearoff=False)
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
        menubar.add_command(label="Settings", command=self.settings)

    def _add_search_filter(
        self,
    ) -> SearchFilter:
        frame_top: tk.Frame = tk.Frame(self)
        frame_left: tk.Frame = tk.Frame(frame_top)
        frame_right: tk.Frame = tk.Frame(frame_top)

        tk.Label(frame_left, text="Type:").pack()
        tk.Label(frame_left, text="Group:").pack()
        tk.Label(frame_left, text="Instance:").pack()
        tk.Label(frame_left, text="Name:").pack()
        tk.Label(frame_left, text="Target:").pack()

        search_type: tk.StringVar = tk.StringVar()
        search_type.set("Any")
        _ = search_type.trace_add("write", self._verify_filters)
        tk.OptionMenu(
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

        search_group: tk.StringVar = tk.StringVar()
        _ = search_group.trace_add("write", self._verify_filters)
        tk.Entry(frame_right, textvariable=search_group, width=13).pack()

        search_instance: tk.StringVar = tk.StringVar()
        _ = search_instance.trace_add("write", self._verify_filters)
        tk.Entry(frame_right, textvariable=search_instance, width=13).pack()

        search_name: tk.StringVar = tk.StringVar()
        tk.Entry(frame_right, textvariable=search_name, width=13).pack()

        search_target: tk.StringVar = tk.StringVar()
        tk.Entry(frame_right, textvariable=search_target, width=13).pack()

        frame_left.pack(side=tk.LEFT)
        frame_right.pack(side=tk.LEFT)
        frame_top.pack()

        return SearchFilter(
            search_type,
            search_group,
            search_instance,
            search_name,
            search_target,
        )

    def _add_searchtype_radio(self) -> tk.IntVar:
        frame_radio: tk.Frame = tk.Frame(self)
        var_file: tk.IntVar = tk.IntVar()
        var_file.set(SearchType.OBJECTS.value)
        tk.Radiobutton(
            frame_radio,
            text="Objects",
            variable=var_file,
            value=SearchType.OBJECTS.value,
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            frame_radio,
            text="Downloads",
            variable=var_file,
            value=SearchType.DOWNLOADS.value,
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            frame_radio,
            text="Other File(s)",
            variable=var_file,
            value=SearchType.FILES.value,
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            frame_radio,
            text="Other Folder",
            variable=var_file,
            value=SearchType.FOLDER.value,
        ).pack(side=tk.LEFT)
        frame_radio.pack()

        return var_file

    def clear_search_results(self) -> None:
        """Clear search results."""
        self.button_clear["state"] = tk.DISABLED
        self.search_results["state"] = tk.NORMAL
        self.search_results.delete("1.0", tk.END)

    def print_search_results(self, chars: str) -> None:
        """Print search results."""
        self.button_clear["state"] = tk.NORMAL
        self.search_results["state"] = tk.NORMAL
        self.search_results.insert(tk.END, chars)
        self.search_results["state"] = tk.DISABLED

    def find_conflicts(self) -> None:
        """Find conflicting mods in downloads folder."""
        self.clear_search_results()

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
        """Find mods conflicting with a selected package."""
        self.clear_search_results()

        mod = tkinter.filedialog.askopenfilename(
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
        """Find conflicting mods in selected folder."""
        self.clear_search_results()

        resources: ResourceSearch = ResourceSearch(
            [b"NOCB", b"VAHB", b"BATT", b"sATT", b"#RTS", b"DJBO", b"fJBO"],
            filter_group=GROUP_PREFIX,
        )
        resources.search_folder(
            tkinter.filedialog.askdirectory(
                initialdir=config.get("paths", "downloads"),
            ),
            limit=LIMIT_FOR_CONFLICT,
        )

        self.print_search_results(resources.print_resources(min_files=2))

    def find_dup_meshes(self) -> None:
        """Find duplicate meshes in downloads folder."""
        self.clear_search_results()

        resources: ResourceSearch = ResourceSearch(
            [b"CDMG"],
            filter_group=b"\x00\x00\x05\x1c",
        )
        resources.search_folder(config.get("paths", "downloads"), limit=0)

        self.print_search_results(resources.print_resources(min_files=2))

    def find_translations(self) -> None:
        """Find string resources that have translations, empty strings, descriptions, or can otherwise be cleaned by SimPE."""
        self.clear_search_results()

        resources: ResourceSearch = ResourceSearch(
            [b"SSTC", b"sATT", b"#RTS"],
            filter_name=["Lua Scripts", "Lua Script", "More Lua Scripts"],
        )

        rootdir: Path
        files: list[str]
        for rootdir, _, files in Path(config.get("paths", "downloads")).walk(
            top_down=False,
        ):
            file: str
            for file in (i for i in files if i[-8:].lower() == ".package"):
                resources.search_strs(rootdir / file)

        self.print_search_results(resources.print_resources())

    def compare_packages(
        self,
        *,
        limit: float | None = None,
        min_files: int = 1,
        max_files: float | None = None,
        min_versions: int = 1,
        max_versions: float | None = None,
    ) -> None:
        """Compare resources in selected packages."""
        self.clear_search_results()

        resources: ResourceSearch = ResourceSearch([b"NOCB", b"VAHB", b"GPJ"])

        files = tkinter.filedialog.askopenfilenames(
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
        """Compare selected resource with original copy in objects.package."""
        self.clear_search_results()

        filename: str = tkinter.filedialog.askopenfilename(
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
            logger.debug("reading file: %s", path.name)
            resource: bytes = file.read()

        resources: ResourceSearch = ResourceSearch(
            [rtype],
            filter_group=group,
            filter_instance=instance,
        )
        _ = resources.append(
            CompResource(
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

    def _verify_filters(self, *_: Any) -> None:  # pyright: ignore[reportExplicitAny]
        if (
            self.filter.rtype.get() == "Any"
            and len(self.filter.group.get().split("x")[-1]) != INSTANCE_LENGTH
            and len(self.filter.instance.get().split("x")[-1])
            not in {INSTANCE_LENGTH, INSTANCE_LENGTH_SHORT}
        ):
            self.button_search["state"] = tk.DISABLED
        else:
            self.button_search["state"] = tk.NORMAL

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
        """Search for resources in package file(s)."""
        self.clear_search_results()

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
            folder: str = tkinter.filedialog.askdirectory()
            if not folder:
                return
            resources.search_folder(folder)
            self.print_search_results(resources.print_resources())
        elif self.var_file.get() == SearchType.DOWNLOADS.value:
            resources.search_folder(config.get("paths", "downloads"))
            self.print_search_results(resources.print_resources())
        elif self.var_file.get() == SearchType.FILES.value:
            files = tkinter.filedialog.askopenfilenames(
                initialdir=config.get("paths", "downloads"),
            )
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

    def settings(self) -> None:
        """Open settings dialog for SiMidge."""
        _ = SettingsDialog(self.master, title="Settings")
        return SettingsDialog.result  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]


class SettingsDialog(tkinter.simpledialog.Dialog):
    """Class to open settings dialog."""

    @override
    def body(self, master: tk.Frame) -> tk.Entry:
        """Create settings dialog body.

        Args:
            master: Tkinter frame containing this dialog.

        Returns:
            Widget to first focus.
        """
        tk.Label(master, text="Downloads:").grid(row=0)
        tk.Label(master, text="Objects:").grid(row=1)

        self.downloads: tk.StringVar = tk.StringVar(  # pyright: ignore[reportUninitializedInstanceVariable]
            value=config.get("paths", "downloads"),
        )
        self.objects: tk.StringVar = tk.StringVar(value=config.get("paths", "objects"))  # pyright: ignore[reportUninitializedInstanceVariable]

        e1 = tk.Entry(master, textvariable=self.downloads)
        e2 = tk.Entry(master, textvariable=self.objects)

        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)

        tk.Button(master, command=self.set_downloads).grid(row=0, column=2)
        tk.Button(master, command=self.set_objects).grid(row=1, column=2)

        return e1

    @override
    def validate(self) -> bool:
        """Validate config values.

        Returns:
            Is valid.
        """
        if not Path(self.downloads.get()).is_dir():
            _ = tkinter.messagebox.showwarning(
                "Illegal value",
                "Not a valid downloads directory.\nPlease try again",
                parent=self,
            )
            return False

        objects: str = self.objects.get()
        if not Path(objects).is_file() or not objects.endswith(".package"):
            _ = tkinter.messagebox.showwarning(
                "Illegal value",
                "Not a valid objects.package.\nPlease try again",
                parent=self,
            )
            return False

        return True

    @override
    def apply(self) -> None:
        """Process settings data."""
        config.set("paths", "downloads", self.downloads.get())
        config.set("paths", "objects", self.objects.get())
        save_config()

    def set_downloads(self) -> None:
        """Configure downloads path."""
        path: str = tkinter.filedialog.askdirectory(
            initialdir=config.get("paths", "downloads"),
        )
        if path:
            self.downloads.set(path)

    def set_objects(self) -> None:
        """Configure objects.package path."""
        path: str = tkinter.filedialog.askopenfilename(
            initialdir=Path(config.get("paths", "objects")).parent,
        )
        if path:
            self.objects.set(path)


def main() -> None:
    """Main function for running SiMidge."""
    config_logging("simidge")

    root: tk.Tk = tk.Tk()
    _ = MainApp(root)

    root.report_callback_exception = handle_exception

    root.mainloop()
