import sys
import os
from pathlib import Path
import subprocess
import json
import threading
import queue
from typing import Optional, Dict, Any
import signal
import torch

class TerminalInterface:
    def __init__(self, model, tokenizer, command_queue: queue.Queue):
        self.model = model
        self.tokenizer = tokenizer
        self.command_queue = command_queue
        self.running = True
        self.last_context = {}
        
    def start(self):
        """Start the terminal interface."""
        print("CyberLab Assistant Terminal Interface")
        print("Type your commands in natural language. Type 'exit' to quit.")
        print("-" * 50)
        
        # Start command processor thread
        processor_thread = threading.Thread(target=self._process_commands)
        processor_thread.daemon = True
        processor_thread.start()
        
        try:
            while self.running:
                try:
                    # Get user input
                    user_input = input("🔒 > ")
                    
                    if user_input.lower() in ['exit', 'quit']:
                        self.running = False
                        break
                    
                    # Add command to processing queue
                    self.command_queue.put(user_input)
                    
                except KeyboardInterrupt:
                    self.running = False
                    break
                except EOFError:
                    self.running = False
                    break
        finally:
            print("\nShutting down terminal interface...")
            self.running = False
    
    def _process_commands(self):
        """Process commands from the queue."""
        while self.running:
            try:
                # Get command from queue with timeout
                command = self.command_queue.get(timeout=1.0)
                
                try:
                    # Process the command
                    self._handle_command(command)
                except Exception as e:
                    print(f"Error processing command: {str(e)}")
                
                self.command_queue.task_done()
            except queue.Empty:
                continue
    
    def _handle_command(self, command: str):
        """Handle a natural language command."""
        # Get current system context
        context = self._get_system_context()
        
        # Prepare input for model
        input_text = json.dumps({
            "command": command,
            "context": context,
            "last_context": self.last_context
        })
        
        # Tokenize input
        tokens = self.tokenizer.encode(input_text)
        
        # Get model prediction
        with torch.no_grad():
            output = self.model.forward(torch.tensor([tokens]))
            response = self.tokenizer.decode(output.argmax(dim=-1).tolist()[0])
        
        try:
            # Parse response
            action = json.loads(response)
            
            if "command" in action:
                # Execute system command
                self._execute_command(action["command"])
            elif "analysis" in action:
                # Display analysis
                self._display_analysis(action["analysis"])
            else:
                print("Unsupported action type")
                
        except json.JSONDecodeError:
            print("Error: Invalid response format")
        
        # Update last context
        self.last_context = context
    
    def _get_system_context(self) -> Dict[str, Any]:
        """Get current system context."""
        context = {
            "os": os.name,
            "platform": sys.platform,
            "cwd": os.getcwd(),
            "env": dict(os.environ)
        }
        
        # Add system-specific information
        if sys.platform == "win32":
            # Windows-specific context
            context.update({
                "windows_version": sys.getwindowsversion()._asdict()
            })
        else:
            # Unix-like system context
            try:
                context.update({
                    "uname": os.uname()._asdict()
                })
            except AttributeError:
                pass
        
        return context
    
    def _execute_command(self, command: str):
        """Execute a system command."""
        try:
            # Run command and capture output
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # Get return code
            return_code = process.poll()
            
            if return_code != 0:
                # Print error if command failed
                error = process.stderr.read()
                print(f"Error (code {return_code}):")
                print(error)
                
        except subprocess.SubprocessError as e:
            print(f"Failed to execute command: {str(e)}")
    
    def _display_analysis(self, analysis: Dict[str, Any]):
        """Display analysis results."""
        print("\nAnalysis Results:")
        print("-" * 20)
        
        if "command" in analysis:
            print(f"Command: {analysis['command']}")
        
        if "explanation" in analysis:
            print(f"\nExplanation:")
            print(analysis["explanation"])
        
        if "recommendations" in analysis:
            print("\nRecommendations:")
            for rec in analysis["recommendations"]:
                print(f"- {rec}")
        
        print("-" * 20)

def main():
    import torch
    from slm.cyberlab.model import CyberLabSLM
    from slm.cyberlab.preprocessing import TokenizerWrapper
    import yaml
    
    # Load configuration
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    tokenizer = TokenizerWrapper(config['tokenizer']['model_path'])
    model = CyberLabSLM(vocab_size=tokenizer.vocab_size, **config['model'])
    
    # Load model weights
    model_path = Path(config['model']['weights_path'])
    if model_path.exists():
        model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Create command queue
    command_queue = queue.Queue()
    
    # Create and start terminal interface
    terminal = TerminalInterface(model, tokenizer, command_queue)
    
    def signal_handler(signum, frame):
        print("\nReceived shutdown signal...")
        terminal.running = False
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start interface
    terminal.start()

if __name__ == "__main__":
    main()
