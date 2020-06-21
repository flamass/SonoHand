# coding= utf-8
import struct

DEFAULT_TICKS_PER_BEAT = 200

# Codigos para apretar tecla y soltar
options = {
    "on": 144,
    "off": 128
}

class Note:
    def __init__(self, note, velocity, time, option):
        self.note = note
        self.velocity = velocity
        self.time = time
        self.option = options[option]

    @property
    def bytes(self):
        return [self.option, self.note, self.velocity]

class Midi:
    REDONDA = DEFAULT_TICKS_PER_BEAT * 4
    BLANCA = DEFAULT_TICKS_PER_BEAT * 2
    NEGRA = DEFAULT_TICKS_PER_BEAT
    CORCHEA = DEFAULT_TICKS_PER_BEAT // 2
    SEMICORCHEA = DEFAULT_TICKS_PER_BEAT // 4
    FUSA = DEFAULT_TICKS_PER_BEAT // 8
    SEMIFUSA = DEFAULT_TICKS_PER_BEAT // 16

    def __init__(self, tracks):
        self.tracks = []
        for _ in range(tracks):
            self.tracks.append([])

    def agregar_nota(self, nota, escala, velocidad, duracion, punto=False,
                     track=0):
        """
               Octave #	Note Numbers
                   do  do# re  re# mi  fa  fa# sol sol# la la# si
                   C	C#	D	D#	E	F 	F#	G	G#	A	A#	B
               -1	0	1	2	3	4	5	6	7	8	9	10	11
               0	12	13	14	15	16	17	18	19	20	21	22	23
               1	24	25	26	27	28	29	30	31	32	33	34	35
               2	36	37	38	39	40	41	42	43	44	45	46	47
               3	48	49	50	51	52	53	54	55	56	57	58	59
               4	60	61	62	63	64	65	66	67	68	69	70	71 # La típica
               5	72	73	74	75	76	77	78	79	80	81	82	83
               6	84	85	86	87	88	89	90	91	92	93	94	95
               7	96	97	98	99	100	101	102	103	104	105	106	107
               8	108	109	110	111	112	113	114	115	116	117	118	119
               9	120	121	122	123	124	125	126	127

        """
        intensidad = {"pppp": 8, "ppp": 20, "pp": 31, "p": 42,
                      "mp": 53, "mf": 64, "f": 80, "ff": 96, "fff": 112,
                      "ffff": 127}

        notas = {"do": 12, "do#": 13, "reb": 13, "re": 14, "re#": 15, "mib": 15,
                 "mi": 16, "fa": 17,
                 "fa#": 18, "solb": 18, "sol": 19, "sol#": 20, "lab": 20,
                 "la": 21, "la#": 22, "sib": 22, "si": 23}

        nota = nota.replace(" ", "").lower()
        velocidad = velocidad.replace(" ", "").lower()

        if punto:
            duracion = duracion + duracion // 2

        self.tracks[track].append(
            Note(notas[nota] + 12 * escala, intensidad[velocidad], 0, "on"))
        self.tracks[track].append(
            Note(notas[nota] + 12 * escala, intensidad[velocidad], duracion,
                 "off"))

    def agregar_silencio(self, duracion, punto=False, track=0):
        if punto:
            duracion = duracion + duracion // 2

        self.tracks[track].append(Note(0, 0, duracion, "off"))

    def save(self, outfile):
        # Primero guardar header
        # el tipo será 1 y la cantidad de tracks será 1 para esta tarea
        header = struct.pack('>hhh', 1, len(self.tracks), DEFAULT_TICKS_PER_BEAT)
        write_chunk(outfile, b'MThd', header)
        for notes in self.tracks:
            data = bytearray()

            for note in notes:
                """
                código para guardar el efecto de un pedal
                if not isinstance(note, Note):
                    if note == "off":
                        data.extend([0, 176, 64, 0])
                    else:
                        data.extend([0, 176, 64, 64])
                else:
                """
                # Guardar cada nota
                data.extend(encode_variable_int(note.time))
                msg_bytes = note.bytes
                data.extend(msg_bytes)

            # Guardar  fin del midi
            data.extend(encode_variable_int(0))
            # Bytes de fin
            data.extend([255, 47, 0])

            write_chunk(outfile, b'MTrk', data)

def to_baytes(n, length):
    #return bytes((n >> i*8) & 0xff for i in reversed(range(length)))
    return ''.join(chr((n >> i*8) & 0xff) for i in reversed(range(length)))

def write_chunk(outfile, name, data):
    """Write an IFF chunk to the file.
    `name` must be a bytestring."""
    outfile.write(name)
    outfile.write(to_baytes(len(data), 4))
    print to_baytes(len(data), 4), b'\x00\x00\x00\x06', len(data)
    outfile.write(data)

def decode_variable_int(value):
    bytes_array = []
    for elem in value:
        bytes_array.append("{:07b}".format(elem & 0x7f))

    return int("".join(bytes_array), 2)

def encode_variable_int(value):
    bytes_array = []
    while value:
        bytes_array.append(value & 0x7f)  # añadimos de a 7 bytes
        value >>= 7  # eliminamos esos 7 bytes

    if bytes_array:
        bytes_array.reverse()  # invertimos la lista
        for i in range(len(bytes_array) - 1):
            bytes_array[i] = bytes_array[i] | 0x80  # Le agrego su octavo bit a todos menos el último
        return bytes_array
    else:
        return [0]

def escribir_aarchivo(name, notas):
    char2notes = {
        'do':("c'"),
        'do#':("cis'"),
        're':("d'"),
        're#':("dis'"),
        'mi':("e'"),
        'fa':("f'"),
        'fa#':("fis'"),
        'sol':("g'"),
        'sol#':("gis'"),
        'la':("a'"),
        'la#':("ais'"),
        'si':("b'"),
        'doAlto':("c''"),
        'do#Alto':("cis''"),
        'reAlto':("d''"),
        're#Alto':("dis''"),
        'miAlto':("e''"),
        'faAlto':("f''"),
        'fa#Alto':("fis''"),
        'solAlto':("g''"),
        'sol#Alto':("gis''"),
        'laAlto':("a''"),
        'la#Alto':("ais''"),
        'siAlto':("b''")
    }
    partitura = "\relative c {\n"
    for i in notas:
        partitura += char2notes[i] + ' '
    partitura = partitura[:-1]
    partitura += '\n}'

    title = """\header {
      title = "A Little Night Music"
      composer = "Wolfgang Amadeus Mozart"
    }"""
    partitura += title
    print partitura

    with open(name, "w") as archivo:
        archivo.write(partitura)

    import os
    os.popen("partituramusical.ly")


if __name__ == "__main__":
    a = 2
    if a == 1:
        song = Midi(2)

        song.agregar_silencio(Midi.NEGRA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("la", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("la", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.BLANCA, False, 1)

        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.BLANCA, False, 1)

        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.BLANCA, False, 1)

        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.BLANCA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("la", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("la", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 5, 'p', Midi.BLANCA, False, 1)

        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("fa", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.BLANCA, False, 1)

#        with open("Estrefail23.mid", "wb") as file:
#            song.save(file)

    elif a == 2:
        song = Midi(2)
        song.agregar_silencio(Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.NEGRA, True, 1)
        song.agregar_silencio(Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("re", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.NEGRA, True, 1)
        song.agregar_silencio(Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("re", 4, 'p', Midi.CORCHEA, False, 1)

        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("re", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.BLANCA, False, 1)
        song.agregar_silencio(Midi.SEMICORCHEA, False, 1)

        song.agregar_nota("do", 5, 'p', Midi.NEGRA, True, 1)
        song.agregar_silencio(Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.NEGRA, True, 1)
        song.agregar_silencio(Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)


        song.agregar_nota("do", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("re", 4, 'p', Midi.BLANCA, False, 1)
        #song.agregar_silencio(Midi.CORCHEA, False, 1)

        song.agregar_nota("sol", 4, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.NEGRA, True, 1)
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)

        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.NEGRA, True, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.CORCHEA, False, 1)

        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        ####
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.NEGRA, True, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.CORCHEA, False, 1)

        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)

        song.agregar_nota("sol", 4, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("mi", 4, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.SEMICORCHEA, False, 1)

        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)

        song.agregar_nota("si", 4, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.SEMICORCHEA, False, 1)
        ######
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)

        song.agregar_nota("re", 5, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("si", 4, 'p', Midi.SEMICORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.SEMICORCHEA, False, 1)

        song.agregar_nota("re", 5, 'p', Midi.BLANCA, False, 1)
        ##
        song.agregar_silencio(2,False,1)
        song.agregar_nota("re", 5, 'p', Midi.BLANCA, False, 1)
        song.agregar_nota("mi", 5, 'p', Midi.BLANCA, False, 1)
        song.agregar_nota("re", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("do", 5, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("si", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("la", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("mi", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("fa#", 4, 'p', Midi.CORCHEA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("si", 4, 'p', Midi.NEGRA, False, 1)
        song.agregar_nota("sol", 4, 'p', Midi.REDONDA, False, 1)

        with open("Pequena Serenata Nocturna.mid", "wb") as file:
            song.save(file)

        list = ["sol", "re", "sol", "re", "sol", "re", "sol", "si", "re", "do",
                "la", "do",
                "la", "fa#", "la", "re", "sol", "sol", "si", "la", "sol", "sol",
                "fa#",
                "fa#", "la", "do", "fa#"]

        escribir_aarchivo("partituramusical.ly",list)
