import setuptools

def readme():
    try:
        with open("README.md") as f:
            return f.read()
    except IOError:
        return ""


setuptools.setup(
    name="psgcompiler",
    version="6.0.1",
    author="PySimpleGUI",
    description="A simple, easy to use tool that is a front-end to PyInstaller created with PySimpleGUI to convert your Python programs to executables.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/PySimpleGUI/psgcompiler",
    packages=["psgcompiler"],
    license='GNU Lesser General Public License v3 (LGPLv3)',
    keywords="GUI UI PySimpleGUI tkinter psgcompiler compile pyinstaller EXE distribute",
    install_requires=["PySimpleGUI","PyInstaller"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Framework :: PySimpleGUI",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: User Interfaces",
    ],
    package_data={"":
                      ["*","*.*"]
                  },
    entry_points={"gui_scripts": [
        "psgcompiler=psgcompiler.psgcompiler:main"
    ], },
)


