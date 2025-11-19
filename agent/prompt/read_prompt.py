def read_prompt_template(prompt_path: str) -> str:
    with open(prompt_path, 'r', encoding='utf-8') as f:
        template = f.read()
    return template

SYSTEM_PROMPT_TEMPLATE = read_prompt_template("agent/prompt/system_prompt.md")


if __name__ == "__main__":
    print(SYSTEM_PROMPT_TEMPLATE[:100])