import os

# Function to rename multiple files
def rename_files(path, old_string, new_string, cnd = ''):
    for filename in os.listdir(path):
        # Get the full path of the file
        file_path = os.path.join(path, filename)
        # Check if the path is a file
        if os.path.isfile(file_path):
            #filter only the files that contain this string
            if cnd in filename:
                # Split the file name and extension
                file_name, file_ext = os.path.splitext(file_path)
                # Replace the old string with the new one
                new_file_name = file_name.replace(old_string, new_string)
                # Build the new file path
                new_file_path = new_file_name + file_ext
                # Rename the file
                os.rename(file_path, new_file_path)
                
                
# test = rename_files(r"C:\Users\chcuk\OneDrive\Desktop\I2GFiles\EC\Patch",
#                     "_02022_02", "_2022_2", "_02022_02")