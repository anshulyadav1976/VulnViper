import argparse
import os
from pathlib import Path

from config import save_config, load_config
from scanner.file_walker import get_target_files
from scanner.ast_parser import parse_file_to_chunks
from scanner.chunker import chunk_by_token_limit
from llm.clients import audit_chunk_with_llm
from storage.db import init_db, save_analysis
from reporter.markdown_writer import write_markdown_report
from storage.models import ChunkAnalysis
from utils.logging import log

DEFAULT_REPORT_PATH = Path.cwd() / "vulnviper_audit_report.md"


def init_command():
    api_key = input("🔑 Enter your API key (OpenAI or Gemini): ").strip()
    
    llm_provider = ""
    while llm_provider not in ["openai", "gemini"]:
        llm_provider = input("🤖 Choose your LLM provider (openai/gemini): ").strip().lower()
        if llm_provider not in ["openai", "gemini"]:
            print("⚠️ Invalid provider. Please choose 'openai' or 'gemini'.")

    llm_model = input(f"⚙️ Enter model name for {llm_provider} (e.g., gpt-4o-mini, gemini-1.5-flash-latest) [optional, press Enter for default]: ").strip()
    if not llm_model:
        llm_model = None

    save_config(api_key, llm_provider, llm_model)


def scan_command(base_dir: str, out_path: str):
    try:
        config = load_config()
    except RuntimeError as e:
        print(f"❌ Configuration error: {e}")
        return

    api_key = config["api_key"]
    llm_provider = config["llm_provider"]
    llm_model = config.get("llm_model")

    init_db()
    base_path = Path(base_dir).resolve()
    files = get_target_files(base_path)

    if not files:
        print("😴 No Python files found to scan.")
        return

    print(f"🐍 VulnViper scanning {len(files)} file(s) using {llm_provider}{(', model: ' + llm_model) if llm_model else ''}...")

    all_results_for_report = []

    for file_path in files:
        log(f"Parsing {file_path}")
        try:
            parsed_chunks = parse_file_to_chunks(file_path)
        except Exception as e:
            log(f"⚠️ Failed to parse {file_path}: {e}")
            continue

        for p_chunk in parsed_chunks:
            sub_code_chunks = chunk_by_token_limit(p_chunk['code'], chunk_token_limit=3000)
            
            for i, sub_code in enumerate(sub_code_chunks):
                log(f"🤖 Auditing chunk {p_chunk['name']} (part {i+1}/{len(sub_code_chunks)}) from {file_path.name}")
                
                analysis_result = audit_chunk_with_llm(
                    code_chunk=sub_code, 
                    api_key=api_key, 
                    provider=llm_provider, 
                    model=llm_model
                )

                if "error" in analysis_result:
                    log(f"⚠️ LLM Error for chunk {p_chunk['name']}: {analysis_result['error']}")
                    summary = f"Error during analysis: {analysis_result['error']}"
                    vulnerabilities = [f"LLM Error: {analysis_result.get('raw_output', '')}"]
                    dependencies = []
                else:
                    summary = analysis_result.get('summary', 'No summary provided.')
                    vulnerabilities = analysis_result.get('vulnerabilities', [])
                    if isinstance(vulnerabilities, str): vulnerabilities = [vulnerabilities]
                    dependencies = analysis_result.get('dependencies', [])
                    if isinstance(dependencies, str): dependencies = [dependencies]

                chunk_analysis_obj = ChunkAnalysis(
                    file=str(file_path.relative_to(base_path) if file_path.is_absolute() and base_path in file_path.parents else file_path.name),
                    function_name=p_chunk['name'],
                    chunk_type=p_chunk['type'],
                    start_line=p_chunk['start_line'],
                    end_line=p_chunk['end_line'],
                    summary=summary,
                    vulnerabilities=vulnerabilities,
                    dependencies=dependencies,
                    parent_module=p_chunk.get('parent_module', '')
                )
                save_analysis(chunk_analysis_obj)
                all_results_for_report.append(chunk_analysis_obj.to_dict())

    if not all_results_for_report:
        print("🤷 No results to generate a report.")
    else:
        write_markdown_report(all_results_for_report, out_path)
        print(f"\n✅ Audit complete. Report saved to: {out_path}")
    
    db_name = ".vulnviper.sqlite3"
    print(f"📦 All results stored in: {Path.home() / db_name}")


def main():
    parser = argparse.ArgumentParser(prog="vulnviper", description="VulnViper: LLM-powered security scanner for Python code.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize VulnViper: set API key and LLM preferences.")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a directory for Python code vulnerabilities with VulnViper.")
    scan_parser.add_argument("--dir", type=str, default=".", help="Directory to scan (default: current directory).")
    scan_parser.add_argument("--out", type=str, default=str(DEFAULT_REPORT_PATH), help=f"Output Markdown report path (default: {DEFAULT_REPORT_PATH.name}).")

    args = parser.parse_args()

    if args.command == "init":
        init_command()
    elif args.command == "scan":
        scan_command(args.dir, args.out)


if __name__ == "__main__":
    main()
