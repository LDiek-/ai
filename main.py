#! /usr/bin/python
# -*- coding: utf-8 -*-

import json

# Neuronales Netz zum erlernen von Nomen-Regelung

__autor__ = "Luca Diekgraefe"
__version__ = 1.0

class Connection():
    def __init__(self, name, connector, connected, weight):
        self.name   = name
        self.mode   = "off"
        self.weight = float(weight)
        self.signalStrength = 0
        self.way    = [connector, connected, self.weight]
        connected.addList(self)
        
    def checkWeight(self, summand):
        # Ändert Gewichtung dieser Verbindung, wenn Hebb-Regel erfüllt ist
        if self.mode == "on" and self.way[1].isActive():
            self.weight += summand
        
    def update(self, signal):
        """
        Erneuert das Signal, indem es diese mit der eigenen Gewichtung multipliziert
        Nach jeder Eingabe wird überprüft, ob die Gewichtungen über 0.1 liegen.

        :type signal: int
        """
        self.mode = "on"
        self.signalStrength = signal * self.weight
        self.kill()
        
    def get_off(self):
        self.mode = "off"
        self.signalStrength = 0

    def getSignal(self):
        if self.mode == "on":
            return self.signalStrength
        else:
            return None

    def kill(self):
        """
        Diese Funktion soll, wenn die Gewichtung dieser Funktion nahe eines geringen Wertes geht,
        sich selbst löschen
        1: Löschen aus der Liste von dem Output-Neuron
        2: Löschen aus verb_infos und verbindungen von dem angschlossenen Input-Neuron
        """

        if self.weight < 0.1:
            #1
            connectedInfo = self.way[1]
            connectedInfo.connections = filter(lambda x: x is not self, connectedInfo.connections)

            #2
            connector = self.way[0]
            connector.verbindungen = filter(lambda x: x is not self, connector.verbindungen)
            for key in connector.verb_infos:
                if key == self.name:
                    del connector.verb_infos[key]
                    print "[-] killed Connection %s" % self.name
                    break

class Input_Neuron():
    def __init__(self, reiz, neuron1):
        # verb_infos: {'name der Connection': Gewichtung der Verbindung,...}
        self.count_con = 0
        self.verbindungen = []
        self.verb_infos = {}
        self.reiz = reiz
        self.name = reiz
        self.neuron1 = neuron1
        self.neuronNames = [neuron1.name]
        self.verbinden(self.neuron1)
        self.eingabe = ""
        
    def inputValue(self, eingabe):
        """
        :type eingabe: basestring

        Erneuert lokale Variable 'eingabe' und öffnet sendSignal()
        Hier wird die Funktion auch aufegrufen, welche das Neuron aus allen Listen löscht und
        somit 'tötet'
        """
        self.eingabe = eingabe
        self.sendSignal()
        
    def verbinden(self, neuron):
        # Fügt ein Verbindungs-Objekt dem Array hinzu
        self.verbindungen.append(Connection(self.name+str(self.count_con),
                                            self, neuron, 1))
        self.count_con += 1
        self.verb_infos[self.name+str(self.count_con)] = 1
    
    def _bewerteEingabe(self):
        #Berechnet ähnlichkeit der letzten silbe
        erg = 0
        self.eingabe = self.eingabe[len(self.eingabe)-len(self.reiz):]
        
        for count in range(len(self.eingabe)):
            if self.eingabe[count] == self.reiz[count]:
                erg += 1.0/float(len(self.reiz))

        return erg

    def changeWeight(self, val):
        """
        Erneurt Gewichtungen der anliegenden Verbindungen per Addition

        :type val: float
        """
        for conn in self.verbindungen:
            conn.weight += val
    
    def sendSignal(self, val=None):
        """
        Bewertet die in der Klasse gespeicherte Eingabe und erneuert das Signal aller
        an diesem Neuron angeschlossenen Verbindungen.
        Wirde passiv durch inputValue() geöffnet.

        Darf positive Signale nur an IsNomen senden
        val ist Optional, falls die Gewichtung von außen her verändert werden soll

        :type val: int
        """
        if val:
            eingabeWert = val
        else:
            eingabeWert = self._bewerteEingabe()

        for verbindung in self.verbindungen:
            verbindung.update(eingabeWert)

    def getDict(self):
        """
        Benutzt __dict__ funktion um alle Variablen als Dictionary auszugeben,
        jedoch werden self.verbindungen nicht ausgegeben, da sie zum wiederherstellen
        aufgrund self.verb_infos nicht nötig sind und trotzdem in umgewandelt werden müssten

        :rtype: dict
        """

        myDict = self.__dict__

        if "verbindungen" in myDict: del myDict['verbindungen']
        if "neuron1" in myDict:  del myDict['neuron1']
        if "neuron2" in myDict:  del myDict['neuron2']

        # myDict in Unicode "ISO-8859-1" verwandeln
        for key in myDict:
            if isinstance(myDict[key], list):
                myDict[key] = map(lambda x: self.make_unicode(x), myDict[key])
            elif isinstance(myDict[key], dict):
                for newKey in myDict[key]:
                    # Daten des types Int müssen nicht umgewandelt werden
                    if not isinstance(myDict[key][newKey], int):
                        myDict[key] = self.make_unicode(myDict[key][newKey])
            elif not isinstance(myDict[key], int):
                myDict[key] = self.make_unicode(myDict[key])

        return myDict

    def getNewConnection(self, conns, outputNeurons):
        """
        :type conns: list
        :type outputNeurons: list

        Hier werden nach laden der alten Daten von einer Datei die neuen
        initialisiert
        Dies funktioniert, indem er zuerst die noch nicht verbundenden verbindet
        und dann alle mit einer neuen Gewichtung aktualisiert
        conns: [{Daten von einer Connection},{Daten zweiter Connection},...]

        Da die Daten einer Connection nur aus dem Name und der Gewichtung entstehen,
        muss als connector das eigene Objekt und als connected muss von außen iteriert werden.
        Das funktioniert aber nur, wenn bei dem abspeichern dieser Daten genauso viele Output-Neuronen
        vorhanden waren, wie jetzt auch!
        """

        for connName in conns:
            if connName not in map(lambda x: x.name, self.verbindungen):
                for outputNeuron in outputNeurons:
                    obj = Connection(connName, self, outputNeuron, conns[connName])
                    self.verbindungen.append(obj)

    def make_unicode(self, string):
        """
        Erzeugt ISO-8859-1 codierte codes

        :rtype: basestring
        :type string: str
        """

        try:
            if isinstance(string, unicode):
                return string
            elif isinstance(string, str):
                return unicode(string, "ISO-8859-1")
        except UnicodeDecodeError:
            return ""

class Output_Neuron():
    def __init__(self, name):
        self.name = name
        self.netinput = 0
        self.connections = []
    
    def addList(self, connection):
        self.connections.append(connection)
        
    def isActive(self):
        return self.netinput

    def getDict(self):
        """
        :rtype: dict
        """
        myDict =  self.__dict__
        del myDict['connections']
        # myDict in Unicode "ISO-8859-1" verwandeln
        for key in myDict:
            if isinstance(myDict[key], list):
                myDict[key] = map(lambda x: unicode(x, "ISO-8859-1"), myDict[key])
            elif not isinstance(myDict[key], int):
                if isinstance(myDict[key], str): myDict[key] = unicode(myDict[key], "ISO-8859-1")

        return myDict
        
    def makeOutput(self):
        for connect in self.connections:
            self.netinput += connect.getSignal()
        
        return self.isActive()
    

def train():
    """
    Trainingsphase
    Lernen ist supervised durch User

    Schritte:
    1) Laden alter Daten
    2) Lesen der zu bearbeitetenden Wörter (Nomen)
    3) Überprüfen, ob es ein Nomen sein soll oder nicht
    4) Erzeugen aller !möglichen! letzten Silben
    5) Erzeugen neuer Input-Neuronen-Nachbarschaften, oder aber alte aktualisieren, indem man die Gewichtungen
       der Verbindungen um 0.5 erhöht
    6) Nun wird das Nomen bei jedem Input-Neuronen 'eingegeben' und somit die Signale und Verbindungen aktiviert
    7) Nun werden die Gewichtungen von hinten nach vorne verändert (sie werden 'belehrt', supervised)
    8) Beim Erreichen des Endes der Datei werden die Neuronen gespeichert

    " n" zeigt an, dass das vorherige Wort kein Nomen ist
    """

    def _save():
        """Diese Funktion soll InputNeuronen speichern, sodass man sie
        später wieder laden kann und keine Daten verloren gehen
        Mit JSONEncoder und o.__dict__ dafür muss jedoch noch eine Funktion
        in den Klassen definiert werden"""
        f_input = open("saved_input.json", "w")
        f_output = open("saved_output.json", "w")

        changedInput = _changeClass(inputNeuronen)
        changedOutput = _changeClass(outputNeuronen)

        open("write.txt", "w").write(str(changedInput))

        f_input.write(json.dumps(changedInput))
        f_output.write(json.dumps(changedOutput))

    def _changeClass(data):
        """
        Verändert Objekte der Art [[Class, Class], [Class, Class, Class], ...] in
        von JSON verarbeitbare 2D-Listen mit Dictionarys anstatt von Klassen
        Diese Dictionarys müssen von loadData() und save() verarbeitbar sein.

        neighborhood := die '2. Dimension' der Liste (Neuronen-Nachbarschaft)
        Diese Funktion überträgt alle Daten aus data -> output, wobei sie jedoch die
        Klassen per __dict__-Aufruf in ein Dictionary umwandeln.

        :rtype: list
        :type data: list
        """

        output = []

        for neighborhoodCount in range(len(data)):
            if isinstance(data[neighborhoodCount], Output_Neuron):
                output.append(data[neighborhoodCount].getDict())
            else:
                output.append([])
                for objCount in range(len(data[neighborhoodCount])):
                    if isinstance(data[neighborhoodCount][objCount], list):
                        # Listen abfangen und per map() bearbeiten
                        output[neighborhoodCount].append(map(
                            lambda x: data[neighborhoodCount][objCount].getDict(),
                            xrange(len(data[neighborhoodCount][objCount])))
                            )
                    else:
                        output[neighborhoodCount].append(data[neighborhoodCount][objCount].getDict())

        return output

    def _learn(aktiveNeuron):
        """
        Guckt alle Neuronen-Nachbarschaften von hinten nach vorne nach
         Erstellt 2 Listen: Sendende / Nicht-Sendende
         verringert gewichtung der Sendenden und steigert die der sendenden um denselben Wert
         benötigt aktives Output-Neuron

         :type aktiveNeuron: Output_Neuron
         """

        conns = aktiveNeuron.connections
        sending = []
        notsending = []

        for conn in conns:
            if conn.mode == "on":
                sending.append(conn)
                conn.weight -= 0.1
            else:
                notsending.append(conn)
                conn.weight += 0.1

    def _getobj(objName):
        """
        Versucht zu gegebenen Namen das richtige Neuron zu finden
        Dabei nutzt der Algorithmus aus, dass alle Neuronen in einer Nachbarschaft Ähnlichkeiten haben Bsp.:
        [['aus', 'us'], ['ab', 'b']]
        Also muss, wenn der Name des gesuchten Neurons in der Nachbarschaft drin ist, der Name
        ähnlichkeit mit dem ersten Wert dieser Nachbarschaft haben
        objName -> Letzte Silbe des eigentlichen Wortes!

        :type objName: str
        :rtype: Input_Neuron
        """
        try:
            for neuron1, neuron2 in inputNeuronen:
                if neuron1.name in objName or objName in neuron1.name:
                    if neuron1.name == objName:
                        return neuron1
                    elif neuron2.name == objName:
                        return neuron2
        except ValueError:
            pass

    #1
    outputNeuronen, inputNeuronen = loadData()
    typ = 'nom'
    f = open("nomen.txt", "r")

    neuronNeighbors = []
    inputNames = []

    for neighbor in inputNeuronen:
        if neighbor:
            inputNames += map(lambda x: x.name, neighbor)

    outputIsNomen = Output_Neuron("IsNomen")
    outputIsAdjektive = Output_Neuron("IsAdjektive")
    outputIsVerb = Output_Neuron("IsVerb")

    outputNeuronen = [outputIsNomen, outputIsAdjektive, outputIsVerb]



    #2
    for nomen in f.readlines():
        nomen = nomen.strip("\n")
        nomen = nomen.split(" ")
        #3
        if len(nomen) > 1:
            typ = {"v": "ver", "a": "adj"}[nomen[1]]
            print "[+] Found %s" % typ
            nomen = nomen[0].strip(" " + typ)
        else:
            typ = "nom"
            print "[+] Found Nomen"
        #4
        lenInput = len(nomen)
        neuronNeighborsNames = [nomen[lenInput-x:] for x in range(2, 4)]
        outputTypes =  {"nom": outputIsNomen, "ver": outputIsVerb, "adj": outputIsAdjektive}
        #5
        for name in neuronNeighborsNames:
            for typstr in ['nom', 'ver', "adj"]:
                if typ == typstr:
                    if name in inputNames:
                        # _getobj gibt das Input-Neuron mit dem Angegebenen Namen wieder
                        if _getobj(name): _getobj(name).changeWeight(0.5)
                    else:
                        neuronNeighbors.append(Input_Neuron(name, outputTypes[typstr]))

        inputNeuronen.append(neuronNeighbors)
        neuronNeighbors = []
        # Allen Input Neuronen 'nomen' als Eingabe geben
        #6

        inputNeuronen = filter(lambda x: x != [], inputNeuronen)

        for neighbor in inputNeuronen:
            for neuron in neighbor:
                neuron.inputValue(nomen)

        # Aktives Output-Neuron finden und "belehren"
        #7
        if typ == "nom":
            _learn(outputIsNomen)
        elif typ == "ver":
            _learn(outputIsVerb)
        else:
            _learn(outputIsAdjektive)
    #8
    if inputNeuronen:
        _save()

def test():
    outputNeuronen, inputNeuronen = loadData()
    print "Got %d Output-Neuronen and %d Input-Neuronen loaded" % (len(outputNeuronen), len(inputNeuronen) * 2)

    outputs = {}

    while True:
        eingabe = raw_input("Nomen Eingeben:")

        if eingabe == "end":
            break

        for neighborhood in inputNeuronen:
            for neuron in neighborhood:
                neuron.inputValue(eingabe)

        for neuron in outputNeuronen:
            outputs[neuron.name] = neuron.makeOutput()

        biggestValue = max(outputs.values())
        for name in outputs:
            if outputs[name] == biggestValue:
                print name
                break

def loadData():
    """
    Diese Funktion soll alle gespeicherten Daten wieder starten
    Dazu muss diese Funktion auch Dictionarys in die dazugehörigen Klassen
    zurückverwandeln

    :rtype: list

    Ausgabe sind 2 Listen (outputNeuronen, inputNeuronen), welche bei nicht vorhandendem bzw. leeren
    Dateien ebenfalls leer sind.

    Output-Neuronen werden verbunden und sind am Anfang ohne Verbindung, weshalb sie einfach nur mit
    einem Namen initialiesiert werden müssen.

    Connections werden in den Klassen (Input-Neuronen, Output-Neuronen) gespeichert.

    Input-Neuronen müssen jedoch mit den richtigen Verbindungen verbunden werden, welche auch die richtige
    Gewichtung haben müssen. Das Gewichten übernimmt eine Funktion der Klasse Input-Neuronen(getNewConnection)
    Da JSON keine Klassen abspeichern kann, werden die wichtigsten Infos über eine Funktion in einem Dictionary
    gespeichert(Name, Gewichtung).

    Damit noch weniger Klassen bei dem Starten genutzt werden, müssen auch die in der Input-Neuronen gespeicherten
    Klasse Output_Neuronen nocheinmal nur als Name gespeichert werden. Dann werden diese in der wiederhergestellten
    Liste von Output-Neuronen gesucht und als Parameter für die IN genutzt
    """

    f_input = open("saved_input.json", "r")
    f_output = open("saved_output.json", "r")

    inputNeuronen = []
    nachbarschaft = []
    outputNeuronen = []

    try:
        oldInputNeuronen = json.load(f_input, encoding='ISO-8859-1')
        oldOutputNeuronen = json.load(f_output, encoding='ISO-8859-1')
    except ValueError:
        return [], []

    # Verbindungen verbinden sich automatisch mit Output_Neuronen
    if not oldOutputNeuronen:
        oldOutputNeuronen = [{'name': "IsNomen"}, {'name': "IsNoNomen"}]

    for obj in oldOutputNeuronen:
        neuronobj = Output_Neuron(obj['name'])
        outputNeuronen.append(neuronobj)

    # Getting outputNeuronenNames
    outputNeuronenNames = map(lambda neuron: neuron.name, outputNeuronen)

    for nachbarschaften in oldInputNeuronen:
        for obj in nachbarschaften:
            # Indexierung bei outputNeuronNames und outputNeuronen dieselbe
            # Sucht Index von der Klasse mit dem Namen und gibt die Klasse zurück für 1(!) Neuronen
            # Wenn Neuron2 doch aktiv sein muss hier ändern : TODO
            neuronen = [outputNeuronen[outputNeuronenNames.index(obj['neuronNames'][0])]]
            neuronobj = Input_Neuron(obj['reiz'], neuronen[0])
            neuronobj.count_con = obj['count_con']
            neuronobj.getNewConnection(obj['verb_infos'], outputNeuronen)
            nachbarschaft.append(neuronobj)
        inputNeuronen.append(nachbarschaft)
        nachbarschaft = []


    return outputNeuronen, inputNeuronen

if __name__ == "__main__":
    mode = raw_input("In welchem Modus soll gestartet werden(test/train): ")

    if mode == "test":
        test()
    elif mode == "train":
        train()
    else:
        print "Wrong Input!"
