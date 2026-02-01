# Security

## Command Execution
- Commands are executed via `subprocess.run` with a list of arguments to prevent shell injection.
- User-provided package names and queries are passed as individual arguments.

## Privilege Management
- Operations that modify the system are prefixed with `sudo` when not run as root.
- Read-only operations run unprivileged.

## Input Validation
- Unsupported flag combinations are rejected with a clear error message.
- Search and info operations require at least one argument.
