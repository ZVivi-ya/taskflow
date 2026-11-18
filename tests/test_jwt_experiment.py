import runpy
from pathlib import Path


def test_jwt_experiment_verifies_token_without_printing_it(capsys):
    script = (
        Path(__file__).resolve().parents[1]
        / "learning_experiments"
        / "test_jwt.py"
    )
    namespace = runpy.run_path(str(script), run_name="__main__")

    assert callable(namespace["main"])
    output = capsys.readouterr().out
    assert "Token 验证成功" in output
    assert "用户 ID：" in output
    assert "eyJ" not in output
