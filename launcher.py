#!/usr/bin/env python3
"""
Logistics Routing System - Desktop Launcher
Simple GUI application to start services and open browser
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import time
import threading
import os
import sys
import platform

class LogisticsLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Logistics Route Planner")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Store process references
        self.processes = []
        self.is_running = False
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="🚀 Logistics Route Planner",
            font=("Arial", 18, "bold"),
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Status indicator
        self.status_label = tk.Label(
            self.root,
            text="Status: Not Running",
            font=("Arial", 11),
            fg="#e74c3c"
        )
        self.status_label.pack(pady=5)
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(self.root, text="Select Mode", padding=10)
        mode_frame.pack(fill='x', padx=20, pady=10)
        
        self.mode_var = tk.StringVar(value="docker")
        
        ttk.Radiobutton(
            mode_frame,
            text="🐳 Docker (Recommended - All-in-one)",
            variable=self.mode_var,
            value="docker"
        ).pack(anchor='w', pady=5)
        
        ttk.Radiobutton(
            mode_frame,
            text="💻 Manual (Backend only - requires Node.js & PostgreSQL)",
            variable=self.mode_var,
            value="manual"
        ).pack(anchor='w', pady=5)
        
        # Info text
        info_text = tk.Text(self.root, height=6, width=60, wrap='word', bg='#ecf0f1')
        info_text.pack(padx=20, pady=10)
        info_text.insert('1.0', 
            "Docker Mode:\n"
            "✓ Starts everything automatically\n"
            "✓ No manual setup needed\n"
            "✓ Requires Docker Desktop\n\n"
            "Manual Mode:\n"
            "✓ Backend + Frontend on your machine\n"
            "✓ Requires Python, Node.js, PostgreSQL\n"
        )
        info_text.config(state='disabled')
        
        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=20, pady=15)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="▶ Start",
            command=self.start_services,
            width=20
        )
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_services,
            width=20,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5)
        
        self.open_btn = ttk.Button(
            button_frame,
            text="🌐 Open App",
            command=self.open_browser,
            width=20,
            state='disabled'
        )
        self.open_btn.pack(side='left', padx=5)
        
    def start_services(self):
        mode = self.mode_var.get()
        
        if not self.check_dependencies(mode):
            messagebox.showerror("Error", "Missing required dependencies. See message above.")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Status: Starting...", fg="#f39c12")
        
        # Run in thread to prevent UI freeze
        thread = threading.Thread(target=self._run_services, args=(mode,), daemon=True)
        thread.start()
    
    def _run_services(self, mode):
        try:
            if mode == "docker":
                self._run_docker()
            else:
                self._run_manual()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start services:\n{str(e)}")
            self.stop_services()
    
    def _run_docker(self):
        """Run with Docker Compose"""
        try:
            process = subprocess.Popen(
                ['docker-compose', 'up'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            
            self.status_label.config(text="Status: Running (Docker)", fg="#27ae60")
            self.open_btn.config(state='normal')
            
            # Wait for startup
            time.sleep(5)
            
            # Keep process alive
            process.wait()
            
        except FileNotFoundError:
            messagebox.showerror("Error", "Docker or docker-compose not found.\nPlease install Docker Desktop.")
            self.stop_services()
    
    def _run_manual(self):
        """Run backend and frontend manually"""
        try:
            # Start backend
            backend_process = subprocess.Popen(
                [sys.executable, '-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(backend_process)
            
            time.sleep(3)
            
            # Start frontend
            frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=os.path.join(os.getcwd(), 'frontend'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(frontend_process)
            
            self.status_label.config(text="Status: Running (Manual)", fg="#27ae60")
            self.open_btn.config(state='normal')
            
            # Wait for processes
            for proc in self.processes:
                proc.wait()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start services:\n{str(e)}")
            self.stop_services()
    
    def stop_services(self):
        """Stop all running services"""
        self.is_running = False
        
        for process in self.processes:
            try:
                if platform.system() == 'Windows':
                    process.terminate()
                else:
                    process.terminate()
                process.wait(timeout=5)
            except:
                pass
        
        self.processes.clear()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.open_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped", fg="#e74c3c")
        messagebox.showinfo("Success", "Services stopped.")
    
    def open_browser(self):
        """Open application in browser"""
        mode = self.mode_var.get()
        
        if mode == "docker":
            url = "http://localhost:3000"
        else:
            url = "http://localhost:5173"
        
        webbrowser.open(url)
        messagebox.showinfo("Opening", f"Opening {url} in your browser...")
    
    def check_dependencies(self, mode):
        """Check if required dependencies are installed"""
        if mode == "docker":
            if not self._command_exists("docker-compose"):
                messagebox.showerror(
                    "Missing Docker",
                    "Docker Compose is not installed.\n\n"
                    "Download Docker Desktop from:\n"
                    "https://www.docker.com/products/docker-desktop"
                )
                return False
        else:
            if not self._command_exists(sys.executable):
                messagebox.showerror("Error", "Python not found.")
                return False
            
            if not self._command_exists("npm"):
                messagebox.showerror(
                    "Missing Node.js",
                    "Node.js is not installed.\n\n"
                    "Download from:\n"
                    "https://nodejs.org/"
                )
                return False
        
        return True
    
    @staticmethod
    def _command_exists(command):
        """Check if a command exists on system"""
        if platform.system() == 'Windows':
            result = os.system(f'where {command} >nul 2>&1')
        else:
            result = os.system(f'command -v {command} >/dev/null 2>&1')
        return result == 0


if __name__ == "__main__":
    root = tk.Tk()
    app = LogisticsLauncher(root)
    root.mainloop()