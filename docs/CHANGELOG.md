# GuardianAI Changelog

## Sprint 15 - Generic Object Watch

Purpose:

- Generalize Person Greeter into a configurable Object Watch application.
- Let students build several intelligent machines by changing command-line options instead of editing Python code.
- Keep `apps/person_greeter.py` as the introductory Hello World application.

Files Added:

- `requirements.txt`
- `docs/CHANGELOG.md`

Files Modified:

- `apps/object_watch.py`
- `README.md`
- `COMMANDS.md`
- `docs/05_Applications_Guide.md`
- `docs/06_Teacher_Guide.md`
- `docs/07_Student_Guide.md`
- `docs/10_Troubleshooting.md`

Validation:

```bash
python3 -m py_compile apps/object_watch.py src/guardian.py apps/person_greeter.py apps/person_greeter_v2.py apps/guardian_console.py src/guardian_runtime.py
python3 -B apps/object_watch.py --help
```

macOS validation:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -B apps/object_watch.py --object person --sound sounds/hello.wav --mode once --threshold 0.01
```

Raspberry Pi validation:

```bash
python3 -m venv ~/venvs/ai --system-site-packages
source ~/venvs/ai/bin/activate
pip install -r requirements.txt
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once --threshold 0.25
python3 -B apps/object_watch.py --camera --object squirrel --sound sounds/hawk.wav --mode continuous --interval 3
```

Lessons Learned:

- A single application can become many student-built machines when behavior is configured through command-line options.
- `Guardian` provides the right application-facing surface for this sprint: apps can ask what is visible and what just changed without wiring the perception pipeline.
- Sound playback should remain simple and non-fatal. Missing sound files or missing Linux audio tools should not stop perception.
