# pylint: disable=too-many-ancestors

from tkinter import (
    BOTH,
    FALSE,
    RIGHT,
    Event,
    Frame,
    Misc,
    PhotoImage,
    Scrollbar,
    Y,
)
from tkinter.ttk import Button, Treeview
from typing import Any, Literal

tabs: list[Treeview] = []


class ImageButton(Button):
    def __init__(
        self,
        master: Misc | None,
        *args: Any,
        imgfile: str | None,
        imgwidth: int | None,
        imgheight: int | None,
        **kwargs: Any,
    ) -> None:
        if "image" in kwargs:
            self.image: PhotoImage = kwargs.pop("image")
        elif imgfile:
            img_kwargs: dict[str, Any] = {}
            if imgwidth:
                img_kwargs["width"] = imgwidth
            if imgheight:
                img_kwargs["height"] = imgheight
            self.image = PhotoImage(file=imgfile, **img_kwargs)
        super().__init__(master, *args, image=self.image, **kwargs)


class SortTree(Treeview):
    def __init__(self, master: Frame, columns: list[str], widths: list[int]) -> None:
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT, fill=Y)

        super().__init__(master, columns=columns, yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.yview)

        self.column("#0", width=150, stretch=FALSE)
        self.heading(
            "#0",
            text="Name",
            command=lambda: self.sort_column("#0", reverse=False),
        )

        i: int
        j: str
        for i, j in enumerate(self["columns"]):
            self.column(j, width=widths[i], stretch=FALSE)
            self.heading(
                j,
                text=j,
                command=lambda column=j: self.sort_column(column, reverse=False),  # type: ignore
            )

        self.bind("<Button-3>", self.right_click)

        tabs.append(self)

    def get_sorted_columns(
        self,
        column: str,
        *,
        reverse: bool,
    ) -> list[tuple[str | int, str]]:
        if column == "#0":
            cols: list[tuple[str | int, str]] = [
                (self.item(i)["text"], i) for i in self.get_children()
            ]
        else:
            try:
                cols = [(int(self.set(i, column)), i) for i in self.get_children()]
            except ValueError:
                cols = [(self.set(i, column), i) for i in self.get_children()]
        cols.sort(reverse=reverse, key=lambda i: i[0])
        return cols

    def sort_column(self, _column: str, *, reverse: bool) -> None:
        pass

    def right_click(self, event: Event) -> None:
        if self.identify("region", event.x, event.y) == "heading":
            column: str = self.identify_column(event.x)
            self.sort_column(column, reverse=True)

    def pack(self, *args: Any, **kwargs: Any) -> None:
        expand: bool = kwargs.pop("expand", True)
        fill: Literal["none", "x", "y", "both"] = kwargs.pop("fill", BOTH)

        super().pack(*args, expand=expand, fill=fill, **kwargs)


class SimsTree(SortTree):
    def __init__(self, master: Frame, columns: list[str], widths: list[int]) -> None:
        super().__init__(master, columns, widths)
        self.bind("<Button-2>", self.unsort)

    @staticmethod
    def unsort(_event: Event) -> None:
        tab: Treeview
        for tab in tabs:
            if not isinstance(tab, SimsTree):
                continue
            children: list[str] = list(tab.get_children())
            children.sort()
            for j, k in enumerate(children):
                tab.move(k, "", j)

    def sort_column(self, column: str, *, reverse: bool) -> None:
        cols: list[tuple[str | int, str]] = super().get_sorted_columns(
            column,
            reverse=reverse,
        )

        tab: Treeview
        for tab in tabs:
            if not isinstance(tab, SimsTree):
                continue

            i: int
            _j: str | int
            k: str
            for i, (_j, k) in enumerate(cols):
                tab.move(k, "", i)


class NonSimsTree(SortTree):
    def __init__(self, master: Frame, columns: list[str], widths: list[int]) -> None:
        super().__init__(master, columns, widths)
        self.bind("<Button-2>", self.unsort)

    def unsort(self, _event: Event) -> None:
        children: list[str] = list(self.get_children())
        children.sort()

        j: int
        k: str
        for j, k in enumerate(children):
            self.move(k, "", j)

    def sort_column(self, column: str, *, reverse: bool) -> None:
        cols: list[tuple[str | int, str]] = self.get_sorted_columns(
            column,
            reverse=reverse,
        )

        i: int
        _j: str | int
        k: str
        for i, (_j, k) in enumerate(cols):
            self.move(k, "", i)
