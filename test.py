from arkitekt_next import easy, register


x = easy("johannes")


@register
def hallo(value: int = 3) -> None:
    """Hallo

    Hallo is what you have been looking for

    """
    print(hallo)


with x:
    x.rekuest.run()
