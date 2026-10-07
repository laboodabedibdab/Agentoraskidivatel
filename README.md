# CPU Core Affinity & Load Balancer (Educational Prototype)

A Python-based proof-of-concept designed to explore OS-level process management and core scheduling mechanics.

## What it does
The script uses `multiprocessing` and `psutil` to:
* Bind worker processes to specific CPU cores (`cpu_affinity`).
* Dynamically monitor core loads in real-time.
* Automatically migrate the heaviest processes from overloaded cores to idle ones on the fly.

## Important Note
This is purely an **educational experiment** written to understand how system schedulers work under the hood. Due to Python's overhead, it is inefficient for production-grade high-frequency load balancing, but it demonstrates a solid, low-level understanding of operating system processes, resource tracking, and custom scheduling logic.
