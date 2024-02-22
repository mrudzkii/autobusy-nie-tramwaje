import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    setuptools.setup(
    name="Autobusy-bez-tramwajow", # <-- update !!!
    version="0.0.1",
    author="Michal Rudzki 448470", # <-- update
    author_email="mr448470@students.mimuw.edu.pl", # <-- update
    description="Analiza predkosci i punktualnosci autobusow warszawskich",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)