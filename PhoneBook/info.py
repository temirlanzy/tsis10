import csv
users=[
    ('personName', 'phoneNumber'),
    ['Ivan', '12345678'],
    ['Kolya', '87654321']
]
with open(r'C:\Users\tnurs\OneDrive\Desktop\tsis10', 'w', newline='') as f:
    writer=csv.writer(f)
    writer.writerows(users)