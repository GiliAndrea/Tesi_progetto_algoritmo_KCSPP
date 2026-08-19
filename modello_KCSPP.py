import gurobipy as gp
from gurobipy import GRB
import time

class KCSPP_Modello:

    def __init__(self):
        pass


    def risoluzione_istanza(self, V: list, A: list, sorgente, destinazione, costi: dict, 
                            colori: dict, k: int):
        '''V: lista dei nodi - 
        A: lista degli archi come tuple (u, v) - 
        sorgente: nodo sorgente - 
        destinazione: nodo destinazione - 
        costi: dizionario con chiavi (u, v) e valori che rappresentano i costi degli archi (d_uv) - 
        colori: dizionario con chiavi (u, v) e valori che rappresentano i colori (c(u, v)) - 
        k: limite massimo di colori distinti utilizzabili nel cammino - 
        file_risultati: nome del file di output'''
        
        # Estrazione dei colori unici disponibili nel grafo
        C = list(set(colori.values()))

        try:
            # Creazione del modello Gurobi
            m = gp.Model("FFP_k_CSPP")

            # === VARIABILI DECISIONALI ===
            
            # Variabile binaria x_uv:
            x = {}
            for (u, v) in A:
                x[u, v] = m.addVar(vtype=GRB.BINARY, name=f"x_{u}_{v}")

            # Variabile binaria y_h:
            y = {}
            for h in C:
                y[h] = m.addVar(vtype=GRB.BINARY, name=f"y_{h}")

            # === FUNZIONE OBIETTIVO ===
            
            # Minimizzazione del costo totale del cammino da s a t
            m.setObjective(gp.quicksum(costi[u, v] * x[u, v] for (u, v) in A), GRB.MINIMIZE)

            # === VINCOLI ===
            
            # Vincoli di conservazione del flusso per la connettività del percorso
            for u in V:
                in_flow = gp.quicksum(x[i, j] for (i, j) in A if j == u)
                out_flow = gp.quicksum(x[i, j] for (i, j) in A if i == u)

                if u == sorgente:
                    rhs = -1
                elif u == destinazione:
                    rhs = 1
                else:
                    rhs = 0

                m.addConstr(in_flow - out_flow == rhs, name=f"flusso_{u}")

            # Vincolo di attivazione del colore: se un arco è nel cammino, il suo colore deve essere usato
            for (u, v) in A:
                h = colori[u, v]
                m.addConstr(x[u, v] <= y[h], name=f"colore_attivo_{u}_{v}")

            # Limite al numero massimo di colori distinti utilizzabili
            m.addConstr(gp.quicksum(y[h] for h in C) <= k, name="max_colori")

            # Limite di tempo sull'ottimizzazione 
            m.setParam('TimeLimit', 500)

            # === OTTIMIZZAZIONE ===
    
            start = time.time()
            m.optimize()
            tempo_calcolo = time.time() - start

            if m.SolCount > 0:
                costo_migliore = m.ObjVal
            else:
                costo_migliore = None 

            try:
                best_bound = m.ObjBound
            except gp.GurobiError:
                best_bound = None 

            if m.status == GRB.OPTIMAL:
                costo_migliore = m.ObjVal

            status_code = m.Status
            stato_testuale = "Sconosciuto"

            if status_code == GRB.OPTIMAL:
                stato_testuale = "Ottima"
            elif status_code == GRB.TIME_LIMIT:
                stato_testuale = "Ammissibile"
            elif status_code == GRB.INFEASIBLE:
                stato_testuale = "Inammissibile"
            elif status_code == GRB.UNBOUNDED:
                stato_testuale = "Illimitata"
            else:
                stato_testuale = f"Altro_{status_code}"
                        
            return costo_migliore, stato_testuale, tempo_calcolo, best_bound

        except gp.GurobiError as e:
            print(f"Errore Gurobi {e.errno}: {e}")
        except AttributeError:
            print("Riscontrato un errore negli attributi delle variabili.")

    # === OUTPUT E SALVATAGGIO ===

    def salvare_risultati(self, file_risultati: str, nome_istanza, valore_Funzione_obiettivo: float,
                           stato_soluzione: str, tempo_di_calcolo: float, best_bound: float):
        """Salva i risultati del modello rispetto ad una istanza nel formato txt nel file specificato"""

        with open(file_risultati, mode='a', encoding='utf-8') as file:
            file.write(f"{nome_istanza} - {valore_Funzione_obiettivo} -" 
                       f"{stato_soluzione} - {tempo_di_calcolo} - {best_bound}\n")

    def risultati_terminale(self, nome_istanza, valore_Funzione_obiettivo: float,
                           stato_soluzione: str, tempo_di_calcolo: float, best_bound: float):
        print(f"{nome_istanza} - {valore_Funzione_obiettivo} -" 
              f"{stato_soluzione} - {tempo_di_calcolo} - {best_bound}\n")




# === TEST DEL MODULO Modello_KCSPP ===
if __name__ == '__main__':
    # Esempio giocattolo basato sull'istanza del k-CSPP
    V_test = ['s', '1', '2', '3', 't']
    A_test = [('s', '1'), ('s', '3'), ('1', '2'), ('3', '2'), ('t', '2'), ('s', 't'), ('1', 't'), ('2', 't')]
    
    costi_test = {
        ('s', '1'): 2, ('s', '3'): 1, 
        ('1', '2'): 5, ('3', '2'): 1, 
        ('t', '2'): 8, ('s', 't'): 10,
        ('1', 't'): 3, ('2', 't'): 1
    }
    
    colori_test = {
        ('s', '1'): 'c1', ('s', '3'): 'c2', 
        ('1', '2'): 'c3', ('3', '2'): 'c3', 
        ('t', '2'): 'c2', ('s', 't'): 'c1',
        ('1', 't'): 'c4', ('2', 't'): 'c4'
    }
    
    modello = KCSPP_Modello()
    
    # Risoluzione con limite di 2 colori
    print("--- Test con k=2 ---")
    costo_migliore, status, tempo_calcolo, best_bound = modello.risoluzione_istanza(V=V_test, A=A_test, sorgente='s', destinazione='t', 
                          costi=costi_test, colori=colori_test, 
                          k=3)

    modello.risultati_terminale("istanza_001", costo_migliore, status, tempo_calcolo, best_bound)
