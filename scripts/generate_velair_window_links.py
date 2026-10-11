from pathlib import Path
import sys
import yaml


AUTOMATIONS_FILE = Path("/config/automations.yaml")
OUTPUT_FILE = Path("/config/packages/boiler/velair_window_links.yaml")

VELAIR_WINDOW_BLUEPRINT = "cgonfer/window_pause.yaml"


def as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def climate_object_id(entity_id):
    return entity_id.split(".", 1)[1]


def pretty_name(entity_id):
    object_id = climate_object_id(entity_id)

    return (
        object_id
        .replace("_termostat", "")
        .replace("_thermostat", "")
        .replace("_", " ")
        .title()
        + " linked windows"
    )


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def make_sensor_yaml(climate_entity, windows):
    object_id = climate_object_id(climate_entity)

    name = pretty_name(climate_entity)
    unique_id = f"{object_id}_linked_windows"

    if windows:
        windows_template = "[\n" + ",\n".join(
            f"              {quote(entity_id)}"
            for entity_id in windows
        ) + "\n            ]"
    else:
        windows_template = "[]"

    return f"""      - name: {name}
        unique_id: {unique_id}
        state: "{len(windows)}"
        attributes:
          climate_entity: {quote(climate_entity)}
          entities: >
            {{{{ {windows_template} }}}}
"""


def main():
    if not AUTOMATIONS_FILE.exists():
        print(f"ERROR: {AUTOMATIONS_FILE} not found")
        sys.exit(1)

    with AUTOMATIONS_FILE.open("r", encoding="utf-8") as file:
        automations = yaml.safe_load(file) or []

    if not isinstance(automations, list):
        print("ERROR: automations.yaml must contain a YAML list")
        sys.exit(1)

    mappings = {}

    print("Searching Velair window pause automations...")
    print()

    for automation in automations:
        if not isinstance(automation, dict):
            continue

        blueprint = automation.get("use_blueprint")

        if not isinstance(blueprint, dict):
            continue

        path = blueprint.get("path")

        if path != VELAIR_WINDOW_BLUEPRINT:
            continue

        inputs = blueprint.get("input", {}) or {}

        climates = as_list(inputs.get("climate_entity"))
        windows = as_list(inputs.get("opening_entities"))

        climates = [
            entity_id
            for entity_id in climates
            if isinstance(entity_id, str)
            and entity_id.startswith("climate.")
        ]

        windows = [
            entity_id
            for entity_id in windows
            if isinstance(entity_id, str)
            and entity_id.startswith("binary_sensor.")
        ]

        alias = automation.get("alias", "<no alias>")

        print(f"Automation: {alias}")
        print(f"Climate:    {climates or 'NONE'}")
        print(f"Windows:    {windows or 'NONE'}")
        print()

        for climate in climates:
            mappings.setdefault(climate, [])

            for window in windows:
                if window not in mappings[climate]:
                    mappings[climate].append(window)

    if not mappings:
        print(
            f"ERROR: No automations using "
            f"{VELAIR_WINDOW_BLUEPRINT} were found."
        )
        sys.exit(1)

    output = [
        "# AUTO-GENERATED FILE",
        "# Source: /config/automations.yaml",
        f"# Blueprint: {VELAIR_WINDOW_BLUEPRINT}",
        "# Do not edit manually.",
        "# Re-run generate_velair_window_links.py after changing",
        "# Velair window pause automations.",
        "",
        "template:",
        "  - sensor:",
    ]

    for climate, windows in sorted(mappings.items()):
        output.append(
            make_sensor_yaml(
                climate,
                windows,
            )
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        "\n".join(output).rstrip() + "\n",
        encoding="utf-8",
    )

    print("=" * 70)
    print(f"Generated: {OUTPUT_FILE}")
    print()
    print("Mappings:")

    for climate, windows in sorted(mappings.items()):
        print()
        print(climate)

        if windows:
            for window in windows:
                print(f"  -> {window}")
        else:
            print("  -> no linked windows")


if __name__ == "__main__":
    main()