import argparse
import os
import zipfile
from typing import List, Optional, Tuple
from FastWrite import file_processor, doc_generator, data_flow, bleu, rouge
from FastWrite.print import readmegen, remove_think_tags

def summarize(text: str, llm_name: str, is_project: bool = False) -> str:
    """
    Generate a 1-paragraph summary for the given text using the selected LLM.
    """
    if is_project:
        summary_prompt = (
            "Given the following documentation for each file in a Python project, "
            "write a single concise paragraph summarizing what the entire project does, "
            "its main purpose, and its key features. Do not include code snippets. "
            "Documentation:\n\n"
            + text
        )
    else:
        summary_prompt = (
            "Summarize the following documentation in a single concise paragraph. "
            "Describe the main purpose and key features. Do not include code snippets.\n\n"
            f"{text}"
        )

    if llm_name == "GROQ":
        return doc_generator.generate_documentation_groq("", summary_prompt)
    elif llm_name == "GEMINI":
        return doc_generator.generate_documentation_gemini("", summary_prompt)
    elif llm_name == "OPENAI":
        return doc_generator.generate_documentation_openai("", summary_prompt)
    elif llm_name == "OPENROUTER":
        return doc_generator.generate_documentation_openrouter("", summary_prompt)
    elif llm_name == "OLLAMA":
        return doc_generator.generate_documentation_ollama("", summary_prompt)
    else:
        return "Summary could not be generated."

def generate_doc(code: str, prompt: str, args: argparse.Namespace) -> Tuple[str, str]:
    if args.GROQ:
        return doc_generator.generate_documentation_groq(code, prompt, model=args.model or "moonshotai/kimi-k2-instruct-0905"), "GROQ"
    elif args.GEMINI:
        return doc_generator.generate_documentation_gemini(code, prompt, model=args.model or "gemini-3-flash-preview"), "GEMINI"
    elif args.OPENAI:
        return doc_generator.generate_documentation_openai(code, prompt, model=args.model or "gpt-5-mini-2025-08-07"), "OPENAI"
    elif args.OPENROUTER:
        return doc_generator.generate_documentation_openrouter(code, prompt, model=args.model or "xiaomi/mimo-v2-flash:free"), "OPENROUTER"
    elif args.OLLAMA:
        return doc_generator.generate_documentation_ollama(code, prompt, model=args.model or "ollama-llama-70b"), "OLLAMA"
    else:
        return "No LLM selected.", "UNKNOWN"

def main():
    parser = argparse.ArgumentParser(description="Generate documentation for a Python file using FastWrite.")
    parser.add_argument("filename", nargs="?", default=None, help="Python source file or directory to document. If omitted, all files in the current directory will be documented.")

    # LLM selection arguments
    parser.add_argument("--GROQ", action="store_true", help="Use GROQ for generating documentation.")
    parser.add_argument("--GEMINI", action="store_true", help="Use Gemini for generating documentation.")
    parser.add_argument("--OPENAI", action="store_true", help="Use OpenAI for generating documentation.")
    parser.add_argument("--OPENROUTER", action="store_true", help="Use OpenRouter for generating documentation.")
    parser.add_argument("--OLLAMA", action="store_true", help="Use Ollama for generating documentation.")
    parser.add_argument("--model", type=str, default=None, help="Optional model name to override default.")

    # Documentation style arguments
    parser.add_argument("--Simplify", action="store_true", help="Generate simplified documentation for broader understanding for less technical users.")
    parser.add_argument("--Formal", action="store_true", help="Generate formal and concise documentation only considering important points.")
    parser.add_argument("--Research", action="store_true", help="Generate extreme detailed documentation with both Novice Friendly and Technical levels.")
    parser.add_argument("--Custom-Prompt", type=str, default=None, help="Custom user-defined prompt (must be enclosed in quotes).")

    # Extra features
    parser.add_argument("--graph", action="store_true", help="Generate a Graphviz data flow diagram.")
    parser.add_argument("--reference", type=str, default=None, help="Reference documentation file to evaluate generated doc against.")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save individual file documentations.")
    parser.add_argument("--template", type=str, default=None, help="Path to a markdown template file for documentation.")

    args = parser.parse_args()

    selected_llms = [args.GROQ, args.GEMINI, args.OPENAI, args.OPENROUTER, args.OLLAMA]
    if sum(selected_llms) != 1:
        print("Error: Please specify exactly one LLM using --GROQ, --GEMINI, --OPENAI, --OPENROUTER, or --OLLAMA.")
        return

    # Compose the prompt
    prompt = "Generate high-quality, developer-friendly documentation for the following Python code Ensure you include Detailed function-level and file-level documentation and a high level slightly less technical documentation at the start to make it friendly. Do not print full code snippets of existing code, just explain them:"
    if args.Simplify:
        prompt += " Simplify the documentation to make it easy for everyone to understand, even if it means sacrificing some detail."
    elif args.Formal:
        prompt += " Make the documentation extremely formal and to the point. Ensure that it is concise and only includes the most important points. Avoid unnecessary details or explanations."
    elif args.Research:
        prompt += """ Create an extremely detailed documentation, with both a Novice Friendly explanation and a Technical Explanation. Go in depth into every aspect of the code including but not limited to:
        - Abstract: Brief summary of the entire project
        - Introduction: Overview of the problem and solution
        - Methodology: Approach and methods used"""
    if args.Custom_Prompt:
        prompt = args.Custom_Prompt

    # Determine which file(s) to process
    target = args.filename or os.getcwd()
    
    # Read template if provided
    template_content = None
    if args.template:
        if os.path.exists(args.template):
            template_content = file_processor.read_file(args.template)
        else:
            print(f"Warning: Template '{args.template}' not found. Using default style.")

    def apply_template(content: str, filename: str) -> str:
        if template_content:
            return template_content.replace("{{content}}", content).replace("{{filename}}", filename)
        return content

    def evaluate(candidate: str, reference_path: Optional[str]) -> None:
        if reference_path and os.path.exists(reference_path):
            reference_content = file_processor.read_file(reference_path)
            bleu_score = bleu.calculate_bleu(candidate, reference_content)
            rouge_scores = rouge.calculate_rouge(candidate, reference_content)
            
            print(f"\nEvaluation Results vs {reference_path}:")
            print(f"- BLEU Score: {bleu_score:.4f}")
            r1 = rouge_scores.get('rouge-1', {}).get('f', 0)
            r2 = rouge_scores.get('rouge-2', {}).get('f', 0)
            rl = rouge_scores.get('rouge-l', {}).get('f', 0)
            print(f"- ROUGE-1 F-Score: {r1:.4f}")
            print(f"- ROUGE-2 F-Score: {r2:.4f}")
            print(f"- ROUGE-L F-Score: {rl:.4f}")

    if os.path.isfile(target):
        code_content = file_processor.read_file(target)
        # Generate documentation
        documentation, llm_used = generate_doc(code_content, prompt, args)
        documentation = remove_think_tags(documentation)
        documentation = apply_template(documentation, os.path.basename(target))
        
        # Save documentation
        output_file = "README.md"
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            output_file = os.path.join(args.output_dir, os.path.basename(target).replace(".py", ".md"))
            
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Documentation for {os.path.basename(target)} (generated by FastWrite using {llm_used})\n\n")
            f.write(documentation)
        print(f"Documentation has been written to {output_file}")
        evaluate(documentation, args.reference)
        
    elif os.path.isdir(target):
        files = file_processor.list_code_files(target)
        all_docs = []
        table_of_contents = "# Project Documentation Index\n\n"
        
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
        
        llm_used = "UNKNOWN" # To be set in loop
        for f in files:
            file_path = os.path.join(target, f)
            print(f"Processing {f}...")
            single_code = file_processor.read_file(file_path)
            doc, llm_used = generate_doc(single_code, prompt, args)
            doc = remove_think_tags(doc)
            doc = apply_template(doc, f)
            
            if args.output_dir:
                rel_doc_path = f.replace(".py", ".md")
                doc_file_path = os.path.join(args.output_dir, rel_doc_path)
                os.makedirs(os.path.dirname(doc_file_path), exist_ok=True)
                with open(doc_file_path, "w", encoding="utf-8") as i_file:
                    i_file.write(f"# Documentation for {f}\n\n{doc}")
                table_of_contents += f"- [{f}]({rel_doc_path})\n"
                all_docs.append(doc) # Keep for summary
            else:
                all_docs.append(f"## File: {f}\n\n" + doc)
        
        combined_doc = "\n\n".join(all_docs)
        if args.output_dir:
            summary_path = os.path.join(args.output_dir, "SUMMARY.md")
            with open(summary_path, "w", encoding="utf-8") as s_file:
                s_file.write(table_of_contents)
            
            project_summary = summarize(combined_doc if combined_doc else "Multiple files processed.", llm_used, is_project=True)
            result_doc = f"# Project Documentation (generated by FastWrite using {llm_used})\n\n## Overview\n{project_summary}\n\n{table_of_contents}"
            with open(os.path.join(args.output_dir, "README.md"), "w", encoding="utf-8") as r_file:
                r_file.write(result_doc)
            print(f"Project documentation generated in {args.output_dir}")
            evaluate(project_summary, args.reference)
        else:
            project_summary = summarize(combined_doc, llm_used, is_project=True)
            result_doc = f"# Project Documentation (generated by FastWrite using {llm_used})\n\n## Overview\n{project_summary}\n\n{combined_doc}"
            with open("README.md", "w", encoding="utf-8") as r_file:
                r_file.write(result_doc)
            print("Combined documentation written to README.md")
            evaluate(project_summary, args.reference)

    # Optional: Generate Data Flow Graph
    # (Note: For directories, we might want a combined graph or skip for now)
    if args.graph and os.path.isfile(target):
        code_content = file_processor.read_file(target)
        graph_code = data_flow.generate_data_flow(code_content)
        with open("data_flow.dot", "w", encoding="utf-8") as dot_file:
            dot_file.write(graph_code)
        print("Data flow diagram generated as data_flow.dot")

if __name__ == "__main__":
    main()
