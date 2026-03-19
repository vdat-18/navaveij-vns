# MIG-5 Test Results

- Status: Verification attempted (runtime commands blocked by environment toolchain gaps)

## Static Validation

- `GetDiagnostics` result: no TypeScript/ESLint diagnostics reported after changes.

## Attempt 1

- Command: `npm run lint`
- Result: failed before lint execution due missing toolchain command.
- Output:
  - `zsh: command not found: npm`

## Attempt 2

- Command: `which node`
- Result: command-runner wrapper failed before shell execution.
- Output:
  - `Error: System { message: "No such file or directory (os error 2)" }`

## Attempt 3

- Command: `uv run pytest scripts/tests/test_frontend_reliability_contract.py -v`
- Result: command failed in environment due missing `uv`.
- Output:
  - `zsh: command not found: uv`

## Current Confidence

- MIG-5 wiring is complete in source:
  - header toggle state and UI,
  - API `force_rule_based` payload,
  - panel re-fetch dependency on toggle,
  - unchanged `key={patientToken}` remount logic,
  - frontend reliability contract checks for MIG-5 wiring.
- Full runtime verification remains pending until Node/npm command execution is available in environment.
