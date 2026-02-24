class Graph:
    """
    Very small directed graph modeling the linear pipeline:
    recon → scan → analyze → report.
    Each node stores a callable that receives the *target* argument.
    """

    def __init__(self):
        self._pipeline = ["recon", "scan", "analyze", "report"]
        self._handlers = {name: self._default_handler for name in self._pipeline}

    def set_handler(self, name, fn):
        """
        Register a custom function for a node.
        fn must accept a single argument – the target.
        """
        if name not in self._pipeline:
            raise ValueError(f"Unknown node {name!r}")
        self._handlers[name] = fn

    def walk(self, target):
        """Execute the pipeline in order, passing target to each handler."""
        for name in self._pipeline:
            handler = self._handlers[name]
            handler(target)

    @staticmethod
    def _default_handler(target):
        print(f"[{target}] default step (no-op)")
