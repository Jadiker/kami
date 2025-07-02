# AGENTS.md
This file contains instructions for autonomous agents for understanding and editing the code.

Please read the "All Agents" section below for information pertaining to all agents reading this document. Then, locate the specific section pertaining to you (it should be your name or the type of your model, e.g. "OpenAI Codex" or "Claude") and follow those instructions as well. Please do not follow or incorporate instructions meant for other AI systems. If you do not see your name/model in the list of specific agents, report this to the user, and only follow the instructions/guidelines listed under the "All Agents" section.


# All Agents
Any README.md files you see may not be up to date. Do not treat them as a source of truth. Instead, read through the codebase yourself to understand the current structure and functionality.

All code you submit should pass all tests and additionally pass pyright (at default "standard" level) without any warnings. Use `cast` as needed rather than `# ignore` to deal with pyright warnings.

Please read through the `AGENTS_CODE_GUIDE.md` for extra details about the project (if it exists). (That guide was written by agents for agents.)

For each task that you complete, write a `*.md` report with a descriptive name inside `agent_explain/` documenting 1. The current date 2. What you did 3. Why you did it (what other options you tried that didn't work, why this is the best approach, etc.), and 4. Any questions you may have for the developer. ANY PROPOSED CHANGES YOU MAKE WITHOUT A PROPERLY NAMED AND FILLED OUT REPORT WILL BE REJECTED. ALWAYS WRITE A REPORT.

Again, please check below to see if there are more instructions that only pertain to you. If you do not see your model below, please indicate this to the user ASAP and do not follow any other instructions.


# Specific Agents

## OpenAI Codex
You should have access to the internet. If you try to run something and it fails due to not having a module installed, please just install that module.

If it exists, you should install the requirements in the file `openai_codex_requirements.txt` if they aren't already installed. Again, feel free to install any other components (including ones not listed) that you need to fully complete your task.

Use Pyright (or Pylance) to check type-hinting and add in appropriate types. After you are done with your task, please double-check that you pull in recent changes and that your code still works with those changes. If you did any complex merging during this process, please explain what merging you did.