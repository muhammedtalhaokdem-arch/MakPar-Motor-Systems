import os
import re
import time
import msvcrt
import sys
import codecs
import subprocess

sys.stdin.reconfigure(encoding='utf-8') if sys.version_info >= (3, 7) else None
sys.stdout.reconfigure(encoding='utf-8') if sys.version_info >= (3, 7) else None

COLORS = {
    "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
    "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m",
    "white": "\033[37m", "black": "\033[30m", "reset": "\033[0m"
}

BG_COLORS = {
    "red": "\033[41m", "green": "\033[42m", "yellow": "\033[43m",
    "blue": "\033[44m", "magenta": "\033[45m", "cyan": "\033[46m",
    "white": "\033[47m", "black": "\033[40m", "none": ""
}

memory = {}
current_text_color = COLORS["reset"]
current_bg_color = ""
imported_libraries = []
plugins = {} 

def load_plugins():
    plugins.clear()
    engine_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_file = os.path.join(engine_dir, "Library", "plugins.txt")
    
    if not os.path.exists(plugin_file): return
    with codecs.open(plugin_file, 'r', 'utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if "=" in line and ":" in line and not line.startswith("//"):
                cmd_part, rest = line.split("=", 1)
                lib_part, file_part = rest.split(":", 1)
                plugins[cmd_part.strip()] = {"lib": lib_part.strip(), "file": file_part.strip()}

def parse_content(content):
    for var_name in sorted(memory.keys(), key=len, reverse=True):
        content = content.replace(f"Box.{var_name}", str(memory[var_name]))
    return content

def solve_math(expression):
    try:
        parsed_expr = parse_content(expression)
        clean_expr = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', parsed_expr)
        return str(eval(clean_expr))
    except: return "MATH_ERROR"

def check_condition(condition_str):
    try:
        parsed = parse_content(condition_str)
        match = re.search(r'["\']?(.*?)["\']?\s*(==|!=|>=|<=|>|<)\s*["\']?(.*?)["\']?$', parsed)
        if match:
            left, op, right = match.group(1).strip(), match.group(2), match.group(3).strip()
            if left.isdigit() and right.isdigit(): return eval(f"{left} {op} {right}")
            return eval(f"'{left}' {op} '{right}'")
        return False
    except: return False

def get_indent(line):
    return len(line) - len(line.lstrip())

def execute_line(line):
    global current_text_color, current_bg_color, imported_libraries
    line = line.strip()
    if not line or line.startswith("//"): return True

    import_match = re.search(r'^import\s*\(\s*["\']?(.*?)["\']?\s*\)', line, re.IGNORECASE)
    if import_match:
        lib_name = import_match.group(1).strip()
        if lib_name not in imported_libraries: imported_libraries.append(lib_name)
        return True

    call_match = re.search(r'^call\s*\(\s*["\']?(.*?)["\']?\s*\)', line, re.IGNORECASE)
    if call_match:
        lib_name = call_match.group(1).strip()
        if lib_name not in imported_libraries: return True
        engine_dir = os.path.dirname(os.path.abspath(__file__))
        lib_file = os.path.join(engine_dir, "Library", f"{lib_name}_library.py")
        if os.path.exists(lib_file):
            try: subprocess.run([sys.executable, lib_file])
            except: pass
        return True

    for cmd, info in plugins.items():
        pattern = fr'^Box\s*\.\s*["\']?(.*?)["\']?\s*=\s*{re.escape(cmd)}\s*\(\s*["\']?(.*?)["\']?\s*\)'
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            var_name = match.group(1).strip()
            arg = parse_content(match.group(2))
            engine_dir = os.path.dirname(os.path.abspath(__file__))
            veri_yolu = os.path.join(engine_dir, "Library-Data", info["file"])
            if arg:
                try:
                    if not os.path.exists(os.path.dirname(veri_yolu)): os.makedirs(os.path.dirname(veri_yolu))
                    with codecs.open(veri_yolu, 'w', 'utf-8') as f: f.write(arg)
                except: pass
            lib_file = os.path.join(engine_dir, "Library", f"{info['lib']}_library.py")
            if os.path.exists(lib_file):
                try: subprocess.run([sys.executable, lib_file])
                except: pass
            try:
                with codecs.open(veri_yolu, 'r', 'utf-8') as f: memory[var_name] = f.read().strip()
            except: memory[var_name] = "HATA"
            return True

    for cmd, info in plugins.items():
        pattern = fr'^{re.escape(cmd)}\s*\(\s*["\']?(.*?)["\']?\s*\)'
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            arg = parse_content(match.group(1))
            engine_dir = os.path.dirname(os.path.abspath(__file__))
            veri_yolu = os.path.join(engine_dir, "Library-Data", info["file"])
            try:
                if not os.path.exists(os.path.dirname(veri_yolu)): os.makedirs(os.path.dirname(veri_yolu))
                with codecs.open(veri_yolu, 'w', 'utf-8') as f: f.write(arg)
            except: pass
            lib_file = os.path.join(engine_dir, "Library", f"{info['lib']}_library.py")
            if os.path.exists(lib_file):
                try: subprocess.run([sys.executable, lib_file])
                except: pass
            return True

    write_match = re.search(r'^Write\s*\(\s*["\'](.*?)["\']\s*\+\s*["\'](.*?)["\']\s*\)', line, re.IGNORECASE)
    if write_match:
        file_path = parse_content(write_match.group(1))
        content = parse_content(write_match.group(2))
        try:
            with codecs.open(file_path, 'w', encoding='utf-8') as f: f.write(content)
        except: pass
        return True

    read_match = re.search(r'^Read\s*\(\s*Box\s*\.\s*["\'](.*?)["\']\s*=\s*["\'](.*?)["\']\s*\)', line, re.IGNORECASE)
    if read_match:
        var_name = read_match.group(1)
        file_path = parse_content(read_match.group(2))
        try:
            with codecs.open(file_path, 'r', encoding='utf-8') as f: memory[var_name] = f.read().strip()
        except: memory[var_name] = "HATA"
        return True

    print_match = re.search(r'Screen\.terminal\.text\s*\(\s*["\'](.*?)["\']\s*\)', line)
    if print_match:
        print(f"{current_bg_color}{current_text_color}{parse_content(print_match.group(1))}{COLORS['reset']}")
        return True

    input_match = re.search(r'input\s*\(\s*["\'](.*?)["\']\s*,\s*["\'](.*?)["\']\s*,\s*(True|False)\s*\)', line)
    if input_match:
        var_name, question = input_match.group(1), parse_content(input_match.group(2))
        prompt = f"{current_bg_color}{current_text_color}{question}{COLORS['reset']}"
        memory[var_name] = input(prompt + " ") if input_match.group(3) == "True" else input(prompt + "\n> ")
        return True

    math_match = re.search(r'Box\s*\.\s*["\'](.*?)["\']\s*=\s*Math\s*\(\s*(.*?)\s*\)', line)
    if math_match:
        memory[math_match.group(1)] = solve_math(math_match.group(2))
        return True

    # [DÜZELTİLDİ]: Box atamasında ismin etrafındaki tırnak işaretleri artık isteğe bağlı!
    box_match = re.search(r'Box\s*\.\s*["\']?(.*?)["\']?\s*=\s*["\'](.*?)["\']', line)
    if box_match:
        memory[box_match.group(1)] = box_match.group(2)
        return True

    tc_match = re.search(r'Screen\.terminal\.textcolor\s*\(\s*["\'](.*?)["\']\s*\)', line)
    if tc_match:
        current_text_color = COLORS.get(tc_match.group(1).lower(), COLORS["reset"])
        return True
    
    bg_match = re.search(r'Screen\.terminal\.backgroundcolor\s*\(\s*["\'](.*?)["\']\s*\)', line)
    if bg_match:
        current_bg_color = BG_COLORS.get(bg_match.group(1).lower(), "")
        return True

    wait_match = re.search(r'wait\.(millisecond|second|minute)\s*\(\s*(\d+)\s*\)', line)
    if wait_match:
        unit, val = wait_match.group(1), int(wait_match.group(2))
        time.sleep(val/1000.0 if unit == "millisecond" else val if unit == "second" else val*60)
        return True

    if "Screen.terminal.clear()" in line:
        os.system('cls' if os.name == 'nt' else 'clear')
        return True

    return False

def get_block_lines(all_lines, start_idx, base_indent):
    block_lines = []
    current_idx = start_idx
    total = len(all_lines)
    while current_idx < total:
        line = all_lines[current_idx]
        if not line.strip() or line.strip().startswith("//"):
            block_lines.append(line)
            current_idx += 1
            continue
        if get_indent(line) > base_indent:
            block_lines.append(line)
            current_idx += 1
        else:
            break
    return block_lines, current_idx

# [DÜZELTİLDİ]: Motor artık iç içe sınırsız If ve Döngü çalıştırabilen "Recursive" yapıya geçti!
def run_lines(raw_lines):
    idx = 0
    total_lines = len(raw_lines)
    if_chain_status = False 

    while idx < total_lines:
        line = raw_lines[idx]
        stripped = line.strip()
        
        if not stripped or stripped.startswith("//"):
            idx += 1
            continue

        base_indent = get_indent(line)

        if re.search(r'^Repeat\s+until\s*\((.*?)\)', stripped, re.IGNORECASE):
            condition_str = re.search(r'^Repeat\s+until\s*\((.*?)\)', stripped, re.IGNORECASE).group(1)
            block_lines, next_idx = get_block_lines(raw_lines, idx + 1, base_indent)
            while not check_condition(condition_str):
                run_lines(block_lines)
                if "MATH_ERROR" in memory.values(): break
            idx = next_idx
            continue

        if re.search(r'^If\s*\((.*?)\)', stripped, re.IGNORECASE):
            condition_str = re.search(r'^If\s*\((.*?)\)', stripped, re.IGNORECASE).group(1)
            if_chain_status = check_condition(condition_str)
            block_lines, next_idx = get_block_lines(raw_lines, idx + 1, base_indent)
            if if_chain_status: run_lines(block_lines)
            idx = next_idx
            continue

        if re.search(r'^Elif\s*\((.*?)\)', stripped, re.IGNORECASE):
            condition_str = re.search(r'^Elif\s*\((.*?)\)', stripped, re.IGNORECASE).group(1)
            block_lines, next_idx = get_block_lines(raw_lines, idx + 1, base_indent)
            if not if_chain_status and check_condition(condition_str):
                if_chain_status = True
                run_lines(block_lines)
            idx = next_idx
            continue

        if stripped.lower() == "else":
            block_lines, next_idx = get_block_lines(raw_lines, idx + 1, base_indent)
            if not if_chain_status: run_lines(block_lines)
            idx = next_idx
            if_chain_status = False
            continue

        if not execute_line(line):
            print(f"{COLORS['red']}[!] SÖZDİZİMİ HATASI: '{stripped}' geçerli bir MakPar komutu değil.{COLORS['reset']}")
        idx += 1

def execute_makpar(target_file):
    global imported_libraries
    imported_libraries = []
    if not os.path.exists(target_file): return
    with codecs.open(target_file, 'r', encoding='utf-8') as file:
        raw_lines = file.readlines()
    run_lines(raw_lines)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    load_plugins() 
    if len(sys.argv) > 1: execute_makpar(sys.argv[1])
    while True:
        if msvcrt.kbhit() and ord(msvcrt.getch()) == 24: break