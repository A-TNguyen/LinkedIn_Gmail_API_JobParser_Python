import json
import importlib
import os

# Get the directory of the current file (parser_runner.py) to build robust paths.
_runner_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to get the project's root directory.
_project_root = os.path.dirname(_runner_dir)

def load_main_config():
    """Loads the main configuration file using an absolute path."""
    config_path = os.path.join(_project_root, 'config', 'main_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ CRITICAL: Main configuration file not found at {config_path}. Exiting.")
        return None
    except json.JSONDecodeError:
        print(f"❌ CRITICAL: Could not decode JSON from {config_path}. Check for syntax errors. Exiting.")
        return None

def run_enabled_parsers(service):
    """
    Loads and runs all parsers that are enabled in the main configuration file.
    
    This function acts as the master controller for the parsing process. It dynamically
    imports and executes the 'run' function from each enabled parser's 'processor.py' module.

    Args:
        service: The authenticated Gmail API service object.

    Returns:
        True if all parsers ran successfully, False otherwise.
    """
    main_config = load_main_config()
    if not main_config:
        return False
        
    enabled_parsers = main_config.get("enabled_parsers", [])
    if not enabled_parsers:
        print("⚠️ No parsers are enabled in config/main_config.json. Exiting.")
        return True

    print(f"✅ Enabled parsers: {', '.join(enabled_parsers)}")

    for parser_name in enabled_parsers:
        try:
            print(f"\n==================== Running Parser: {parser_name.upper()} ====================")
            # Dynamically import the processor module for the given parser
            parser_module = importlib.import_module(f"parsers.{parser_name}.processor")
            
            # Call the 'run' function from that module
            success = parser_module.run(service)
            if not success:
                print(f"❌ Parser '{parser_name}' reported a critical failure.")
                return False
            print(f"====================================================================")

        except ImportError:
            print(f"❌ CRITICAL: Could not find parser module for '{parser_name}'.")
            print(f"   Check that 'src/parsers/{parser_name}/processor.py' exists.")
            return False
        except Exception as e:
            print(f"❌ CRITICAL: An unexpected error occurred while running the '{parser_name}' parser: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    return True 