import argparse
import os
from FastWrite import file_processor, doc_generator

def main():
    parser = argparse.ArgumentParser(description="Generate documentation for a Python file using FastWrite.")
    parser.add_argument("filename", help="Python source file to document.")

    # LLM selection arguments
    parser.add_argument("--GROQ", action="store_true", help="Use GROQ for generating documentation.")
    parser.add_argument("--GEMINI", action="store_true", help="Use Gemini for generating documentation.")
    parser.add_argument("--OPENAI", action="store_true", help="Use OpenAI for generating documentation.")
    parser.add_argument("--model", type=str, default=None, help="Optional model name to override default.")

    args = parser.parse_args()

    if not os.path.isfile(args.filename):
        print(f"Error: File '{args.filename}' does not exist.")
        return

    selected_llms = [args.GROQ, args.GEMINI, args.OPENAI]
    if sum(selected_llms) != 1:
        print("Error: Please specify exactly one LLM using --GROQ, --GEMINI, or --OPENAI.")
        return

    with open(args.filename, 'r') as f:
        code = f.read()

    prompt = "Generate high-quality, developer-friendly documentation for the following Python code:"

    if args.GROQ:
        documentation = doc_generator.generate_documentation_groq(code, prompt, model=args.model or "deepseek-r1-distill-llama-70b")
        llm_used = "GROQ"
    elif args.GEMINI:
        documentation = doc_generator.generate_documentation_gemini(code, prompt, model=args.model or "models/gemini-pro")
        llm_used = "GEMINI"
    elif args.OPENAI:
        documentation = doc_generator.generate_documentation_openai(code, prompt, model=args.model or "gpt-3.5-turbo")
        llm_used = "OPENAI"

    with open("README.md", "w") as readme_file:
        readme_file.write(f"# Documentation generated by FastWrite using {llm_used}\n\n")
        readme_file.write(documentation)

    print("Documentation has been written to README.md")

if __name__ == "__main__":
    main()
