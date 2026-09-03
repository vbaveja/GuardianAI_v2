# GuardianAI Changelog

## Sprint 16 - Perception Dashboard Action Demo

Purpose:

- Show the complete Camera -> Perception -> Detection -> Decision/Event -> Action flow in the visual Perception Dashboard.
- Support ETHOS demo recording where detecting a person plays `hello.wav`.
- Keep the change dashboard-scoped without changing the validated perception platform.

Files Modified:

- `apps/perception_dashboard.py`
- `README.md`
- `COMMANDS.md`
- `docs/05_Applications_Guide.md`
- `docs/06_Teacher_Guide.md`
- `docs/07_Student_Guide.md`
- `docs/10_Troubleshooting.md`
- `docs/CHANGELOG.md`

Behavior Added:

- Added optional `--sound <wav file>` to the Perception Dashboard.
- When `--sound` is provided, the watched object appearance transition plays the WAV once.
- Remaining visible does not replay the sound; disappearing re-arms the trigger.
- The embedded Guardian Console shows watching label, state, confidence, and action status.
- Sound playback warnings are non-fatal, and playback starts without blocking the dashboard loop.

Validation Performed:

```bash
python3 -m py_compile apps/perception_dashboard.py
python3 -B apps/perception_dashboard.py --help
```

Raspberry Pi validation still required:

```bash
aplay sounds/hello.wav
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/hello.wav
```

Lessons Learned:

- The dashboard can demonstrate action behavior by reusing the existing watched-object state transition after its single perception pass.
- For visual demos, a simple persistent action status is enough to make the system response visible in recordings.
- Audio failures should be shown as warnings and should not stop the perception display.

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
