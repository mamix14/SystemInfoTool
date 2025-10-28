#!/usr/bin/env python3
"""
System Information Tool with GUI - Similar to Speccy
Collects and displays detailed hardware information
"""

import platform
import psutil
from datetime import datetime
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

def get_size(bytes_val, suffix="B"):
    """Convert bytes to human-readable format"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_val < factor:
            return f"{bytes_val:.2f}{unit}{suffix}"
        bytes_val /= factor

class SystemInfoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Information Tool")
        self.root.geometry("900x700")
        
        # Initialize text_widgets dictionary FIRST
        self.text_widgets = {}
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="System Information Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_tab("Summary")
        self.create_tab("All Components")
        self.create_tab("CPU")
        self.create_tab("Memory")
        self.create_tab("GPU")
        self.create_tab("Storage")
        self.create_tab("Motherboard")
        self.create_tab("Network")
        self.create_tab("OS")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        # Scan button
        self.scan_button = ttk.Button(button_frame, text="Scan System", 
                                     command=self.start_scan)
        self.scan_button.grid(row=0, column=0, padx=5)
        
        # Export button
        self.export_button = ttk.Button(button_frame, text="Export to Text", 
                                       command=self.export_to_text)
        self.export_button.grid(row=0, column=1, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to scan", 
                                     foreground="blue")
        self.status_label.grid(row=3, column=0, pady=5)
        
    def create_tab(self, name):
        """Create a tab with a scrolled text widget"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=name)
        
        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, 
                                               font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widgets[name] = text_widget
        
    def update_tab(self, tab_name, content):
        """Update tab content"""
        if tab_name in self.text_widgets:
            widget = self.text_widgets[tab_name]
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.insert(1.0, content)
            widget.config(state=tk.DISABLED)
    
    def start_scan(self):
        """Start system scan in a separate thread"""
        self.scan_button.config(state=tk.DISABLED)
        self.status_label.config(text="Scanning system...", foreground="orange")
        
        # Clear all tabs
        for widget in self.text_widgets.values():
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.config(state=tk.DISABLED)
        
        # Run scan in thread to prevent GUI freezing
        thread = threading.Thread(target=self.scan_system, daemon=True)
        thread.start()
    
    def scan_system(self):
        """Perform system scan"""
        try:
            # Get all information
            os_info = self.get_os_info()
            cpu_info = self.get_cpu_info()
            memory_info = self.get_memory_info()
            gpu_info = self.get_gpu_info()
            storage_info = self.get_disk_info()
            motherboard_info = self.get_motherboard_info()
            network_info = self.get_network_info()
            
            # Get component names for summary
            components_summary = self.get_components_summary()
            
            # Create summary
            summary = f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            summary += f"System: {platform.system()} {platform.release()}\n"
            summary += f"Processor: {platform.processor()}\n"
            summary += f"CPU Cores: {psutil.cpu_count(logical=False)} Physical, {psutil.cpu_count(logical=True)} Logical\n"
            
            svmem = psutil.virtual_memory()
            summary += f"Total RAM: {get_size(svmem.total)}\n"
            
            partitions = psutil.disk_partitions()
            summary += f"Storage Devices: {len(partitions)}\n"
            
            summary += "\n" + "="*50 + "\n"
            summary += "Click other tabs for detailed information"
            
            # Update tabs
            self.root.after(0, self.update_tab, "Summary", summary)
            self.root.after(0, self.update_tab, "All Components", components_summary)
            self.root.after(0, self.update_tab, "CPU", cpu_info)
            self.root.after(0, self.update_tab, "Memory", memory_info)
            self.root.after(0, self.update_tab, "GPU", gpu_info)
            self.root.after(0, self.update_tab, "Storage", storage_info)
            self.root.after(0, self.update_tab, "Motherboard", motherboard_info)
            self.root.after(0, self.update_tab, "Network", network_info)
            self.root.after(0, self.update_tab, "OS", os_info)
            
            self.root.after(0, self.scan_complete)
            
        except Exception as e:
            error_msg = f"Error during scan: {str(e)}"
            self.root.after(0, self.status_label.config, 
                          {"text": error_msg, "foreground": "red"})
            self.root.after(0, self.scan_button.config, {"state": tk.NORMAL})
    
    def scan_complete(self):
        """Called when scan is complete"""
        self.status_label.config(text="Scan complete!", foreground="green")
        self.scan_button.config(state=tk.NORMAL)
    
    def get_components_summary(self):
        """Get a clean summary of all component names"""
        info = "ALL COMPONENTS - QUICK OVERVIEW\n"
        info += "="*60 + "\n\n"
        
        # CPU
        info += "┌─ PROCESSOR\n"
        info += "│\n"
        cpu_name = "Unknown"
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
                winreg.CloseKey(key)
            except:
                cpu_name = platform.processor()
        else:
            cpu_name = platform.processor()
        
        info += f"└─ {cpu_name}\n"
        info += f"   • Cores: {psutil.cpu_count(logical=False)} Physical / {psutil.cpu_count(logical=True)} Logical\n"
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            info += f"   • Frequency: {cpu_freq.max:.0f} MHz\n"
        info += "\n"
        
        # GPU
        info += "┌─ GRAPHICS CARD(S)\n"
        info += "│\n"
        
        gpu_found = False
        
        # Try nvidia-smi
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    info += f"└─ {line.strip()}\n"
                    gpu_found = True
        except:
            pass
        
        # Windows GPU
        if platform.system() == "Windows":
            try:
                ps_command = 'Get-CimInstance Win32_VideoController | Select-Object Name | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        gpu_data = json.loads(result.stdout)
                        if isinstance(gpu_data, dict):
                            gpu_data = [gpu_data]
                        
                        for gpu in gpu_data:
                            name = gpu.get('Name', '').strip()
                            if name:
                                info += f"└─ {name}\n"
                                gpu_found = True
                    except:
                        pass
            except:
                pass
        
        if not gpu_found:
            info += "└─ No GPU detected\n"
        
        info += "\n"
        
        # RAM
        info += "┌─ MEMORY (RAM)\n"
        info += "│\n"
        svmem = psutil.virtual_memory()
        info += f"└─ Total: {get_size(svmem.total)}\n"
        
        if platform.system() == "Windows":
            try:
                ps_command = 'Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, PartNumber, Capacity, Speed | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        ram_data = json.loads(result.stdout)
                        if isinstance(ram_data, dict):
                            ram_data = [ram_data]
                        
                        for i, module in enumerate(ram_data, 1):
                            manufacturer = module.get('Manufacturer', '').strip()
                            part_number = module.get('PartNumber', '').strip()
                            capacity = module.get('Capacity')
                            speed = module.get('Speed')
                            
                            if capacity:
                                module_str = f"   • Module {i}: {get_size(int(capacity))}"
                                if speed:
                                    module_str += f" @ {speed}MHz"
                                if manufacturer and manufacturer != 'Unknown':
                                    module_str += f" ({manufacturer}"
                                    if part_number:
                                        module_str += f" {part_number}"
                                    module_str += ")"
                                info += module_str + "\n"
                    except:
                        pass
            except:
                pass
        
        info += "\n"
        
        # Motherboard
        info += "┌─ MOTHERBOARD\n"
        info += "│\n"
        
        if platform.system() == "Windows":
            try:
                ps_command = 'Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        mobo_data = json.loads(result.stdout)
                        manufacturer = mobo_data.get('Manufacturer', '').strip()
                        product = mobo_data.get('Product', '').strip()
                        
                        if manufacturer or product:
                            mobo_name = f"{manufacturer} {product}".strip()
                            info += f"└─ {mobo_name}\n"
                        else:
                            info += "└─ Unknown motherboard\n"
                    except:
                        info += "└─ Unknown motherboard\n"
                else:
                    info += "└─ Unknown motherboard\n"
            except:
                info += "└─ Unknown motherboard\n"
        else:
            info += "└─ Motherboard info not available\n"
        
        info += "\n"
        
        # Storage
        info += "┌─ STORAGE DEVICES\n"
        info += "│\n"
        
        if platform.system() == "Windows":
            try:
                ps_command = 'Get-CimInstance Win32_DiskDrive | Select-Object Model, Size | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        disk_data = json.loads(result.stdout)
                        if isinstance(disk_data, dict):
                            disk_data = [disk_data]
                        
                        for disk in disk_data:
                            model = disk.get('Model', '').strip()
                            size = disk.get('Size')
                            
                            if model:
                                disk_str = f"└─ {model}"
                                if size:
                                    disk_str += f" ({get_size(int(size))})"
                                info += disk_str + "\n"
                    except:
                        pass
            except:
                pass
        
        partitions = psutil.disk_partitions()
        total_storage = 0
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_storage += usage.total
            except:
                pass
        
        if total_storage > 0:
            info += f"   • Total Storage: {get_size(total_storage)}\n"
        
        info += "\n"
        
        # OS
        info += "┌─ OPERATING SYSTEM\n"
        info += "│\n"
        uname = platform.uname()
        info += f"└─ {uname.system} {uname.release}\n"
        info += f"   • Version: {uname.version}\n"
        
        info += "\n" + "="*60 + "\n"
        info += "\n💡 Click other tabs for detailed specifications"
        
        return info
    
    def get_cpu_info(self):
        """Get CPU information"""
        info = "CPU INFORMATION\n"
        info += "="*50 + "\n\n"
        
        # Get detailed CPU name on Windows - try multiple methods
        cpu_name = "Unknown CPU"
        
        if platform.system() == "Windows":
            # Method 1: Try registry (most reliable)
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
                winreg.CloseKey(key)
            except:
                # Method 2: Try WMIC
                try:
                    result = subprocess.run(
                        ['wmic', 'cpu', 'get', 'name'],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            cpu_name = lines[1].strip()
                except:
                    # Method 3: Fallback to platform
                    cpu_name = platform.processor()
        else:
            cpu_name = platform.processor()
        
        info += f"Processor: {cpu_name}\n"
        info += f"Architecture: {platform.machine()}\n"
        info += f"Physical Cores: {psutil.cpu_count(logical=False)}\n"
        info += f"Total Cores: {psutil.cpu_count(logical=True)}\n\n"
        
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            info += f"Max Frequency: {cpu_freq.max:.2f} MHz\n"
            info += f"Min Frequency: {cpu_freq.min:.2f} MHz\n"
            info += f"Current Frequency: {cpu_freq.current:.2f} MHz\n\n"
        
        info += "CPU Usage Per Core:\n"
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            info += f"  Core {i}: {percentage}%\n"
        
        info += f"\nTotal CPU Usage: {psutil.cpu_percent()}%\n"
        
        return info
    
    def get_memory_info(self):
        """Get memory information"""
        info = "MEMORY INFORMATION\n"
        info += "="*50 + "\n\n"
        
        svmem = psutil.virtual_memory()
        info += f"Total RAM: {get_size(svmem.total)}\n"
        info += f"Available: {get_size(svmem.available)}\n"
        info += f"Used: {get_size(svmem.used)} ({svmem.percent}%)\n"
        info += f"Free: {get_size(svmem.free)}\n"
        
        # Get detailed RAM info on Windows
        if platform.system() == "Windows":
            info += "\n" + "="*50 + "\n"
            info += "RAM MODULES:\n"
            info += "="*50 + "\n\n"
            
            try:
                # Use PowerShell for better compatibility
                ps_command = 'Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, PartNumber, Capacity, Speed, DeviceLocator | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        ram_data = json.loads(result.stdout)
                        
                        # Handle single module (not a list)
                        if isinstance(ram_data, dict):
                            ram_data = [ram_data]
                        
                        for i, module in enumerate(ram_data, 1):
                            info += f"Module {i}:\n"
                            
                            capacity = module.get('Capacity')
                            if capacity:
                                info += f"  Capacity: {get_size(int(capacity))}\n"
                            
                            manufacturer = module.get('Manufacturer', '').strip()
                            if manufacturer:
                                info += f"  Manufacturer: {manufacturer}\n"
                            
                            part_number = module.get('PartNumber', '').strip()
                            if part_number:
                                info += f"  Part Number: {part_number}\n"
                            
                            speed = module.get('Speed')
                            if speed:
                                info += f"  Speed: {speed} MHz\n"
                            
                            device_locator = module.get('DeviceLocator', '').strip()
                            if device_locator:
                                info += f"  Slot: {device_locator}\n"
                            
                            info += "\n"
                    except json.JSONDecodeError:
                        info += "Could not parse RAM module information\n\n"
                else:
                    # Fallback to WMIC if PowerShell fails
                    try:
                        result = subprocess.run(
                            ['wmic', 'memorychip', 'get', 'capacity,speed,manufacturer,partnumber,devicelocator'],
                            capture_output=True, text=True, timeout=5, 
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        if result.returncode == 0 and result.stdout.strip():
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                # Parse header
                                header_line = lines[0]
                                
                                module_num = 1
                                for line in lines[1:]:
                                    line = line.strip()
                                    if line:
                                        parts = line.split()
                                        if len(parts) >= 2 and parts[0].isdigit():
                                            capacity = int(parts[0])
                                            if capacity > 0:
                                                info += f"Module {module_num}:\n"
                                                info += f"  Capacity: {get_size(capacity)}\n"
                                                
                                                if len(parts) >= 2:
                                                    info += f"  Speed: {parts[1]} MHz\n"
                                                if len(parts) >= 3:
                                                    info += f"  Manufacturer: {parts[2]}\n"
                                                if len(parts) >= 4:
                                                    info += f"  Part Number: {' '.join(parts[3:])}\n"
                                                
                                                info += "\n"
                                                module_num += 1
                        else:
                            info += "RAM module details unavailable\n\n"
                    except Exception as e:
                        info += f"RAM module details unavailable: {str(e)}\n\n"
                        
            except Exception as e:
                info += f"Detailed RAM info unavailable: {str(e)}\n\n"
        
        swap = psutil.swap_memory()
        info += "\nSwap Memory:\n"
        info += f"  Total: {get_size(swap.total)}\n"
        info += f"  Used: {get_size(swap.used)} ({swap.percent}%)\n"
        info += f"  Free: {get_size(swap.free)}\n"
        
        return info
    
    def get_gpu_info(self):
        """Get GPU information"""
        info = "GPU INFORMATION\n"
        info += "="*50 + "\n\n"
        
        gpu_found = False
        
        # Try nvidia-smi
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,driver_version,temperature.gpu,memory.total,memory.used,memory.free,utilization.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_found = True
                info += "NVIDIA GPU(s):\n\n"
                for i, line in enumerate(result.stdout.strip().split('\n')):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 7:
                        info += f"GPU {i}: {parts[0]}\n"
                        info += f"  Driver Version: {parts[1]}\n"
                        info += f"  Temperature: {parts[2]}°C\n"
                        info += f"  Memory Total: {parts[3]} MB\n"
                        info += f"  Memory Used: {parts[4]} MB\n"
                        info += f"  Memory Free: {parts[5]} MB\n"
                        info += f"  GPU Utilization: {parts[6]}%\n\n"
        except:
            pass
        
        # Windows WMIC
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ['wmic', 'path', 'win32_videocontroller', 'get', 
                     'name,driverversion,adapterram', '/format:list'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    if not gpu_found:
                        info += "Detected GPU(s):\n\n"
                    
                    current_gpu = {}
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if value:
                                current_gpu[key] = value
                        elif current_gpu and 'Name' in current_gpu:
                            info += f"{current_gpu.get('Name', 'Unknown')}\n"
                            if 'DriverVersion' in current_gpu:
                                info += f"  Driver: {current_gpu['DriverVersion']}\n"
                            if 'AdapterRAM' in current_gpu:
                                try:
                                    ram = int(current_gpu['AdapterRAM'])
                                    info += f"  Memory: {get_size(ram)}\n"
                                except:
                                    pass
                            info += "\n"
                            current_gpu = {}
                            gpu_found = True
            except:
                pass
        
        if not gpu_found:
            info += "No GPU information available\n"
        
        return info
    
    def get_disk_info(self):
        """Get storage information"""
        info = "STORAGE INFORMATION\n"
        info += "="*50 + "\n\n"
        
        partitions = psutil.disk_partitions()
        for partition in partitions:
            info += f"Device: {partition.device}\n"
            info += f"  Mountpoint: {partition.mountpoint}\n"
            info += f"  File System: {partition.fstype}\n"
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info += f"  Total: {get_size(usage.total)}\n"
                info += f"  Used: {get_size(usage.used)} ({usage.percent}%)\n"
                info += f"  Free: {get_size(usage.free)}\n"
            except:
                info += "  (Permission denied)\n"
            info += "\n"
        
        disk_io = psutil.disk_io_counters()
        if disk_io:
            info += "Total Disk I/O:\n"
            info += f"  Read: {get_size(disk_io.read_bytes)}\n"
            info += f"  Written: {get_size(disk_io.write_bytes)}\n\n"
        
        # Physical disks on Windows
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ['wmic', 'diskdrive', 'get', 'model,size,interfacetype', '/format:list'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    info += "Physical Disks:\n"
                    current_disk = {}
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if value:
                                current_disk[key] = value
                        elif current_disk and 'Model' in current_disk:
                            info += f"\n  {current_disk.get('Model', 'Unknown')}\n"
                            if 'Size' in current_disk:
                                try:
                                    size = int(current_disk['Size'])
                                    info += f"    Capacity: {get_size(size)}\n"
                                except:
                                    pass
                            if 'InterfaceType' in current_disk:
                                info += f"    Interface: {current_disk['InterfaceType']}\n"
                            current_disk = {}
            except:
                pass
        
        return info
    
    def get_motherboard_info(self):
        """Get motherboard information"""
        info = "MOTHERBOARD INFORMATION\n"
        info += "="*50 + "\n\n"
        
        if platform.system() == "Windows":
            try:
                # Use PowerShell for motherboard info
                ps_command = 'Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, Version, SerialNumber | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        mobo_data = json.loads(result.stdout)
                        
                        manufacturer = mobo_data.get('Manufacturer', '').strip()
                        if manufacturer:
                            info += f"Manufacturer: {manufacturer}\n"
                        
                        product = mobo_data.get('Product', '').strip()
                        if product:
                            info += f"Model: {product}\n"
                        
                        version = mobo_data.get('Version', '').strip()
                        if version:
                            info += f"Version: {version}\n"
                        
                        serial = mobo_data.get('SerialNumber', '').strip()
                        if serial and serial != 'Default string':
                            info += f"Serial Number: {serial}\n"
                            
                    except json.JSONDecodeError:
                        info += "Could not parse motherboard information\n"
                else:
                    info += "Motherboard information unavailable\n"
                
                # Get BIOS info
                info += "\n" + "-"*50 + "\n"
                info += "BIOS Information:\n"
                info += "-"*50 + "\n\n"
                
                ps_command = 'Get-CimInstance Win32_BIOS | Select-Object Manufacturer, Name, Version, ReleaseDate | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        bios_data = json.loads(result.stdout)
                        
                        manufacturer = bios_data.get('Manufacturer', '').strip()
                        if manufacturer:
                            info += f"Manufacturer: {manufacturer}\n"
                        
                        name = bios_data.get('Name', '').strip()
                        if name:
                            info += f"Name: {name}\n"
                        
                        version = bios_data.get('Version', '').strip()
                        if version:
                            info += f"Version: {version}\n"
                        
                        release_date = bios_data.get('ReleaseDate', '').strip()
                        if release_date:
                            # Parse date
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                                info += f"Release Date: {dt.strftime('%Y-%m-%d')}\n"
                            except:
                                info += f"Release Date: {release_date}\n"
                                
                    except json.JSONDecodeError:
                        info += "Could not parse BIOS information\n"
                else:
                    info += "BIOS information unavailable\n"
                        
            except Exception as e:
                info += f"Unavailable: {str(e)}\n"
        elif platform.system() == "Linux":
            try:
                with open('/sys/devices/virtual/dmi/id/board_vendor') as f:
                    info += f"Manufacturer: {f.read().strip()}\n"
                with open('/sys/devices/virtual/dmi/id/board_name') as f:
                    info += f"Product: {f.read().strip()}\n"
                with open('/sys/devices/virtual/dmi/id/board_version') as f:
                    info += f"Version: {f.read().strip()}\n"
            except:
                info += "Unavailable (may need root)\n"
        else:
            info += "Not available on this platform\n"
        
        # Temperature sensors
        info += "\n" + "="*50 + "\n"
        info += "TEMPERATURE SENSORS\n"
        info += "="*50 + "\n\n"
        
        temp_found = False
        
        # Try psutil first (works on Linux)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                temp_found = True
                for name, entries in temps.items():
                    info += f"{name}:\n"
                    for entry in entries:
                        label = entry.label or 'Sensor'
                        info += f"  {label}: {entry.current}°C"
                        if entry.high:
                            info += f" (High: {entry.high}°C)"
                        if entry.critical:
                            info += f" (Critical: {entry.critical}°C)"
                        info += "\n"
                    info += "\n"
        except:
            pass
        
        # On Windows, try to get CPU temp via PowerShell WMI
        if platform.system() == "Windows" and not temp_found:
            try:
                # Try to get CPU temperature from WMI (works on some systems)
                ps_command = 'Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature | Select-Object CurrentTemperature | ConvertTo-Json'
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True, text=True, timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip() and 'CurrentTemperature' in result.stdout:
                    import json
                    try:
                        temp_data = json.loads(result.stdout)
                        if isinstance(temp_data, list):
                            temp_data = temp_data[0] if temp_data else {}
                        
                        if 'CurrentTemperature' in temp_data:
                            # Convert from tenths of Kelvin to Celsius
                            temp_kelvin = temp_data['CurrentTemperature'] / 10
                            temp_celsius = temp_kelvin - 273.15
                            info += f"CPU Temperature: {temp_celsius:.1f}°C\n\n"
                            temp_found = True
                    except:
                        pass
            except:
                pass
        
        if not temp_found:
            info += "Temperature sensors not available.\n"
            info += "\nNote: Windows does not expose temperature sensors through standard APIs.\n"
            info += "For temperature monitoring on Windows, use:\n"
            info += "  - HWMonitor (https://www.cpuid.com/softwares/hwmonitor.html)\n"
            info += "  - Core Temp (https://www.alcpu.com/CoreTemp/)\n"
            info += "  - Open Hardware Monitor (https://openhardwaremonitor.org/)\n\n"
        
        # Battery info
        info += "\n" + "="*50 + "\n"
        info += "POWER / BATTERY\n"
        info += "="*50 + "\n\n"
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                info += f"Battery: {battery.percent}%\n"
                info += f"Power Plugged: {'Yes' if battery.power_plugged else 'No'}\n"
                if not battery.power_plugged:
                    secs = battery.secsleft
                    if secs not in [psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN]:
                        h = secs // 3600
                        m = (secs % 3600) // 60
                        info += f"Time Remaining: {h}h {m}m\n"
            else:
                info += "No battery (desktop system)\n"
        except:
            info += "Battery info unavailable\n"
        
        return info
    
    def get_network_info(self):
        """Get network information"""
        info = "NETWORK INFORMATION\n"
        info += "="*50 + "\n\n"
        
        if_addrs = psutil.net_if_addrs()
        for interface, addrs in if_addrs.items():
            info += f"{interface}:\n"
            for addr in addrs:
                try:
                    if addr.family.name == 'AF_INET':
                        info += f"  IPv4: {addr.address}\n"
                        info += f"  Netmask: {addr.netmask}\n"
                    elif addr.family.name == 'AF_INET6':
                        info += f"  IPv6: {addr.address}\n"
                except:
                    pass
            info += "\n"
        
        net_io = psutil.net_io_counters()
        info += "Total Network I/O:\n"
        info += f"  Sent: {get_size(net_io.bytes_sent)}\n"
        info += f"  Received: {get_size(net_io.bytes_recv)}\n"
        
        return info
    
    def get_os_info(self):
        """Get OS information"""
        info = "OPERATING SYSTEM\n"
        info += "="*50 + "\n\n"
        
        uname = platform.uname()
        info += f"System: {uname.system}\n"
        info += f"Node Name: {uname.node}\n"
        info += f"Release: {uname.release}\n"
        info += f"Version: {uname.version}\n"
        info += f"Machine: {uname.machine}\n"
        info += f"Processor: {uname.processor}\n\n"
        
        boot_time = psutil.boot_time()
        boot_dt = datetime.fromtimestamp(boot_time)
        info += f"Boot Time: {boot_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return info
    
    def export_to_text(self):
        """Export all information to a text file"""
        filename = f"system_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for tab_name, widget in self.text_widgets.items():
                    f.write(f"\n{'='*60}\n")
                    f.write(f"{tab_name.upper()}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(widget.get(1.0, tk.END))
                    f.write("\n")
            
            self.status_label.config(text=f"Exported to {filename}", 
                                   foreground="green")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {str(e)}", 
                                   foreground="red")

def main():
    root = tk.Tk()
    app = SystemInfoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
