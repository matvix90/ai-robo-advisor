from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich.panel import Panel
import time

console = Console()

def display_data_list(data, title="Data List"):
    """
    Display a list of data in a user-friendly CLI format with progress bar.
    
    Args:
        data (list): List of items to display
        title (str): Title for the display
    """
    console.print(Panel(f"[bold green]{title}[/bold green]", expand=False))
    
    for item in track(data, description="Processing items"):
        time.sleep(0.1)  # simulate processing delay
        console.print(f"[cyan]Processed:[/cyan] {item}")

    console.print("[bold blue]✅ All items displayed successfully![/bold blue]\n")


def display_table(data, columns=None, title="Table"):
    """
    Display data in a formatted table.
    
    Args:
        data (list of dict): List of dictionary items
        columns (list): Optional list of columns to display
        title (str): Table title
    """
    if not data:
        console.print("[red]No data to display.[/red]")
        return

    if columns is None:
        columns = data[0].keys()

    table = Table(title=title)
    for col in columns:
        table.add_column(col, style="magenta")

    for row in data:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    console.print(table)


def display_message(message, msg_type="info"):
    """
    Display a formatted message.
    
    Args:
        message (str): The message to display
        msg_type (str): Type of message: 'info', 'success', 'warning', 'error'
    """
    colors = {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }
    console.print(f"[bold {colors.get(msg_type, 'white')}]{message}[/bold {colors.get(msg_type, 'white')}]")

# Example usage
if __name__ == "__main__":
    sample_list = ["Item 1", "Item 2", "Item 3"]
    display_data_list(sample_list, title="Sample List")

    sample_table = [
        {"Name": "Alice", "Age": 25, "Role": "Engineer"},
        {"Name": "Bob", "Age": 30, "Role": "Manager"},
    ]
    display_table(sample_table, title="Sample Table")

    display_message("This is an info message.", "info")
    display_message("Operation successful!", "success")
    display_message("Be careful!", "warning")
    display_message("Something went wrong!", "error")
