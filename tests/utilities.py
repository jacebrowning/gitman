"""Test helpers."""


def strip(text, tabs=None, end='\n'):
    """Strip leading whitespace indentation on multiline string literals."""
    lines = []

    for line in text.strip().splitlines():
        if not tabs:
            tabs = line.count(' ' * 4)
        lines.append(line.replace(' ' * tabs * 4, '', 1))

    return '\n'.join(lines) + end
