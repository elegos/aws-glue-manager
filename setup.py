import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='AWSGlueManager',
    version="0.0.1-dev",
    author="Giacomo Furlan",
    author_email="giacomo+awsgluemanager@giacomofurlan.name",
    description="AWS Glue manager to keep jobs under control, filtering, reading logs etc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elegos/aws-glue-manager",
    project_urls={
        "Bug Tracker": "https://github.com/elegos/aws-glue-manager/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where=''),
    python_requires=">=3.9",
)
