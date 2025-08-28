"""Search neighborhood package for information about sims and families."""

import xml.etree.ElementTree as ET
from binascii import hexlify
from logging import Logger, getLogger
from pathlib import Path

from sims2.dbpf import Resource, ResourceHeader, get_headers
from sims2.simtracker._config import config, config_traits
from sims2.simtracker.sim import Family, Sim, SupernaturalFlags

logger: Logger = getLogger(__name__)

sims: dict[bytes, Sim] = {}
families: dict[bytes, Family] = {}


def search_nhood(nhood: str, nhoods_folder: Path) -> None:
    """Search neighborhood for information about sims and families.

    Args:
        nhood: Identifier of neighborhood.
        nhoods_folder: Folder containing neighborhood.
    """
    sims.clear()
    families.clear()

    directory: Path = nhoods_folder / nhood

    with (directory / f"{nhood}_Neighborhood.package").open("rb") as file:
        logger.debug("searching neighborhood %s", nhood)
        package: bytes = file.read()

    guid2nid: dict[bytes, bytes] = _search_nhood_pkg(nhood, package)

    _search_nhood_chars(directory, guid2nid)
    _search_nhood_lots(directory, nhood)


def _search_nhood_pkg(nhood: str, package: bytes) -> dict[bytes, bytes]:
    nids: list[bytes] = []
    guid2nid: dict[bytes, bytes] = {}

    inventory: Resource | None = None
    strs: list[ResourceHeader] = []
    owners: list[bytes] = []
    dnas: list[ResourceHeader] = []
    wants: list[ResourceHeader] = []

    header: ResourceHeader
    for header in get_headers(package):
        match header.rtype:
            case b"HBGN":
                inventory = Resource(package, header)
            case b"\xfb\x2e\xce\xaa":
                resource: bytes = Resource(package, header).contents
                if int.from_bytes(resource[134:136], byteorder="little") > 0 or (
                    nhood != "N001"
                    and int.from_bytes(resource[148:150], byteorder="little") > 0
                ):
                    sims[resource[474:476]] = Sim(resource)
                    guid2nid[resource[476:480]] = resource[474:476]
                    nids.append(resource[474:476])
            case b"IMAF":
                families[header.instance[:2]] = Family(
                    int.from_bytes(
                        Resource(package, header).contents[12:16],
                        byteorder="little",
                    ),
                )
            case b"#RTS":
                strs.append(header)
            case b"\xe7\x99\xf9\x0b":
                owners.append(Resource(package, header).contents[-25:-23])
            case b"\x3f\xe3\xfe\xeb":
                dnas.append(header)
            case b"\x8e\x54\x95\xcd":
                wants.append(header)
            case _:
                pass

    _search_nhood_strs(strs, package)
    _search_nhood_business_owners(owners)
    _search_nhood_sdna(dnas, package)
    _search_nhood_wants(wants, package)
    _search_nhood_inventory(inventory, nids)

    return guid2nid


def _search_nhood_strs(strs: list[ResourceHeader], package: bytes) -> None:
    header: ResourceHeader
    for header in strs:
        i: bytes = header.instance[:2]
        if i in families:
            resource: bytes = Resource(package, header).contents
            name: list[bytes] = resource[68:].split(b"\x01")
            families[i].name = name[1].split(b"\x00")[0].decode("utf-8")
            desc_index: int = 2
            if len(name) > desc_index:
                families[i].desc = name[desc_index].split(b"\x00")[0].decode("utf-8")


def _search_nhood_business_owners(owners: list[bytes]) -> None:
    owner: bytes
    for owner in owners:
        if owner != b"\x00\x00" and owner in sims and not sims[owner].job.career:
            sims[owner].job.career = "OFB Business"
            sims[owner].job.title = "Owner"


def _search_nhood_sdna(dnas: list[ResourceHeader], package: bytes) -> None:
    header: ResourceHeader
    for header in dnas:
        nid: bytes = header.instance[:2]
        if nid not in sims or sims[nid].species != b"\x00\x00":
            continue
        resource: bytes = Resource(package, header).contents
        if resource[:4] == b"\xe0\x50\xe7\xcb":
            sims[nid].genes.skin.dominant = config.get(
                "genetics.skins",
                resource.split(b"6$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
            sims[nid].genes.skin.recessive = config.get(
                "genetics.skins",
                resource.split(b"268435462$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
            sims[nid].genes.skin.range1 = config.get(
                "genetics.skins",
                resource.split(b"2$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
            sims[nid].genes.skin.range2 = config.get(
                "genetics.skins",
                resource.split(b"268435458$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
            sims[nid].genes.hair.dominant = config.get(
                "genetics.hairs",
                resource.split(b"1$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
            sims[nid].genes.hair.recessive = config.get(
                "genetics.hairs",
                resource.split(b"268435457$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
            sims[nid].genes.eyes.dominant = config.get(
                "genetics.eyes",
                resource.split(b"3$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
            sims[nid].genes.eyes.recessive = config.get(
                "genetics.eyes",
                resource.split(b"268435459$\x00\x00\x00")[1][:36].decode("utf-8"),
                fallback="Custom",
            )
        else:
            xmlroot: ET.Element = ET.fromstring(resource.decode("utf-8"))

            def get_txt_from_xml(section: str, xmlroot: ET.Element, key: int) -> str:
                xmltree: ET.Element | None = xmlroot.find(f"./AnyString[@key='{key}']")
                if xmltree is None:
                    return "Custom"
                if xmltree.text is None:
                    return "Custom"
                return config.get(
                    f"genetics.{section}",
                    xmltree.text,
                    fallback="Custom",
                )

            sims[nid].genes.skin.dominant = get_txt_from_xml("skins", xmlroot, 6)
            sims[nid].genes.skin.recessive = get_txt_from_xml(
                "skins",
                xmlroot,
                268435462,
            )
            sims[nid].genes.skin.range1 = get_txt_from_xml("skins", xmlroot, 2)
            sims[nid].genes.skin.range2 = get_txt_from_xml("skins", xmlroot, 268435458)
            sims[nid].genes.hair.dominant = get_txt_from_xml("hairs", xmlroot, 1)
            sims[nid].genes.hair.recessive = get_txt_from_xml(
                "hairs",
                xmlroot,
                268435457,
            )
            sims[nid].genes.eyes.dominant = get_txt_from_xml("eyes", xmlroot, 3)
            sims[nid].genes.eyes.recessive = get_txt_from_xml(
                "eyes",
                xmlroot,
                268435459,
            )


def _search_nhood_wants(wants: list[ResourceHeader], package: bytes) -> None:
    header: ResourceHeader
    for header in wants:
        nid: bytes = header.instance[:2]
        if (
            nid not in sims
            or sims[nid].species != b"\x00\x00"
            or sims[nid].age < config.getint("ages", "teen")
        ):
            continue
        sims[nid].ltw = config.get(
            "ltws",
            str(hexlify(Resource(package, header).contents[14:18])),
            fallback="Custom",
        )


def _search_nhood_inventory(inventory: Resource | None, nids: list[bytes]) -> None:
    if inventory is None:
        return

    try:
        resource: bytes = inventory.contents[
            inventory.contents.index(b"\xff\x7f\x00\x00\xbe\x00\x00\x00") :
        ]
    except (KeyError, ValueError):
        resource = inventory.contents
    res: list[bytes] = resource.split(b"\x00\x00\xbe\x00\x00\x00")
    nid: bytes = nids[0]
    for i in range(2, len(res)):
        if (nids.index(nid) < len(nids) - 1) and res[i - 1][-2:] == nids[
            nids.index(nid) + 1
        ]:
            nid = res[i - 1][-2:]
        if sims[nid].species != b"\x00\x00":
            continue
        _search_sim_inventory(res[i], sims[nid])

    sim: Sim
    for sim in sims.values():
        sim.set_aspirations()
        if config_traits:
            for _ in range(len(sim.traits), 5):
                sim.traits.append("")


def _search_sim_inventory(inventory: bytes, sim: Sim) -> None:
    if b"\x89\x89\xd0\x53" in inventory:
        index: int = inventory.index(b"\x89\x89\xd0\x53") + 18
        sim.asp[1] = int.from_bytes(inventory[index : index + 2], byteorder="little")

    if config_traits:
        items = inventory.split(b"\xbb\x87\x00")
        if len(items) > 1:
            item: bytes
            for item in items:
                sim.traits.append(
                    config.get("traits", str(hexlify(item[-1:])), fallback="Unknown"),
                )

        items = inventory.split(b"\xbb\x8e\x00")
        for item in items:
            match item[-1:]:
                case b"\x8b\x27":
                    sim.spnflags += SupernaturalFlags.MERMAID
                case b"\x75\x27":
                    sim.spnflags += SupernaturalFlags.GENIE
                case b"\x76\x27":
                    sim.spnflags += SupernaturalFlags.FAIRY
                case b"\x9b\x27":
                    sim.spnflags += SupernaturalFlags.GHOST
                case _:
                    pass


def _search_nhood_chars(directory: Path, guid2nid: dict[bytes, bytes]) -> None:
    char: Path
    for char in (directory / "Characters").iterdir():
        with char.open("rb") as file:
            logger.debug("reading file: %s", char.name)
            package: bytes = file.read()

        name: list[bytes] = []
        guid: bytes = b""

        header: ResourceHeader
        for header in get_headers(package):
            match header.rtype:
                case b"DJBO":
                    guid = Resource(package, header).contents[92:96]
                case b"SSTC":
                    name = Resource(package, header).contents[68:].split(b"\x01")
                case _:
                    pass

        if guid not in guid2nid:
            continue
        nid: bytes = guid2nid[guid]
        sims[nid].name[0] = name[1].split(b"\x00")[0].decode("utf-8")
        if sims[nid].name[0][:6] == "Prof. ":
            sims[nid].name[0] = sims[nid].name[0][6:]
        sims[nid].bio = name[2].split(b"\x00")[0].decode("utf-8")
        sims[nid].name[1] = name[3].split(b"\x00")[0].decode("utf-8")


def _search_nhood_lots(directory: Path, nhood: str) -> None:
    directory /= "Lots"
    family: Family
    for family in families.values():
        lot: int = family.lot
        if lot > 0:
            with (directory / f"{nhood}_Lot{lot}.package").open("rb") as file:
                logger.debug("searching lot %s in neighborhood %s", lot, nhood)
                package = file.read()

            header: ResourceHeader
            for header in get_headers(package):
                match header.rtype:
                    case b"IMIS":
                        resource: bytes = Resource(package, header).contents
                        family.time = f"{int.from_bytes(resource[76:78], byteorder='little')}:{int.from_bytes(resource[86:88], byteorder='little'):02d}"
                        family.day = int.from_bytes(
                            resource[132:134],
                            byteorder="little",
                        )
                    case b"\x8b\xe2\x1b\xb2":
                        resource = Resource(package, header).contents
                        index = int.from_bytes(resource[4:8], byteorder="little")
                        family.season = int.from_bytes(
                            resource[index + 12 : index + 16],
                            byteorder="little",
                        )
                        family.ssnlngth = int.from_bytes(
                            resource[index + 16 : index + 20],
                            byteorder="little",
                        )
                    case _:
                        pass
