from pyo import *

class myChorus(PyoObject):

    def __init__(self, input, depth=1, feedback=0.1, bal=0.5, mul=1, add=0):
        #Chiamo il costruttore della superclasse per inizializzare mul e add
        super().__init__(mul,add)

        #Definisco e inizializzo gli attributi
        self._input = input
        self._depth = depth
        self._feedback = feedback
        self._bal = bal
        self._in_fader = InputFader(input)

        #Converto gli argomenti in liste per espansione multi-canale
        (in_fader, depth, feedback, bal, mul, add, 
         lmax) = convertArgsToLists(self._in_fader, depth,
                                    feedback, bal, mul, add)
        
        #Definisco la costruzione dell'effetto Chorus
        #1. Sig per alterare ampiezza delle sinusoidi
        self._modamp = Sig(depth, mul = 0.005)
        #2. Sinusoidi per modulare il ritardo di ogni Delay
        fr = 0.05
        inizio = 0
        fine = 8
        self._mod = [Sine(freq=fr+i/100, mul=self._modamp, add=0.0175) for i in range (inizio,fine)]
        #3. Delays applicati sul segnale in ingresso
        self._dls = [Delay(self._in_fader, delay = self._mod[i], feedback = feedback) for i in range (inizio,fine)]
        #4. Chorus che unisce il segnale Dry con il segnale Wet
        self._chorus = Interp(self._in_fader, self._dls, interp = bal, mul = mul, add = add)

        #Definisco come l'output viene visto da fuori: self._base_objs
        self._base_objs = self._chorus.getBaseObjects()
        

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        #Creazione delle map_list per controllare i parametri del Chorus
        self._map_list = [SLMap(0., 5., "lin", "depth", self._depth),
                          SLMap(0., 1., "lin", "feedback", self._feedback),
                          SLMap(0., 1., "lin", "bal", self._bal),
                          SLMapMul(self._mul)]
        super().ctrl(map_list, title, wxnoserver)

    def play(self, dur=0, delay=0):
        self._modamp.play(dur,delay)
        for i in range (len(self._mod)):
            self._mod[i].play(dur,delay)
            self._dls[i].play(dur, delay)
        return super().play(dur, delay)

    def stop(self):
        self._modamp.stop()
        for i in range (len(self._mod)):
            self._mod[i].stop()
            self._dls[i].stop()
        return super().stop()

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._modamp.play(dur, delay)
        for i in range (len(self._mod)):
            self._mod[i].play(dur, delay)
            self._dls[i].play(dur, delay)
        return super().out(chnl, inc, dur, delay)

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x : PyoObject
                New signal to process.
            fadetime : float, optional
                Crossfade time between old and new input. Defaults to 0.05.

        """
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setDepth(self, x):
        """
        Replace the `depth` attribute.

        :Args:

            x : float or PyoObject
                New `depth` attribute.

        """
        self._depth = x
        self._modamp.value = x

    def setFeedback(self, x):
        """
        Replace the `feedback` attribute.

        :Args:

            x : float or PyoObject
                New `feedback` attribute.

        """
        self._feedback = x
        for i in range (len(self._dls)):
            self._dls[i].feedback = x

    def setBal(self, x):
        """
        Replace the `bal` attribute.

        :Args:

            x : float or PyoObject
                New `bal` attribute.

        """
        self._bal = x
        self._chorus.interp = x

    @property
    def input(self):
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def depth(self):
        return self._depth
    @depth.setter
    def depth(self, x):
        self.setDepth(x)

    @property
    def feedback(self):
        return self._feedback
    @feedback.setter
    def feedback(self, x):
        self.setFeedback(x)

    @property
    def bal(self):
        return self._bal
    @bal.setter
    def bal(self, x):
        self.setBal(x)

#Eseguo lo script per testare la classe MyChorus
if __name__ == "__main__":
    
    s = Server(sr=44100,buffersize=8)
    #Seleziono l'ingresso e l'uscita della scheda audio
    s.setOutputDevice(5)
    s.setInputDevice(1)
    
    s.boot()
    #Assegno alla variabile a il segnale in ingresso dalla scheda audio
    a = Input(chnl=1, mul=.7).out()
    #Applico l'effetto Chorus al segnale a
    ch = myChorus(a, depth=.9, feedback=.5, mul=.5).out()
    ch.ctrl()
    #Da Mono passo a 2 canali
    ch = Pan(ch, outs=2)
    Scope(ch)

    #Apre l'interfaccia grafica del server
    s.gui(locals()) 


