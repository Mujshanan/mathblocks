# Integration tests

Integration tests exercise MathBlocks at host boundaries rather than only testing isolated classes.

- `test_jupyter_kernel.py` launches a real IPython kernel through nbclient, executes notebook cells, and inspects the Jupyter widget-view MIME messages. It verifies that repeated notebook displays reference the same widget model and that Python-side state changes persist between cells.
- `tests/frontend/bootstrap-lifecycle.test.ts` exercises the AnyWidget frontend entry point with two views sharing one model. It verifies state propagation, independent `AbortSignal` cleanup, reconnecting a view to the existing model, and preservation of model state after view disposal.
- `test_marimo.py` checks the optional Marimo adapter when the Marimo extra is installed.
- `test_anywidget_hosts.py` contains lightweight AnyWidget compatibility smoke tests.

The Jupyter kernel test exercises the real kernel/display protocol. The frontend lifecycle test exercises the AFM render/abort contract with a test model and minimal DOM double; it does not launch a browser. Actual JupyterLab/Notebook browser rendering, output removal, and browser-managed reconnect/disposal remain separate end-to-end coverage to add when a browser-host test harness is introduced.
