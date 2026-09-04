#!/usr/bin/env python3

import json
import sys
from pathlib import Path

import yaml


REQUIRED_KEYS = {
    "id",
    "repo",
    "category",
    "collect",
    "include_in_rollups",
}


def fail(message: str) -> None:
    raise SystemExit(f"configuration error: {message}")


def load_config(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except yaml.YAMLError as exc:
        fail(f"invalid YAML in {path}: {exc}")

    if not isinstance(data, dict):
        fail("top-level YAML value must be a mapping")

    if data.get("version") != 1:
        fail("unsupported or missing configuration version")

    repositories = data.get("repositories")
    if not isinstance(repositories, list):
        fail("'repositories' must be a list")

    return data


def build_matrix(data: dict) -> list[dict[str, str]]:
    matrix: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_repos: set[str] = set()

    for index, item in enumerate(data["repositories"], start=1):
        if not isinstance(item, dict):
            fail(f"repository entry #{index} must be a mapping")

        missing = REQUIRED_KEYS - item.keys()
        if missing:
            fail(
                f"repository entry #{index} is missing: "
                + ", ".join(sorted(missing))
            )

        repo_id = item["id"]
        repo = item["repo"]

        if not isinstance(repo_id, str) or not repo_id.strip():
            fail(f"repository entry #{index} has an invalid id")

        if not isinstance(repo, str) or repo.count("/") != 1:
            fail(f"repository '{repo_id}' has an invalid repo value")

        if repo_id in seen_ids:
            fail(f"duplicate repository id: {repo_id}")

        if repo in seen_repos:
            fail(f"duplicate repository: {repo}")

        seen_ids.add(repo_id)
        seen_repos.add(repo)

        for boolean_key in ("collect", "include_in_rollups"):
            if not isinstance(item[boolean_key], bool):
                fail(
                    f"repository '{repo_id}' field '{boolean_key}' must be boolean"
                )

        if item["include_in_rollups"] and not item["collect"]:
            fail(
                f"repository '{repo_id}' cannot be included in rollups when collect=false"
            )

        if item["collect"]:
            matrix.append(
                {
                    "id": repo_id,
                    "repository": repo,
                }
            )

    return matrix


def main() -> None:
    config_path = Path(sys.argv[1] if len(sys.argv) > 1 else "config/repositories.yml")
    data = load_config(config_path)
    matrix = build_matrix(data)
    print(json.dumps(matrix, separators=(",", ":")))


if __name__ == "__main__":
    main()
