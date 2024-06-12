import psutil
import datetime
import pandas as pd

def get_system_stats():
    # Get CPU usage percentage
    cpu_usage = psutil.cpu_percent(interval=4)

    # Get memory usage information
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / (1024 ** 2)  # Convert bytes to MB
    available_memory = memory_info.available / (1024 ** 2)  # Convert bytes to MB
    used_memory = memory_info.used / (1024 ** 2)  # Convert bytes to MB
    memory_usage_percent = memory_info.percent

    return cpu_usage, total_memory, available_memory, used_memory, memory_usage_percent

def write_stats_to_file(file_path):
    cpu_usage, total_memory, available_memory, used_memory, memory_usage_percent = get_system_stats()

    # Get the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the content to write
    content = f"""
    System Resource Usage Report: {current_time}: CPU Usage: {cpu_usage}% | Total Memory: {total_memory:.2f} MB | Available Memory: {available_memory:.2f} MB | Used Memory: {used_memory:.2f} MB | Memory Usage: {memory_usage_percent}%"""
    print(f'\n\nTime: {current_time}')
    print(f'CPU Usage: {cpu_usage}%')
    print(f'Available Memory: {available_memory:.2f} MB')
    print(f'Memory Usage: {memory_usage_percent}%')
    print('----------------------------------------\n\n')
    # Write the content to the file
    with open(file_path, 'a') as file:
        file.write(content + "")
        # file.write("----------------------------------------\n")
        
    # Existing Excel file
    existing_file = 'check_server_status_output.xlsx'
    # New data to append
    new_data = {'Time':[current_time], 'CPU Usage': [cpu_usage], 'Total Memory (MB)': [total_memory], 'Available Memory (MB)': [available_memory], 'Used Memory (MB)': [used_memory], 'Memory Usage (%)': [memory_usage_percent]}
    df_new = pd.DataFrame(new_data)
    # Read existing data
    df_existing = pd.read_excel(existing_file)
    # Append new data
    df_combined = df_existing._append(df_new, ignore_index=True)
    # Save the combined data to Excel
    df_combined.to_excel(existing_file, index=False)


# Specify the file path
file_path = 'check_server_status_output.txt'

# Write stats to the file
write_stats_to_file(file_path)
#print(f"System stats have been written to {file_path}")
