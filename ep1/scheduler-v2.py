import os
from collections import deque

class Process:
    def __init__(self, name, commands):
        self.name = name
        self.commands = commands
        self.PC = 0
        self.X = 0
        self.Y = 0
        self.state = "READY"
        self.blocked_counter = 0
        self.swaps = 0
        self.instructions = 0

    def execute_next(self):
        if self.PC < len(self.commands):
            cmd = self.commands[self.PC]
            self.PC += 1
            self.instructions += 1

            if "X=" in cmd:
                self.X = int(cmd.split('=')[1])
            elif "Y=" in cmd:
                self.Y = int(cmd.split('=')[1])
            elif "E/S" in cmd:
                self.state = "BLOCKED"
                self.blocked_counter = 2
                self.swaps += 1
            elif "COM" in cmd:
                pass
            elif "SAIDA" in cmd:
                self.state = "TERMINATED"
                self.swaps += 1
            return cmd
        return None

class Scheduler:
    def __init__(self, quantum):
        self.ready_queue = deque()
        self.blocked_queue = deque()
        self.processes = {}
        self.quantum = quantum

    def run(self, dir_path):
        log_file_name = f"log{self.quantum:02d}.txt"
        with open(log_file_name, 'w') as log_file:
            files = sorted(os.listdir(dir_path))
            for f in files:
                if f.endswith(".txt") and not f == "quantum.txt":
                    with open(os.path.join(dir_path, f), 'r') as fp:
                        lines = fp.readlines()
                        name = lines[0].strip()
                        commands = [cmd.strip() for cmd in lines[1:]]
                        process = Process(name, commands)
                        self.ready_queue.append(process)
                        self.processes[name] = process
                        log_file.write(f"Carregando {process.name}\n")
            
            while self.ready_queue or self.blocked_queue:
                if self.ready_queue:
                    current_process = self.ready_queue.popleft()
                    current_process.state = "RUNNING"
                    log_file.write(f"Executando {current_process.name}\n")
                    quanta = 0
                    for i in range(self.quantum):
                        quanta = i + 1
                        if current_process.state == "RUNNING":
                            cmd = current_process.execute_next()
                            if cmd is None or current_process.state == "BLOCKED":
                                break

                if current_process.state == "RUNNING":
                    current_process.state = "READY"
                    log_file.write(f"Interrompendo {current_process.name} após {quanta} instruções\n")
                    self.ready_queue.append(current_process)
                elif current_process.state == "BLOCKED":
                    log_file.write(f"E/S iniciada em {current_process.name}\n")
                    log_file.write(f"Interrompendo {current_process.name} após {quanta} instruções\n") if quanta > 1 else log_file.write(f"Interrompendo {current_process.name} após {quanta} instrução\n")
                    self.blocked_queue.append(current_process)
                elif current_process.state == "TERMINATED":
                    log_file.write(f"{current_process.name} terminado. X={current_process.X}. Y={current_process.Y}\n")

                for process in list(self.blocked_queue):
                    process.blocked_counter -= 1
                    if process.blocked_counter == 0:
                        process.state = "READY"
                        self.ready_queue.append(process)
                        self.blocked_queue.remove(process)

            total_swaps = sum(process.swaps for process in self.processes.values())
            total_instructions = sum(process.instructions
                        for process in self.processes.values())
            average_swaps = total_swaps / len(self.processes)
            average_instructions = total_instructions / len(self.processes)

            log_file.write(f"MEDIA DE TROCAS: {average_swaps:.2f}\n")
            log_file.write(f"MEDIA DE INSTRUÇÕES: {average_instructions:.2f}\n")
            log_file.write(f"QUANTUM: {quantum}\n")

if __name__ == "__main__":
    with open('C:\sistemas-informacao\so-ACH2044\ep1\programas\quantum.txt','r') as q:
        quantum = int(q.read().strip())
    scheduler = Scheduler(quantum)
    # scheduler.load_programs()
    scheduler.run("C:\sistemas-informacao\so-ACH2044\ep1\programas")
