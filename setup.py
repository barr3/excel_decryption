import encryption
import io
import os
import getpass

def write_to_bashrc(key, value):
    home_directory = os.path.expanduser("~")

    if (os.environ['SHELL'] == "/bin/zsh"):
        shell_rc_file = os.path.join(home_directory, ".zshrc")  
    else: # assumes bash if not zsh
        shell_rc_file = os.path.join(home_directory, ".bashrc") 

    # Append the export command to the shell's configuration file
    with open(shell_rc_file, "a") as file:
        file.write(f'\nexport {key}={value}\n')


file_path = input("Please input the file path of your encrypted file: ")
password = getpass.getpass("Please input your password: ")
key = encryption.derive_key_from_mac()
encrypted_password = encryption.encrypt_value(password, key)

write_to_bashrc("ASCLEPIUS", encrypted_password.decode("utf-8"))
write_to_bashrc("ASCLEPIUS_FILEPATH", file_path)