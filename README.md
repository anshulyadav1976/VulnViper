# VulnViper: LLM-Powered Security Scanner for Python Code

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)

**VulnViper is an intelligent security auditing tool designed to help developers identify and understand potential vulnerabilities in their Python codebases. Leveraging the power of Large Language Models (LLMs) like OpenAI\'s GPT series and Google\'s Gemini, VulnViper analyzes your code chunk by chunk, providing summaries, identifying potential security issues, and offering recommendations for mitigation.**

It features both a Command-Line Interface (CLI) for quick scans and automation, and a Graphical User Interface (GUI) for a more interactive experience.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
  - [1. Code Discovery & Parsing](#1-code-discovery--parsing)
  - [2. Intelligent Chunking](#2-intelligent-chunking)
  - [3. LLM-Powered Audit](#3-llm-powered-audit)
  - [4. Data Storage & Reporting](#4-data-storage--reporting)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
  - [Command-Line Interface (CLI)](#command-line-interface-cli)
  - [Graphical User Interface (GUI)](#graphical-user-interface-gui)
- [Output](#output)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

## Features

*   **LLM-Powered Analysis:** Utilizes state-of-the-art LLMs (OpenAI GPT, Google Gemini) for deep code understanding and vulnerability detection.
*   **Comprehensive Audits:** Identifies a range of potential security concerns, not just specific CWEs.
*   **Actionable Recommendations:** Provides suggestions for fixing identified issues.
*   **Code Summaries:** Generates summaries of code chunks for better understanding.
*   **Dual Interface:**
    *   **CLI:** For automation, integration into CI/CD pipelines, and terminal power users.
    *   **GUI:** For an easy-to-use, visual way to configure scans and view results.
*   **Flexible Configuration:** Choose your LLM provider and model.
*   **Local Data Storage:** Scan results are stored locally in an SQLite database.
*   **Markdown Reports:** Generates detailed audit reports in Markdown format.
*   **Dynamic Report Naming:** Default report names are generated based on the scanned folder.
*   **Progress Tracking:** Visual progress bar in the GUI and informational messages in the CLI.

## How It Works

VulnViper employs a multi-stage process to analyze your Python code:

### 1. Code Discovery & Parsing

*   **File Discovery:** VulnViper starts by walking through the specified target directory to find all Python files (`.py`).
*   **Abstract Syntax Tree (AST) Parsing:** Each Python file is parsed into an Abstract Syntax Tree. This tree represents the grammatical structure of the code, allowing VulnViper to understand its components like functions, classes, and global statements.

### 2. Intelligent Chunking

*   **Logical Units:** The AST is traversed to identify logical code chunks. These chunks primarily consist of:
    *   Function definitions
    *   Class definitions
    *   Global code blocks (code outside functions or classes)
*   **Contextual Information:** For each chunk, VulnViper extracts metadata such as the file name, chunk name (e.g., function name, class name), type (e.g., `FunctionDef`, `ClassDef`), and start/end line numbers.
*   **Token-Based Sub-Chunking:** Since LLMs have token limits for their input prompts, larger code chunks (like very long functions or entire classes) are further divided into smaller sub-chunks. This is done by carefully splitting the code while trying to maintain logical coherence, ensuring each sub-chunk sent to the LLM is within its processing capacity.

### 3. LLM-Powered Audit

*   **Prompt Engineering:** For each code sub-chunk, a specialized prompt is constructed. This prompt instructs the LLM to act as a security auditor and analyze the provided code for:
    *   A brief **summary** of what the code does.
    *   A list of potential **vulnerabilities** or security concerns.
    *   A list of **recommendations** for mitigating these issues.
    *   Identification of any **dependencies** or modules used (though this is a more basic extraction).
*   **API Interaction:** The code chunk and the engineered prompt are sent to the configured LLM (OpenAI or Gemini) via their respective APIs.
*   **Response Parsing:** The LLM\'s response, which is expected in a JSON format, is then parsed. VulnViper includes logic to handle cases where the LLM might wrap its JSON in markdown code fences and attempts to strip these before parsing. If JSON parsing fails, an error is logged along with the raw LLM output.

### 4. Data Storage & Reporting

*   **Local Database:** All analysis results (summaries, vulnerabilities, recommendations, file info, chunk details) are saved into a local SQLite database (`.vulnviper.sqlite3`) located in the project\'s root directory. The database is cleared at the beginning of each new scan initiated via the CLI or GUI, ensuring reports are specific to the latest scan.
*   **Markdown Report Generation:** Once all chunks have been analyzed, VulnViper compiles the findings from the database into a comprehensive Markdown report. This report details the analysis for each chunk, making it easy to review the identified issues and suggestions. The report name is dynamically generated (e.g., `your_folder_name_vulnviper_audit_report.md`) unless a specific output path is provided by the user.

## Tech Stack

*   **Python:** Core language for the application.
*   **Large Language Models:**
    *   OpenAI API (e.g., GPT-4o-mini, GPT-3.5-turbo)
    *   Google Gemini API
*   **Flet:** For the Graphical User Interface (GUI), enabling a Python-native way to build web, mobile, and desktop apps.
*   **SQLite:** For local storage of scan results.
*   **Pathlib:** For robust and cross-platform path manipulations.
*   **Argparse:** For parsing command-line arguments in the CLI.
*   **Logging:** Standard Python logging module for application events and errors.
*   **JSON:** For data interchange with LLMs.

## Getting Started

### Prerequisites

*   **Python 3.9 or higher:** Download from [python.org](https://www.python.org/downloads/).
*   **PIP:** Python package installer (usually comes with Python).
*   **Git:** For cloning the repository (optional, if you download the source directly).
*   **API Key:** An API key for either OpenAI or Google Gemini, depending on which LLM provider you intend to use.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/VulnViper.git # Replace with actual repo URL
    cd VulnViper
    ```
    Alternatively, download the source code ZIP and extract it.

2.  **Install Dependencies:**
    It\'s highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    ```
    Then, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Before you can start scanning, VulnViper needs to know your API key and preferred LLM provider.

**Using the CLI `init` command (Recommended for first-time setup):**

Run the following command in your terminal from the VulnViper project root:

```bash
python cli.py init
```

This will guide you through:
1.  Entering your API key (for OpenAI or Gemini).
2.  Choosing your LLM provider (`openai` or `gemini`).
3.  Optionally specifying a particular model name for the chosen provider (e.g., `gpt-4o-mini`, `gemini-1.5-flash-latest`). If you skip this, a default model will be used.

This information will be saved to a `.vulnviper_config` file in the project directory.

**Using the GUI:**

1.  Run the GUI: `python run_gui.py`
2.  The GUI will open, presenting fields for "API Key", "LLM Provider", and "LLM Model".
3.  Enter your details.
4.  Click "Save Configuration". This will create or update the `.vulnviper_config` file.

**Environment Variables (Alternative):**

You can also configure VulnViper using environment variables. These will override settings in the config file if both are present:
*   `VULNVIPER_API_KEY`: Your API key.
*   `VULNVIPER_LLM_PROVIDER`: `openai` or `gemini`.
*   `VULNVIPER_LLM_MODEL`: (Optional) The specific model name.

## Usage

### Command-Line Interface (CLI)

The CLI is a powerful way to run scans, especially for automation.

**Basic Scan:**

To scan the current directory and save the report to a dynamically named file (e.g., `current_folder_vulnviper_audit_report.md`):

```bash
python cli.py scan
```

**Scan a Specific Directory:**

```bash
python cli.py scan --dir /path/to/your/python_project
```
or for a relative path:
```bash
python cli.py scan --dir subfolder/my_project
```

**Specify Output Report File:**

```bash
python cli.py scan --dir /path/to/your/project --out /path/to/custom_report_name.md
```

**Help:**

To see all available CLI options:

```bash
python cli.py --help
python cli.py scan --help
```

### Graphical User Interface (GUI)

The GUI provides a user-friendly way to configure and run scans.

1.  **Run the GUI:**
    Navigate to the VulnViper project directory in your terminal and run:
    ```bash
    python run_gui.py
    ```

2.  **Configure LLM Settings:**
    *   If you haven\'t already, enter your API Key, select the LLM Provider, and optionally specify an LLM Model.
    *   Click "Save Configuration".

3.  **Select Target Directory:**
    *   Click the "folder_open" icon next to the "Target Directory" field.
    *   Browse and select the Python project directory you want to scan.

4.  **Output Report File:**
    *   The "Output Report File" field will automatically update to a name like `your_selected_folder_name_vulnviper_audit_report.md`.
    *   You can manually change this if you prefer a different name or location.

5.  **Start Scan:**
    *   Click the "Start Scan" button.
    *   Scan progress and any messages will appear in the "Scan Output" text area.
    *   A progress bar will indicate scan activity.

6.  **View Report:**
    *   Once the scan is complete, a success message will indicate where the Markdown report has been saved. You can then open and view this file.

## Output

VulnViper produces two main outputs:

1.  **SQLite Database (`.vulnviper.sqlite3`):**
    *   Located in the root of the VulnViper project directory.
    *   Stores all detailed analysis results from the scan.
    *   This database is cleared at the start of each new scan.

2.  **Markdown Report (`*_vulnviper_audit_report.md`):**
    *   A human-readable report detailing the findings for each code chunk.
    *   Includes file and chunk information, summaries, identified vulnerabilities, and recommendations.
    *   By default, saved in the current working directory (for CLI) or the project root (often for GUI context, though the path is relative to where `run_gui.py` is executed or where the CLI command is run from if no `--out` is used). The exact default save location depends on how the application is run and if an output path is specified.

## Contributing

Contributions are welcome and greatly appreciated! Whether it\'s reporting a bug, suggesting an enhancement, or submitting a pull request, your help makes VulnViper better.

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) guide (to be created) for details on our code of conduct and the process for submitting pull requests.

**Possible areas for contribution:**

*   Improving LLM prompts for more accurate or detailed analysis.
*   Adding support for more LLM providers or models.
*   Enhancing the GUI with more features (e.g., report viewing within the app).
*   Improving error handling and resilience.
*   Adding more sophisticated code parsing or chunking logic.
*   Developing new reporting formats (e.g., HTML, JSON).
*   Writing unit and integration tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file (to be created) for details.

## Disclaimer

VulnViper is a tool to aid in security auditing and is not a replacement for manual code review by security experts. The vulnerabilities and recommendations it provides are based on the capabilities of the configured Large Language Model and may not be exhaustive or perfectly accurate. Always critically evaluate the output and use it as one part of a comprehensive security strategy. The developers of VulnViper are not responsible for any security incidents or damages arising from the use or misuse of this tool.

