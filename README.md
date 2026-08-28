# SOMEF - Core package functionality

SOMEF-Core is the lightweight metadata extraction engine behind SOMEF. It works both as a command line tool and as a reusable library, without the machine learning components (supervised classifiers, ontology detection) that are part of the full SOMEF tool. See the SOMEF repository for the full documentation and ML capabilities.

**Demo:** See a [demo running somef as a service](https://somef.linkeddata.es), through the [SOMEF-Vider tool](https://github.com/SoftwareUnderstanding/SOMEF-Vider/).

**Authors:** Daniel Garijo, Allen Mao, Miguel Ángel García Delgado, Haripriya Dharmala, Vedant Diwanji, Jiaying Wang, Aidan Kelley, Jenifer Tabita Ciuciu-Kiss, Luca Angheluta, Juanje Mendoza, Anas El Hounsri and Thomas Vuillaume.

## Features

Given a readme file (or a GitHub/Gitlab/Codeberg/Bitbucket repository) SOMEF-Core will extract the following categories (if present), listed in alphabetical order:

- **Acknowledgement**: Text acknowledging funding sources or contributors
- **Authors**: Person(s) or organization(s) responsible for the project. We recognize the following properties:
  - Name: name of the author (including last name)
  - Given name: First name of an author
  - Family name: Last name of an author
  - Email: email of author
  - URL: website or ORCID associated with the author
- **Application type**: type of software (command line application, notebook,scientific workflow, etc.). Note: Ontology type only detectect in SOMEF.
- **Build file**: Build file(s) of the project. For example, files used to create a Docker image for the target software, package files, etc.
- **Citation**: Preferred citation(s) as the authors have stated in their readme file. SOMEF-Core recognizes Bibtex, Citation File Format files and other means by which authors cite their papers (e.g., by in-text citation). 
For CITATION.cff files, SOMEF-Core now generates two separate entries: one for the software tool and another for the preferred citation (if available). This ensures metadata like DOI or version is correctly assigned to each entity.
SOMEF-Core now performs citation reconciliation: scholarly publications (articles) are assigned in codemeta to `referencePublication`, while the software itself is credited in `creditText`. (See https://somef.readthedocs.io/en/latest/output/#codemeta-format).
When using `-e`, publication metadata is enriched via OpenAlex. We recognize the following properties:
  - Title: Title of the publication
  - Author: list of author names in the publication
  - URL: URL of the publication 
  - DOI: Digital object identifier of the publication
  - Date published
  - Journal: Journal name where the paper was published
  - Year: Year of publication
  - Pages: Page range in the journal
  - `openalex_id`: OpenAlex ID of the publication
- **Code of conduct**: Link to the code of conduct of the project
- **Code repository**: Link to the GitHub/GitLab/Codeberg and Bitbucket repository used for the extraction
- **Contact**: Contact person responsible for maintaining a software component
- **Continuous integration**: Link to continuous integration service(s)
- **Contribution guidelines**: Text indicating how to contribute to this code repository
- **Contributor**: Contributors to a software component. Note: Contributor metadata is exported from metadata files (e.g., CodeMeta, CONTRIBUTORS, etc.) not from git logs.
- **Creation date**: Date when the repository was created
- **Copyright holder**: Entity or individual owning the rights to the software. The year is also extracted, if available.
- **Date updated**: Date of last release.
- **Description**: A description of what the software does
- **Documentation**: Where to find additional documentation about a software component
- **Download URL**: URL where to download the target software (typically the installer, package or a tarball to a stable version)
- **Executable examples**: Jupyter notebooks ready for execution (e.g., files, or through myBinder/colab links)
- **FAQ**: Frequently asked questions about a software component
- **Forks count**: Number of forks of the project
- **Forks url**: Links to forks made of the project
- **Full name**: Name + owner (owner/name)
- **Full title**: If the repository is a short name, we will attempt to extract the longer version of the repository name
- **Funding**: Funding information associated with the project. **Note**: This information is extracted from `codemeta.json` files within the repository and from the README (funding section headers and links to crowdfunding platforms). When using `-e`, the project data is enriched with OpenAIRE, adding:
- `project_code`: Project code
- `project_title`: Project title
- `project_acronym`: Project acronym
- `grant_id`: Call/grant identifier
- **Identifier**: Identifier associated with the software (if any), such as Digital Object Identifiers and Software Heritage identifiers (SWH). DOIs associated with publications will also be detected. When using `-e`, the following enrichment identifiers are also added:
- `openaire_id`: URL to the OpenAIRE explore page for the software
- `swhid`: Software Heritage identifier (for Zenodo DOIs)
- **Images**: Images used to illustrate the software component
- **Installation instructions**: A set of instructions that indicate how to install a target repository
- **Invocation**: Execution command(s) needed to run a scientific software component
- **Issue tracker**: Link where to open issues for the target repository
- **Keywords**: set of terms used to commonly identify a software component
- **License**: License and usage terms of a software component. Now we also extract license from citation.cff.
- **Logo**: Main logo used to represent the target software component
- **Maintainer**: Individuals or teams responsible for maintaining the software component, extracted from the CODEOWNERS file
- **Name**: Name identifying a software component
- **Owner**: Name and type of the user or organization in charge of the repository
- **Package distribution**: Links to package sites like pypi in case the repository has a package available.
- **Package files**: Links to package files used to wrap the project in a package.
- **Programming languages**: Languages used in the repository
- **Related papers**: URL to possible related papers within the repository stated within the readme file (from Arxiv)
- **Releases**: Pointer to the available versions of a software component. For each release, somef will track the following properties:
  - Description: Release notes
  - Author: Agent responsible of creating the release
  - Name: Name of the release
  - Tag: version number of the release
  - Date of publication
  - Date of creation
  - Link to the html page of the release
  - Id of the release
  - Link to the tarball zip and code of the release 
- **Repository status**: Repository status as it is described in [repostatus.org](https://www.repostatus.org/).
- **Requirements**: Pre-requisites and dependencies needed to execute a software component
- **Run**: Running instructions of a software component. It may be wider than the `invocation` category, as it may include several steps and explanations.
- **Runtime platform**: specifies the runtime environment or script interpreter dependencies (e.g., Python, Java).
- **Script files**: Bash script files contained in the repository
- **Stargazers count**: Total number of stargazers of the project
- **Support**: Guidelines and links of where to obtain support for a software component
- **Support channels**: Help channels one can use to get support about the target software component
- **Usage examples**: Assumptions and considerations recorded by the authors when executing a software component, or examples on how to use it
- **Workflows**: URL and path to the computational workflow files present in the repository


### Confidence values in header analysis

When extracting metadata through header analysis, SOMEF-Core filters out headers
whose confidence is below a certain threshold to avoid false positives.
For instance, a header with 11+ words receives a confidence of 0.1, which
is considered too low for a reliable classification — such headers are
discarded from the results. The filtering ensures that only headers with a
reasonable match quality are reported in the output.

| Header length | Confidence |
|---------------|------------|
| 1–3 words     | 1.0        |
| 4–6 words     | 0.8        |
| 7–10 words    | 0.5        |
| 11+ words     | 0.1        |

## Documentation

See full documentation at [https://somef.readthedocs.io/en/latest/](https://somef.readthedocs.io/en/latest/)

## Cite SOMEF-Core:

Journal publication (preferred):

```
@article{10.1162/qss_a_00167,
    author = {Kelley, Aidan and Garijo, Daniel},
    title = "{A Framework for Creating Knowledge Graphs of Scientific Software Metadata}",
    journal = {Quantitative Science Studies},
    pages = {1-37},
    year = {2021},
    month = {11},
    issn = {2641-3337},
    doi = {10.1162/qss_a_00167},
    url = {https://doi.org/10.1162/qss_a_00167},
    eprint = {https://direct.mit.edu/qss/article-pdf/doi/10.1162/qss\_a\_00167/1971225/qss\_a\_00167.pdf},
}
```

Conference publication (first):

```
@INPROCEEDINGS{9006447,
author={A. {Mao} and D. {Garijo} and S. {Fakhraei}},
booktitle={2019 IEEE International Conference on Big Data (Big Data)},
title={SoMEF: A Framework for Capturing Scientific Software Metadata from its Documentation},
year={2019},
doi={10.1109/BigData47090.2019.9006447},
url={http://dgarijo.com/papers/SoMEF.pdf},
pages={3032-3037}
}
```

## Requirements

- Python 3.11 + (default version support). Python 3.9 and 3.10 will work, but are not supported anymore.

SOMEF-Core has been tested on Unix, MacOS and Windows Microsoft operating systems.

If you face any issues when installing SOME-Core, please make sure you have installed the following packages: `build-essential`, `libssl-dev`, `libffi-dev` and `python3-dev`.


## Install from GitHub

To run SOMEF, please follow the next steps:

Clone this GitHub repository

```
git clone https://github.com/SciCodes/somef-core.git
```

We use [Poetry](https://python-poetry.org/) to ensure library compatibility. It can be installed as follows:

```
curl -sSL https://install.python-poetry.org | python3 -
```

This option is recommended over installing Poetry with pip install.

Now Poetry will handle the installation of SOMEF and all its dependencies configured in the `toml` file.

To test the correct installation of poetry run (poetry version `> 2.0.0`):

```
poetry --version
```

Install somef and all their dependencies.

```
cd /somef_core
poetry install
```

Now we need to access our virtual environment, to do so you can run the following command:

```bash
poetry env activate
```
If the environment is not active, paste the command shown when `poetry env activate` is run, typically something like the command below: 

```bash
source /path_to_env/ENV_NAME/bin/activate
```

To learn more about poetry environment management, visit their official documentation [here](https://python-poetry.org/docs/managing-environments/).

Test the SOMEF installation run:

```bash
somef_core --help
```

If everything goes fine, you should see:

```bash
Usage: somef [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  configure  Configure credentials file path
  describe   Running the Command Line Interface
  version    Show somef version.
```


## Configure

Before running SOMEF-Core for the first time, you must **configure** it appropriately (you only need to do this once). Run:

```bash
somef_core configure
```

And you will be asked to provide the following:

- A **GitHub** authentication token [**optional, leave blank if not used**], which SOMEF uses to retrieve metadata from GitHub. If you don't include an authentication token, you can still use SOMEF. However, you may be limited to a series of requests per hour. For more information, see [https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
- A **GitLab** authentication token [**optional**], used for GitLab.com and self-hosted GitLab instances (e.g., `gitlab.in2p3.fr`). Tokens are per-instance. Note: **a token from GitLab.com does not work for self-hosted servers**. Create one at `https://gitlab.com/-/user_settings/personal_access_tokens` (scope: `read_api`). Without a token, some self-hosted GitLab instances may not return rate limit information.
- A **Codeberg** authentication token [**optional**], used to retrieve metadata from Codeberg. Create one at `https://codeberg.org/user/settings/applications` (permissions: `read:repository`, `read:user`). Codeberg (Forgejo) does not expose rate limit headers even with a token.
- A **Bitbucket** authentication token [**optional**], used for Bitbucket Cloud. Create an API token with scopes at `https://bitbucket.org/account/settings/api-tokens/` (permissions: `read:repository:bitbucket`, `read:account`). You will also need to provide your Atlassian account email, as Bitbucket API tokens use Basic authentication (`email:token` encoded in base64). Without a token you are limited to 60 requests/hour.
- A download size limit in MB [**optional, default 200**]. SOMEF skips repository archives larger than this limit. Increase it if you need to process large repositories. You can also override it with the `--download-limit` parameter in the `describe` command.

If you want SOMEF to be automatically configured (without any tokens) just type:

```bash
somef_core configure -a
```

For showing help about the available options, run:

```bash
somef_core configure --help
```

Which displays:

```bash
Usage: somef_core configure [OPTIONS]

  Configure GitHub credentials file path

Options:
  -a, --auto  Automatically configure SOMEF
  -b, --base_uri URL  Base URI for somef transformations
  -h, --help  Show this message and exit.

Commands:
  test  Test the configured API tokens
```

### Testing your tokens

To verify that the authentication tokens stored in your configuration file are valid **without having to run SOMEF**, run:

```bash
somef_core configure test
```

This contacts each configured provider's API (api.github.com, gitlab.com, codeberg.org, bitbucket.org) with the token stored in ~/.somef_core/config.json and reports the status of each one, e.g.:
```bash
GitHub: token valid
GitLab: token valid
Codeberg: token valid
Bitbucket: token valid but with limited permissions (403)
```

401 means the token is invalid; 403 means it is valid but lacks the required scopes; any other non-200 response is reported as unexpected.
Providers without a configured token are simply skipped.
Bitbucket tokens must start with Basic (as set by somef configure); otherwise the test reports an incorrect format without contacting the API.
The command exits with a non-zero status code if any configured token is invalid, which is useful for scripts and CI.


### Updating SOMEF-Core

If you update SOMEF to a newer version, you must `configure` again the library (by running `somef_core configure`). 

If you installed through poetry and you  have upgraded the python environment (e.g., from 3.10 to 3.11), you may need to run `poetry env use python3.11` and `poetry install` to update your environment.

## Usage

```bash
$ somef_core describe --help
  SOMEF Command Line Interface
Usage: somef_core describe [OPTIONS]

  Running the Command Line Interface

Options:
  -t, --threshold FLOAT           Threshold to classify the text  [required]
  Input: [mutually_exclusive, required]
    -r, --repo_url URL            Github/Gitlab/Codeberg/Bitbucket Repository URL
    -d, --doc_src PATH            Path to the README file source
    -i, --in_file PATH            A file of newline separated links to GitHub/
                                  Gitlab/Codeberg/Bitbucket repositories
    -l, --local_repo PATH         Path to the local repository source. No APIs will be used

  Output: [required_any]
    -o, --output PATH             Path to the output file. If supplied, the
                                  output will be in JSON
    -c, --codemeta_out PATH       Path to an output codemeta file
    -g, --graph_out PATH          Path to the output Knowledge Graph export
                                  file. If supplied, the output will be a
                                  Knowledge Graph, in the format given in the
                                  --format option chosen (turtle, json-ld)
    -gc, --google_codemeta_out PATH Path to a Google-compliant Codemeta JSON-LD
                                    file. This output transforms the standard
                                    Codemeta to follow Google’s expected JSON-LD
                                    structure.
                                    
  -f, --graph_format [turtle|json-ld]
                                  If the --graph_out option is given, this is
                                  the format that the graph will be stored in

  -p, --pretty                    Pretty print the JSON output file so that it
                                  is easy to compare to another JSON output
                                  file.

  -m, --missing                   The JSON will include a field
                                  somef_missing_categories to report with the
                                  missing metadata fields that SOMEF was not
                                  able to find.

  -kt, --keep_tmp PATH            SOMEF will NOT delete the temporary folder
                                  where files are stored for analysis. Files
                                  will be stored at the
                                  desired path

  -all, --requirements_all        Export all detected requirements, including
                                  text and libraries (default).

  -v, --requirements_v            Export only requirements from structured
                                  sources (pom.xml, requirements.txt, etc.)


  -ra, --reconcile_authors         SOMEF will extract additional information 
                                  from certain files like CODEOWNERS. 
                                  This may require extra API
                                  requests and increase execution time
  --download-limit INTEGER        Download size limit in MB for repository
                                  archives. Overrides the value set in the
                                  configuration file.

  -h, --help                      Show this message and exit.

  -e, --enrichment                Enrich metadata with external APIs (OpenAlex, 
                                  OpenAIRE, Zenodo)

  --github-token TEXT             GitHub personal access token (if invalid,
                                  stored config is used instead)

  --gitlab-token TEXT             GitLab personal access token (if invalid,
                                  stored config is used instead)

  --codeberg-token TEXT           Codeberg personal access token (if invalid,
                                  stored config is used instead)

  --bitbucket-token TEXT          Bitbucket app password (if invalid, stored 
                                  config is used instead)

  --bitbucket-email TEXT          Bitbucket Atlassian account email (required
                                  with --bitbucket-token)
              

  
  Repoository versions [mutually_exclusive] (see section *Repository versions*t):
  -b, --branch name branch        Branch of the repository to analyze. Overrides the default branch.

  --tag text                      Tag of the repository to analyze. Cannot be used together with --branch and --commit

  --commit  TEXT                  Commit SHA to analyze. Cannot be used together 
                                  with --branch or --tag.
```

Alternatively, you can set tokens via environment variables or by running `somef_core configure`, which stores them permanently.
The CLI flags take precedence over stored config when valid.


### Enrichment with `-e`

The `-e` (or `--enrichment`) flag queries external APIs to complete the extracted metadata:
- **OpenAlex**: Adds `openalex_id` to DOIs of publications and reconciles missing author ORCIDs.
- **OpenAIRE**: Adds `openaire_id` to publications/identifiers and enriches project funding metadata.
- **Zenodo**: Adds `swhid` (Software Heritage ID) for records matching Zenodo DOIs.

For a detailed technical breakdown of the fields mapped by each external service, please refer to the specific documentation pages:
- See the [OpenAlex Mapping Guide](openalex.md) for citation and author properties.
- See the [OpenAIRE and Zenodo Mapping Guide](openaire.md) for funding and identifier properties.

**Note:** Enrichment makes additional network requests to external services, which may slow down the overall execution time. Use this flag only when you need the extra metadata.

## Usage example:

The following command extracts all metadata available from [https://github.com/dgarijo/Widoco/](https://github.com/dgarijo/Widoco/).

```bash
somef_core describe -r https://github.com/dgarijo/Widoco/ -o test.json -t 0.8
```

We recommend having a high value for the `threshold` parameter, 0.8 (default) or above.
Additional configuration parameters (such as the `similarity_threshold` for header analysis) 
can be set in `~/.somef_core/config.json`. See the [usage documentation](https://somef.readthedocs.io/en/latest/usage/) for details.


## Contribute:

If you want to contribute with a pull request, please do so by submitting it to the `dev` branch.

## Contributors:
Priyanka O.

## Next features:

To see upcoming features, please have a look at our [open issues](https://github.com/KnowledgeCaptureAndDiscovery/somef/issues) and [milestones](https://github.com/KnowledgeCaptureAndDiscovery/somef/milestones)
For the time being, issues, feature requests and improvements are tracked and managed in the SOMEF repository. Please open your issues there.


## Metadata Support

SOMEF-Core supports the extraction and analysis of metadata in package files of several programming languages.  Current support includes: `setup.py` and `pyproject.toml` for Python, `pom.xml` for Java, `.gemspec` for Ruby, `DESCRIPTION` for R, `bower.json` for JavaScript, HTML or CSS, `.cabal` for Haskell, `cargo.toml` for RUST, `composer` for PHP, `.juliaProject.toml` for Julia , `AUTHORS`, `codemeta.json`, `publiccode.yml`, `dockerfile` and `citation.cff`
This includes identifying dependencies, runtime requirements, and development tools specified in project configuration files.  

## Limitations

SOMEF-Core is designed to work primarily with repositories written in English.  
Repositories in other languages may not be processed as effectively, and results could be incomplete or less accurate.

### Enrichment with `-e`

The `-e` (or `--enrichment`) flag queries external APIs to complete the extracted metadata:
- **OpenAlex**: adds `openalex_id` to DOIs of publications.
- **OpenAIRE**: adds `openaire_id` and enriches funding information (project code, title, acronym, grant id).
- **Zenodo**: adds `swhid` (Software Heritage ID) for Zenodo DOIs.

**Note:** Enrichment makes additional network requests to external services, which may slow down the overall execution time. Use this flag only when you need the extra metadata.

## Repository versions: default behavior, branch tag and commit

SOMEF-Core allows analyzing specific versions of a repository. If no version is specified, SOMEF will analyze the default branch of the repository (usually `main` or `master`). The following options let you control exactly which version of the codebase is inspected.

### Default behavior

If neither `--branch` nor `--tag` is provided, SOMEF-Core will:

- Clone the repository.
- Detect and analyze the **default branch** set up in github.

This is the recommended option when you want to describe the current version of a a project.

### Using a branch

```bash
somef_core describe -r <repo_url> --branch <branch_name> ...
somef_core describe -r <repo_url> --b <branch_name> ...
```

Forces SOMEF-Core to analyze a specific branch of the repository.

Useful when:

- The project maintains development, release or feature branches.
- You need to compare metadata across branches.
- You want to reproduce an analysis on a branch that is not the default one.

### Using a tag

```bash
somef_core describe -r <repo_url> --tag <tag_name> ...
```

Analyzes a specific tagged version of the repository.

Recommended when:

- You need reproducible results (tags do not change over time).
- You want to document a released version of the software.
- You integrate SOMEF-Core into pipelines that operate on versioned artifacts.


### Using a commit

```bash
somef_core describe -r <repo_url> --commit <commit_sha> ...
```

### Restrictions

- `--branch`, `--tag` and `--commit` are mutually exclusive.
- If either option is provided, it overrides the default branch behavior.