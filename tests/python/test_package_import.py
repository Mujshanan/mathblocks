def test_package_imports():
    import mathblocks

    assert isinstance(mathblocks.__version__, str)
