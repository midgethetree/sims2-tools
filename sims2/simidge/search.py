from logging import Logger, getLogger
from pathlib import Path

from sims2.dbpf import Resource, ResourceHeader, get_headers

logger: Logger = getLogger(__name__)

GROUP_PREFIX: bytes = b"0x7F"


class CompResource(Resource):
    def __init__(
        self,
        package: bytes,
        header: ResourceHeader,
        limit: float = float("inf"),
    ) -> None:
        super().__init__(package, header, limit)
        self.files: list[str] = []
        self.versions: list[bytes] = []

    def add_version(self, filename: str, resource: bytes) -> None:
        self.files.append(filename)
        self.versions.append(resource)

    def print_files(self) -> str:
        chars: str = "Packages Using This Procedure:\n"
        for i in self.files:
            chars += f"\t{i}\n"
        return chars

    def print_versions(self) -> str:
        if len(self.versions) <= 1:
            return "No differences found."
        if len(self.versions[0]) > len(self.versions[1]):
            size: int = len(self.versions[1])
        else:
            size = len(self.versions[0])
        if self.rtype == b"NOCB":
            index: int = 66
        else:
            index = 64

        chars: str = "Changed Lines:\n"
        for i in range(index, size, 2):
            x = int.from_bytes(self.versions[0][i : i + 2], byteorder="little")
            if x >= 2**15:
                x -= 2**16 - 1
            y = int.from_bytes(self.versions[1][i : i + 2], byteorder="little")
            if y >= 2**15:
                y -= 2**16 - 1
            if x != y:
                chars += f"Line:\t{(i - index) // 2}\tValue:\t{y}\t->\t{x}\n"
        return chars


class ResourceSearch:
    def __init__(
        self,
        filter_type: list[bytes],
        *,
        filter_group: bytes | None = None,
        filter_instance: bytes | None = None,
        filter_name: str | list[str] | None = None,
        target: bytes | None = None,
    ) -> None:
        self._dict: dict[
            bytes,
            dict[bytes, dict[bytes, dict[bytes, CompResource]]],
        ] = {}
        for rtype in filter_type:
            self._dict[rtype] = {}

        self.filter_group: bytes | None = filter_group
        self.filter_instance: bytes | None = filter_instance
        self.filter_name: str | list[str] | None = filter_name
        self.target: bytes | None = target

    def validate_group(self, group: bytes) -> bool:
        if self.filter_group:
            if self.filter_group == GROUP_PREFIX:
                if group[-1] != int(GROUP_PREFIX, 0):
                    return False
            elif group != self.filter_group:
                return False
        return True

    def validate_instance(self, instance: bytes) -> bool:
        return not (self.filter_instance and instance != self.filter_instance)

    def validate_resource(self, resource: Resource) -> bool:
        if self.target:
            if resource.rtype in {b"#RTS", b"SSTC", b"sATT"}:
                if self.target not in resource.contents.lower():
                    return False
            elif self.target not in resource.contents:
                return False
        if self.filter_name:
            if isinstance(self.filter_name, str):
                if self.filter_name not in resource.name.lower():
                    return False
            elif (
                isinstance(self.filter_name, list) and resource.name in self.filter_name
            ):
                return False
        return True

    def search_folder(
        self,
        folder: Path | str,
        limit: float = float("inf"),
        *,
        unique: bool = True,
    ) -> None:
        if isinstance(folder, str):
            folder = Path(folder)

        rootdir: Path
        _dirs: list[str]
        files: list[str]
        for rootdir, _dirs, files in folder.walk(top_down=False):
            file: str
            for file in (i for i in files if i[-8:].lower() == ".package"):
                self.search_package(rootdir / file, limit=limit, unique=unique)

    def search_package(
        self,
        path: Path | str,
        limit: float = float("inf"),
        *,
        unique: bool = True,
    ) -> None:
        if isinstance(path, str):
            path = Path(path)

        with path.open("rb") as file:
            logger.debug("reading file: %s", path.name)
            package: bytes = file.read()

        if int.from_bytes(package[36:40], byteorder="little") == 0:
            logger.warning("empty file: %s", path.name)
            return

        header: ResourceHeader
        for header in get_headers(package):
            if header.rtype not in self._dict:
                continue
            if not self.validate_group(header.group):
                continue
            if not self.validate_instance(header.instance):
                continue

            resource: CompResource = CompResource(package, header, limit)

            if self.validate_resource(resource) is False:
                continue

            if (
                self.append(resource, path.name, resource.contents, unique=unique)
                is False
            ):
                break

    @staticmethod
    def validate_strs(resource: CompResource) -> bool:
        num: int = int.from_bytes(resource.contents[66:68], byteorder="little")
        strings: list[bytes] = resource.contents[68:].split(b"\x00\x01")
        if strings[-1][-2:] == b"\x00\x00":
            strings[-1] = strings[-1][:-2]

        lengths: list[int] = []
        string: bytes
        for string in strings:
            if len(string.rstrip(b"\x00").split(b"\x00")) > 1:
                num = 0
            lengths.append(len(string))

        return num == 0 or len(strings) != num or max(lengths) <= 1

    def search_strs(self, path: Path | str, limit: float = float("inf")) -> None:
        if isinstance(path, str):
            path = Path(path)

        with path.open("rb") as file:
            logger.debug("reading file: %s", path.name)
            package: bytes = file.read()

        if int.from_bytes(package[36:40], byteorder="little") == 0:
            logger.warning("empty file: %s", path.name)
            return

        header: ResourceHeader
        for header in get_headers(package):
            if header.rtype not in self._dict:
                continue
            if not self.validate_group(header.group):
                continue
            if not self.validate_instance(header.instance):
                continue

            resource: CompResource = CompResource(package, header, limit)

            if self.validate_resource(resource) is False:
                continue

            if self.validate_strs(resource):
                self.append(resource, path.name, resource.contents)

    def append(
        self,
        v: CompResource,
        filename: str,
        resource: bytes,
        *,
        unique: bool = True,
    ) -> bool:
        if not isinstance(v, CompResource):
            return False
        if v.rtype not in self._dict:
            return False

        if v.group not in self._dict[v.rtype]:
            self._dict[v.rtype][v.group] = {}
        if v.classid not in self._dict[v.rtype][v.group]:
            self._dict[v.rtype][v.group][v.classid] = {}
        if v.instance in self._dict[v.rtype][v.group][v.classid]:
            if filename in self._dict[v.rtype][v.group][v.classid][v.instance].files:
                return False
            self._dict[v.rtype][v.group][v.classid][v.instance].add_version(
                filename,
                resource,
            )
        elif unique:
            v.add_version(filename, resource)
            self._dict[v.rtype][v.group][v.classid][v.instance] = v
        return True

    def get_items(self) -> list[CompResource]:
        items: list[CompResource] = []
        for rtype in self._dict.values():
            for group in rtype.values():
                for classid in group.values():
                    items += list(classid.values())
        return items

    def print_resources(
        self,
        *,
        min_files: int = 1,
        max_files: float = float("inf"),
        min_versions: int = 1,
        max_versions: float = float("inf"),
        printfiles: bool = True,
    ) -> str:
        chars: str = ""
        count: int = 0
        resource: CompResource
        for resource in self.get_items():
            if (
                len(resource.files) >= min_files
                and len(resource.files) <= max_files
                and len(set(resource.versions)) >= min_versions
                and len(set(resource.versions)) <= max_versions
            ):
                chars += resource.print()
                if printfiles:
                    chars += resource.print_files()
                chars += "\n"
                count += 1
        chars += f"{count} results found."
        return chars

    def print_resource(
        self,
        rtype: bytes,
        group: bytes,
        classid: bytes,
        instance: bytes,
    ) -> str:
        chars = self._dict[rtype][group][classid][instance].print_versions()
        chars += "\nSearch complete."
        return chars
