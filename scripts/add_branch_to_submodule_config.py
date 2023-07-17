import configparser


def add_submodule_branch():
    gitmodules_path = "./data/.gitmodules"
    output_path = "./data/.gitmodules-new"
    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    for section in config.sections():
        if section.startswith("submodule "):
            submodule_branch = config.get(section, "branch", fallback=None)

            if submodule_branch is None:
                submodule_branch = "main"
                config.set(section, "branch", submodule_branch)

    with open(output_path, "w") as configfile:
        config.write(configfile)

    print("Branches added/updated in .gitmodules file.")


if __name__ == "__main__":
    add_submodule_branch()
