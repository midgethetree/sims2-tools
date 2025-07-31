"""Utilities for reading The Sims 2 dbpf (.package) files."""

from binascii import hexlify
from dataclasses import dataclass

LIMIT_FOR_CONFLICT: int = 64

types2name: dict[bytes, bytes] = {
    b"dgP\xac": b"RDI3",
    b"\x87\x86\x4f\xac": b"CDMG",
    b"\x27\x3e\xcf\xeb": b"SPZG",
    b"\xb5\x80\x15\x8c": b"NTHX",
    b"\x42\xe3\xfe\xeb": b"SREV",
    b"\x76\x9a\x7e\x0c": b"GPJ",
}


@dataclass
class ResourceHeader:
    """Class describing a resource within a dbpf file.

    Attributes:
        rtype: Type of resource.
        group: Group containing the resource.
        instance: Instance of the resource.
        classid: Class ID (aka instance (high)) of the resource.
        index: Location of the resource within package.
        length: Length of the resource.
    """

    def __init__(self, header: bytes) -> None:
        """Initialize a resource header from  bytes.

        Args:
            header: The raw resource header as seen in the dbpf file.
        """
        self.rtype: bytes = header[:4]
        self.rtype = types2name.get(self.rtype, self.rtype)
        self.group: bytes = header[4:8]
        self.instance: bytes = header[8:12]

        min_step_for_classid = 24
        if len(header) >= min_step_for_classid:
            self.classid: bytes = header[12:16]
        else:
            self.classid = b"0x00"

        self.index: int = int.from_bytes(header[-8:-4], byteorder="little")
        self.length: int = int.from_bytes(header[-4:], byteorder="little")


class Resource:  # pylint: disable=too-few-public-methods
    """Resource inside a dbpf file.

    Attributes:
        rtype: Type of resource.
        group: Group containing the resource.
        instance: Instance of the resource.
        classid: Class ID (aka instance (high)) of the resource.
        contents: Contents of the resource.
        name: Name of the resource.
    """

    def __init__(
        self,
        package: bytes,
        header: ResourceHeader,
        limit: float = float("inf"),
    ) -> None:
        """Initialize a resource within a package from its header.

        Args:
            package: Contents of dbpf file containing resource.
            header: Header describing resource.
            limit: Limit on how much of the contents of the resource to store.
        """
        self.rtype: bytes = header.rtype
        self.group: bytes = header.group
        self.instance: bytes = header.instance
        self.classid: bytes = header.classid

        if limit == 0:
            self.contents: bytes = package[header.index : header.index + 74]
        else:
            if limit == LIMIT_FOR_CONFLICT:
                self.contents = package[header.index : header.index + 74]
            else:
                self.contents = package[header.index : header.index + header.length]
            if int.from_bytes(self.contents[:4], byteorder="little") == header.length:
                self._decompress(limit)

        if limit == 0:
            self.name: str = ""
        else:
            try:
                self.name = self.contents[:64].split(b"\x00")[0].decode("utf-8")
            except UnicodeDecodeError:
                self.name = ""

    def _decompress(self, limit: float = float("inf")) -> None:
        x: bytes = b""
        index: int = 9
        while index < len(self.contents):
            if self.contents[index] < 128:  # noqa: PLR2004
                control: bytes = self.contents[index : index + 2]
                numplain: int = control[0] & 3
                numcopy: int = ((control[0] & 28) >> 2) + 3
                offset: int = ((control[0] & 96) << 3) + control[1] + 1
                index += 2
            elif self.contents[index] < 192:  # noqa: PLR2004
                control = self.contents[index : index + 3]
                numplain = ((control[1] & 192) >> 6) & 3
                numcopy = (control[0] & 63) + 4
                offset = ((control[1] & 63) << 8) + control[2] + 1
                index += 3
            elif self.contents[index] < 224:  # noqa: PLR2004
                control = self.contents[index : index + 4]
                numplain = control[0] & 3
                numcopy = ((control[0] & 12) << 6) + control[3] + 5
                offset = ((control[0] & 16) << 12) + (control[1] << 8) + control[2] + 1
                index += 4
            elif self.contents[index] < 252:  # noqa: PLR2004
                control = self.contents[index : index + 1]
                numplain = ((control[0] & 31) + 1) << 2
                numcopy = 0
                offset = 0
                index += 1
            else:
                control = self.contents[index : index + 1]
                numplain = control[0] & 3
                numcopy = 0
                offset = 0
                index += 1
            if numplain > 0:
                x += self.contents[index : index + numplain]
                index += numplain
            while numcopy > 0:
                x += bytes({x[-offset]})
                numcopy -= 1
            if len(x) >= limit:
                break
        self.contents = x

    def print(self) -> str:
        """Get information about the resource in a printable string.

        Returns:
            String describing the resource.
        """
        chars: str = ""
        if self.name is not None:
            chars += f"{self.name}\n"
        chars += f"File Type: {self.rtype[::-1].decode('utf-8')}\n"
        chars += f"Group ID: 0x{str(hexlify(self.group[::-1]))[2:-1]}\n"
        chars += f"Instance ID: 0x{str(hexlify(self.instance[::-1]))[2:-1]}\n"
        return chars


def get_headers(package: bytes) -> list[ResourceHeader]:
    """Get all headers in package.

    Args:
        package: Contents of dbpf file to search for headers.

    Returns:
        List of resource headers.
    """
    start: int = int.from_bytes(package[40:44], byteorder="little")
    stop: int = start + int.from_bytes(package[44:48], byteorder="little")
    step: int = int((stop - start) / int.from_bytes(package[36:40], byteorder="little"))
    return [ResourceHeader(package[x : x + step]) for x in range(start, stop, step)]
