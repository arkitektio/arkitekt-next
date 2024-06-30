from arkitekt_next_next.builders import easy


def test_easy():
    with easy("johannes", "latest"):
        print("Hello world!")
