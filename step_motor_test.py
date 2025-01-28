from machine import Pin
from utime import sleep

class Stepper:
    '''
    Classe para controle de motor de passo
    '''
    # aciona os sinais de controle do motor
    def aciona(self, val=[0, 0, 0, 0]):
        for i in range(len(self.pinos)):
            self.pinos[i].value(val[i])

    # init
    def __init__(self, pinos=None, fullStep=True, delay=0.002):
        # Salva os pinos de conexão
        if pinos is None:
            raise ValueError("Obrigatório especificar os pinos")
        if len(pinos) != 4:
            raise ValueError("Devem ser especificados 4 pinos")
        self.pinos = pinos
        if fullStep:
            self.passos = [[1, 0, 0, 1], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]]
        else:
            self.passos = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        self.delay = delay
        self.aciona()
        self.passo = 0

    # avança npassos passos
    def avanca(self, npassos=1):
        for i in range(npassos):
            self.aciona(self.passos[self.passo])
            sleep(self.delay)
            self.passo = self.passo + 1
            if self.passo >= len(self.passos):
                self.passo = 0

    # recua npassos passos
    def recua(self, npassos=1):
        for i in range(npassos):
            self.passo = self.passo - 1
            if self.passo < 0:
                self.passo = len(self.passos) - 1
            self.aciona(self.passos[self.passo])
            sleep(self.delay)

# Configuração dos pinos
pinos = [
    Pin(4, Pin.OUT),
    Pin(5, Pin.OUT),
    Pin(6, Pin.OUT),
    Pin(7, Pin.OUT)
]

# Instancia o motor de passo
stepper = Stepper(pinos)

# Loop principal
while True:
    stepper.avanca(1024)
    sleep(1)
    stepper.recua(512)
    sleep(1)
