import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imagetaggers",
    version="0.0.1",
    author="Matti Nelimarkka",
    author_email="matti.nelimarkka@helsinki.fi",
    description="Automating social science work around image tagging via various online services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/uh-soco/image-taggers/",
    project_urls={
        "Bug Tracker": "https://github.com/uh-soco/image-taggers/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.5",
    install_requires = """progress
    configparser
    google-cloud-vision
    google-auth
    msrest
    azure-cognitiveservices-vision-computervision
    boto3""".split('\n')
)
