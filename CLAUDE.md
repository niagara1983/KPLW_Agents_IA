# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KPLW Strategic Innovations Multi-Agent AI System - A professional consulting deliverable production system powered by 4 specialized AI agents (TIMBO, ZAT, MARY, RANA) that collaboratively analyze projects, design solutions, produce deliverables, and validate quality at Big 3 consulting firm standards.

## Key Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the System
```bash
# Interactive mode - user enters project brief
python main.py

# Direct mode - provide brief as argument
python main.py --brief "Your project description here"

# Demo mode - uses built-in example project
python main.py --demo

# From file - load brief from text file
python main.py --file path/to/brief.txt

# Specify custom output directory
python main.py --output custom_output_dir
```

### Development and Testing
```bash
# Run in simulation mode (no API calls)
# Set SIMULATION_MODE=true in .env

# Check if API key is configured correctly
grep ANTHROPIC_API_KEY .env
```

## System Architecture

### Multi-Agent Workflow
The system implements a sequential workflow with feedback loops orchestrated through LangGraph:

1. **TIMBO (Strategic Analyst)** - Receives project brief, applies strategic frameworks (Porter's Value Chain, SWOT, PESTEL, Risk Matrix), produces detailed requirements specification
   - Temperature: 0.3 (rigorous analysis)
   - Outputs: Cahier des charges (requirements specification)

2. **ZAT (Solution Architect)** - Receives TIMBO's requirements, designs 3 solution scenarios with comparison matrix, produces detailed blueprint
   - Temperature: 0.5 (moderate creativity for scenarios)
   - Outputs: Blueprint with multi-scenario analysis

3. **MARY (Deliverable Producer)** - Receives ZAT's blueprint, produces complete professional deliverable in Big 3 consulting format
   - Temperature: 0.4 (balanced production)
   - Outputs: Final deliverable document

4. **RANA (Quality Validator)** - Evaluates MARY's output using 7-dimension rubric, validates (score ≥80) or routes back with corrections
   - Temperature: 0.2 (deterministic evaluation)
   - Outputs: Evaluation report with score and routing decision

### Feedback Loop Logic (agents.py:511-543)
- **Score ≥80**: VALIDE - deliverable approved for client
- **Score 60-79**: Routed back to MARY for minor corrections
- **Score 40-59**: Routed back to ZAT for redesign
- **Score <40**: Routed back to TIMBO for strategic reorientation
- **Max 3 iterations** before human escalation

### State Management (agents.py:43-66)
`ProjectState` TypedDict maintains shared state across all agents:
- Project metadata: brief, ID, language, timestamps
- Agent outputs: timbo_analysis, zat_blueprint, mary_deliverable, rana_evaluation
- Workflow control: rana_score, rana_decision, iteration_count, status
- Audit trail: workflow_log

### Output Parsing (agents.py:556-589)
RANA's output must end with standardized format for automated routing:
```
SCORE:[0-100]
DECISION:[VALIDE|MARY|ZAT|TIMBO]
```

## Configuration System (config.py)

### Model Assignment Strategy
Default: All agents use `claude-sonnet-4-5-20250929`
Recommended for production:
- TIMBO & RANA: `claude-opus-4-5-20251101` (deep reasoning)
- ZAT & MARY: `claude-sonnet-4-5-20250929` (speed + quality)

### Temperature Differentiation
Each agent has calibrated temperature for its role:
- TIMBO: 0.3 (rigorous, low variance)
- ZAT: 0.5 (creative for scenarios)
- MARY: 0.4 (balanced production)
- RANA: 0.2 (deterministic evaluation)

### Workflow Parameters
- `MAX_ITERATIONS=3`: Maximum feedback loop iterations before escalation
- `QUALITY_THRESHOLD=80`: Score required for validation (0-100)
- `MAX_TOKENS=8192`: Token limit per agent call

### Cost Tracking (config.py:69-81)
Per-million-token pricing configured for budget tracking:
- Sonnet: $3/$15 (input/output)
- Opus: $15/$75 (input/output)
- Haiku: $0.80/$4.00 (input/output)

## Agent Prompts System (prompts.py)

Each agent has a detailed system prompt defining:
- Identity and role within KPLW
- Mission and responsibilities
- Analytical frameworks/methodologies to apply
- Output format requirements
- Operational rules and constraints

### Strategic Frameworks Applied by TIMBO
- Porter's Value Chain
- Diagnostic 360 (internal/external)
- Risk Management Matrix
- SWOT, PESTEL, Porter 5 Forces
- Blue Ocean Strategy
- Business Model Canvas
- TAM-SAM-SOM market sizing

### RANA Evaluation Rubric (7 Dimensions)
1. Logical coherence (20%)
2. Data accuracy (20%)
3. Strategic alignment (15%)
4. Completeness (15%)
5. Actionability (10%)
6. Presentation quality (10%)
7. Sophistication (10%)

## File Structure and Outputs

### Output Organization (main.py:42-113)
All outputs saved to `outputs/` directory with project ID prefix:
- `{project_id}_1_TIMBO_analyse.md` - TIMBO's requirements
- `{project_id}_2_ZAT_blueprint.md` - ZAT's solution design
- `{project_id}_3_MARY_livrable.md` - MARY's deliverable
- `{project_id}_4_RANA_evaluation.md` - RANA's quality report
- `{project_id}_RAPPORT_COMPLET.md` - Comprehensive report with all outputs

### Project ID Format
`KPLW-YYYYMMDD-HHMMSS` (e.g., KPLW-20260207-133533)

## Simulation Mode

When `SIMULATION_MODE=true` or Anthropic library unavailable, system runs with mock outputs (agents.py:109-366). Useful for:
- Testing workflow logic without API costs
- Development without API key
- Demonstrations

## Language Support

System automatically adapts to language of input brief (French or English). All agent prompts instruct adaptation to input language.

## Error Handling

### LLM Client (agents.py:72-107)
- Falls back to simulation mode on API errors
- Validates API key format on initialization
- Wraps exceptions with informative error messages

### Workflow Resilience
- Maximum iteration limit prevents infinite loops
- Human escalation when quality threshold not met after MAX_ITERATIONS
- Workflow log tracks all agent transitions for debugging

## Important Implementation Details

### Dependencies
- `anthropic>=0.40.0` - Claude API client (REQUIRED)
- `langgraph>=0.2.0` - Multi-agent orchestration
- `python-dotenv>=1.0.0` - Environment configuration
- `python-docx>=1.1.0` - Professional deliverable generation
- `rich>=13.0.0` - CLI formatting

### RANA Output Parsing (agents.py:556-589)
Critical for workflow routing. System extracts:
1. Score from patterns like "SCORE: 82/100" or "SCORE:82"
2. Decision from keywords: VALIDE, MARY, ZAT, TIMBO
3. Fallback to score-based decision if keywords not found

### Workflow State Transitions
All state changes logged to `workflow_log` with timestamps for auditability and debugging.
