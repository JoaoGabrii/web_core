import hashlib,secrets,getpass
password=getpass.getpass('Defina uma senha forte para o portal: ')
if len(password)<12:raise SystemExit('Use no mínimo 12 caracteres.')
salt=secrets.token_bytes(16)
print('\nConfigure estas variáveis no ambiente de execução (NÃO publique no Git):')
print('ADMIN_USER=admin')
print('ADMIN_SALT='+salt.hex())
print('ADMIN_PASSWORD_HASH='+hashlib.pbkdf2_hmac('sha256',password.encode(),salt,250000).hex())
print('SESSION_SECRET='+secrets.token_urlsafe(48))
