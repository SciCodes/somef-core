#!/usr/bin/env python3
"""
rebuild-from-somef.py
=====================
Regenerates somef-core from the latest version of somef (KnowledgeCaptureAndDiscovery/somef).

This script was built step by step with the help of AI, adding each requirement
as we discovered it while porting from somef to somef_core. It is meant to be
re-run whenever we want to pull in upstream changes.

Removes everything related to machine learning:
  - Full ML files/directories
  - ML imports and code blocks in shared files
  - ML dependencies in pyproject.toml
  - ML test files

File	        Test	                            Reason for removal
test_cli.py	    test_categorization	                application_type → check_ontologies
test_cli.py	    test_issue_314_2	                description → supervised_classification
test_cli.py	    test_issue_314_3	                description → supervised_classification
test_cli.py	    test_issue_379	                    description → supervised_classification
test_cli.py	    test_issue_388	                    ontologies → extract_ontologies
test_cli.py	    test_issue_428	                    description → supervised_classification
test_cli.py	    test_issue_457	                    description → supervised_classification
test_cli.py	    test_issue_531_ontology_metadata	ontologies → extract_ontologies

*Note: New tests from somef about classifieres, models, ontolggies should be removed or comeented in somef-core


It also removes (by decision of the original fork maintainers):
  - extract_ontologies.py, mapping/, export/turtle_export.py (they are not ML but
    the original fork removed them and that behavior is kept).

On top of the ML removal, it also applies a set of "surgeries" so that the
result keeps our tweaks in every regeneration:
  - configuration.py / __main__.py / utils/constants.py: no ML model prompts and
    config file moved to ~/.somef_core/config.json
  - test files: @patch("somef.X") -> @patch("somef_core.X")
  - namespace rename: src/somef -> src/somef_core (including imports)

IMPORTANT: src/somef_core/ is regenerated from somef every time this script
runs. Any change that only exists in somef-core will be replaced by whatever
somef has at that moment. If a local tweak must survive, it has to be added to
the script as a surgery (like the ones above), not made directly in the code.

Usage:
    python3 rebuild_from_somef/rebuild-from-somef.py [somef-branch]
    (by default it uses the 'dev' branch of the somef-upstream remote)

The script works on a temporary tree and does NOT modify your working tree
until the end. When finished, it syncs the files of the current somef-core
branch with the result. It never commits: git add/commit is up to you.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Full ML files/directories to delete (relative to src/somef)
ML_FILES_TO_DELETE = [
    "evaluation",           # ML classifier evaluation
    "rolf",                 # Related Ontology Learning Framework
    "models",               # trained models (.p, .sk)
    "mapping",              # RML/YARRRML (not ML, but the original fork removed it)
    "supervised_classification.py",
    "extract_ontologies.py",
    "export/turtle_export.py",
]

ML_TEST_FILES_TO_DELETE = [
    "test_supervised_classification.py",
    "test_extract_ontologies.py",
    "test_turtle_export.py",
]

# ML dependencies that are removed from pyproject.toml
ML_DEPENDENCIES = [
    "xgboost",
    "imbalanced-learn",
    "scikit-learn",
    "morph-kgc",
    "rdflib",
]


def run_git(args, cwd=None):
    """Runs a git command and returns the stdout."""
    result = subprocess.run(
        ["git"] + args, cwd=cwd or REPO_ROOT,
        capture_output=True, text=True, check=True
    )
    return result.stdout


def git_rev_exists(rev):
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", rev],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    return result.returncode == 0


def checkout_remote(rev, dest):
    """Checks out the content of a git revision into a directory."""
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, ".gitignore"), "w") as fh:
        fh.write("")
    archive = subprocess.run(
        ["git", "archive", rev], cwd=REPO_ROOT, capture_output=True, check=True
    )
    subprocess.run(
        ["tar", "-x", "-C", dest], input=archive.stdout, check=True
    )


def delete_paths(base_dir, paths):
    for rel in paths:
        full = os.path.join(base_dir, rel)
        if os.path.isdir(full):
            shutil.rmtree(full)
        elif os.path.isfile(full):
            os.remove(full)


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def remove_block(content, start_marker, end_marker, label):
    """Removes a code block starting at start_marker (inclusive)
    and ending at end_marker (exclusive, first match after start)."""
    idx = content.find(start_marker)
    if idx == -1:
        print(f"  [WARN] Block start not found: {label}")
        return content
    end = content.find(end_marker, idx + len(start_marker))
    if end == -1:
        print(f"  [WARN] Block end not found: {label}")
        return content
    removed = content[idx:end]
    print(f"  [OK] Block removed ({label}): {len(removed)} chars")
    return content[:idx] + content[end:]


def surgery_somef_cli(content):
    """Removes the import and blocks of supervised_classification from somef_cli.py."""
    # 1. Remove supervised_classification from the import
    content = re.sub(
        r"from \. import header_analysis, regular_expressions, process_repository, "
        r"configuration, process_files, \\\n\s+supervised_classification",
        "from . import header_analysis, regular_expressions, process_repository, "
        "configuration, process_files",
        content,
    )
    print("  [OK] Import supervised_classification removed")

    # 2. Remove imports from mardown_parser/create_excerpts
    content = re.sub(
        r"from \.parser import mardown_parser, create_excerpts\n",
        "", content,
    )
    print("  [OK] Import mardown_parser/create_excerpts removed")

    # 3. Remove import of DataGraph (turtle_export)
    content = re.sub(
        r"from \.export\.turtle_export import DataGraph\n",
        "", content,
    )
    print("  [OK] Import of DataGraph removed")

    # 4. Remove the block of supervised classification
    start = "        if not ignore_classifiers and readme_unfiltered_text != '':\n"
    end = "        if readme_text_unmarked != \"\":\n"
    content = remove_block(content, start, end, "supervised_classification en cli_get_data")

    # 5. Remove the block of DataGraph/graph_out
    start = "    if graph_out is not None:\n"
    end = "def verify_and_resolve_token"
    content = remove_block(content, start, end, "function graph_out/DataGraph")

    return content


def surgery_process_files(content):
    """Removes extract_ontologies from process_files.py."""
    # 1. Remove extract_ontologies from the import
    content = re.sub(
        r"from \. import extract_ontologies, extract_workflows",
        "from . import extract_workflows",
        content,
    )
    print("  [OK] Import extract_ontologies removed (process_files.py)")

    # 2. Remove the block of ontology detection
    start = '                if filename.endswith(".ttl") or filename.endswith(".owl") or filename.endswith(".nt") or filename. \\\n                        endswith(".xml"):\n'
    end = "                if filename.upper() == constants.CODEOWNERS_FILE:\n"
    content = remove_block(content, start, end, "ontology detection (process_files.py)")

    return content


def surgery_extract_software_type(content):
    """Removes check_ontologies from extract_software_type.py."""
    # 1. Remove import of is_file_ontology
    content = re.sub(
        r"from \.extract_ontologies import is_file_ontology\n",
        "", content,
    )
    print("  [OK] Import of is_file_ontology removed")

    # 2. Remove the block elif check_ontologies
    start = "    elif check_ontologies(path_repo):\n"
    end = "    elif check_notebooks(path_repo):\n"
    content = remove_block(content, start, end, "elif check_ontologies")

    # 3. Remove the function check_ontologies
    start = "def check_ontologies(path_repo):\n"
    end = "def check_command_line(path_repo):\n"
    content = remove_block(content, start, end, "function check_ontologies")

    return content

def surgery_test_software_type(content):
    """Removes check_ontologies from test_software_type.py."""
    # 1. Remove check_ontologies from the import
    content = re.sub(
        r"from \.\.extract_software_type import check_ontologies, ",
        "from ..extract_software_type import ",
        content,
    )
    print("  [OK] Import check_ontologies removed (test_software_type.py)")

    # 2. Comment out the ontology tests (they use the removed function)
    start = "    def test_true_ontology(self):\n"
    end = "    def test_true_notebooks(self):\n"
    block = remove_block(content, start, end, "ontology tests (test_software_type.py)")
    commented = "\n".join(
        "# " + line if line.strip() else line
        for line in block.split("\n")
    )
    return commented
def rename_namespace(tree_dir):
    """Renames src/somef -> src/somef_core and updates absolute imports."""
    src = os.path.join(tree_dir, "src", "somef")
    dst = os.path.join(tree_dir, "src", "somef_core")
    if os.path.exists(src) and not os.path.exists(dst):
        os.rename(src, dst)

    # Update absolute imports 'from somef.X' -> 'from somef_core.X'
    for root, _, files in os.walk(dst):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            full = os.path.join(root, fname)
            content = read_file(full)
            new_content = re.sub(r"\bfrom somef\.", "from somef_core.", content)
            new_content = re.sub(r"\bimport somef\.", "import somef_core.", new_content)
            new_content = new_content.replace('"somef.', '"somef_core.') 
            if new_content != content:
                write_file(full, new_content)
    print("  [OK] Namespace somef -> somef_core (src)")

    # Same for tests (they may import 'somef.X')
    test_dir = os.path.join(tree_dir, "src", "somef_core", "test")
    if os.path.exists(test_dir):
        for root, _, files in os.walk(test_dir):
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                full = os.path.join(root, fname)
                content = read_file(full)
                new_content = re.sub(r"\bfrom somef\.", "from somef_core.", content)
                new_content = re.sub(r"\bimport somef\.", "import somef_core.", new_content)
                new_content = new_content.replace('"somef.', '"somef_core.')
                if new_content != content:
                    write_file(full, new_content)


def update_pyproject(tree_dir, somef_version):
    """Updates pyproject.toml: name, homepage, dependencies and scripts."""
    path = os.path.join(tree_dir, "pyproject.toml")
    content = read_file(path)

    content = content.replace('name = "somef"', 'name = "somef_core"')
    content = content.replace(
        'homepage = "https://github.com/KnowledgeCaptureAndDiscovery/somef"',
        'homepage = "https://github.com/SciCodes/somef-core"',
    )
    # Packages to include
    content = content.replace(
        '{ include = "somef", from = "src" }',
        '{ include = "somef_core", from = "src" }',
    )
    # CLI entry script
    content = content.replace(
        'somef = "somef.__main__:cli"',
        'somef_core = "somef_core.__main__:cli"',
    )

    # remove ML dependencies
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        stripped = line.strip()
        dep_name = stripped.split("=")[0].strip().strip('"')
        if dep_name in ML_DEPENDENCIES:
            continue
        new_lines.append(line)
    content = "\n".join(new_lines)

    write_file(path, content)
    print("  [OK] pyproject.toml updated")


def update_config_json(tree_dir):
    """Removes references to models/ from config.json."""
    path = os.path.join(tree_dir, "config.json")
    if not os.path.exists(path):
        return
    content = read_file(path)
    # remove keys pointing to ML models
    content = re.sub(r'\s*"(description|citation|installation|invocation)"\s*:\s*"\./models/[^"]*",?\n', "", content)
    write_file(path, content)
    print("  [OK] config.json updated")


def sync_to_working_tree(tree_dir):
    """Synchronizes the reconstructed content with the current branch of somef-core."""

    src_dst = os.path.join(REPO_ROOT, "src", "somef_core")
    src_src = os.path.join(tree_dir, "src", "somef_core")
    if os.path.exists(src_dst):
        shutil.rmtree(src_dst)
    if os.path.exists(src_src):
        shutil.copytree(src_src, src_dst)

    # Copy key root files
    for fname in ["pyproject.toml", "config.json", "README.md", "LICENSE"]:
        full = os.path.join(tree_dir, fname)
        if os.path.exists(full):
            shutil.copy2(full, os.path.join(REPO_ROOT, fname))

def surgery_configuration(content):
    """Removes ML model handling from configuration.py."""

    # a) comment out the default model file paths
    content = content.replace(
        'default_description = os.path.join(str(path), "models", "description.p")',
        '# default_description = os.path.join(str(path), "models", "description.p")')
    content = content.replace(
        'default_invocation = os.path.join(str(path), "models", "invocation.p")',
        '# default_invocation = os.path.join(str(path), "models", "invocation.p")')
    content = content.replace(
        'default_installation = os.path.join(str(path), "models", "installation.p")',
        '# default_installation = os.path.join(str(path), "models", "installation.p")')
    content = content.replace(
        'default_citation = os.path.join(str(path), "models", "citation.p")',
        '# default_citation = os.path.join(str(path), "models", "citation.p")')

    # b) point the config file to the somef_core location
    content = content.replace(
        "os.getenv(\"SOMEF_CONFIGURATION_FILE\", '~/.somef/config.json')",
        "os.getenv(\"SOMEF_CONFIGURATION_FILE\", '~/.somef_core/config.json')")

    # c) signature defaults: model files -> None
    content = content.replace('description=default_description,', 'description=None,')
    content = content.replace('invocation=default_invocation,', 'invocation=None,')
    content = content.replace('installation=default_installation,', 'installation=None,')
    content = content.replace('citation=default_citation,', 'citation=None,')

    # d) do not write model keys into the saved config dict
    content = content.replace('        constants.CONF_DESCRIPTION: description,\n', '')
    content = content.replace('        constants.CONF_INVOCATION: invocation,\n', '')
    content = content.replace('        constants.CONF_INSTALLATION: installation,\n', '')
    content = content.replace('        constants.CONF_CITATION: citation,\n', '')

    print("  [OK] Model handling removed from configuration.py")
    return content

def surgery_main(content):
    """Removes classifier model prompts from __main__.py."""

    # a) comment out the 4 model prompts
    content = content.replace(
        '        description = click.prompt("Documentation classifier model file", default=configuration.default_description)',
        '        # description = click.prompt(... model file ...)')
    content = content.replace(
        '        invocation = click.prompt("Invocation classifier model file", default=configuration.default_invocation)',
        '        # invocation = click.prompt(...)')
    content = content.replace(
        '        installation = click.prompt("Installation classifier model file", default=configuration.default_installation)',
        '        # installation = click.prompt(...)')
    content = content.replace(
        '        citation = click.prompt("Citation classifier model file", default=configuration.default_citation)',
        '        # citation = click.prompt(...)')

    # b) pass None for the model args in the configure() call
    content = content.replace(
        "description, invocation, installation, citation, base_uri,  download_limit_mb= download_limit)",
        "description=None, invocation=None, installation=None, citation=None, base_uri=base_uri, download_limit_mb=download_limit)")

    print("  [OK] Model prompts removed from __main__.py")
    return content


def surgery_constants(content):
    """Points the default config file location to somef_core."""
    content = content.replace(
        '__DEFAULT_SOMEF_CONFIGURATION_FILE__ = "~/.somef/config.json"',
        '__DEFAULT_SOMEF_CONFIGURATION_FILE__ = "~/.somef_core/config.json"')
    print("  [OK] Default config path moved to ~/.somef_core")
    return content

def main():
    parser = argparse.ArgumentParser(description="Rebuild somef-core from somef")
    parser.add_argument(
        "branch", nargs="?", default="somef-upstream/dev",
        help="Revision of somef to use (default: somef-upstream/dev)",
    )
    args = parser.parse_args()

    branch = args.branch
    if not git_rev_exists(branch):
        print(f"[ERROR] The revision '{branch}' does not exist. "
              f"Make sure you have the somef-upstream remote updated (git fetch somef-upstream).")
        sys.exit(1)

    print(f"[1/6] Extracting somef from {branch} ...")
    tmp = tempfile.mkdtemp(prefix="somef_rebuild_")
    try:
        checkout_remote(branch, tmp)
        somef_version = "?"
        for line in read_file(os.path.join(tmp, "pyproject.toml")).splitlines():
            if line.strip().startswith("version"):
                somef_version = line.split("=")[1].strip().strip('"')
                break
        print(f"      Version of somef: {somef_version}")

        print("[2/6] Eliminating ML files/directories ...")
        src_base = os.path.join(tmp, "src", "somef")
        delete_paths(src_base, ML_FILES_TO_DELETE)
        delete_paths(os.path.join(src_base, "test"), ML_TEST_FILES_TO_DELETE)
        # experiments and notebooks (contain models/training)
        for extra in ["experiments", "notebook"]:
            full = os.path.join(tmp, extra)
            if os.path.exists(full):
                shutil.rmtree(full)
                print(f"      [OK] {extra} removed")

        print("[3/6] Applying surgery to shared files ...")
        for fname, surgery in [
            ("somef_cli.py", surgery_somef_cli),
            ("process_files.py", surgery_process_files),
            ("extract_software_type.py", surgery_extract_software_type),
            ("test/test_software_type.py", surgery_test_software_type),
            ("configuration.py", surgery_configuration),
            ("__main__.py", surgery_main),
            ("utils/constants.py", surgery_constants),
        ]:
            full = os.path.join(src_base, fname)
            if os.path.exists(full):
                content = surgery(read_file(full))
                write_file(full, content)

        print("[4/6] Renaming namespace somef -> somef_core ...")
        rename_namespace(tmp)

        print("[5/6] Updating pyproject.toml, config.json ...")
        update_pyproject(tmp, somef_version)
        update_config_json(tmp)

        print("[6/6] Synchronizing with the current branch of somef-core ...")
        sync_to_working_tree(tmp)

        print("\n[OK] Rebuild completed.")
        print("\n[REMINDER] Tests that depend on removed ML/ontology features must be removed or commented:")
        print("  - test_cli.py: test_categorization, test_issue_314_2, test_issue_314_3, test_issue_379,")
        print("    test_issue_388, test_issue_428, test_issue_457, test_redundant_files")
        print("  - test_codemeta_export.py: test_issue_544")
        print("  - test_process_repository.py: test_issue_611")
        print("  Run pytest and delete/comment any NEW test that fails with KeyError of")
        print("  'description', 'ontologies', 'application_type' or 'applicationCategory'.")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
