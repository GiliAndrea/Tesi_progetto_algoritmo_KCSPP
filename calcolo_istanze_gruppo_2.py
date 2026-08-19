from tester import Tester 
from modello_KCSPP import KCSPP_Modello

tester = Tester()
modello = KCSPP_Modello()

sorgente = "s"
destinazione = "t"

for i in range(1, 31):
    nome_istanza = f"istanza_{i}_gruppo2"
    G, k = tester.genera_istanza_gruppo2(15, 10, sorgente, destinazione)
    V, A, costi, colori = tester.estrazione_dati_istanza(G)
    valore_ottimo, stato_soluzione, tempo_calcolo, best_bound = modello.risoluzione_istanza(V, A, sorgente, destinazione, costi, colori, k)
    modello.salvare_risultati("risultati_istanze.txt", nome_istanza, valore_ottimo, stato_soluzione, 
                              tempo_calcolo, best_bound)