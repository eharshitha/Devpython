import time

X = int(input('Enter Seconds: '))
print("Starting now......")
print("Seconds: ", X)
time.sleep(X)
for i in range(1, X+1) :
    print(i)
    time.sleep(1)

print("DING DING DING!!!")