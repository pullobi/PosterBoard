# ANSI Escape Codes for Colors
reset = "\033[0m"

# Colors mapping, including SwiftUI colors
colors = {
    # Basic colors
    'black': "\033[30m",
    'red': "\033[31m",
    'green': "\033[32m",
    'yellow': "\033[33m",
    'blue': "\033[34m",
    'magenta': "\033[35m",
    'cyan': "\033[36m",
    'white': "\033[37m",
    'gray': "\033[90m",
    'bright_red': "\033[91m",
    'bright_green': "\033[92m",
    'bright_yellow': "\033[93m",
    'bright_blue': "\033[94m",
    'bright_magenta': "\033[95m",
    'bright_cyan': "\033[96m",
    'bright_white': "\033[97m",

    # SwiftUI colors
    'indigo': "\033[38;5;57m",     # Indigo in ANSI 256 colors
    'lilac': "\033[38;5;170m",     # Lilac in ANSI 256 colors
    'pink': "\033[38;5;218m",      # SwiftUI pink
    'orange': "\033[38;5;214m",    # SwiftUI orange
    'purple': "\033[38;5;93m",     # SwiftUI purple
    'swift_blue': "\033[38;5;33m", # SwiftUI blue
    'swift_green': "\033[38;5;34m",
    'swift_yellow': "\033[38;5;226m",
    'swift_red': "\033[38;5;9m",
}

# Function generator for all colors
def color(color: str, text: str) -> str:
    """Apply the given color to the text."""
    if color in colors:
        return f"{colors[color]}{text}{reset}"
    raise ValueError(f"Color '{color}' is not defined.")

# Custom hex color
def hex(hex: str, text: str) -> str:
    """Apply a custom hex color to the text."""
    hex = hex.lstrip('#')
    r, g, b = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m{text}{reset}"
