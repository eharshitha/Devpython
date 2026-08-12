import keyboard

keys = ['Space']

while True:
    if all(keyboard.is_pressed(key) for key in keys):
        print('Space key is pressed!')
        break