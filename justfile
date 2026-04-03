# Bump version: just bump [major|minor|patch] (default: patch)
bump part="patch":
    #!/usr/bin/env bash
    old=$(hatch version)
    hatch version {{part}}
    new=$(hatch version)
    sed -i "s/python-ly $old/python-ly $new/g" tests/test_xml_files/*.xml
    echo "Bumped $old -> $new"
