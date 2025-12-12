#!/usr/bin/env python3
"""
Logistics Routing System - Setup Wizard
Helps users set up and run the application
"""

import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path


class SetupWizard:
    def __init__(self):
        self.os_type = platform.system()
        self.project_root = Path(__file__).parent
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if self.os_type == 'Windows' else 'clear')
    
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*50)
        print(f"  {text}")
        print("="*50 + "\n")
    
    def check_docker(self):
        """Check if Docker is installed"""
        try:
            subprocess.run(['docker', '--version'], capture_output=True, check=True)
            subprocess.run(['docker-compose', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def check_python(self):
        """Check Python version"""
        version = sys.version_info
        return version.major == 3 and version.minor >= 11
    
    def check_nodejs(self):
        """Check if Node.js is installed"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def check_postgresql(self):
        """Check if PostgreSQL is available"""
        try:
            subprocess.run(['psql', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def run_docker_mode(self):
        """Run with Docker Compose"""
        self.print_header("🐳 Docker Mode")
        print("Starting all services with Docker Compose...")
        print("\nServices will be available at:")
        print("  • Frontend: http://localhost:3000")
        print("  • API Docs: http://localhost:8000/docs")
        print("  • Database: localhost:5432")
        print("\nPress Enter to continue...")
        input()
        
        try:
            os.chdir(self.project_root)
            subprocess.run(['docker-compose', 'up'], check=False)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            subprocess.run(['docker-compose', 'down'], check=False)
        except Exception as e:
            print(f"Error: {e}")
    
    def run_manual_mode(self):
        """Run with manual setup"""
        self.print_header("💻 Manual Mode")
        
        # Install backend
        print("Installing backend dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
                          cwd=self.project_root, check=True)
            print("✓ Backend dependencies installed")
        except Exception as e:
            print(f"✗ Failed to install dependencies: {e}")
            return
        
        # Install frontend
        print("\nInstalling frontend dependencies...")
        try:
            subprocess.run(['npm', 'install', '-q'],
                          cwd=self.project_root / 'frontend', check=True)
            print("✓ Frontend dependencies installed")
        except Exception as e:
            print(f"✗ Failed to install frontend: {e}")
            return
        
        print("\n" + "="*50)
        print("  Services Starting")
        print("="*50)
        print("\nBackend will run on: http://localhost:8000")
        print("Frontend will run on: http://localhost:5173")
        print("API Docs: http://localhost:8000/docs")
        print("\nPress Enter to start services...")
        input()
        
        # Start services
        try:
            # Backend
            print("\nStarting Backend...")
            backend = subprocess.Popen(
                [sys.executable, '-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'],
                cwd=self.project_root
            )
            
            # Frontend
            print("Starting Frontend (this may take a moment)...")
            frontend = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=self.project_root / 'frontend'
            )
            
            print("\n✓ Services started!")
            print("  Opening browser in 5 seconds...")
            import time
            time.sleep(5)
            webbrowser.open('http://localhost:5173')
            
            # Wait for both
            backend.wait()
            frontend.wait()
            
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            try:
                backend.terminate()
                frontend.terminate()
            except:
                pass
        except Exception as e:
            print(f"Error: {e}")
    
    def main_menu(self):
        """Display main menu"""
        self.clear_screen()
        self.print_header("🚀 Logistics Route Planner Setup")
        
        print("Available startup modes:\n")
        
        # Check Docker
        docker_available = self.check_docker()
        if docker_available:
            print("✓ [1] DOCKER MODE (Recommended)")
            print("       - All services in containers")
            print("       - No local setup needed")
            print("       - Docker Desktop required\n")
        else:
            print("✗ [1] DOCKER MODE")
            print("       - Docker not installed\n")
        
        # Check Manual setup
        python_ok = self.check_python()
        nodejs_ok = self.check_nodejs()
        
        if python_ok and nodejs_ok:
            print("✓ [2] MANUAL MODE")
            print("       - Backend + Frontend locally")
            print("       - Full development setup\n")
        else:
            print("✗ [2] MANUAL MODE")
            if not python_ok:
                print("       - Python 3.11+ required")
            if not nodejs_ok:
                print("       - Node.js required\n")
        
        if not docker_available and not (python_ok and nodejs_ok):
            print("\n❌ ERROR: No startup method available")
            print("\nInstall one of:")
            print("  • Docker Desktop: https://docker.com/products/docker-desktop")
            print("  • Python 3.11: https://python.org")
            print("  • Node.js 18+: https://nodejs.org")
            return
        
        print("[0] EXIT\n")
        
        choice = input("Select mode (0-2): ").strip()
        
        if choice == '1':
            if docker_available:
                self.run_docker_mode()
            else:
                print("Docker not available")
                input("Press Enter to continue...")
        elif choice == '2':
            if python_ok and nodejs_ok:
                self.run_manual_mode()
            else:
                print("Manual mode requirements not met")
                input("Press Enter to continue...")
        elif choice == '0':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice")
            input("Press Enter to try again...")
            self.main_menu()
    
    def run(self):
        """Run the wizard"""
        try:
            while True:
                self.main_menu()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)


if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()