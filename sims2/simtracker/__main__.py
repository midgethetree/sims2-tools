"""A program for viewing information about your neighborhoods in a tabulated spreadsheet."""

import tkinter as tk
from logging import Logger, getLogger
from pathlib import Path
from tkinter import ttk

from sims2.common.logging import config_logging, handle_exception
from sims2.simtracker._config import config_traits, folders_nhoods
from sims2.simtracker.search import families, search_nhood, sims
from sims2.simtracker.sim import Family, Sim, SupernaturalFlags, TurnOns1
from sims2.simtracker.widgets import ImageButton, SimsTree, SortTree

logger: Logger = getLogger(__name__)


# pylint: disable=too-many-ancestors
class MainApp(ttk.Notebook):
    """The main GUI application."""

    def __init__(self, master: tk.Tk) -> None:
        """Initialize the main GUI application with a Tkinter root.

        Args:
            master: Tkinter widget representing window.
        """
        master.geometry("960x1080")
        master.title("SimTracker")

        super().__init__(master)

        self._add_nhood_frame()

        self.trees: dict[str, ttk.Treeview] = {}

        self._add_sims_tree(
            "Sims",
            [
                "Family",
                "Age",
                "Death",
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
        )

        if config_traits:
            self._add_sims_tree(
                "Traits",
                ["Trait 1", "Trait 2", "Trait 3", "Trait 4", "Trait 5"],
                [150 for _ in range(5)],
            )

        self._add_sims_tree(
            "Interests",
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
            [43 for _ in range(18)],
        )

        self._add_sims_tree(
            "Hobbies",
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
        )

        self._add_sims_tree(
            "Jobs",
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
        )

        self._add_sims_tree(
            "Chemistry",
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
        )

        self._add_sims_tree(
            "Genetics",
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
            [75 for _ in range(8)],
        )

        self._add_sims_tree(
            "Supernatural",
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
            [75 for _ in range(10)],
        )

        tab: tk.Frame = tk.Frame(self)
        self.add(tab, text="Bio")
        ttk.Style().configure("Bio.Treeview", rowheight=50)  # pyright: ignore[reportUnknownMemberType]
        tree: ttk.Treeview = ttk.Treeview(
            tab,
            style="Bio.Treeview",
            columns=["Bio"],
        )
        _ = tree.column("#0", width=150, stretch=tk.FALSE)
        tree.heading("#0", text="Name")
        tree.heading("Bio", text="Bio")
        tree.pack(expand=True, fill=tk.BOTH)
        self.trees["Bios"] = tree

        self._add_sort_tree("Pets", ["Family", "Age"], [100, 50])

        self._add_sort_tree(
            "Families",
            ["Day", "Time", "Season", "SSN Length"],
            [50, 50, 50, 50],
        )

        self.pack(expand=True, fill=tk.BOTH)

    def _add_nhood_frame(self) -> None:
        nhoods: tk.Frame = tk.Frame(self)
        folders: list[tuple[str, Path]] = []
        nhoods_folder: Path
        for nhoods_folder in folders_nhoods:
            if not nhoods_folder.exists():
                logger.error("missing folder: %s", nhoods_folder.name)
                continue

            nhood: Path
            for nhood in nhoods_folder.iterdir():
                if nhood.name == "Tutorial":
                    continue
                if nhood.is_dir():
                    folders.append((nhood.name, nhoods_folder))

        if len(folders) > 0:
            i: int
            n: tuple[str, Path]
            for i, n in enumerate(folders):
                button: ImageButton = ImageButton(
                    nhoods,
                    imgfile=f"{n[1]}/{n[0]}/{n[0]}_Neighborhood.png",
                    imgwidth=300,
                    imgheight=225,
                    text=n[0],
                    compound="top",
                    command=lambda x=n[0], y=n[1]: self.search(x, y),
                )
                button.grid(row=i // 3, column=i % 3)

        self.add(nhoods, text="Neighborhoods")

    def _add_sort_tree(self, text: str, columns: list[str], widths: list[int]) -> None:
        tab: tk.Frame = tk.Frame(self)
        self.add(tab, text=text)

        tree: SortTree = SortTree(tab, columns, widths)
        tree.pack()

        self.trees[text] = tree

    def _add_sims_tree(self, text: str, columns: list[str], widths: list[int]) -> None:
        tab: tk.Frame = tk.Frame(self)
        self.add(tab, text=text)

        tree: SimsTree = SimsTree(tab, columns, widths)
        tree.pack()

        self.trees[text] = tree

    def search(self, nhood: str, nhoods_folder: Path) -> None:
        """Search neighborhood for information about sims and families.

        Args:
            nhood: Identifier of neighborhood.
            nhoods_folder: Folder containing neighborhood.
        """
        tree: ttk.Treeview
        for tree in self.trees.values():
            tree.delete(*tree.get_children())

        search_nhood(nhood, nhoods_folder)

        i: bytes
        sim: Sim
        for i, sim in sims.items():
            if sim.species != b"\x00\x00":
                _ = self.trees["Pets"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]}",
                    values=[families[sim.fam].name, sim.age],
                )
            else:
                if sim.name[0] in {
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
                }:
                    continue
                _ = self.trees["Sims"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]} ({int.from_bytes(i, byteorder='little')})",
                    values=[
                        families[sim.fam].name,
                        sim.age,
                        sim.death if sim.death != 0 else "",
                        sim.personality.neat,
                        sim.personality.outgoing,
                        sim.personality.active,
                        sim.personality.playful,
                        sim.personality.nice,
                        sim.asp[0],
                        sim.asp[1],
                        sim.ltw,
                        sim.lta,
                        sim.lta_benefits,
                    ],
                )
                if config_traits:
                    _ = self.trees["Traits"].insert(
                        "",
                        tk.END,
                        text=f"{sim.name[0]} {sim.name[1]}",
                        values=[
                            sim.traits[0],
                            sim.traits[1],
                            sim.traits[2],
                            sim.traits[3],
                            sim.traits[4],
                        ],
                    )
                _ = self.trees["Interests"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]}",
                    values=[
                        sim.interests.environment,
                        sim.interests.food,
                        sim.interests.weather,
                        sim.interests.culture,
                        sim.interests.money,
                        sim.interests.politics,
                        sim.interests.paranormal,
                        sim.interests.health,
                        sim.interests.fashion,
                        sim.interests.travel,
                        sim.interests.crime,
                        sim.interests.sports,
                        sim.interests.entertainment,
                        sim.interests.animals,
                        sim.interests.work,
                        sim.interests.school,
                        sim.interests.toys,
                        sim.interests.scifi,
                    ],
                )
                _ = self.trees["Hobbies"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]}",
                    values=[
                        sim.oth,
                        sim.hobbies.cuisine,
                        sim.hobbies.art,
                        sim.hobbies.lit,
                        sim.hobbies.sports,
                        sim.hobbies.games,
                        sim.hobbies.nature,
                        sim.hobbies.tinkering,
                        sim.hobbies.fitness,
                        sim.hobbies.science,
                        sim.hobbies.music,
                    ],
                )
                _ = self.trees["Jobs"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]}",
                    values=[
                        sim.skills.cooking,
                        sim.skills.mechanical,
                        sim.skills.charisma,
                        sim.skills.body,
                        sim.skills.logic,
                        sim.skills.creativity,
                        sim.skills.cleaning,
                        sim.major,
                        sim.job.career,
                        sim.job.title,
                        sim.job.level if sim.job.level != 0 else "",
                    ],
                )
                _ = self.trees["Chemistry"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]}",
                    values=[
                        sim.sexuality,
                        "True" if sim.has_turnon_trait(TurnOns1.FAT, 0) else "",
                        "True" if sim.has_turnon_trait(TurnOns1.FIT, 0) else "",
                        "True" if sim.has_turnon_trait(TurnOns1.BEARD, 0) else "",
                        "True" if sim.has_turnon_trait(TurnOns1.GLASSES, 0) else "",
                        "True" if sim.has_turnon_trait(TurnOns1.MAKEUP, 0) else "",
                        "True" if sim.has_turnon_trait(TurnOns1.FULLFACE, 0) else "",
                        "True" if sim.has_turnon_trait(TurnOns1.HATS, 0) else "",
                        "True" if sim.has_turnon_trait(TurnOns1.JEWELRY, 0) else "",
                        sim.tos[0],
                        sim.tos[1],
                        sim.tos[-1],
                    ],
                )
                _ = self.trees["Genetics"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]}",
                    values=[
                        sim.genes.skin.dominant,
                        sim.genes.skin.recessive,
                        sim.genes.skin.range1,
                        sim.genes.skin.range2,
                        sim.genes.hair.dominant,
                        sim.genes.hair.recessive,
                        sim.genes.eyes.dominant,
                        sim.genes.eyes.recessive,
                    ],
                )
                _ = self.trees["Supernatural"].insert(
                    "",
                    tk.END,
                    text=f"{sim.name[0]} {sim.name[1]}",
                    values=[
                        "True" if sim.is_supernatural(SupernaturalFlags.GHOST) else "",
                        "True" if sim.is_supernatural(SupernaturalFlags.ZOMBIE) else "",
                        "True"
                        if sim.is_supernatural(SupernaturalFlags.VAMPIRE)
                        else "",
                        "True" if sim.is_supernatural(SupernaturalFlags.SERVO) else "",
                        "True"
                        if sim.is_supernatural(SupernaturalFlags.WEREWOLF)
                        else "",
                        "True"
                        if sim.is_supernatural(SupernaturalFlags.PLANTSIM)
                        else "",
                        "True" if sim.is_supernatural(SupernaturalFlags.GENIE) else "",
                        "True" if sim.is_supernatural(SupernaturalFlags.WITCH) else "",
                        "True"
                        if sim.is_supernatural(SupernaturalFlags.MERMAID)
                        else "",
                        "True" if sim.is_supernatural(SupernaturalFlags.FAIRY) else "",
                    ],
                )
                if sim.bio:
                    _ = self.trees["Bios"].insert(
                        "",
                        tk.END,
                        text=f"{sim.name[0]} {sim.name[1]}",
                        values=[sim.bio],
                    )

        family: Family
        for i, family in families.items():
            min_special_fam: int = 32000
            if (
                i == b"\x00\x00"
                or int.from_bytes(i, byteorder="little") >= min_special_fam
            ):
                continue
            _ = self.trees["Families"].insert(
                "",
                tk.END,
                text=f"{family.name}",
                values=[
                    family.day,
                    family.time,
                    family.season,
                    family.ssnlngth,
                ],
            )

        self.select(self.tabs()[1])  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]


def main() -> None:
    """Main function for running simtracker."""
    config_logging("simtracker")

    root: tk.Tk = tk.Tk()
    _ = MainApp(root)

    root.report_callback_exception = handle_exception

    root.mainloop()
