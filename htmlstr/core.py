from dataclasses import dataclass
from typing import List, Optional, Union

from selectolax.lexbor import LexborHTMLParser, LexborNode

# copy
Element = Union[
    "Anchor",
    "Image",
    "Text",
    "Button",
    "Heading",
    "Paragraph",
    "TextInput",
    "UrlInput",
    "CheckboxInput",
    "RadioInput",
    "Label",
    "Select",
    "Option",
    "Details",
    "Summary",
]


@dataclass
class Anchor:
    href: str
    inner: List[Element]


@dataclass
class Image:
    src: str
    alt: Optional[str]


@dataclass
class Text:
    content: str


@dataclass
class Button:
    id: int
    inner: List[Element]


@dataclass
class Heading:
    level: int
    inner: List[Element]


@dataclass
class Paragraph:
    inner: List[Element]


@dataclass
class TextInput:
    id: int
    placeholder: Optional[str]


@dataclass
class UrlInput:
    id: int
    placeholder: Optional[str]


@dataclass
class CheckboxInput:
    id: int
    checked: bool


@dataclass
class RadioInput:
    id: int
    checked: bool


@dataclass
class Label:
    inner: List[Element]


@dataclass
class Select:
    inner: List[Element]
    multiple: bool


@dataclass
class Option:
    text: str


@dataclass
class Details:
    inner: List[Element]


@dataclass
class Summary:
    inner: List[Element]


class Parser:
    """Represents a parser for (interactivity-content-balanced) structured HTML.

    Creating this class is a cheap operation.
    There's no need to consider the performance cost by keeping this constructed.
    """

    __slots__ = ("id",)

    id: int

    def __init__(self):
        self.id = 0

    def fetch_advance_id(self) -> int:
        """(internal) Advance the ID counting, and return the previous value."""
        p = self.id
        self.id += 1
        return p

    def parse(self, html: str) -> List[Element]:
        """Parse from HTML.

        Returns:
            list[Element]: A list of elements, structured.
        """
        parser = LexborHTMLParser(html)
        body = parser.body

        if not body:
            return []

        return self.parse_children(body)

    def parse_children(self, root: LexborNode) -> List[Element]:
        """(internal) Parse the children.

        Args:
            root (LexborNode): The root to iterate from.
        """

        elements: List[Element] = []

        for node in root.iter(include_text=True):
            if not node.tag or node.tag == "-text":
                # "None" is possibly a text node
                text = node.text(strip=True)
                if text:
                    elements.append(Text(text))

            elif node.tag == "a":
                href = node.attributes.get("href", None)
                if not href:
                    continue

                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Anchor(href=href, inner=children))

            elif node.tag == "img":
                src = node.attributes.get("src", None)
                if not src:
                    continue

                alt = node.attributes.get("alt", None)

                elements.append(Image(src=src, alt=alt))

            elif node.tag == "button":
                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Button(id=self.fetch_advance_id(), inner=children))

            elif (
                len(node.tag) == 2
                and node.tag.startswith("h")
                and node.tag[-1].isdigit()
            ):
                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Heading(level=int(node.tag[1:]), inner=children))

            elif node.tag == "p":
                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Paragraph(children))

            elif node.tag == "input":
                type_ = node.attributes.get("type", "text")
                if type_ == "text":
                    placeholder = node.attributes.get("placeholder", None)
                    elements.append(
                        TextInput(id=self.fetch_advance_id(), placeholder=placeholder)
                    )

                elif type_ == "url":
                    placeholder = node.attributes.get("placeholder", None)
                    elements.append(
                        UrlInput(id=self.fetch_advance_id(), placeholder=placeholder)
                    )

                elif type_ == "checkbox":
                    attributes = node.attributes
                    if "checked" in attributes:
                        if attributes["checked"] == "true" or not attributes["checked"]:
                            checked = True
                        else:
                            checked = False
                    else:
                        checked = False

                    elements.append(
                        CheckboxInput(
                            id=self.fetch_advance_id(),
                            checked=checked,
                        )
                    )

                elif type_ == "radio":
                    attributes = node.attributes
                    if "checked" in attributes:
                        if attributes["checked"] == "true" or not attributes["checked"]:
                            checked = True
                        else:
                            checked = False
                    else:
                        checked = False

                    elements.append(
                        RadioInput(
                            id=self.fetch_advance_id(),
                            checked=checked,
                        )
                    )

            elif node.tag == "select":
                children = self.parse_children(node)
                if children:
                    attributes = node.attributes
                    if "multiple" in attributes:
                        if (
                            attributes["multiple"] == "true"
                            or not attributes["multiple"]
                        ):
                            multiple = True
                        else:
                            multiple = False
                    else:
                        multiple = False

                    elements.append(
                        Select(
                            children,
                            multiple=multiple,
                        )
                    )

            elif node.tag == "option":
                text = node.text(strip=True)
                if text:
                    elements.append(Option(text))

            elif node.tag == "label":
                children = self.parse_children(node)
                if children:
                    elements.append(Label(children))

            elif node.tag == "details":
                children = self.parse_children(node)
                if children:
                    elements.append(Details(children))

            elif node.tag == "summary":
                children = self.parse_children(node)
                if children:
                    elements.append(Summary(children))

            else:
                # treat as fragments
                children = self.parse_children(node)
                if children:
                    elements.extend(children)

        return elements
