# Data Insight Studio

An independent clean-room implementation of an AI-assisted desktop data analysis workflow. It accepts CSV/XLSX files, turns natural-language questions into pandas analysis code when an LLM is configured, executes approved local analysis code, and displays tabular results and charts.

> Inspired by the general idea of AI-assisted data analysis. This repository is independently implemented and is not a copy of the source project.

## Features
- CSV and Excel ingestion
- Multiple datasets in one session
- Natural-language analysis with optional Groq/OpenAI backends
- Deterministic fallback analytics when no API key is configured
- Generated pandas code preview
- Matplotlib chart output
- Basic code validation before local execution

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Optional environment variables:
- `GROQ_API_KEY`
- `OPENAI_API_KEY`

## Example questions
- What is the average sales by region?
- Show the top 10 products by revenue.
- How strongly are price and quantity correlated?
- Count rows by category.

## Important security note
The application executes generated Python locally. The validator is intentionally conservative but is **not a security sandbox**. Only use trusted LLM output and trusted datasets.

## Suggested GitHub topics
`python` `tkinter` `pandas` `data-analysis` `llm` `groq` `openai` `matplotlib`

## Preview

![UI preview](assets/preview.png)


## Portfolio note
This is an independent reimplementation created for learning and portfolio practice. The implementation and project structure were written independently rather than copied from another repository.
