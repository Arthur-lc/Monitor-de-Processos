import os
import subprocess
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer
from textual.widgets import DataTable, Footer, Header, RadioButton, RadioSet, Static
from textual.containers import Horizontal, Container


def get_cpu_usage():
    try:
        cmd = "mpstat 1 1 | grep 'Average' | awk '{print 100 - $NF}'"
        output = subprocess.check_output(cmd, shell=True, text=True)
        cpu_percent = float(output.strip())
        return f"{cpu_percent:.2f}%"
    except (subprocess.CalledProcessError, ValueError):
        # Fallback to top if mpstat is not available or fails
        try:
            cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%*id.*/\\1/' | awk '{print 100 - $1}'"
            output = subprocess.check_output(cmd, shell=True, text=True)
            cpu_percent = float(output.strip())
            return f"{cpu_percent:.2f}%"
        except Exception:
            return "N/A"

def get_memory_usage():
    try:
        cmd = "free -h | grep 'Mem:'"
        output = subprocess.check_output(cmd, shell=True, text=True)
        parts = output.split()
        total_mem = parts[1]
        used_mem = parts[2]
        free_mem = parts[3]
        return f"Total: {total_mem}, Used: {used_mem}, Free: {free_mem}"
    except Exception:
        return "N/A"

def get_processes(sort_by):
    if sort_by == 'c':
        sort_string = '-%cpu'
    elif sort_by == 'm':
        sort_string = '-%mem'

    cmd = f"ps aux --sort={sort_string}"
    output = subprocess.check_output(cmd, shell=True, text=True)
    lines = output.strip().split('\n')
    processes = []
    # Parse header
    header = lines[0].split()

    
    pid_idx = header.index('PID')
    user_idx = header.index('USER')
    cpu_idx = header.index('%CPU')
    mem_idx = header.index('%MEM')
    cmd_start_idx = header.index('COMMAND')

    for line in lines[1:]: # Skip header
        parts = line.split(None, cmd_start_idx - 1) # Split up to command
        if len(parts) >= cmd_start_idx:
            pid = parts[pid_idx]
            user = parts[user_idx]
            cpu = parts[cpu_idx]
            mem = parts[mem_idx]
            command = ' '.join(line.split()[cmd_start_idx:])

            if command.startswith('[') and command.endswith(']'):
                name = command
            else:
                name = command.split(" ")[0].split('/')[-1]
            processes.append((pid, user, name, cpu, mem))
    return processes


class ProcessMonitorApp(App):
    BINDINGS = [("q", "quit", "Quit")]

    sort_key = 'c'

    CSS = """
    #summary-container {
        height: auto;
        padding: 0 1;
        padding-bottom: 1;
    }
    #radio-container {
        height: auto;
        padding: 1;
    }

    DataTable {
        height: 1fr; /* This is the key: makes the table fill the remaining space */
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal(id="radio-container"):
            with Container(id="summary-container"):
                yield Static("CPU Usage:  ...", id="cpu-summary")
                yield Static("Mem Usage:  ...", id="mem-summary")

            with RadioSet(id="sort-select"):
                yield RadioButton("Sort by CPU", id="c", value=True)
                yield RadioButton("Sort by Memory", id="m")
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(.5, self.update_table)

    async def update_table(self) -> None:
        table = self.query_one(DataTable)

        cpu_usage = get_cpu_usage()
        mem_usage = get_memory_usage()
        
        cpu_widget = self.query_one("#cpu-summary", Static)
        mem_widget = self.query_one("#mem-summary", Static)

        cpu_widget.update(f"CPU Usage:  {cpu_usage}")
        mem_widget.update(f"Mem Usage:  {mem_usage}")
        
        if not table.columns:
            table.cursor_type = "none"
            table.add_columns("PID", "User", "Name", "%CPU", "%MEM")

        processes = get_processes(self.sort_key)
        
        table.clear() 
        for proc in processes:
            table.add_row(*proc, key=proc[0])

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        if event.pressed.id:
            self.sort_key = event.pressed.id

    async def watch_sort_key(self, old_key: str, new_key: str) -> None:
        await self.update_table()


if __name__ == "__main__":
    app = ProcessMonitorApp()
    app.run()