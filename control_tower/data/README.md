# Control Tower Data Files

- `scenarios.json`: scenario definitions, costs, and modeling knobs.
- `scenario_outputs.json`: generated precomputed outputs consumed by `app.py`.

Regenerate outputs with:

```bash
python control_tower/precompute_scenarios.py
```

