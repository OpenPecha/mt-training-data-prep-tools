import configparser


def add_submodule_branch():
    gitmodules_path = "./data/.gitmodules"
    output_path = "./data/.gitmodules-new"
    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    for section in config.sections():
        if section.startswith("submodule "):
            submodule_path = config.get(section, "path", fallback=None)

            config.set(section, "path", f"data/{submodule_path}")

    with open(output_path, "w") as configfile:
        config.write(configfile)

    print("Branches added/updated in .gitmodules file.")


if __name__ == "__main__":
    add_submodule_branch()
