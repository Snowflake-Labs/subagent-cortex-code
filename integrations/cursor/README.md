# Cortex Code Integration for Cursor IDE

A Cursor skill that enables seamless Snowflake operations through Cortex Code CLI, providing specialized Snowflake expertise directly in your IDE.

## 🎯 What This Does

This skill allows Cursor IDE to leverage Cortex Code's specialized Snowflake capabilities:
- **Execute SQL queries** on Snowflake databases
- **Data quality checks** and validation
- **Schema exploration** and analysis
- **Cortex AI features** (Cortex Search, Analyst, ML functions)
- **Snowpark operations** and dynamic tables
- **Security and governance** queries

## 📋 Prerequisites

Before installing this skill, ensure you have:

1. **Cursor IDE** installed
2. **Cortex Code CLI** installed and configured
   ```bash
   # Verify cortex CLI is available
   cortex --version
   ```
3. **Snowflake connection** configured in Cortex
   ```bash
   # Test your Snowflake connection
   cortex -p "SHOW DATABASES" --input-format stream-json
   ```
4. **Python 3.8+** installed
   ```bash
   python3 --version
   ```

## 🚀 Installation

### Step 1: Install the Skill

Clone the Cortex Code integration repository and run the installation script:

```bash
# Clone the repository
git clone https://github.com/Snowflake-Labs/subagent-cortex-code.git
cd subagent-cortex-code

# Run the installation script
cd integrations/cursor
./install.sh
```

This will:
- Copy shared scripts and security modules to `~/.cursor/skills/cortex-code/`
- Parameterize for Cursor environment
- Make scripts executable

### Step 2: Set Up Automatic Routing (Optional)

For automatic Snowflake query detection, add routing rules to your project:

```bash
# Copy the template to your project root
cp /path/to/subagent-cortex-code/integrations/cursor/.cursorrules.template /path/to/your/project/.cursorrules
```

Or manually create `.cursorrules` in your project root with:

```markdown
# Snowflake and Cortex Routing - Direct Skill Invocation

When the user asks about Snowflake, databases, warehouses, Cortex, or data operations, you MUST use the cortex-code skill directly by invoking:

```
/cortex-code
```

## Detection Keywords

Invoke `/cortex-code` when user mentions:
- Snowflake, warehouse, database, schema, table, view
- SQL query, SELECT, data quality, data analysis
- Cortex Search, Cortex Analyst, Cortex AI
- Snowpark, dynamic tables, streams, tasks
- "how many databases", "show me", "query", "check data"
```

### Step 3: Restart Cursor

Restart Cursor IDE to load the new skill.

### Step 4: Verify Installation

1. Open Cursor IDE
2. Open the AI chat window
3. Type `/cortex-code` - you should see the skill in the autocomplete
4. Or type a Snowflake query and the skill should auto-invoke (if you set up .cursorrules)

## 💡 Usage

### Direct Invocation

Use the `/cortex-code` command followed by your question:

```
/cortex-code How many databases do I have in Snowflake?
```

```
/cortex-code Show me top 10 customers by revenue
```

```
/cortex-code Check data quality for SALES_DATA table
```

### Automatic Invocation

With `.cursorrules` configured, just ask naturally:

```
User: How many databases do I have?
```

The skill will automatically invoke and route to Cortex Code.

### Multi-Turn Conversations

The skill enriches context automatically for follow-up questions:

```
User: Which databases have stock data?
Agent: [uses /cortex-code, identifies DB_STOCK, FINANCE_ECONOMICS]

User: Show me the schema for the main table
Agent: [uses /cortex-code with context: "User previously identified databases..."]
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Cursor IDE    │
│   (AI Chat)     │
└────────┬────────┘
         │
         │ /cortex-code "query"
         ▼
┌─────────────────────────────┐
│   Cortex Code Skill         │
│   (~/.cursor/skills/)       │
├─────────────────────────────┤
│ 1. Build enriched context   │
│ 2. Route request            │
│ 3. Execute via CLI          │
└────────┬────────────────────┘
         │
         │ python3 scripts/execute_cortex.py
         ▼
┌─────────────────────────────┐
│   Cortex Code CLI           │
│   (headless mode)           │
├─────────────────────────────┤
│ - Stream-JSON format        │
│ - Auto-approval mode        │
│ - RW envelope               │
└────────┬────────────────────┘
         │
         │ snowflake_sql_execute
         ▼
┌─────────────────────────────┐
│   Snowflake Database        │
└─────────────────────────────┘
```

## 📁 File Structure

```
skill/
├── SKILL.md                    # Skill definition (Cursor format)
├── scripts/
│   ├── execute_cortex.py      # Main execution script
│   ├── route_request.py       # Routing logic
│   ├── discover_cortex.py     # Capability discovery
│   ├── predict_tools.py       # Tool prediction
│   ├── read_cortex_sessions.py # Session reading
│   └── security_wrapper.py    # Security wrapper
└── security/                   # Security modules (if present)
```

## 🔧 Configuration

### Security Envelope

The skill uses `RW` (Read-Write) envelope by default. Modify in `SKILL.md`:

```bash
--envelope "RO"   # Read-only operations
--envelope "RW"   # Read-write operations (default)
```

### Approval Mode

Set to `auto` for non-interactive execution. Modify in `SKILL.md`:

```bash
--approval-mode "auto"    # Auto-approve (with audit logging)
--approval-mode "prompt"  # Prompt for each operation
```

### Audit Logging

Executions are logged to:
```
~/.cursor/skills/cortex-code/audit.log
```

## 🆚 Cursor vs Claude Code CLI

| Feature | Cursor Skill | Claude Code CLI |
|---------|--------------|-----------------|
| **Interface** | IDE chat window | Terminal CLI |
| **Invocation** | `/cortex-code` | `claude -p "..."` |
| **Context Enrichment** | Manual (via skill instructions) | Automatic (memory + chat history) |
| **Installation** | `~/.cursor/skills/` | `~/.claude/skills/` |
| **Routing** | `.cursorrules` | Skill description |
| **Approval** | Auto (headless) | Auto or prompt |
| **Audit Logs** | `~/.cursor/skills/cortex-code/audit.log` | `~/.claude/skills/cortex-code/audit.log` |
| **Best For** | IDE-based workflows | CLI-based workflows |

## 🐛 Troubleshooting

### Skill Not Found

```
Error: /cortex-code skill not found
```

**Solution**:
1. Verify skill installation: `ls ~/.cursor/skills/cortex-code/SKILL.md`
2. Restart Cursor IDE
3. Check skill file name is `SKILL.md` (uppercase)

### Cortex CLI Not Found

```
Error: cortex: command not found
```

**Solution**:
1. Install Cortex Code CLI
2. Verify: `which cortex`
3. Ensure `cortex` is in your PATH

### Connection Errors

```
Error: Failed to connect to Snowflake
```

**Solution**:
1. Check Cortex configuration: `cortex --config`
2. Test connection: `cortex -p "SHOW DATABASES" --input-format stream-json`
3. Verify Snowflake credentials

### Permission Denied

```
Error: Permission denied: scripts/execute_cortex.py
```

**Solution**:
```bash
chmod +x ~/.cursor/skills/cortex-code/scripts/*.py
```

### Python Import Errors

```
Error: No module named 'xyz'
```

**Solution**:
```bash
# Install required dependencies
pip3 install anthropic pyyaml requests
```

## 📊 Examples

### Query Databases

```
/cortex-code How many databases do I have in Snowflake?
```

**Output**:
```
Executing SQL: SELECT COUNT(*) FROM SNOWFLAKE.INFORMATION_SCHEMA.DATABASES
Result: 12 databases
```

### Data Quality Check

```
/cortex-code Check data quality for SALES_DATA table
```

**Output**:
```
Data Quality Report for SALES_DATA:
- Total rows: 1,234,567
- Null rates: CUSTOMER_ID (0%), ORDER_DATE (0.1%), AMOUNT (0%)
- Duplicates: 5 duplicate ORDER_IDs found
- Data types: All columns match expected types
```

### Complex Query with Context

```
User: Which databases have stock data?
Agent: Found 2 databases: DB_STOCK, FINANCE_ECONOMICS

User: Show me the top 5 tables in DB_STOCK by row count
Agent: [automatically includes context: "User previously identified DB_STOCK"]
```

## 🤝 Contributing

Issues and pull requests welcome at the repository.

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Related Projects

- **Cortex Code CLI**: https://github.com/anthropics/cortex-code
- **Cursor IDE**: https://cursor.com
- **Cursor Skills Documentation**: https://cursor.com/docs/skills

## 📮 Support

For issues specific to:
- **This skill**: Open an issue in this repository
- **Cortex Code CLI**: Check Cortex Code documentation
- **Cursor IDE**: Check Cursor documentation

## ⚙️ Advanced Configuration

### Custom Routing Logic

Edit `scripts/route_request.py` to customize routing logic:

```python
def analyze_with_llm_logic(query: str, capabilities: Dict) -> Tuple[str, float]:
    # Add custom routing logic here
    pass
```

### Custom Tool Prediction

Edit `scripts/predict_tools.py` to customize tool prediction:

```python
def predict_tools(query: str) -> List[str]:
    # Add custom tool prediction logic here
    pass
```

### Custom Security Rules

Edit `scripts/security_wrapper.py` to add custom security rules:

```python
def check_credential_allowlist(query: str) -> Dict:
    # Add custom security checks here
    pass
```

## 🎓 Learning Resources

- **Snowflake Documentation**: https://docs.snowflake.com
- **Cortex AI Features**: https://docs.snowflake.com/en/user-guide/snowflake-cortex
- **Cursor Skills Guide**: https://cursor.com/docs/skills
