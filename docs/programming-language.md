# Programming language selection

## Decision
**Python.**

Three project-specific reasons support this decision:
1. **Existing GBGB scraper**: The data extraction pipeline is already implemented in Python. Keeping the same language avoids rewriting working components or introducing unnecessary communication between different language runtimes.
2. **Professional experience**: During my Software Engineering Internship at **Constella Intelligence**, I used Python for backend development in an identity-protection platform. Its work involved processing and ingesting information originating from data breaches, including exposed credentials and personal-data attributes, to support customer notifications identifying which specific fields had been compromised. This gave me practical experience with backend data-processing workflows closely related to HoundIQ's ingestion requirements.
3. **Core analytical workload**: HoundIQ needs to process historical race records, compare greyhounds across different tracks, distances, classes and traps, and evaluate statistical consistency. Python provides an established ecosystem for this type of work through libraries such as pandas, NumPy and SciPy.

## Candidates considered
| Language | Why it was considered | Why it was not selected |
|---|---|---|
| **Python** | Existing scraper, my previous professional experience and mature data-analysis ecosystem. | **Selected.** |
| TypeScript | Strong backend and API ecosystem, excellent for web applications and LLM orchestration. | Would require maintaining a separate Python component or rewriting the existing scraper. Its data-analysis ecosystem is less suitable for HoundIQ's central workload. |
| Go | Efficient backend services, concurrency and straightforward deployment. | No demonstrated performance or concurrency requirement justifies sacrificing direct scraper reuse and Python's analytical ecosystem. |

TypeScript is a particularly credible alternative. In fact, developer discussions frequently distinguish between API-oriented AI applications, where TypeScript is a strong choice, and data-intensive AI applications, where Python offers a more established ecosystem.

## Community evidence
- The [2026 Stack Overflow Developer Survey](https://survey.stackoverflow.co/2026/technology/data/languages/) reports that 58.0% of respondents had done extensive development work with Python over the previous year, compared with 43.8% for TypeScript (14,099 respondents).
- In this [Python vs TypeScript discussion on r/AI_Agents](https://www.reddit.com/r/AI_Agents/comments/1udbkke/python_vs_typescript/), developers discuss the same trade-off relevant to HoundIQ: Python for data processing and ML-oriented workloads, TypeScript for web products and API-driven orchestration. This project is not going to be a web product.
- This [Stack Overflow discussion comparing JavaScript data-processing libraries with pandas](https://stackoverflow.com/questions/30610675/python-pandas-equivalent-in-javascript) illustrates that alternatives such as Danfo.js and Data-Forge exist, but also highlights the additional ecosystem choices involved when moving away from Python's established data tools.

LLM integration and MCP are not decisive differentiators: [OpenRouter provides SDKs for Python, TypeScript and Go](https://openrouter.ai/developers), while [MCP has official SDKs for multiple languages](https://github.com/modelcontextprotocol).

## Trade-offs
No project-specific disadvantage has been identified that outweighs Python's advantages for the current MVP.

# Python version management

## Decision
Use **pyenv** to manage Python installations and project-specific versions.

The project will use **CPython 3.15.2**, with Python 3.15 as its supported minor version. The exact interpreter version will be stored in a `.python-version` file at the repository root.

Python 3.15.2 is the latest stable patch release at the time of this decision. The main analytical libraries considered for HoundIQ, including NumPy, pandas, SciPy and scikit-learn, already support Python 3.15.

## Alternatives considered
| Tool | Advantages | Trade-offs |
|---|---|---|
| **pyenv** | Dedicated Python version manager, project-level `.python-version`, **works on Linux and WSL.** | Builds most Python versions from source, requiring system build dependencies. Does not support native Windows. |
| uv | Installs managed Python builds, supports `.python-version` and works on Linux and Windows. | Also provides dependency and project management, potentially overlapping with the decision in Issue #8. Uses prebuilt distributions maintained by Astral rather than building CPython from source. |
| mise | Manages Python and multiple other development runtimes; supports project-specific versions and Linux/Windows. | Broader than HoundIQ currently needs and introduces another configuration mechanism. |

## Rationale
pyenv is the most appropriate option because HoundIQ currently needs to manage one runtime: Python. Its `.python-version` file provides a simple, repository-level declaration that is automatically recognised when entering the project directory.

Development will use Linux environments, including WSL on Windows. pyenv supports this setup directly, its Windows limitation is not a blocker because the project will run using the Linux interpreter rather than a native Windows installation (who codes on Windows in 2026?).

The main trade-off is that pyenv builds CPython from source and therefore requires build dependencies to be installed once on each Linux environment. This is acceptable for the current project and avoids introducing a broader tool solely to manage one language.

Keeping Python version management separate from dependency management also leaves the decision in Issue #8 independent.

## Version policy
- **Supported version line:** CPython 3.15.x.
- **Current project pin:** CPython 3.15.2.
- **Version declaration:** `.python-version`, containing `3.15.2`.
- **Upgrades:** Install the new patch version, update the project pin and verify the application before accepting the change. Minor-version upgrades require checking dependency compatibility first.

When `pyproject.toml` is established, its `requires-python` metadata should declare `>=3.15,<3.16`, while `.python-version` continues to pin the exact development interpreter.

# Dependency Management

## Decision
Use **uv** to manage HoundIQ's dependencies and project environment.

## Alternatives considered
| Approach | Advantages | Trade-offs |
|---|---|---|
| pip + `venv` | Native Python tooling, no additional manager. | Requires more manual coordination to declare, lock, separate and synchronize dependencies. |
| pip-tools | Compiles pinned dependency files and synchronizes environments using `pip-compile` and `pip-sync`. | Requires separate input and generated files, with additional commands and environment management. |
| Poetry | Mature dependency manager with lockfiles, dependency groups and environment isolation. | Introduces its own project and environment management workflow. |
| **uv** | Centralizes dependency declaration, resolution, locking, installation and virtual environment management. | Introduces a dedicated tool and its own native lockfile format. |

## Rationale
uv offers the most straightforward workflow for this project. It uses `pyproject.toml` for dependency declarations and `uv.lock` for exact resolved versions, including transitive dependencies.

Its lockfile supports universal resolution across platforms, which is useful when reproducing the environment beyond the current WSL setup. It also creates and synchronizes the project's `.venv` automatically.

Importantly, uv recognises the Python interpreter selected by the existing `.python-version` file, including installations managed by pyenv. To preserve the responsibility established in Issue #7, automatic Python downloads will be disabled.

## Dependency conventions
- **Runtime dependencies:** Declared in `[project].dependencies`.
- **Development and testing dependencies:** Declared in a single `dev` dependency group. Separate testing groups are unnecessary for the current solo-developed MVP.
- **Version control:** `pyproject.toml` and `uv.lock` are committed. `.venv` remains local and must not be committed.
- **Reproducibility:** Use `uv sync --locked` to install the committed dependency resolution without silently modifying the lockfile.
- **Updates:** Dependency upgrades must be deliberate and followed by the relevant tests.

The `pylock.toml` standard (PEP 751) is also supported as an export format, providing an alternative to uv's native lockfile if interoperability becomes necessary.