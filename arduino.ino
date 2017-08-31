<pre style='color:#000000;background:#ffffff;'><span style='color:#696969; '>//librerie per funzionare</span>
<span style='color:#004a43; '>#</span><span style='color:#004a43; '>include</span><span style='color:#800000; '>&lt;</span><span style='color:#40015a; '>Servo.h</span><span style='color:#800000; '>></span><span style='color:#696969; '>//controllo del servo motore</span>

<span style='color:#696969; '>//oggetti che utilizzero per controllare tutto</span>
<span style='color:#800000; font-weight:bold; '>int</span> pinRuote <span style='color:#808030; '>=</span> <span style='color:#008c00; '>6</span><span style='color:#800080; '>;</span>
<span style='color:#800000; font-weight:bold; '>int</span> mezzo <span style='color:#808030; '>=</span><span style='color:#008c00; '>101</span><span style='color:#800080; '>;</span> <span style='color:#696969; '>//calibro il mezzo del servo motore (sono 90gradi) </span>
Servo sterzo<span style='color:#800080; '>;</span> <span style='color:#696969; '>//creo l oggetto per il controllo dello sterzo</span>

<span style='color:#800000; font-weight:bold; '>void</span> setup<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span> <span style='color:#800080; '>{</span>
  <span style='color:#696969; '>//preparo pin per ruote, pin sterzo, e interfaccia usb</span>
  pinMode<span style='color:#808030; '>(</span>pinRuote<span style='color:#808030; '>,</span>OUTPUT<span style='color:#808030; '>)</span><span style='color:#800080; '>;</span>
  sterzo<span style='color:#808030; '>.</span>attach<span style='color:#808030; '>(</span><span style='color:#008c00; '>9</span><span style='color:#808030; '>)</span><span style='color:#800080; '>;</span>
  Serial<span style='color:#808030; '>.</span>begin<span style='color:#808030; '>(</span><span style='color:#008c00; '>9600</span><span style='color:#808030; '>)</span><span style='color:#800080; '>;</span>
  sterzo<span style='color:#808030; '>.</span>write<span style='color:#808030; '>(</span>mezzo<span style='color:#808030; '>)</span><span style='color:#800080; '>;</span>

<span style='color:#800080; '>}</span>

<span style='color:#800000; font-weight:bold; '>int</span> mov<span style='color:#808030; '>=</span><span style='color:#008c00; '>0</span><span style='color:#800080; '>;</span> <span style='color:#696969; '>//var che conterra la posizione dello sterzo</span>
<span style='color:#800000; font-weight:bold; '>void</span> loop<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span> <span style='color:#800080; '>{</span>
  
  mov<span style='color:#808030; '>=</span>mezzo<span style='color:#800080; '>;</span> <span style='color:#696969; '>//di default è in mezzo</span>

  <span style='color:#800000; font-weight:bold; '>if</span><span style='color:#808030; '>(</span>Serial<span style='color:#808030; '>.</span>available<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span><span style='color:#808030; '>></span><span style='color:#008c00; '>0</span><span style='color:#808030; '>)</span><span style='color:#800080; '>{</span><span style='color:#696969; '>//se ho da leggere</span>
      
  <span style='color:#696969; '>//leggo dall usb e aggiorno lo stato dello sterzo</span>
  mov <span style='color:#808030; '>=</span> Serial<span style='color:#808030; '>.</span>read<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span><span style='color:#800080; '>;</span>
  Serial<span style='color:#808030; '>.</span>println<span style='color:#808030; '>(</span>mov<span style='color:#808030; '>)</span><span style='color:#800080; '>;</span><span style='color:#696969; '>//stampo er debug</span>
  analogWrite<span style='color:#808030; '>(</span>pinRuote<span style='color:#808030; '>,</span><span style='color:#008c00; '>65</span><span style='color:#808030; '>)</span><span style='color:#800080; '>;</span><span style='color:#696969; '>//aggiorno velocita ruote</span>
<span style='color:#800080; '>}</span><span style='color:#800000; font-weight:bold; '>else</span><span style='color:#800080; '>{</span>
  analogWrite<span style='color:#808030; '>(</span>pinRuote<span style='color:#808030; '>,</span><span style='color:#008c00; '>55</span><span style='color:#808030; '>)</span><span style='color:#800080; '>;</span> <span style='color:#696969; '>//altrimenti vanno un po piu lente (perche significha che a livello di pi o pc c'e' stato un err)</span>
<span style='color:#800080; '>}</span>
sterzo<span style='color:#808030; '>.</span>write<span style='color:#808030; '>(</span>mov<span style='color:#808030; '>)</span><span style='color:#800080; '>;</span><span style='color:#696969; '>//scrivo la nuova posizione sul servo</span>
delay<span style='color:#808030; '>(</span><span style='color:#008c00; '>70</span><span style='color:#808030; '>)</span><span style='color:#800080; '>;</span><span style='color:#696969; '>//do tempo per muovere il motore e ricevere le prossime correzioni</span>
  
<span style='color:#800080; '>}</span>
</pre>
