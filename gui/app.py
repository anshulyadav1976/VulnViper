import flet as ft
import os
import sys
import subprocess

# Adjust system path to include the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import load_config, save_config, CONFIG_PATH

def main(page: ft.Page):
    page.title = "VulnViper GUI"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK # Modern look
    page.scroll = ft.ScrollMode.AUTO # ADDED FOR PAGE SCROLLING

    # --- Helper to show snack bar ---
    def show_snackbar(message, color=ft.Colors.GREEN):
        # MODIFIED: Flet's way to show SnackBar
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            open=True,
            bgcolor=color
        )
        page.update() # Update the page to show the snackbar

    # --- Configuration Section ---
    # Load initial config, providing defaults for GUI fields if not set
    try:
        current_config = load_config()
    except RuntimeError: # Handles cases where API key or provider isn't set
        current_config = {} # Start with an empty config for the GUI

    api_key_field = ft.TextField(
        label="API Key",
        value=current_config.get("api_key", ""), # Use .get for safety
        password=True,
        can_reveal_password=True,
        width=400
    )
    llm_provider_dropdown = ft.Dropdown(
        label="LLM Provider",
        value=current_config.get("llm_provider", "openai"), # Default to openai if not found
        options=[
            ft.dropdown.Option("openai"),
            ft.dropdown.Option("gemini"),
        ],
        width=400
    )
    llm_model_field = ft.TextField(
        label="LLM Model (Optional)",
        value=current_config.get("llm_model", ""), # Use .get for safety
        hint_text="e.g., gpt-4o-mini, gemini-1.5-flash-latest",
        width=400
    )

    def save_configuration(e):
        try:
            save_config(
                api_key_field.value,
                llm_provider_dropdown.value,
                llm_model_field.value
            )
            show_snackbar(f"Configuration saved to {CONFIG_PATH}") # MODIFIED PATH VARIABLE
        except Exception as ex:
            show_snackbar(f"Error saving config: {ex}", ft.Colors.RED) # MODIFIED

    config_section = ft.Column(
        [
            ft.Text("LLM Configuration", size=20, weight=ft.FontWeight.BOLD),
            api_key_field,
            llm_provider_dropdown,
            llm_model_field,
            ft.ElevatedButton("Save Configuration", on_click=save_configuration, icon="save"),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    # --- Scanning Section ---
    target_dir_field = ft.TextField(label="Target Directory", value=".", width=300, read_only=True)
    output_file_field = ft.TextField(label="Output Report File", value="vulnviper_gui_report.md", width=300)
    scan_results_area = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    scan_progress_bar = ft.ProgressBar(width=400, visible=False)


    def pick_target_directory(e: ft.FilePickerResultEvent):
        if e.path:
            target_dir_field.value = e.path
            target_dir_field.update()
            show_snackbar(f"Selected directory: {e.path}")

    target_dir_picker = ft.FilePicker(on_result=pick_target_directory)
    # page.overlay.append(target_dir_picker) # This needs to be added for FilePicker to work.

    # Ensure FilePicker is added to overlay. It's good practice to do this once.
    # It's usually added to page.overlay in main(page) if it's going to be used.
    if target_dir_picker not in page.overlay:
        page.overlay.append(target_dir_picker)


    def run_scan_logic(e):
        if not api_key_field.value or not llm_provider_dropdown.value:
            show_snackbar("Please configure API Key and LLM Provider first.", ft.Colors.ORANGE) # MODIFIED
            return

        target_dir = target_dir_field.value
        output_file = output_file_field.value

        if not target_dir:
            show_snackbar("Target directory cannot be empty.", ft.Colors.RED) # MODIFIED
            return
        if not output_file:
            show_snackbar("Output file name cannot be empty.", ft.Colors.RED) # MODIFIED
            return
        
        scan_results_area.controls.clear()
        scan_results_area.controls.append(ft.Text(f"Starting scan for {target_dir}..."))
        scan_results_area.update()
        scan_progress_bar.visible = True
        page.update()

        try:
            # This is a simplified way to call the CLI's scan logic.
            # In a real app, you'd import and call functions directly.
            # For now, we'll use subprocess to call the CLI command.
            # This requires `vulnviper` to be installed and in PATH, or use `python -m cli`
            
            command = [
                sys.executable, # Use the current Python interpreter
                os.path.join(project_root, "cli.py"), # Path to cli.py
                "scan",
                "--dir", target_dir,
                "--out", output_file
            ]
            
            # Ensure environment variables are set for the subprocess if not using config file
            env = os.environ.copy()
            # Check if config exists, or if API key from GUI should be preferred
            # load_config in the main app already handles env vars.
            # The subprocess for cli.py will also use load_config which respects VULNVIPER_ env vars.
            # If the user saves the config through the GUI, cli.py will pick it up from ~/.vulnviper_config
            # If they don't save, but have entered values, we can pass them as env vars to the subprocess
            # This gives precedence to what's currently in the GUI fields if not saved yet.

            if api_key_field.value: # Pass GUI values as env vars to give them precedence for this run
                 env["VULNVIPER_API_KEY"] = api_key_field.value
            if llm_provider_dropdown.value:
                 env["VULNVIPER_LLM_PROVIDER"] = llm_provider_dropdown.value
            if llm_model_field.value:
                 env["VULNVIPER_LLM_MODEL"] = llm_model_field.value
            else: # If model field is empty, ensure it's not set in env for subprocess
                 if "VULNVIPER_LLM_MODEL" in env:
                     del env["VULNVIPER_LLM_MODEL"]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env, # Pass the environment
                cwd=project_root # Run from project root
            )

            def stream_output():
                if process.stdout:
                    for line in iter(process.stdout.readline, ''):
                        scan_results_area.controls.append(ft.Text(line.strip()))
                        scan_results_area.update()
                process.stdout.close()
                
                if process.stderr:
                    for line in iter(process.stderr.readline, ''):
                        scan_results_area.controls.append(ft.Text(line.strip(), color=ft.Colors.RED)) # MODIFIED
                        scan_results_area.update()
                    process.stderr.close()
                
                process.wait()
                scan_progress_bar.visible = False
                if process.returncode == 0:
                    show_snackbar(f"Scan complete! Report saved to {output_file}")
                else:
                    show_snackbar(f"Scan failed. Check output for details.", ft.Colors.RED) # MODIFIED
                page.update()

            # Run stream_output in a separate thread to keep UI responsive
            # MODIFIED: Use page.run_thread for Flet compatibility
            page.run_thread(stream_output)

        except Exception as ex:
            scan_results_area.controls.append(ft.Text(f"Error during scan: {ex}", color=ft.Colors.RED))
            scan_progress_bar.visible = False
            show_snackbar(f"Scan execution error: {ex}", ft.Colors.RED) # MODIFIED
            page.update()


    scan_button = ft.ElevatedButton(
        "Start Scan",
        on_click=run_scan_logic,
        icon="search",
        bgcolor=ft.Colors.BLUE_ACCENT,
        color=ft.Colors.WHITE
    )

    scan_section = ft.Column(
        [
            ft.Text("Security Scan", size=20, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    target_dir_field,
                    ft.IconButton(
                        icon="folder_open",
                        tooltip="Select Directory",
                        on_click=lambda _: target_dir_picker.get_directory_path(dialog_title="Select Project Directory")
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            output_file_field,
            scan_button,
            scan_progress_bar,
            ft.Text("Scan Output:", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=scan_results_area,
                border=ft.border.all(1, ft.Colors.OUTLINE), # MODIFIED
                border_radius=5,
                padding=10,
                height=300, # Fixed height for the scrollable area
                width=500,
                #expand=True # If you want it to take available space
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    # --- Main Layout ---
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    config_section,
                    ft.Divider(height=20, thickness=1),
                    scan_section,
                ],
                spacing=30,
                #scroll=ft.ScrollMode.AUTO # REMOVED: Page level scroll is added
            ),
            padding=20,
            #expand=True, # Make container take full space
            alignment=ft.alignment.top_center
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main) 