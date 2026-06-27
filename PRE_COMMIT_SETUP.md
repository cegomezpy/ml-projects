# Pre-Commit Setup Guide

This project uses **pre-commit hooks** to ensure code quality and consistency before each commit.

## What Pre-Commit Hooks Do

Pre-commit will automatically run these checks **before every commit**:

1. **Black** - Format code to maintain consistent style
2. **Ruff** - Fast Python linter to catch common issues
3. **MyPy** - Type checking to ensure type safety
4. **Bandit** - Security vulnerability scanning
5. **Standard Checks** - Trailing whitespace, file endings, large files, etc.

## Installation

### Step 1: Install Dev Dependencies

If you haven't already installed dev dependencies:

```bash
# Using uv (recommended)
uv sync --all-extras

# OR using pip
pip install -e ".[dev]"
```

### Step 2: Install Pre-Commit Hooks

```bash
# This installs the git hooks
pre-commit install
```

You should see:
```
pre-commit installed at .git/hooks/pre-commit
```

## Usage

### Automatic (Recommended)

Once installed, pre-commit runs **automatically** on every `git commit`:

```bash
git add .
git commit -m "Your commit message"
# Pre-commit hooks will run automatically
```

If any hook fails, the commit will be blocked and you'll see what needs to be fixed.

### Manual Run

Run pre-commit on all files manually:

```bash
# Check all files
pre-commit run --all-files

# Check only staged files
pre-commit run
```

### Skip Hooks (Not Recommended)

Only in rare cases when you need to commit without running hooks:

```bash
git commit --no-verify -m "Emergency fix"
```

## What Each Hook Does

### 1. Black (Code Formatter)
- **What**: Formats your Python code to PEP 8 standard
- **Auto-fix**: Yes
- **Example**: Fixes line length, spacing, quotes

### 2. Ruff (Linter)
- **What**: Checks for code quality issues
- **Auto-fix**: Some issues (use `--fix`)
- **Example**: Unused imports, undefined names, syntax errors

### 3. MyPy (Type Checker)
- **What**: Verifies type hints are correct
- **Auto-fix**: No (you must fix manually)
- **Example**: Ensures functions have proper type annotations

### 4. Bandit (Security)
- **What**: Scans for security vulnerabilities
- **Auto-fix**: No
- **Example**: SQL injection risks, unsafe functions

### 5. Standard Hooks
- **What**: Basic file hygiene
- **Auto-fix**: Most (trailing whitespace, file endings)
- **Example**: Removes trailing spaces, ensures files end with newline

## Common Scenarios

### Scenario 1: Hook Fails - Auto-Fixed

```bash
$ git commit -m "Add feature"

Trim trailing whitespace.....................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing src/domain/entities/model.py
```

**Solution**: The hook fixed the issue. Just add and commit again:
```bash
git add .
git commit -m "Add feature"
```

### Scenario 2: Hook Fails - Manual Fix Required

```bash
$ git commit -m "Add feature"

Type check with MyPy.........................Failed
- hook id: mypy
- exit code: 1

src/application/use_cases/train_model.py:45: error: Function is missing a return type annotation
```

**Solution**: Fix the issue in your code, then commit:
```bash
# Fix the code (add return type)
def execute(self, ...) -> dict:  # Add -> dict

git add .
git commit -m "Add feature"
```

### Scenario 3: All Hooks Pass

```bash
$ git commit -m "Add feature"

Trim trailing whitespace.....................Passed
Fix end of files.............................Passed
Check YAML syntax............................Passed
Format code with Black.......................Passed
Lint with Ruff...............................Passed
Type check with MyPy.........................Passed
Security check with Bandit...................Passed

[main abc1234] Add feature
 3 files changed, 50 insertions(+)
```

**Success!** Your commit was created.

## Configuration

All configurations are in `pyproject.toml`:

- **Black**: Line length 100, Python 3.10+
- **Ruff**: Line length 100, Python 3.10+
- **MyPy**: Strict type checking, ignore sklearn/joblib imports
- **Bandit**: Exclude tests, skip assert checks

## Updating Hooks

Update to the latest hook versions:

```bash
pre-commit autoupdate
```

## Bypassing Specific Hooks

If you need to skip a specific hook (rare):

```bash
SKIP=mypy git commit -m "WIP: incomplete types"
```

## CI/CD Integration

Pre-commit can also run in CI/CD pipelines:

```bash
# In your CI workflow
pip install pre-commit
pre-commit run --all-files
```

## Troubleshooting

### Issue: "pre-commit: command not found"

**Solution**: Install pre-commit:
```bash
uv sync --all-extras
# OR
pip install pre-commit
```

### Issue: Hooks are slow

**Solution**: Pre-commit caches environments. First run is slower, subsequent runs are fast.

### Issue: MyPy errors in third-party libraries

**Solution**: Already configured in `pyproject.toml`:
```toml
[[tool.mypy.overrides]]
module = ["sklearn.*", "joblib.*"]
ignore_missing_imports = true
```

Add more modules if needed.

## Best Practices

1. ✅ **Run manually before committing** large changes:
   ```bash
   pre-commit run --all-files
   ```

2. ✅ **Keep hooks updated**:
   ```bash
   pre-commit autoupdate
   ```

3. ✅ **Fix issues immediately** - don't accumulate technical debt

4. ❌ **Don't skip hooks** unless absolutely necessary

5. ✅ **Commit often** - small commits are easier to validate

## Summary

Pre-commit ensures:
- **Consistent code style** (Black)
- **No common bugs** (Ruff)
- **Type safety** (MyPy)
- **Security** (Bandit)
- **Clean files** (Standard hooks)

This maintains high code quality and follows the DDD/SOLID principles defined in our [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md).

---

**Questions?** See the [Pre-Commit Documentation](https://pre-commit.com/)
