import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full", app_title="robusta")


@app.cell
def _():
    import json
    import tempfile
    from pathlib import Path

    import marimo as mo
    import tomli_w
    from marimo_toml_editor import TomlConfigEditor

    import robusta
    return Path, TomlConfigEditor, json, mo, robusta, tempfile, tomli_w


@app.cell
def _():
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_label = (
        f"GPU ({torch.cuda.get_device_name(0)})"
        if device == "cuda"
        else "CPU (no CUDA available)"
    )
    return device, device_label


@app.cell
def _(device_label, mo):
    mo.md(
        f"""
        # robusta — adversarial robustness scanner

        Edit the TOML config below, then click **Run scan**.

        > Set `HF_TOKEN` in the secrets tab (🔑) before running, otherwise
        > the scan will fail with a config error.
        >
        > Running on **{device_label}**.
        """
    )
    return


@app.cell
def _(Path, TomlConfigEditor, mo):
    config_path = Path("config.toml")
    widget = mo.ui.anywidget(
        TomlConfigEditor(
            path=str(config_path) if config_path.exists() else "",
            name="robusta",
        )
    )
    widget  # noqa: B018 (marimo idiom: last expression is rendered)
    return (widget,)


@app.cell
def _(mo):
    run_btn = mo.ui.run_button(label="Run scan")
    mo.hstack([run_btn], justify="start")
    return (run_btn,)


@app.cell
def _(Path, device, json, mo, robusta, run_btn, tempfile, tomli_w, widget):
    mo.stop(
        not run_btn.value,
        mo.callout(mo.md("Click **Run scan** to start."), kind="info"),
    )

    data = widget.value["data"]
    mo.stop(
        not data,
        mo.callout(
            mo.md(
                "The config editor is empty. Add at least `model` and `dataset`, "
                "plus one `[attack.*]` table."
            ),
            kind="warn",
        ),
    )

    toml_text = tomli_w.dumps(data)
    with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
        f.write(toml_text)
        tmp_path = Path(f.name)
    try:
        report_or_error = "ok"
        try:
            report = robusta.run(tmp_path, quiet=True, device=device)
        except robusta.ConfigError as e:
            report_or_error = str(e)
    finally:
        tmp_path.unlink(missing_ok=True)

    mo.stop(
        report_or_error != "ok",
        mo.callout(mo.md(f"**Config error:** {report_or_error}"), kind="danger"),
    )

    mo.callout(
        mo.md(
            f"**Done.** Wrote scan with {report['size'] or 'all'} samples; "
            f"attacks run: {', '.join(report['attacks'])}."
        ),
        kind="success",
    )
    mo.json(report)
    mo.download(
        data=json.dumps(report, indent=2).encode(),
        filename="results.json",
        mimetype="application/json",
        label="Download results.json",
    )
    return


if __name__ == "__main__":
    app.run()
