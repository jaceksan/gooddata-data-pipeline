from setuptools import find_packages, setup

REQUIRES = [
    "gooddata-sdk==1.2.0",
    "pyyaml>=5.1",
]


def _read_version():
    with open("VERSION", "rt") as version_file:
        return version_file.readline().strip()


setup(
    name="dbt-gooddata",
    description="dbt plugin for GoodData",
    version=_read_version(),
    author="GoodData",
    license="MIT",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["tests"]),
    python_requires="~=3.10.0",
    scripts=[
        "bin/dbt-gooddata",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Typing :: Typed",
    ],
    keywords=[],
    include_package_data=True,
)
