"""Classes for handling TS2 Sims and Families."""

from binascii import hexlify
from dataclasses import dataclass, field
from enum import IntFlag, auto
from math import log2

from sims2.simtracker._config import config, config_traits


@dataclass
class SimGene:
    """Genes for a Sim genetic trait.

    Attributes:
        dominant: Dominant (expressed) gene that sim can pass on.
        recessive: Recessive (carried) gene that sim can pass on.
        range1: For skins, darker inherited gene.
        range2: For skins, lighter inherited gene.
    """

    dominant: str = ""
    recessive: str = ""
    range1: str = ""
    range2: str = ""


@dataclass
class SimGenes:
    """All of a Sim's genes.

    Attributes:
        skin: Sim's skin genes.
        hair: Sim's hair genes.
        eyes: Sims's eye genes.
    """

    skin: SimGene = field(default_factory=SimGene)
    hair: SimGene = field(default_factory=SimGene)
    eyes: SimGene = field(default_factory=SimGene)


@dataclass
class SimPersonality:
    """A Sim's personality.

    Attributes:
        nice: How nice/grouchy a sim is.
        active: How active/lazy a sim is.
        playful: How playful/serious a sim is.
        outgoing: How outgoing/shy a sim is.
        neat: How neat/sloppy a sim is.
    """

    nice: int
    active: int
    playful: int
    outgoing: int
    neat: int


@dataclass
class SimCareer:
    """A Sim's career.

    Attributes:
        career: Name of career.
        title: Name of job title.
        level: Level in career.
    """

    career: str
    title: str
    level: int


@dataclass
class SimSkills:
    """A Sim's skills.

    Attributes:
        cleaning: Cleaning skill level.
        cooking: Cooking skill level.
        charisma: Charisma skill level.
        mechanical: Mechanical skill level.
        creativity: Creativity skill level.
        body: Body skill level.
        logic: Logic skill level.
    """

    cleaning: int = 0
    cooking: int = 0
    charisma: int = 0
    mechanical: int = 0
    creativity: int = 0
    body: int = 0
    logic: int = 0


@dataclass
# pylint: disable=too-many-instance-attributes
class SimInterests:
    """A sim's interests.

    Attributes:
        politics: Interest in politics.
        money: Interest in money.
        environment: Interest in environment.
        crime: Interest in crime.
        entertainment: Interest in entertainment.
        culture: Interest in culture.
        food: Interest in food.
        health: Interest in health.
        fashion: Interest in fashion.
        sports: Interest in sports.
        paranormal: Interest in paranormal.
        travel: Interest in travel.
        work: Interest in work.
        weather: Interest in weather.
        animals: Interest in animals.
        school: Interest in school.
        toys: Interest in toys.
    """

    politics: int = 0
    money: int = 0
    environment: int = 0
    crime: int = 0
    entertainment: int = 0
    culture: int = 0
    food: int = 0
    health: int = 0
    fashion: int = 0
    sports: int = 0
    paranormal: int = 0
    travel: int = 0
    work: int = 0
    weather: int = 0
    animals: int = 0
    school: int = 0
    toys: int = 0
    scifi: int = 0


@dataclass
# pylint: disable=too-many-instance-attributes
class SimHobbies:
    """A Sim's hobby enthusiasm.

    Attributes:
        cuisine: Enthusiasm in cuisine.
        art: Enthusiasm in art.
        lit: Enthusiasm in lit.
        sports: Enthusiasm in sports.
        games: Enthusiasm in games.
        nature: Enthusiasm in nature.
        tinkering: Enthusiasm in tinkering.
        fitness: Enthusiasm in fitness.
        science: Enthusiasm in science.
        music: Enthusiasm in music.
    """

    cuisine: int = 0
    art: int = 0
    lit: int = 0
    sports: int = 0
    games: int = 0
    nature: int = 0
    tinkering: int = 0
    fitness: int = 0
    science: int = 0
    music: int = 0


class PersonFlags1(IntFlag):
    """Flags stored in PersonFlags1."""

    ZOMBIE = 1
    VAMPIRE = 4
    WEREWOLF = 32
    PLANTSIM = 256
    WITCH = 1024
    MERMAID = 4096
    GENIE = 8192


class PersonFlags2(IntFlag):
    """Flags stored in PersonFlags2."""

    FAIRY = 32


class SupernaturalFlags(IntFlag):
    """Flags for different supernatural lifestates."""

    GHOST = auto()
    SERVO = auto()
    ZOMBIE = auto()
    VAMPIRE = auto()
    WEREWOLF = auto()
    PLANTSIM = auto()
    WITCH = auto()
    MERMAID = auto()
    GENIE = auto()
    FAIRY = auto()


class TurnOns1(IntFlag):
    """Flags for the first group of turn ons."""

    COLOGNE = auto()
    STINK = auto()
    FAT = auto()
    FIT = auto()
    FORMAL = auto()
    SWIM = auto()
    UNDERWEAR = auto()
    VAMPIRE = auto()
    BEARD = auto()
    GLASSES = auto()
    MAKEUP = auto()
    FULLFACE = auto()
    HATS = auto()
    JEWELRY = auto()


class TurnOns2(IntFlag):
    """Flags for the second group of turn ons."""

    BLONDE = auto()
    RED = auto()
    BROWN = auto()
    BLACK = auto()
    CUSTOM = auto()
    GREY = auto()
    HARDWORKER = auto()
    UNEMPLOYED = auto()
    LOGICAL = auto()
    CHARISMATIC = auto()
    COOK = auto()
    HANDY = auto()
    CREATIVE = auto()
    ATHLETIC = auto()
    CLEANING = auto()
    ZOMBIE = auto()


class TurnOns3(IntFlag):
    """Flags for the third group of turn ons."""

    ROBOTS = auto()
    PLANTSIM = auto()
    WEREWOLF = auto()
    WITCH = auto()


# pylint: disable=too-many-instance-attributes
class Sim:
    """A TS2 Sim.

    Attributes:
        name: Name of the Sim.
        bio: The Sim's biography.
        genes: The Sim's genes.
        personality: The Sim's personality.
        skills: The Sim's skills.
        sexuality: The Sim's gender preference.
        asp: The SIm's aspirations.
        ltw: The Sim's lifetime want.
        fam: The id of the Sim's family.
        spnflags: Flags specifying supernatural lifestate of the sim.
        species: The Sim's species.
        job: The Sim's job.
        age: The Sim's age (in in-game days).
        death: The age the Sim will be when they die of old age.
        interests: The Sim's interests.
        major: The Sim's major.
        to_traits: The Sim's turn on traits.
        tos: The Sim's turn ons and turn off.
        hobbies: The Sim's hobbies.
        oth: The Sim's one true hobby.
        lta: The Sim's lifetime aspiration score.
        lta_benefits: The Sim's unspend lifetime benefits points.
        traits: The Sim's 3t2 traits.
    """

    def __init__(self, resource: bytes) -> None:
        """Initialize Sim from SDSC resource.

        Args:
            resource: Contents of SDSC.
        """
        self.name: list[str] = ["Unknown", "Unknown"]
        self.bio: str = ""
        self.genes: SimGenes = SimGenes()
        self.personality: SimPersonality = self._get_personality(resource)
        self.skills: SimSkills = self._get_skills(resource)
        self.sexuality: str = self._get_sexuality(resource[56:60])
        self.asp: list[int | str] = [
            int.from_bytes(resource[104:106], byteorder="little"),
            "",
        ]
        self.ltw: str = ""
        self.fam: bytes = resource[134:136]
        self.spnflags: int = self._get_supernatural(resource)
        self.species: bytes = resource[384:386]
        self.job: SimCareer = self._get_job(resource)
        self.age: int
        self.death: int
        self.age, self.death = self._get_age(resource)
        self.interests: SimInterests = self._get_interests(resource)

        if self.age >= config.getint("ages", "adult"):
            self.major: str = config.get(
                "majors",
                str(hexlify(resource[352:356])),
                fallback="Custom",
            )
        else:
            self.major = ""

        self.to_traits: list[int] = [
            int.from_bytes(resource[372:374], byteorder="little"),
            int.from_bytes(resource[374:376], byteorder="little"),
            int.from_bytes(resource[418:420], byteorder="little"),
        ]
        self.tos: list[str] = self._get_turnons(resource)

        self.hobbies: SimHobbies = self._get_hobbies(resource)
        self.oth: str = config.get(
            "hobbies",
            str(hexlify(resource[442:444])),
            fallback="Unknown",
        )
        self.lta: int = int.from_bytes(resource[444:446], byteorder="little")
        self.lta_benefits: int = int.from_bytes(
            resource[446:448],
            byteorder="little",
        ) - int.from_bytes(resource[448:450], byteorder="little")

        if config_traits:
            self.traits: list[str] = []

    @staticmethod
    def _get_personality(resource: bytes) -> SimPersonality:
        return SimPersonality(
            int.from_bytes(resource[16:18], byteorder="little") // 100,
            int.from_bytes(resource[18:20], byteorder="little") // 100,
            int.from_bytes(resource[22:24], byteorder="little") // 100,
            int.from_bytes(resource[24:26], byteorder="little") // 100,
            int.from_bytes(resource[26:28], byteorder="little") // 100,
        )

    @staticmethod
    def _get_skills(resource: bytes) -> SimSkills:
        return SimSkills(
            int.from_bytes(resource[30:32], byteorder="little") // 100,
            int.from_bytes(resource[32:34], byteorder="little") // 100,
            int.from_bytes(resource[34:36], byteorder="little") // 100,
            int.from_bytes(resource[36:38], byteorder="little") // 100,
            int.from_bytes(resource[42:44], byteorder="little") // 100,
            int.from_bytes(resource[46:48], byteorder="little") // 100,
            int.from_bytes(resource[48:50], byteorder="little") // 100,
        )

    @staticmethod
    def _get_sexuality(resource: bytes) -> str:
        m: int = int.from_bytes(resource[0:2], byteorder="little")
        f: int = int.from_bytes(resource[2:4], byteorder="little")
        if m >= 2**15:
            m -= 2**16 - 1
        if f >= 2**15:
            f -= 2**16 - 1
        if m > 0:
            if f > 0:
                return "Bi"
            return "M"
        if f > 0:
            return "F"
        return ""

    @staticmethod
    def _get_supernatural(resource: bytes) -> int:
        spnflags: int = SupernaturalFlags(0)

        if resource[322:324] == b"\x28\x00":
            spnflags += SupernaturalFlags.SERVO

        pflags: int = int.from_bytes(resource[180:182], byteorder="little")
        pflag: int
        spnflag: int
        for pflag, spnflag in {
            PersonFlags1.ZOMBIE: SupernaturalFlags.ZOMBIE,
            PersonFlags1.VAMPIRE: SupernaturalFlags.VAMPIRE,
            PersonFlags1.WEREWOLF: SupernaturalFlags.WEREWOLF,
            PersonFlags1.PLANTSIM: SupernaturalFlags.PLANTSIM,
            PersonFlags1.WITCH: SupernaturalFlags.WITCH,
        }.items():
            if pflags & pflag:
                spnflags += spnflag

        if config.getboolean("config", "midge", fallback=False):
            if pflags & PersonFlags1.MERMAID:
                spnflags += SupernaturalFlags.MERMAID
            if pflags & PersonFlags1.GENIE:
                spnflags += SupernaturalFlags.GENIE

            pflags = int.from_bytes(resource[330:332], byteorder="little")

            if pflags & PersonFlags2.FAIRY:
                spnflags += SupernaturalFlags.FAIRY

            if int.from_bytes(resource[148:150], byteorder="little") & (2**8):
                spnflags += SupernaturalFlags.GHOST

        return spnflags

    def _get_job(self, resource: bytes) -> SimCareer:
        career_guid: str = str(hexlify(resource[190:194]))
        if career_guid != "b'00000000'" and self.species == b"\x00\x00":
            career: str = config.get(
                f"careers.{career_guid}",
                "name",
                fallback="Custom",
            )

            level: int = int.from_bytes(resource[126:128], byteorder="little")
            max_career_level = 10
            if level > max_career_level:
                level = max_career_level
            elif level < 0:
                level = 1

            title: str = config.get(
                f"careers.{career_guid}",
                str(level),
                fallback="Custom",
            )
        elif self.fam == b"\xff\x7f":
            career = "NPC"
            level = 0
            title = config.get(
                "npcs",
                str(hexlify(resource[322:324])),
                fallback="Unknown NPC",
            )
        else:
            career = ""
            level = 0
            title = ""

        return SimCareer(career, title, level)

    def _get_age(self, resource: bytes) -> tuple[int, int]:
        death: int = int.from_bytes(resource[194:196], byteorder="little")
        age: int = int.from_bytes(
            resource[196:198],
            byteorder="little",
        ) + int.from_bytes(resource[324:326], byteorder="little")
        if self.species != b"\x00\x00":
            lifestage = resource[128:130]
            if lifestage > b"\x13\x00":
                age += 2
            elif lifestage == b"\x13\x00":
                age += 1
        if death > age:
            age += 1
        else:
            age -= death
        if (
            resource[128:130] == b"\x02\x00"
            and int.from_bytes(resource[196:198], byteorder="little") == 0
        ):
            age += config.getint("ages", "toddler")
        if age >= config.getint("ages", "elder"):
            if death > age:
                death = age
            else:
                death += age + 1
        else:
            death = 0

        return age, death

    @staticmethod
    def _get_interests(resource: bytes) -> SimInterests:
        return SimInterests(
            int.from_bytes(resource[260:262], byteorder="little") // 100,
            int.from_bytes(resource[262:264], byteorder="little") // 100,
            int.from_bytes(resource[264:266], byteorder="little") // 100,
            int.from_bytes(resource[266:268], byteorder="little") // 100,
            int.from_bytes(resource[268:270], byteorder="little") // 100,
            int.from_bytes(resource[270:272], byteorder="little") // 100,
            int.from_bytes(resource[272:274], byteorder="little") // 100,
            int.from_bytes(resource[274:276], byteorder="little") // 100,
            int.from_bytes(resource[276:278], byteorder="little") // 100,
            int.from_bytes(resource[278:280], byteorder="little") // 100,
            int.from_bytes(resource[280:282], byteorder="little") // 100,
            int.from_bytes(resource[282:284], byteorder="little") // 100,
            int.from_bytes(resource[284:286], byteorder="little") // 100,
            int.from_bytes(resource[286:288], byteorder="little") // 100,
            int.from_bytes(resource[288:290], byteorder="little") // 100,
            int.from_bytes(resource[290:292], byteorder="little") // 100,
            int.from_bytes(resource[292:294], byteorder="little") // 100,
            int.from_bytes(resource[294:296], byteorder="little") // 100,
        )

    @staticmethod
    def _get_turnons(resource: bytes) -> list[str]:
        turn_ons: list[str] = []
        turn_off: str = ""

        tons: list[int] = [
            int.from_bytes(resource[376:378], byteorder="little"),
            int.from_bytes(resource[378:380], byteorder="little"),
            int.from_bytes(resource[414:416], byteorder="little"),
        ]
        toffs: list[int] = [
            int.from_bytes(resource[380:382], byteorder="little"),
            int.from_bytes(resource[382:384], byteorder="little"),
            int.from_bytes(resource[416:418], byteorder="little"),
        ]
        toflags: list[type[IntFlag]] = [TurnOns1, TurnOns2, TurnOns3]

        index: int = 1
        i: int
        for i in range(3):
            for flag in toflags[i]:
                if tons[i] & flag:
                    turn_ons.append(
                        config.get("turnons", str(index), fallback="Unknown"),
                    )
                if toffs[i] & flag:
                    turn_off = config.get("turnons", str(index), fallback="Unknown")
                index += 1

        turn_ons.extend("" for x in range(len(turn_ons), 2))
        turn_ons.append(turn_off)

        return turn_ons

    @staticmethod
    def _get_hobbies(resource: bytes) -> SimHobbies:
        return SimHobbies(
            int.from_bytes(resource[420:422], byteorder="little") // 100,
            int.from_bytes(resource[422:424], byteorder="little") // 100,
            int.from_bytes(resource[424:426], byteorder="little") // 100,
            int.from_bytes(resource[426:428], byteorder="little") // 100,
            int.from_bytes(resource[428:430], byteorder="little") // 100,
            int.from_bytes(resource[430:432], byteorder="little") // 100,
            int.from_bytes(resource[432:434], byteorder="little") // 100,
            int.from_bytes(resource[434:436], byteorder="little") // 100,
            int.from_bytes(resource[436:438], byteorder="little") // 100,
            int.from_bytes(resource[438:440], byteorder="little") // 100,
        )

    def set_aspirations(self) -> None:
        """Set aspirations.

        Aspirations are stored together as flags with the secondary aspiration being determined by a separate token, so once SimTracker has finished searching inventories call this method to properly convert the stored flags/token value into strings.
        """
        asp1: int | str = self.asp[0]
        asp2: int | str = self.asp[1]
        if isinstance(asp1, str):
            return
        if isinstance(asp2, int):
            self.asp[1] = config.get("aspirations", str(int(log2(asp2))))
            self.asp[0] = config.get(
                "aspirations",
                str(int(log2(asp1 ^ (asp2 & asp1)))),
            )
        elif asp1 > 0:
            self.asp[0] = config.get("aspirations", str(int(log2(asp1))))

    def has_turnon_trait(self, to: int, to_group: int) -> bool:
        """Check if the Sim fulfills a turn on.

        Args:
            to: Flag of turn on to check.
            to_group: Whether the turn on is in group 1, 2, or 3.

        Returns:
            True if the Sim fulfills the turn on, otherwise false.
        """
        if to_group < 0 or to_group > len(self.to_traits):
            return False
        return bool(self.to_traits[to_group] & to)

    def is_supernatural(self, spn: int) -> bool:
        """Check if the Sim is a type of supernatural.

        Args:
            spn: Flag of type of supernatural to check.

        Returns:
            True if the Sim is that type of supernatural, otherwise false.
        """
        return bool(self.spnflags & spn)


@dataclass
class Family:
    """A TS2 Sim family.

    Attributes:
        lot: ID of the lot the family lives in.
        day: In-game days running of the lot the family lives in.
        time: In-game time of day that the lot the family lives in was last saved at.
        season: In-game season that the lot the family lives in was last saved in.
        ssnlngth: In-game days left in season for the lot the family lives in.
        name: Name of the family.
        desc: Description of the family.
    """

    lot: int
    day: int | None = None
    time: str = ""
    season: int | None = None
    ssnlngth: int | None = None
    name: str = ""
    desc: str = ""
