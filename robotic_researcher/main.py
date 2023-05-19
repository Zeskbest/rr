from typing import Optional

import click

from .robotics import Robot, CannotFind
from .ui import cmd, validate_scientist_arg, FLAG


@click.command(help='I am here to provide information about scientists:')
@click.option(f'--scientist', prompt=f'Enter a scientist name or "{FLAG}" to choose from the known ones',
              help='Name of the scientist', default=FLAG)
@click.option('--number', type=int, help='Scientist number', callback=validate_scientist_arg)
def main(scientist: str, number: Optional[int]):
    robot = Robot("Quandrinaut")
    robot.say_hello()
    try:
        scientist = cmd(scientist, number)
        robot.say_wait()
        robot.scientist_info(scientist)
    except CannotFind as exc:
        print('Try fulfilling both the Name and the Surname next time')
    finally:
        robot.say_goodbye()


if __name__ == "__main__":
    main()
