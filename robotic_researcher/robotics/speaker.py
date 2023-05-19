"""
Speaking entity.
"""


class CanSpeakMixin:
    """Mixin for speaking robots"""

    name: str

    def say_hello(self) -> None:
        """Introduce yourself"""
        print(f"\nHello, my name is {self.name}\n")
        print(
            "I am here to help you to find the following information about the scientist: "
            "birth date, date of death, age, and a short article."
        )

    @staticmethod
    def say_wait() -> None:
        """Asks to wait"""
        print("Please wait...\n")

    def say_goodbye(self) -> None:
        """Say `bye`"""
        print(f"Goodbye, my name is {self.name}")
