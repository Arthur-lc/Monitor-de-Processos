import subprocess

def get_cpu_usage():
    """Fetches current CPU usage."""
    try:
        # Using mpstat for a more precise CPU idle percentage
        # Requires sysstat package (e.g., sudo apt-get install sysstat)
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
    """Fetches current memory usage."""
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

def get_processes():
    """Fetches a list of active processes."""
    try:
        # Get PID, User, %CPU, %MEM, Command
        cmd = "ps aux --sort=-%cpu,-%mem" # Sort by CPU then Memory
        output = subprocess.check_output(cmd, shell=True, text=True)
        lines = output.strip().split('\n')
        processes = []
        # Parse header
        header = lines[0].split()
        # Find index for relevant columns
        try:
            pid_idx = header.index('PID')
            user_idx = header.index('USER')
            cpu_idx = header.index('%CPU')
            mem_idx = header.index('%MEM')
            cmd_start_idx = header.index('COMMAND') # Command can have spaces
        except ValueError:
            # Fallback for systems with slightly different ps output headers
            pid_idx = 1
            user_idx = 0
            cpu_idx = 2
            mem_idx = 3
            cmd_start_idx = 10 # Common index for COMMAND

        for line in lines[1:]: # Skip header
            parts = line.split(None, cmd_start_idx - 1) # Split up to command
            if len(parts) >= cmd_start_idx:
                pid = parts[pid_idx]
                user = parts[user_idx]
                cpu = parts[cpu_idx]
                mem = parts[mem_idx]
                command = ' '.join(line.split()[cmd_start_idx:]) # Rejoin the command part
                processes.append((pid, user, cpu, mem, command))
        return processes
    except Exception:
        return []

def main():
     # --- CPU Section ---
    print("CPU Usage: ", get_cpu_usage())

    # --- Memory Section ---
    print("Mem Usage: ", get_memory_usage())

    # Montar a arvore de processos
    print ("\nProcessos")
    processes = get_processes()
    i = 0
    for pid, user, cpu, mem, command in processes:
        print("pid: ", pid, "| user: ", user, "| cpu: ", cpu, "| mem: ", mem, "\n")
        i += 1
        if i == 5 : 
            print("...")
            return
        

if __name__ == "__main__":
    main()