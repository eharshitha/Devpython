Y = input('Odd or Even:')
y = Y.upper()
while y == 'ODD' or 'EVEN':
    if y == 'ODD':
        Z = 1
        break
    elif y == 'EVEN':
        Z = 0
        break
    else:
       print('ERROR ERROR!')
       Y = input('Odd or Even:')
       y = Y.upper()

X = int(input('Enter a number: '))
while True:
    if Z > X:
        break
    else:
        print(Z)
    Z = Z + 2