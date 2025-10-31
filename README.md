# gsp_calculator_svc

## Overview

gsp_calculator_svc is a high-precision calculator service implemented as a Streamlit application. The project follows the Thesen AI mandated technology stack and conventions: Python for implementation, Streamlit for UI, Python's decimal module for precision arithmetic, and Poetry for dependency and build management. This README serves as the project plan and documentation for the calculator-web subsystem.

## Technology Stack

- Language: Python (3.11+ recommended)
- UI Framework: Streamlit
- Precision arithmetic: Python builtin decimal module
- Build and dependency management: Poetry
- Configuration: .env with a Config class in src/gsp_calculator/config.py
- Deployment: Docker (managed by Thesen AI automation)

Legacy technologies that are not used in this project and intentionally removed from documentation:
- React
- TypeScript / JavaScript
- Tailwind CSS
- decimal.js
- npm / yarn
- Vite

## Project Structure (documentation-targeted)

The repository is organized to reflect a Python/Streamlit application. Example structure:

- app.py (Streamlit application entrypoint)
- src/gsp_calculator/
  - __init__.py
  - config.py (Config class reading .env)
  - calculator_engine.py (core arithmetic functions using decimal)
  - ui.py (Streamlit UI components, if separated)
- tests/
  - test_readme_stack.py (example validation test)
- .env (development configuration; not committed)

Note: This README describes the intended module/file paths for clarity. Actual implementation files should follow this structure.

## Feature Overview (Streamlit-focused)

- High-precision basic arithmetic using Python's decimal module (add, subtract, multiply, divide)
- Minimal, responsive UI implemented with Streamlit components
- Calculation history using Streamlit session_state for persistence within a user session
- Keyboard input guidance: Streamlit widgets and session_state can approximate keyboard-driven workflows; exact keybindings depend on Streamlit capabilities and future implementation details

## Setup and Run Instructions

Prerequisites:
- Python 3.11+ installed
- Poetry installed

Install dependencies:

- poetry install

Environment variables and configuration:

- Create a .env file in the project root as needed
- Implement a Config class in src/gsp_calculator/config.py to centralize configuration reading (use python-dotenv or similar if required)

Run the app locally:

- poetry run streamlit run app.py

## Module and File Reference Mapping

Replace legacy TypeScript/React file references with Python module paths. Example mappings:

- src/utils/calculatorEngine.ts -> src/gsp_calculator/calculator_engine.py
- Any .tsx/.tsx/.ts component references -> corresponding .py modules in src/gsp_calculator/
- Tailwind class references -> Streamlit native layout and styling descriptions
- npm/yarn/Vite dev/build instructions -> Poetry commands (poetry install, poetry run <cmd>) and Streamlit run

Make sure in-code and documentation examples reference .py paths, not .ts or .tsx files.

## Acceptance Criteria (Documentation)

This README meets the action item acceptance criteria when:

- The core technology stack is clearly Python + Streamlit
- All references to React, TypeScript/JavaScript, Tailwind CSS, decimal.js, npm, yarn, and Vite are removed or replaced
- Poetry is identified as the build and dependency tool
- Module structure and file paths reflect Python conventions (e.g., calculator_engine.py)
- Document aligns with Thesen AI constraints and Streamlit capabilities

## Consistency Checklist

Before finalizing documentation, ensure:

- No occurrences of: React, TypeScript, Tailwind, decimal.js, npm, yarn, Vite
- All example file paths use .py and Python package structures
- Build and run instructions use Poetry and Streamlit commands
- Feature descriptions are framed in Streamlit terminology, not React component language

## Testing / Verification (documentation-only)

A simple README validation test can be added to ensure documentation correctness. Example checks:

- README contains: "Streamlit", "Python", "Poetry", "decimal"
- README does not contain: "React", "TypeScript", "Tailwind", "decimal.js", "npm", "yarn", "Vite"
- File path examples include "calculator_engine.py" and do not include ".ts" or ".tsx"

Example (conceptual) test file path: tests/test_readme_stack.py

## Notes and Constraints

- This action item is documentation-only. No functional code changes or infrastructure changes are performed here.
- Follow Thesen AI guidance for configuration management (central Config class reading .env) when implementing actual code later.

## Contact / Next Steps

- Implement the Streamlit UI and Python modules following the documented structure in future action items.
- Add README validation unit tests or CI checks if desired.
