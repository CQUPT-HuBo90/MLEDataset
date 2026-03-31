# Reproduction

This directory stores the virtual environment configuration files used for reproducing submitted code from teams that satisfied both of the following conditions:

1. They obtained a valid result submission between 21:00:00 on March 21, 2026 (UTC+8) and 20:59:59 on March 22, 2026 (UTC+8).
2. They submitted valid code files before 23:00 on March 29, 2026 (UTC+8).

For all teams meeting the criteria above, the organizers reproduced their submitted code and archived the corresponding environment configuration files in this directory for record and reference.

The main reproduction hardware and system environment was:

- AMD Ryzen 5 7500F
- 32 GB RAM
- NVIDIA GeForce RTX 5070 Ti
- Windows 11

Some submissions were reproduced on CPU instead of GPU because their required `torch` versions were too old to run properly in the current GPU environment.

### How to use

Each team directory contains a `pixi.toml` file describing the corresponding reproduction environment and tasks. In general, inference can be reproduced through the unified entry point below from within the target team directory:

```bash
pixi run test
```

This command follows the execution method provided by the corresponding team for inference and reproduction.
