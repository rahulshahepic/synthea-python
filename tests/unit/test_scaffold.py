from synthea import resources


def test_resources_dir_points_at_java_resources() -> None:
    assert resources.resource_path("synthea.properties").is_file()
    assert resources.resource_path("modules").is_dir()
