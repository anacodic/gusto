# Installation Tips

## Why Installation Takes Time

The requirements.txt includes several heavy packages:
- **sentence-transformers** (~500MB+ with models)
- **numpy, pandas, scikit-learn** (large data science libraries)
- **strands-agents** (may require C++ compilation)
- **cryptography** (needs compilation)

## Speed Up Installation

### Option 1: Use pip cache (recommended)
```bash
# Enable pip cache (usually enabled by default)
pip install --cache-dir ~/.cache/pip -r requirements.txt
```

### Option 2: Install in parallel
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 3: Skip optional heavy packages (if not needed immediately)
```bash
# Install core packages first
pip install fastapi uvicorn sqlalchemy aiosqlite python-dotenv

# Then install ML packages (takes longer)
pip install sentence-transformers scikit-learn pandas numpy

# Finally install agent system
pip install strands-agents strands-agents-tools
```

### Option 4: Use pre-built wheels
```bash
# Upgrade pip to get latest wheels
pip install --upgrade pip setuptools wheel

# Then install requirements
pip install -r requirements.txt
```

## Expected Installation Time

- **Fast network + good CPU**: 5-10 minutes
- **Normal conditions**: 10-20 minutes
- **Slow network or old CPU**: 20-40 minutes

## Troubleshooting

If installation is stuck or very slow:

1. **Check network**: Test with `ping pypi.org`
2. **Use different index**: `pip install -i https://pypi.org/simple/ -r requirements.txt`
3. **Skip problematic packages**: Comment out `strands-agents` if C++ compilation fails
4. **Check disk space**: Ensure you have at least 2GB free

## Progress Indicators

You should see:
- ✅ "Collecting..." messages (downloading metadata)
- ✅ "Downloading..." messages (downloading packages)
- ✅ "Building wheel..." (compiling packages)
- ✅ "Installing..." (installing packages)

If you see the same package name repeating, it might be stuck - try Ctrl+C and restart.
