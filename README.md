# AI Execution Engine

LLM proposes. System disposes.

This runtime is used by higher-level agent systems such as:
https://github.com/Slyog/lightwell-runtime-agent

---

## Overview

AI Execution Engine runs AI-generated Python code in an isolated Docker runtime and determines correctness through actual execution.

Each attempt is executed, observed, and recorded as a trace.
Exit code, stdout, stderr, timeout state, and status define whether an attempt succeeded.

---

## What This Is

* Controlled runtime for AI-generated Python code
* Docker-based isolation
* Deterministic execution results
* Self-repair loop using real runtime feedback
* Persisted sessions, runs, and traces

---

## What This Is Not

* A chatbot
* A code-generation demo
* LLM-only verification

---

## Architecture

The model proposes code. The system determines truth through execution.

```txt
Client → /agent-runs → AgentLayer → RunManager → DockerRunner → TraceManager
```

- AgentLayer generates candidate Python code
- RunManager orchestrates execution attempts
- DockerRunner executes code in an isolated container
- TraceManager records every attempt and result

---

## Example API Call

```bash
curl -X POST http://localhost:8000/agent-runs \
  -H "Content-Type: application/json" \
  -d '{"objective":"Write Python code that prints hello from runtime","max_attempts":3}'
```

---

## Example Response

```json
{
  "status": "completed",
  "attempts": 1,
  "final_stdout": "hello from runtime\n",
  "trace_ids": ["816ba0ca-7a32-4ebc-bcad-204237a5ebcb"]
}
```

---

## Example Run (Real Execution)

A real execution result recorded by the engine:

```json
{
  "objective": "Write Python code that prints hello from runtime",
  "generated_code": "print(\"hello from runtime\")",
  "exit_code": 0,
  "stdout": "hello from runtime",
  "status": "completed",
  "trace_id": "816ba0ca-7a32-4ebc-bcad-204237a5ebcb"
}
```

The trace shows that correctness is determined by actual execution (exit code and stdout), not by model output alone.

---

## Design Principles

This system exists because LLM output is unreliable until it has been executed.

* Execution result is the source of truth
* Status is never decided by the model
* Failed runs are repaired from observed runtime output
* Retries are explicit and traceable
* Session state is deterministic and file-backed

---

## System Composition

This repository provides the runtime layer of a larger system.

- **AI Execution Engine** → runtime + truth layer
- **Lightwell Runtime Agent** → interface + observation layer

The separation is intentional:
execution is isolated from interaction and agent behavior.

---

## Running Locally

```bash
pip install -r requirements.txt
cp .env.example .env
```

Set in `.env`:

```txt
OPENAI_API_KEY=your_key
SESSION_DATA_DIR=./data/sessions
```

Start the engine:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
