"""Custom widgets for SimTracker."""
# pylint: disable=too-many-ancestors

import tkinter as tk
from tkinter import ttk
from typing import Any, Literal

tabs: list[ttk.Treeview] = []


class ImageButton(ttk.Button):
    """Tk Button widget with image on it."""

    def __init__(
        self,
        master: tk.Misc | None,
        *args: Any,
        imgfile: str | None,
        imgwidth: int | None,
        imgheight: int | None,
        **kwargs: Any,
    ) -> None:
        """Construct an image button with parent master and image.

        Args:
            master: Tk widget containing this image button.
            *args: Other positional arguments for button.
            imgfile: Filepath of image.
            imgwidth: Width to display image with.
            imgheight: Height to display image with.
            **kwargs: Other keyword arguments for button and image.
        """
        if "image" in kwargs:
            self.image: tk.PhotoImage = kwargs.pop("image")
        elif imgfile:
            img_kwargs: dict[str, Any] = {}
            if imgwidth:
                img_kwargs["width"] = imgwidth
            if imgheight:
                img_kwargs["height"] = imgheight
            self.image = tk.PhotoImage(file=imgfile, **img_kwargs)
        super().__init__(master, *args, image=self.image, **kwargs)


class SortTree(ttk.Treeview):
    """Tk Treeview widget that can be sorted."""

    def __init__(self, master: tk.Frame, columns: list[str], widths: list[int]) -> None:
        """Construct a sorttree with parent master, columns, and widths.

        Args:
            master: Tk frame containing this treeview.
            columns: List of column names.
            widths: List of column widths.
        """
        scrollbar = tk.Scrollbar(master)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        super().__init__(master, columns=columns, yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.yview)

        self.column("#0", width=150, stretch=tk.FALSE)
        self.heading(
            "#0",
            text="Name",
            command=lambda: self.sort_column("#0", reverse=False),
        )

        i: int
        j: str
        for i, j in enumerate(self["columns"]):
            self.column(j, width=widths[i], stretch=tk.FALSE)
            self.heading(
                j,
                text=j,
                command=lambda column=j: self.sort_column(column, reverse=False),
            )

        self.bind("<Button-3>", self.right_click)
        self.bind("<Button-2>", self.middle_click)

        tabs.append(self)

    def sort(self, cols: list[tuple[str | int, str]]) -> None:
        """Sort tree.

        Args:
            cols: Sorted list of tuples with value and identifier for each row in column.
        """
        i: int
        k: str
        for i, (_, k) in enumerate(cols):
            self.move(k, "", i)

    def unsort(self) -> None:
        """Undo any sorting."""
        children: list[str] = list(self.get_children())
        children.sort()

        j: int
        k: str
        for j, k in enumerate(children):
            self.move(k, "", j)

    def get_sorted_columns(
        self,
        column: str,
        *,
        reverse: bool,
    ) -> list[tuple[str | int, str]]:
        """Get sorted columns.

        Args:
            column: Name of column to sort by.
            reverse: Whether to sort in reverse.

        Returns:
            Sorted list of tuples with value and identifier for each row in column.
        """
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

    def sort_column(self, column: str, *, reverse: bool) -> None:
        """Sort by column.

        Args:
            column: Name of column to sort by.
            reverse: Whether to sort in reverse.
        """
        cols: list[tuple[str | int, str]] = self.get_sorted_columns(
            column,
            reverse=reverse,
        )

        self.sort(cols)

    def right_click(self, event: tk.Event) -> None:
        """On right click, identify column heading clicked on and sort by that column in reverse."""
        if self.identify("region", event.x, event.y) == "heading":
            column: str = self.identify_column(event.x)
            self.sort_column(column, reverse=True)

    def middle_click(self, _: tk.Event) -> None:
        """On middle click, undo any sorting."""
        self.unsort()

    def pack(self, *args: Any, **kwargs: Any) -> None:
        """Pack configure."""
        expand: bool = kwargs.pop("expand", True)
        fill: Literal["none", "x", "y", "both"] = kwargs.pop("fill", tk.BOTH)

        super().pack(*args, expand=expand, fill=fill, **kwargs)


class SimsTree(SortTree):
    """Tk Treeview widget that can be sorted together with other SimsTree widgets."""

    def sort_column(self, column: str, *, reverse: bool) -> None:
        """Sort by column.

        Args:
            column: Name of column to sort by.
            reverse: Whether to sort in reverse.
        """
        cols: list[tuple[str | int, str]] = self.get_sorted_columns(
            column,
            reverse=reverse,
        )

        tab: ttk.Treeview
        for tab in tabs:
            if not isinstance(tab, SimsTree):
                continue
            tab.sort(cols)

    def middle_click(self, _: tk.Event) -> None:  # noqa: PLR6301
        """On middle click, undo any sorting."""
        tab: ttk.Treeview
        for tab in tabs:
            if not isinstance(tab, SimsTree):
                continue
            tab.unsort()
