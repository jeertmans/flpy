import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="flpy",
    version="1.0.3",
    author="Jérome Eertmans",
    author_email="jeertmans@icloud.com",
    description="Functional but Lazy Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeertmans/flpy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.8",
)
