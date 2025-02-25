import os
import base64
from cryptography.fernet import Fernet
from getmac import get_mac_address
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Function to derive a key from the MAC address
def derive_key_from_mac():
    # Get the MAC address of the device (can be customized to use specific interface)
    mac_address = get_mac_address()
    
    if mac_address is None:
        raise Exception("Unable to fetch MAC address")
    
    # Use the MAC address as the "master key" and derive the Fernet key
    # Salt can be set to a constant value or random for extra security
    salt = b"some_salt_for_security"  # You can use a random salt if needed
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Fernet key length is 32 bytes
        salt=salt,
        iterations=100000,
    )
    
    # Use the MAC address as input to the key derivation
    key = kdf.derive(mac_address.encode())
    return base64.urlsafe_b64encode(key)

# Encrypt a value
def encrypt_value(value, key):
    fernet = Fernet(key)
    encrypted_value = fernet.encrypt(value.encode())
    return encrypted_value

# Decrypt a value
def decrypt_value(encrypted_value, key):
    fernet = Fernet(key)
    decrypted_value = fernet.decrypt(encrypted_value).decode()
    return decrypted_value

# Example usage
if __name__ == "__main__":
    # Derive the encryption key from the MAC address
    key = derive_key_from_mac()

    # Example environment variable to encrypt
    env_var_name = "MY_SECRET"
    os.environ[env_var_name] = "ThisIsASecret"

    # Encrypt the environment variable value
    encrypted_value = encrypt_value(os.environ[env_var_name], key)
    print(f"Encrypted Value: {encrypted_value}")

    # Decrypt the value back
    decrypted_value = decrypt_value(encrypted_value, key)
    print(f"Decrypted Value: {decrypted_value}")
