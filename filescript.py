import shutil
import os
import time
import threading
import msoffcrypto
import io
import getpass
import encryption

def copy_and_delete(file_path, password=None):
    # Get the filename from the given path
    file_name = os.path.basename(file_path)

    
    current_directory = os.getcwd()
    # Get the parent directory
    parent_directory = os.path.dirname(current_directory)

    destination_path = os.path.join(parent_directory, file_name)


    # Copy the file to the current directory
    shutil.copy(file_path, destination_path)
    print(f"File copied to {destination_path}")
    

    if password:
        destination_path = remove_excel_password(destination_path, password) 

    # Function to delete the file after one hour
    def delete_file():
        time.sleep(3600)  # Wait for one hour
        if os.path.exists(destination_path):
            os.remove(destination_path)
            print(f"File deleted after one hour.")
    
    # Start the deletion thread
    deletion_thread = threading.Thread(target=delete_file, daemon=True)
    deletion_thread.start()
    deletion_thread.join()


def remove_excel_password(file_path, password):
    temp_path = file_path.replace(".xlsx", "_unlocked.xlsx")


    try:
        # If the file is fully encrypted
        with open(file_path, "rb") as f:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(f)
            office_file.load_key(password=password)
            office_file.decrypt(decrypted)

        # Save decrypted file
        with open(temp_path, "wb") as f:
            f.write(decrypted.getvalue())

        print(f"Password removed: {temp_path}")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Encrypted file deleted.")        

        return temp_path

    except Exception as e:
        print(f"Failed to remove password: {e}")
        return file_path  # Return original file if decryption fails


def write_to_bashrc(key, value):
    home_directory = os.path.expanduser("~")

    if (os.environ['SHELL'] == "/bin/zsh"):
        shell_rc_file = os.path.join(home_directory, ".zshrc")  
    else: # assumes bash if not zsh
        shell_rc_file = os.path.join(home_directory, ".bashrc") 

    # Append the export command to the shell's configuration file
    with open(shell_rc_file, "a") as file:
        file.write(f'\nexport {key}={value}\n')

    

# Example usage
if __name__ == "__main__":
    file_path = os.getenv("ASCLEPIUS_FILEPATH")

    # get encrypted password and check if it exists
    encrypted_password = os.getenv("ASCLEPIUS") 
    key = encryption.derive_key_from_mac()

    if not file_path:
        file_path = input("File path not found. Please input file path... ")
        write_to_bashrc("ASCLEPIUS_FILEPATH", file_path)

    if encrypted_password:
        print("Encrypted password found.")
    else:
        print("No encrypted password stored. Please input password")
        password = getpass.getpass("Password: ")
        print("Setting password as environment variable.")
        encrypted_password = encryption.encrypt_value(password, key)
        #os.environ["ASCLEPIUS"] = encrypted_password.decode("utf-8")
        write_to_bashrc("ASCLEPIUS", encrypted_password.decode("utf-8"))
        print("\nEnvironment variable set in .bashrc. Please restart the terminal with 'source ~/.bashrc' for changes to take place.") 

    
    decrypted_password = encryption.decrypt_value(encrypted_password, key)


    if os.path.exists(file_path):
        copy_and_delete(file_path, decrypted_password)
    else:
        print("File not found.")
