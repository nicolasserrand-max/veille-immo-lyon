"""Point d'entrée du worker : découvre les workflows et démarre le worker."""

from mistralai_workflows import discover_workflows, run_worker


async def main() -> None:
    discovered = discover_workflows()
    await run_worker(discovered)
