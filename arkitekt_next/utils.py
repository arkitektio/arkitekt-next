import os


def create_arkitekt_next_folder(with_cache: bool = True) -> str:
    """Creates the .arkitekt_next folder in the current directory.

    If the folder already exists, it does nothing.
    It automatically creates a .gitignore file, and a .dockerignore file,
    so that the ArkitektNext credential files are not added to git.

    Parameters
    ----------
    with_cache : bool, optional
        Should we create a cache dir?, by default True

    Returns
    -------
    str
        The path to the .arkitekt_next folder.
    """
    os.makedirs(".arkitekt_next", exist_ok=True)
    if with_cache:
        os.makedirs(".arkitekt_next/cache", exist_ok=True)

    gitignore = os.path.join(".arkitekt_next", ".gitignore")
    dockerignore = os.path.join(".arkitekt_next", ".dockerignore")
    if not os.path.exists(gitignore):
        with open(gitignore, "w") as f:
            f.write(
                "# Hiding ArkitektNext Credential files from git\n*.json\n*.temp\ncache/\nservers/"
            )
    if not os.path.exists(dockerignore):
        with open(dockerignore, "w") as f:
            f.write(
                "# Hiding ArkitektNext Credential files from git\n*.json\n*.temp\ncache/\nservers/"
            )

    return os.path.abspath(".arkitekt_next")
