import os
import re
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Radiobutton, Label, Button, StringVar, LEFT, RIGHT, W
import pandas as pd

# --- GUI Functions ---

def get_radiance_folder():
    """Opens a dialog to ask the user for the Radiance results folder."""
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Radiance Results Folder")
    root.destroy()
    if not folder_path:
        messagebox.showinfo("Info", "No folder selected. Exiting.")
        return None
    return folder_path

def select_metric_from_list(metric_types):
    """Presents a dialog for the user to select a metric type."""
    if not metric_types:
        messagebox.showinfo("Info", "No .wpd files or metric types found in the folder.")
        return None

    dialog_root = tk.Tk()
    dialog_root.title("Select Metric Type")
    dialog_root.geometry("300x400")

    Label(dialog_root, text="Select the daylight metric to export:").pack(pady=10)
    var = StringVar(dialog_root)
    if metric_types:
        var.set(metric_types[0])

    for metric_type in metric_types:
        rb = Radiobutton(dialog_root, text=metric_type, variable=var, value=metric_type)
        rb.pack(anchor=W, padx=20)

    selected_metric = None
    def on_ok():
        nonlocal selected_metric
        selected_metric = var.get()
        dialog_root.destroy()
    def on_cancel():
        dialog_root.destroy()

    Button(dialog_root, text="OK", command=on_ok).pack(side=LEFT, padx=(20,10), pady=20)
    Button(dialog_root, text="Cancel", command=on_cancel).pack(side=RIGHT, padx=(10,20), pady=20)
    dialog_root.wait_window()

    if not selected_metric:
        messagebox.showinfo("Info", "No metric selected. Exiting.")
        return None
    return selected_metric

def select_area_type():
    """Presents a dialog for the user to select Full Area or AOI."""
    dialog_root = tk.Tk()
    dialog_root.title("Select Area Type")
    dialog_root.geometry("300x200")

    Label(dialog_root, text="Select statistics to extract:", justify=LEFT).pack(pady=10, padx=20, anchor=W)
    Label(dialog_root, text="(AOI stats depend on simulation setup)", font=('Helvetica', 8), justify=LEFT).pack(padx=20, anchor=W)

    var = StringVar(dialog_root)
    var.set("Full") # Default to Full Area

    Radiobutton(dialog_root, text="Full Area", variable=var, value="Full").pack(anchor=W, padx=40, pady=5)
    Radiobutton(dialog_root, text="Area Of Interest (AOI)", variable=var, value="AOI").pack(anchor=W, padx=40, pady=5)

    selected_area = None
    def on_ok():
        nonlocal selected_area
        selected_area = var.get()
        dialog_root.destroy()
    def on_cancel():
        dialog_root.destroy()

    Button(dialog_root, text="OK", command=on_ok).pack(side=LEFT, padx=(20,10), pady=20)
    Button(dialog_root, text="Cancel", command=on_cancel).pack(side=RIGHT, padx=(10,20), pady=20)
    dialog_root.wait_window()

    if not selected_area:
        messagebox.showinfo("Info", "No area type selected. Exiting.")
        return None
    return selected_area

# --- File Processing Functions ---

def get_available_metrics_from_files(folder_path):
    """Scans .wpd files in the folder to find unique metric types from filenames."""
    metric_types = set()
    if not os.path.isdir(folder_path):
        return list(metric_types)

    for filename in os.listdir(folder_path):
        if filename.endswith(".wpd"):
            parts = os.path.splitext(filename)[0].split('_')
            if len(parts) > 1:
                metric_types.add(parts[-1])
    return sorted(list(metric_types))

def parse_wpd_file(file_path, expected_metric_type_from_filename, area_choice):
    """
    Parses a single .wpd file, extracting stats for the chosen area type (Full/AOI).
    """
    results = []
    room_id = "Unknown"
    room_name_from_file = "Unknown"

    base_filename = os.path.basename(file_path)
    filename_parts = os.path.splitext(base_filename)[0].split('_')
    if len(filename_parts) > 0:
        room_id_from_filename = filename_parts[0]

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        current_sim_block_data = {}
        in_sim_block = False

        # Get Zone info
        for line in lines:
            line = line.strip()
            zone_match = re.match(r"\[Zone\]\s*\[(.*?)\]\s*(.*)", line)
            if zone_match:
                room_id = zone_match.group(1)
                room_name_from_file = zone_match.group(2).strip()
                break
        if room_id == "Unknown":
            room_id = room_id_from_filename

        # Process Sim blocks
        for line in lines:
            line = line.strip()

            if line.startswith("[Sim]"):
                in_sim_block = True
                current_sim_block_data = {
                    'Room ID': room_id,
                    'Room Name': room_name_from_file,
                    'File Metric Type': expected_metric_type_from_filename,
                    'Area Type': area_choice, # Store the requested type
                    'Metric Description': 'N/A',
                    'Min': 'N/A',
                    'Max': 'N/A',
                    'Average': 'N/A',
                    'MMA Values': 'N/A',
                    'Parse Status': 'OK' # To track issues like missing AOI
                }
                continue

            if in_sim_block:
                metric_desc_match = re.match(r"\[([A-Za-z0-9\s][^\]]*)\]\s*(.*)", line) # Slightly improved regex
                if metric_desc_match:
                    tag_content = metric_desc_match.group(1)
                    description_content = metric_desc_match.group(2).strip()
                    # Exclude known structural tags
                    known_tags = ["RADIANCE", "Date", "Geometry", "Location", "Zone", "Stat", "Sim", "XYZ", "NxNy", "Period", "Data", "MMA"]
                    if tag_content not in known_tags and description_content:
                        current_sim_block_data['Metric Description'] = f"[{tag_content}] {description_content}"

                if line.startswith("[MMA]"):
                    parts = line.replace("[MMA]", "").strip().split()
                    current_sim_block_data['MMA Values'] = " | ".join(parts) # Store all raw values

                    min_val, max_val, avg_val = 'N/A', 'N/A', 'N/A' # Default values

                    if area_choice == "Full":
                        if len(parts) >= 3:
                            try:
                                min_val = float(parts[0])
                                max_val = float(parts[1])
                                avg_val = float(parts[2])
                            except (ValueError, IndexError):
                                print(f"Warning: Could not parse Full Area MMA (first 3) in {base_filename}: {line}")
                                current_sim_block_data['Parse Status'] = 'MMA Parse Error (Full)'
                        else:
                             print(f"Warning: Not enough MMA values for Full Area in {base_filename}: {line}")
                             current_sim_block_data['Parse Status'] = 'MMA Too Short (Full)'

                    elif area_choice == "AOI":
                        if len(parts) >= 8: # Need at least 8 parts for indices 5, 6, 7
                            try:
                                min_val = float(parts[5])
                                max_val = float(parts[6])
                                avg_val = float(parts[7])
                            except (ValueError, IndexError):
                                print(f"Warning: Could not parse AOI MMA (values 6-8) in {base_filename}: {line}")
                                current_sim_block_data['Parse Status'] = 'MMA Parse Error (AOI)'
                        else:
                            print(f"Warning: AOI stats requested but not found (MMA line too short) in {base_filename}")
                            current_sim_block_data['Parse Status'] = 'AOI Stats Missing'
                            current_sim_block_data['Area Type'] = 'AOI (Not Found)' # Update area type status

                    # Assign parsed values
                    current_sim_block_data['Min'] = min_val
                    current_sim_block_data['Max'] = max_val
                    current_sim_block_data['Average'] = avg_val

                    results.append(current_sim_block_data.copy())
                    in_sim_block = False
                    current_sim_block_data = {} # Reset for next potential block

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        # Add a placeholder result indicating the file error
        results.append({
            'Room ID': room_id_from_filename, 'Room Name': 'File Error', 'File Metric Type': expected_metric_type_from_filename,
            'Area Type': area_choice, 'Metric Description': f'Error processing file: {e}',
            'Min': 'ERROR', 'Max': 'ERROR', 'Average': 'ERROR', 'MMA Values': 'ERROR', 'Parse Status': 'File Read Error'
        })
    return results

# --- Main Execution ---

def main():
    """Main function to orchestrate the process."""
    radiance_folder = get_radiance_folder()
    if not radiance_folder: return

    available_metrics = get_available_metrics_from_files(radiance_folder)
    if not available_metrics: return

    selected_metric_type = select_metric_from_list(available_metrics)
    if not selected_metric_type: return

    selected_area_type = select_area_type()
    if not selected_area_type: return

    all_room_stats = []
    file_count = 0
    print(f"\nProcessing files for Metric: '{selected_metric_type}', Area: '{selected_area_type}'...")
    for filename in os.listdir(radiance_folder):
        if filename.endswith(f"_{selected_metric_type}.wpd"):
            file_path = os.path.join(radiance_folder, filename)
            print(f"  Parsing: {filename}")
            file_stats = parse_wpd_file(file_path, selected_metric_type, selected_area_type)
            if file_stats:
                all_room_stats.extend(file_stats)
                file_count += 1

    if not all_room_stats:
        messagebox.showinfo("Info", f"No data extracted for metric '{selected_metric_type}' and area '{selected_area_type}'. Check files and settings.")
        return

    print(f"\nProcessed {file_count} files. Found {len(all_room_stats)} metric entries.")

    # Create and structure DataFrame
    df = pd.DataFrame(all_room_stats)
    cols_order = ['Room ID', 'Room Name', 'File Metric Type', 'Area Type', 'Metric Description', 'Min', 'Max', 'Average', 'Parse Status', 'MMA Values']
    for col in cols_order:
        if col not in df.columns:
            df[col] = 'N/A' # Add missing columns if any error occurred
    df = df[cols_order]

    # Ask for save location
    save_path_gui_root = tk.Tk()
    save_path_gui_root.withdraw()
    initial_filename = f"Daylight_Stats_{selected_metric_type}_{selected_area_type}.xlsx"
    excel_file_path = filedialog.asksaveasfilename(
        title="Save Excel File",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=initial_filename
    )
    save_path_gui_root.destroy()

    # Export to Excel
    if excel_file_path:
        try:
            df.to_excel(excel_file_path, index=False, sheet_name=f"{selected_metric_type}_{selected_area_type}"[:31]) # Sheet name limit is 31 chars
            messagebox.showinfo("Success", f"Stats exported to {excel_file_path}")
            print(f"\nStats successfully exported to {excel_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save Excel file: {e}")
            print(f"Error saving Excel file: {e}")
    else:
        messagebox.showinfo("Info", "Save operation cancelled.")

if __name__ == "__main__":
    main()