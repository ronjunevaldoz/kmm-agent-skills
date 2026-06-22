### Claude Code CLI Project Profile

### Enforces the loading of custom KMP/JNI agent skills on initialization

### Automatically read the master agent instructions

\--system-prompt-file="AGENTS.md"

### Restrict the agent's behavior to high-density, non-conversational outputs

\--compact  
\--verbose=false

### Prevent accidental modifications to external dependencies or vendor folders

\--ignore="**/vendor/**"  
\--ignore="**/third\_party/**"  
\--ignore="**/.gradle/**"  
\--ignore="**/build/**"