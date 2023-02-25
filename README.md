<!--
<p align="center">
  <img src="https://github.com/cthoyt/quickstatements-client/raw/main/docs/source/logo.png" height="150">
</p>
-->

<h1 align="center">
  QuickStatements Client
</h1>

<p align="center">
    <a href="https://github.com/cthoyt/quickstatements_client/actions/workflows/tests.yml">
        <img alt="Tests" src="https://github.com/cthoyt/quickstatements_client/actions/workflows/tests.yml/badge.svg" />
    </a>
    <a href="https://pypi.org/project/quickstatements_client">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/quickstatements_client" />
    </a>
    <a href="https://pypi.org/project/quickstatements_client">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/quickstatements_client" />
    </a>
    <a href="https://github.com/cthoyt/quickstatements-client/blob/main/LICENSE">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/quickstatements_client" />
    </a>
    <a href='https://quickstatements-client.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/quickstatements-client/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href="https://codecov.io/gh/cthoyt/quickstatements-client/branch/main">
        <img src="https://codecov.io/gh/cthoyt/quickstatements-client/branch/main/graph/badge.svg" alt="Codecov status" />
    </a>  
    <a href="https://github.com/cthoyt/cookiecutter-python-package">
        <img alt="Cookiecutter template from @cthoyt" src="https://img.shields.io/badge/Cookiecutter-snekpack-blue" /> 
    </a>
    <a href='https://github.com/psf/black'>
        <img src='https://img.shields.io/badge/code%20style-black-000000.svg' alt='Code style: black' />
    </a>
    <a href="https://github.com/cthoyt/quickstatements-client/blob/main/.github/CODE_OF_CONDUCT.md">
        <img src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg" alt="Contributor Covenant"/>
    </a>
    <a href="https://zenodo.org/badge/latestdoi/606491168">
        <img src="https://zenodo.org/badge/606491168.svg" alt="DOI">
    </a>
</p>

A data model and client for Wikidata [QuickStatements](https://quickstatements.toolforge.org).

## 💪 Getting Started

Here's how to quickly construct some QuickStatements

```python
import datetime
from quickstatements_client import DateQualifier, EntityQualifier, TextQualifier, EntityLine

subject_qid = "Q47475003"  # Charles Tapley Hoyt
subject_orcid = "0000-0003-4423-4370"
reference_url_qualifier = TextQualifier(
   predicate="S854", target=f"https://orcid.org/0000-0003-4423-4370"
)
start_date = datetime.datetime(year=2021, day=15, month=2)
start_date_qualifier = DateQualifier.start_time(start_date)
position_held_qualifier = EntityQualifier(predicate="P39", target="Q1706722")
employment_line = EntityLine(
   subject=subject_qid,
   predicate="P108",  # employer
   target="Q49121",  # Harvard medical school
   qualifiers=[reference_url_qualifier, start_date_qualifier, position_held_qualifier],
)

>>> employment_line.get_line()
'Q47475003|P108|Q49121|S854|"https://orcid.org/0000-0003-4423-4370"|P580|+2021-02-15T00:00:00Z/11|P39|Q1706722',
```

How to send some QuickStatements to the API:

```python
from quickstatements_client import QuickStatementsClient

lines = [
   employment_line,
   ...
]

client = QuickStatementsClient(token=..., username=...)
res = client.post(lines, batch_name="Test Batch")
# see also res.batch_id

import webbrowser
webbrowser.open_new_tab(res.batch_url)
```

Note: `token` and `username` are automatically looked up with `pystow` if they aren't given.
Specifically, using `pystow.get_config("quickstatements", "token)` and
`pystow.get_config("quickstatements", "username")`.


## 🚀 Installation

The most recent release can be installed from
[PyPI](https://pypi.org/project/quickstatements_client/) with:

```shell
$ pip install quickstatements_client
```

The most recent code and data can be installed directly from GitHub with:

```bash
$ pip install git+https://github.com/cthoyt/quickstatements-client.git
```

## 👐 Contributing

Contributions, whether filing an issue, making a pull request, or forking, are appreciated. See
[CONTRIBUTING.md](https://github.com/cthoyt/quickstatements-client/blob/master/.github/CONTRIBUTING.md) for more information on getting involved.

## 👋 Attribution

This code was originally written as a contribution to [PyORCIDator](https://github.com/lubianat/pyorcidator).
Special thanks to Tiago Lubiana [@lubianat] and João Vitor [@jvfe] for discussions and testing.

### ⚖️ License

The code in this package is licensed under the MIT License.

<!--
### 📖 Citation

Citation goes here!
-->

<!--
### 🎁 Support

This project has been supported by the following organizations (in alphabetical order):

- [Harvard Program in Therapeutic Science - Laboratory of Systems Pharmacology](https://hits.harvard.edu/the-program/laboratory-of-systems-pharmacology/)

-->

<!--
### 💰 Funding

This project has been supported by the following grants:

| Funding Body                                             | Program                                                                                                                       | Grant           |
|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------|
| DARPA                                                    | [Automating Scientific Knowledge Extraction (ASKE)](https://www.darpa.mil/program/automating-scientific-knowledge-extraction) | HR00111990009   |
-->

### 🍪 Cookiecutter

This package was created with [@audreyfeldroy](https://github.com/audreyfeldroy)'s
[cookiecutter](https://github.com/cookiecutter/cookiecutter) package using [@cthoyt](https://github.com/cthoyt)'s
[cookiecutter-snekpack](https://github.com/cthoyt/cookiecutter-snekpack) template.

## 🛠️ For Developers

<details>
  <summary>See developer instructions</summary>

The final section of the README is for if you want to get involved by making a code contribution.

### Development Installation

To install in development mode, use the following:

```bash
$ git clone git+https://github.com/cthoyt/quickstatements-client.git
$ cd quickstatements-client
$ pip install -e .
```

### 🥼 Testing

After cloning the repository and installing `tox` with `pip install tox`, the unit tests in the `tests/` folder can be
run reproducibly with:

```shell
$ tox
```

Additionally, these tests are automatically re-run with each commit in a [GitHub Action](https://github.com/cthoyt/quickstatements-client/actions?query=workflow%3ATests).

### 📖 Building the Documentation

The documentation can be built locally using the following:

```shell
$ git clone git+https://github.com/cthoyt/quickstatements-client.git
$ cd quickstatements-client
$ tox -e docs
$ open docs/build/html/index.html
``` 

The documentation automatically installs the package as well as the `docs`
extra specified in the [`setup.cfg`](setup.cfg). `sphinx` plugins
like `texext` can be added there. Additionally, they need to be added to the
`extensions` list in [`docs/source/conf.py`](docs/source/conf.py).

### 📦 Making a Release

After installing the package in development mode and installing
`tox` with `pip install tox`, the commands for making a new release are contained within the `finish` environment
in `tox.ini`. Run the following from the shell:

```shell
$ tox -e finish
```

This script does the following:

1. Uses [Bump2Version](https://github.com/c4urself/bump2version) to switch the version number in the `setup.cfg`,
   `src/quickstatements_client/version.py`, and [`docs/source/conf.py`](docs/source/conf.py) to not have the `-dev` suffix
2. Packages the code in both a tar archive and a wheel using [`build`](https://github.com/pypa/build)
3. Uploads to PyPI using [`twine`](https://github.com/pypa/twine). Be sure to have a `.pypirc` file configured to avoid the need for manual input at this
   step
4. Push to GitHub. You'll need to make a release going with the commit where the version was bumped.
5. Bump the version to the next patch. If you made big changes and want to bump the version by minor, you can
   use `tox -e bumpversion -- minor` after.
</details>
