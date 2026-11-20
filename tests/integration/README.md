# Integration tests

Integration tests exercise MathBlocks at host boundaries rather than only testing isolated classes.

- `test_jupyter_kernel.py` launches a real IPython kernel through nbclient, executes notebook cells, and inspects the Jupyter widget-view MIME messages. It verifies that repeated notebook displays reference the same widget model and that Python-side state changes persist between cells.
- `test_marimo.py` checks the optional Marimo adapter when the Marimo extra is installed.
- `test_anywidget_hosts.py` contains lightweight AnyWidget compatibility smoke tests.

The Jupyter kernel test does not launch a browser or claim to verify a notebook frontend's DOM rendering. Browser-host view creation, reconnection, and disposal remain separate end-to-end coverage to add when a browser-host test harness is introduced.
