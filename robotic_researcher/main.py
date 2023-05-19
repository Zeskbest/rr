"""
User Interface file
"""
from typing import Optional

import click

from .robotics import Robot, CannotFind
from .known_scientists import getdefault, validate_scientist_arg, FLAG


@click.command(help="provides information about scientists")
@click.option(
    f"--scientist",
    prompt=f'Enter a scientist "Name Surname" or leave empty to choose from the known ones',
    help="Full Name of the scientist",
    default=FLAG,
    show_default=False,
)
@click.option("--number", type=int, help="scientist number from the known ones", callback=validate_scientist_arg)
def main(scientist: str, number: Optional[int]) -> None:
    """
    Args:
        scientist: input name of the scientist
        number: optional number of scientist from the `SCIENTISTS` list
    """
    robot = Robot()
    robot.say_hello()
    try:
        scientist = getdefault(scientist, number)
        robot.say_wait()
        robot.run(scientist)
    except CannotFind as exc:
        print(
            f'\nSorry, I can not find the scientist "{exc.args[0]}".\n'
            "Try to correct name and/or fulfil both the Name and the Surname next time"
        )
    finally:
        robot.say_goodbye()
        robot.shutdown()


if __name__ == "__main__":
    main()
