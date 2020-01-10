import setuptools

setuptools.setup(
    name="licalendarlib",
    version="0.1dev",
    packages=setuptools.find_packages(),
    install_requires = [
        "nltk",
        "Pillow",
        "requests",
        "tqdm"]
    )