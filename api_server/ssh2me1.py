import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('193.30.96.57', username='faysal', password='lasyaf', port=22, allow_agent=False, look_for_keys=False)
shell = client.invoke_shell()
_, stdout, stderr = client.exec_command(' system clock set time-zone-name="Asia/Beirut"')
data = "{}".format(stdout.read().decode('utf-8'))
Err = stderr.read()
print("{0}".format(data))
print("Error is \n{0}".format(stderr.read().decode('utf-8')))
shell.close()
client.close()
