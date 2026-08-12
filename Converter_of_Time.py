print('Welcome to the Converter of Time program')
X = float(input('Enter a number<It can also be a Decimal>: '))
Y = input('Convert from<S,M,H>').upper()
Z = input('to<S,M,H>').upper()
if Y == 'S':
    if Z == 'S':
        print(X)
    elif Z == 'M':
        print(X*60)
    elif Z == 'H':
        print(X*60*60)
elif Y == 'M':
    if Z == 'S':
        print(X/60)
    elif Z == 'M':
        print(X)
    elif Z == 'H':
        print(X*60)
elif Y == 'H':
    if Z == 'S':
        print(X/60/60)
    elif Z == 'M':
        print(X/60)
    elif Z == 'H':
        print(X)