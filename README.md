# ScienceDirect AI Research Agent

A proof-of-concept AI agent that uses the ScienceDirect API to answer scientific questions by searching and analyzing academic literature.

## Features

- Search scientific articles on ScienceDirect
- AI-powered research assistant using Pydantic-AI
- Interactive chat interface
- Structured article retrieval with citations
- Rich terminal output with formatted tables and panels

## Windows Setup Guide (For Non-Technical Users)

If you're setting this up on Windows and aren't familiar with programming, follow this detailed guide first. Mac/Linux users can skip to the Quick Start section below.

### Step 1: Install Python on Windows

1. **Download Python:**
   - Open your web browser and go to https://www.python.org/downloads/
   - Click the big yellow "Download Python" button (get version 3.11 or newer)
   - Save the installer to your Downloads folder

2. **Install Python:**
   - Go to your Downloads folder and double-click the Python installer
   - **VERY IMPORTANT:** Check the box that says "Add Python to PATH" at the bottom of the first screen
   - Click "Install Now"
   - Wait for the installation to complete (this may take a few minutes)
   - Click "Close" when you see "Setup was successful"

3. **Verify Python is Working:**
   - Press the `Windows key + R` on your keyboard
   - Type `cmd` and press Enter (a black window will open)
   - Type exactly: `python --version`
   - Press Enter
   - You should see something like "Python 3.11.x" or "Python 3.12.x"
   - If you see an error instead, restart your computer and try again

### Step 2: Install uv (The Package Manager)

1. **Open PowerShell as Administrator:**
   - Right-click the Windows Start button (bottom-left corner)
   - Click "Windows PowerShell (Admin)" or "Terminal (Admin)"
   - Click "Yes" when Windows asks for permission

2. **Install uv:**
   - In the PowerShell window, copy and paste this entire command:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   - Press Enter and wait for it to finish (you'll see text scrolling)
   - When it's done, you'll see the prompt again

3. **Verify uv is Working:**
   - Close the PowerShell window
   - Open a new Command Prompt (Windows key + R, type `cmd`, press Enter)
   - Type: `uv --version`
   - Press Enter
   - You should see a version number like "uv 0.x.x"

### Step 3: Download the ScienceDirect Agent

1. **Option A: Download as ZIP (Easiest):**
   - Go to the project page on GitHub
   - Click the green "Code" button
   - Click "Download ZIP"
   - Save it to your Downloads folder
   - Go to Downloads, right-click the ZIP file
   - Select "Extract All..."
   - Choose `C:\Projects\` as the destination (create this folder if it doesn't exist)
   - Click "Extract"

2. **Option B: Use Git (If you have it):**
   - Open Command Prompt
   - Type: `cd C:\Projects`
   - Type: `git clone https://github.com/yourusername/sciencedirect-agent.git`
   - Press Enter

### Step 4: Set Up the Project

1. **Navigate to the Project Folder:**
   - Open File Explorer
   - Go to `C:\Projects\sciencedirect-agent` (or wherever you extracted it)
   - Click in the address bar at the top
   - Type `cmd` and press Enter
   - A Command Prompt window will open in that folder

2. **Install Project Dependencies:**
   - In the Command Prompt, type exactly:
   ```cmd
   uv sync
   ```
   - Press Enter
   - Wait for all packages to install (this may take 5-10 minutes the first time)
   - You'll see "Done!" or similar when complete

### Step 5: Get Your API Keys

You need two API keys to use this tool:

#### Elsevier API Key (for searching scientific papers):
1. Go to https://dev.elsevier.com in your browser
2. Click "Register" in the top-right corner
3. Fill out the registration form and create an account
4. Check your email and click the verification link
5. Log back into https://dev.elsevier.com
6. Click on "My API Keys" in your account menu
7. Click "Create API Key"
8. Give it a name like "ScienceDirect Agent"
9. Copy the long string of letters and numbers that appears
10. Save this somewhere safe (like a text file)

#### OpenAI API Key (for AI responses):
1. Go to https://platform.openai.com/signup
2. Create an account or sign in
3. You may need to add payment information (the agent uses very little credit)
4. Go to https://platform.openai.com/api-keys
5. Click "Create new secret key"
6. Give it a name like "ScienceDirect"
7. Copy the key that starts with "sk-"
8. **IMPORTANT:** Save this immediately - you won't be able to see it again!

### Step 6: Configure the Application

1. **Create the Configuration File:**
   - Open Notepad (search for it in the Start menu)
   - Copy and paste these two lines exactly:
   ```
   ELSEVIER_API_KEY=paste_your_elsevier_key_here
   OPENAI_API_KEY=paste_your_openai_key_here
   ```
   - Replace `paste_your_elsevier_key_here` with your actual Elsevier key
   - Replace `paste_your_openai_key_here` with your actual OpenAI key
   - Click File → Save As
   - Navigate to your project folder (`C:\Projects\sciencedirect-agent`)
   - **IMPORTANT:** In the "Save as type" dropdown, select "All Files (*.*)"
   - Type `.env` as the filename (yes, starting with a dot)
   - Click Save

2. **Verify Configuration:**
   - In your Command Prompt (still in the project folder), type:
   ```cmd
   uv run python main.py config
   ```
   - Press Enter
   - You should see "API keys are configured" or similar

### Step 7: Using the Application

Now you can use the application! Here are some examples:

**Search for articles:**
```cmd
uv run python main.py search "diabetes treatment" --limit 5
```

**Ask a research question:**
```cmd
uv run python main.py ask "What are the side effects of metformin?"
```

**Start an interactive chat:**
```cmd
uv run python main.py chat
```
(Type your questions, press Enter. Type "exit" to quit)

### Windows Troubleshooting

**"python is not recognized as a command"**
- You forgot to check "Add Python to PATH" during installation
- Solution: Uninstall Python, restart computer, reinstall with the box checked

**"uv is not recognized as a command"**
- The installation didn't complete properly
- Solution: Close all windows, run PowerShell as Administrator again, reinstall uv

**Can't save .env file**
- Notepad might be adding .txt to the filename
- Solution: When saving, put quotes around the filename: `".env"`

**"Access denied" or permission errors**
- You need administrator privileges
- Solution: Right-click Command Prompt/PowerShell, select "Run as Administrator"

**API key errors**
- Double-check you copied the entire key (no spaces before or after)
- Make sure you're using the correct keys in the right places
- OpenAI keys start with "sk-"

**Still having issues?**
- Take a screenshot of the error
- Note exactly what command you typed
- Ask for help with these details

## Quick Start (Mac/Linux)

### Prerequisites

- Python 3.11+
- Elsevier API key (get one at https://dev.elsevier.com)
- OpenAI API key (for AI responses)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd sciencedirect-agent

# Install dependencies with uv
uv sync
```

### Configuration

1. Create a `.env` file in the project root:
```bash
# Create .env file with your API keys
cat > .env << 'EOF'
ELSEVIER_API_KEY=your_elsevier_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
EOF
```

2. Optional: Add institutional token for full access:
```bash
ELSEVIER_INST_TOKEN=your_institutional_token_here
```

## Usage

### Running the Scripts

There are multiple ways to run the ScienceDirect Agent:

#### Method 1: Using uv run (recommended)
```bash
# Run with uv directly
uv run python main.py [command] [options]

# Examples:
uv run python main.py chat
uv run python main.py ask "What are the latest advances in CRISPR technology?"
uv run python main.py search "machine learning healthcare" --limit 10
```

#### Method 2: Using uv run with module
```bash
# Run as a module with uv
uv run python -m src.cli [command] [options]

# Examples:
uv run python -m src.cli chat
uv run python -m src.cli ask "What are the latest advances in CRISPR technology?"
uv run python -m src.cli search "machine learning healthcare" --limit 10
```

### Available Commands

#### Interactive Chat
Start an interactive research session:
```bash
uv run python main.py chat
```

#### Ask a Research Question
Get an AI-powered answer with citations:
```bash
uv run python main.py ask "What are the latest advances in CRISPR technology?"
```

#### Search Articles
Direct search for articles:
```bash
uv run python main.py search "machine learning healthcare" --limit 10
```

#### Check Configuration
Verify your API keys are set:
```bash
uv run python main.py config
```

## CLI Commands

- `chat` - Interactive research assistant
- `ask` - Get AI-powered answer to a research question
- `search` - Search for articles directly
- `config` - Show configuration status

### Command Options

All commands support:
- `--api-key / -k` - Override Elsevier API key
- `--inst-token / -t` - Override institutional token
- `--debug / -d` - Enable debug mode for detailed error information

Additional options:
- `ask --max-articles / -m` - Maximum articles to analyze (default: 5)
- `search --limit / -l` - Maximum search results (default: 5)

### Debug Mode

Enable debug mode to see detailed API error responses:

```bash
# Via command flag
uv run python main.py search "quantum computing" --debug

# Via environment variable
export DEBUG=true
uv run python main.py search "quantum computing"
```

See [DEBUG.md](DEBUG.md) for detailed debugging information.

## Project Structure

```
sciencedirect-agent/
   src/
      agent.py         # Pydantic-AI agent implementation
      sciencedirect.py # ScienceDirect API client
      cli.py           # Typer CLI interface
   tests/
      test_agent.py    # Basic tests
   .env                 # API keys (not in git)
   pyproject.toml       # Project configuration
```

## Testing

Run the test suite:

```bash
uv run pytest tests/
```

## API Limitations

- ScienceDirect API limits searches to 200 results per query
- Rate limiting may apply based on your API key tier
- Full-text access depends on institutional subscriptions

## Development

### Development Setup

```bash
# Install the project in development mode
uv sync

# Install development dependencies if needed
uv pip install pytest pytest-asyncio
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_agent.py
```

### Code Quality

```bash
# Format code (if black is installed)
uv run black src/ tests/

# Type checking (if mypy is installed)
uv run mypy src/
```

### Future Improvements

This is a proof of concept for rapid development. Potential improvements:
- Add database persistence for search history
- Implement caching for API responses
- Add more sophisticated prompt engineering
- Support for other academic databases
- Web interface option
- Export results to various formats

## License

MIT