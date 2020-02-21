import setuptools
from setuptools.command.install import install as _install


class Install(_install):
    def run(self):
        _install.do_egg_install(self)
        import nltk
        nltk.download("punkt")

setuptools.setup(
    name="licalendarlib",
    version="0.1dev",
    packages=setuptools.find_packages(),
    cmdclass = {"install" : Install},
    install_requires = [
        "nltk",
        "Pillow",
        "requests",
        "tqdm",
        "pytz",
        "python-slugify"],
    setup_requires = ["nltk"]
    )