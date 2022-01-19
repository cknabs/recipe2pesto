import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional

import parse_ingredients
from simplefractions import simplest_from_float


@dataclass(frozen=True, eq=True)
class Ingredient:
    name: str
    quantity: int
    unit: str
    comment: str
    original_string: str

    @staticmethod
    def _str_comment(comment: str):
        comment = comment.strip()
        if comment.startswith("(") and comment.endswith(")"):
            return comment
        elif len(comment) == 0:
            return ""
        else:
            return paren(comment)

    def __str__(self):
        return "+" + " ".join([
            str(simplest_from_float(self.quantity)),
            self.unit,
            quote(self.name),
            self._str_comment(self.comment),
        ])


@dataclass(frozen=True, eq=True)
class Instruction:
    ingredients: set[Ingredient]
    original_string: str

    def __str__(self):
        return "[" + self.original_string + "]"


def parse_ingredient(ingredient: str) -> Ingredient:
    parsed = parse_ingredients.parse_ingredient(ingredient)
    return Ingredient(name=parsed.name, quantity=parsed.quantity, unit=parsed.unit, comment=parsed.comment,
                      original_string=parsed.original_string)


def parse_instruction(instruction: dict, ingredients) -> Instruction:
    current_ingredients = [i for i in ingredients if i.name in instruction]
    return Instruction(original_string=instruction["text"], ingredients=set(current_ingredients))


@dataclass(frozen=True, eq=True)
class Recipe:
    title: Optional[str]
    description: Optional[str]
    language: Optional[str]
    yield_: Optional[str]
    time: Optional[datetime.datetime]
    image: Optional[str]
    author: Optional[str]
    other: Dict[str, Optional[str]]

    def __str__(self):
        return "\n".join([
                             f">{self.title}",
                             "" if self.description is None else f"(description: {self.description})",
                             "" if self.language is None else f"(language: {self.language})",
                             "" if self.yield_ is None else f"(yield: {self.yield_})",
                             "" if self.time is None else f"(time: {self.time})",
                             "" if self.image is None else f"(image: {self.image})",
                             "" if self.author is None else f"(author: {self.author})",
                         ] + [
                             "" if v is None else f"(x-schema-{k}: {v})" for k, v in self.other.items()
                         ]
                         )


def parse_metadata(d: dict) -> Recipe:
    other = {
        k: v for k, v in d.items() if
        isinstance(v, str) and k not in ["name", "headline", "inLanguage", "recipeYield", "totalTime", "image", "author"]
    }
    dd = defaultdict(lambda: None, d)

    image = None if dd["image"] is None else dd["image"]["url"]
    author = None if dd["author"] is None else " and ".join(a["name"] for a in dd["author"])
    return Recipe(title=dd["name"], description=dd["headline"], language=dd["inLanguage"], yield_=dd["recipeYield"],
                  time=dd["totalTime"], image=image, author=author, other=other)


def quote(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def paren(s: str) -> str:
    return "(" + s.replace("(", "\\(").replace(")", "\\)") + ")"


def dict2pesto(d):
    ingredients = list(map(parse_ingredient, d["recipeIngredient"]))
    instructions = list(map(lambda i: parse_instruction(i, ingredients), d["recipeInstructions"]))
    metadata = parse_metadata(d)

    found_ingredients = set().union(*(
        {i for i in instruction.ingredients}
        for instruction in instructions))
    notfound_ingedients = {i for i in ingredients if i.name not in found_ingredients}

    res = ["%pesto"]
    for ingredient in notfound_ingedients:
        res += [str(ingredient)]

    for instruction in instructions:
        for ingredient in instruction.ingredients:
            res += [str(ingredient)]
        res += [str(instruction)]

    res += [str(metadata)]

    return "\n".join(res)
