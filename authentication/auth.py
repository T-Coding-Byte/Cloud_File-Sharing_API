from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)

def verify_password(attempt_pass, stored_hash):
    return password_hash.verify(attempt_pass, stored_hash)