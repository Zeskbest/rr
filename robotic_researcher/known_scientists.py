"""
Known scientists' processing.
"""
from typing import Optional, Union

import click

SCIENTISTS = ["Albert Einstein", "Isaac Newton", "Marie Curie", "Charles Darwin"]
_SCIENTISTS_AS_PROMPT = "\n".join((f"{num + 1}) {name}" for num, name in enumerate(SCIENTISTS)))

FLAG = "choose"


def validate_scientist_number(value: Union[str, int]) -> Optional[int]:
    """
    Validate the `number`.
    Args:
        value: input value
    Returns:
        valid value
    Raises:
        click.BadParameter otherwise
    """
    try:
        value = int(value)
    except ValueError:
        raise click.BadParameter(f"Argument should be a number.")

    min_, max_ = 1, len(SCIENTISTS)
    if min_ <= value <= max_:
        return value
    raise click.BadParameter(f"Number must be in range {[min_, max_]}.")


def validate_scientist_arg(ctx, param, value: Optional[int]) -> Optional[int]:
    """
    Validate the `number` arg.
    Args:
        ctx:
        param:
        value: inout value
    Returns:
        value
    Raises:
        click.BadParameter otherwise
    """
    if value is None:
        return None
    return validate_scientist_number(value)


def getdefault(scientist: str, number: Optional[int]):
    """
    Set default scientist if needed.
    Args:
        scientist: scientist arg
        number: number arg
    Returns:
        usable scientist arg
    """
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
