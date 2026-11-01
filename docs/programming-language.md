# Programming language selection

## Decision
Python.

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