puncts = """
0F01	—༁—	opening_punct
0F02	—༂—	opening_punct
0F03	—༃—	opening_punct
0F04	—༄—	opening_punct
0F05	—༅—	opening_punct
0F06	—༆—	opening_punct
0F07	—༇—	opening_punct
0F08	—༈—	opening_punct
0F09	—༉—	opening_punct
0F0A	—༊—	opening_punct
0F0D	—།—	closing_punct
0F0E	—༎—	closing_punct
0F0F	—༏—	closing_punct
0F10	—༐—	closing_punct
0F11	—༑—	opening_punct
0F12	—༒—	opening_punct
0F14	—༔—	closing_punct
0F34	—༴—	closing_punct
0F3A	—༺—	opening_punct
0F3B	—༻—	closing_punct
0F3C	—༼—	opening_punct
0F3D	—༽—	closing_punct
0F3E	—༾—	closing_punct
0F3F	—༿—	opening_punct
0FD0	—࿐—	opening_punct
0FD1	—࿑—	opening_punct
0FD3	—࿓—	opening_punct
0FD4	—࿔—	opening_punct
0FD9	—࿙—	opening_punct
0FDA	—࿚—	closing_punct
"""

opening_puncts = []
closing_puncts = []
for punct_line in puncts.splitlines():
    if not punct_line:
        continue
    punct_line = punct_line.strip().replace("\t", " ")
    code, punct, punct_type = punct_line.split(" ")
    punct_char = chr(int(code, 16))
    if punct_type == "opening_punct":
        opening_puncts.append(punct_char)
    elif punct_type == "closing_punct":
        closing_puncts.append(punct_char)

print(opening_puncts)
print("--------")
print(closing_puncts)
