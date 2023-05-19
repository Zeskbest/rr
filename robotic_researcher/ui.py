from typing import Optional, Union

import click

from .robotics import CannotFind

SCIENTISTS = ["Albert Einstein", "Isaac Newton", "Marie Curie", "Charles Darwin"]
_SCIENTISTS_AS_PROMPT = "\n".join((f"{num + 1}) {name}" for num, name in enumerate(SCIENTISTS)))

FLAG = "choose"


def validate_scientist_number(value: Union[str, int]) -> Optional[int]:
    try:
        value = int(value)
    except ValueError:
        raise click.BadParameter(f"Argument should be a number.")

    min_, max_ = 1, len(SCIENTISTS)
    if min_ <= value <= max_:
        return value
    raise click.BadParameter(f"Number must be in range {[min_, max_]}.")


def validate_scientist_arg(ctx, param, value: int) -> Optional[int]:
    if value is None:
        return None
    return validate_scientist_number(value)


def cmd(scientist: str, number: Optional[int]):
    if scientist == FLAG:
        if number is None:
            number = click.prompt(
                f"Known scientists:\n{_SCIENTISTS_AS_PROMPT}\ntype number",
                type=int,
                default=1,
                value_proc=validate_scientist_number,
            )
        scientist = SCIENTISTS[number - 1]
    click.echo(f"You selected scientist: {scientist}")
    return scientist
