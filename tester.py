import random
import math
import networkx as nx
import csv
import os


class Tester:

    def __init__(self):
        pass


    def calcolatore_k_mcpp(self):

        # per questa versione si è scelto per la scelta arbitraria del k

        """Simula il calcolo del parametro k (Minimum Color Path Problem).
        Restituisce un valore difinito e alcune volte sovrastimato per l'istanza.
        Il valore di K definito è relativo a grafi con 15 strati da 10 nodi l'uno."""

        k = 8
        return k


    def assegnazione_costo_colore(self, G):
        """Assegna costi e colori agli archi del grafo come attributi."""

        num_edges = G.number_of_edges()
        # La numerosità dei colori deve essere un quarto del numero dei vertici
        num_colors = max(1, math.floor(num_edges / 4))  
        
        for u, v in G.edges():
            G[u][v]['costo'] = random.randint(1, 1000) # Costo casuale e compreso nell'intervallo [1, 1000]
            G[u][v]['colore'] = random.randint(1, num_colors) # Numero colore nell'intervallo  [1, |C|]
            
        return G

    def creazione_base_nodes(self, w: int, r: int, sorgente: str, destinazione: str):
        """Crea i nodi di base organizzati per strati.""" 

        G = nx.DiGraph()
        G.clear()
        G.add_node(sorgente, layer=0)
        G.add_node(destinazione, layer=w+1)
        
        for i in range(1, w + 1):
            for j in range(1, r + 1):
                G.add_node(f'v_{i}_{j}', layer=i)
        return G

    def genera_istanza_gruppo1(self, w: int, r: int , sorgente: str, destinazione: str):
        """Genera istanze del Gruppo 1 (Grafi a strati standard)."""
        
        G = self.creazione_base_nodes(w, r, sorgente, destinazione)
        
        # Connessioni sorgente -> strato 1
        for j in range(1, r + 1):
            G.add_edge(sorgente, f'v_1_{j}')
            
        # Connessioni strato i -> strato i+1
        for i in range(1, w):
            for j in range(1, r + 1):
                for z in range(1, r + 1):
                    G.add_edge(f'v_{i}_{j}', f'v_{i+1}_{z}')
                    
        # Connessioni strato w -> destinazione
        for j in range(1, r + 1):
            G.add_edge(f'v_{w}_{j}', destinazione)
            
        G = self.assegnazione_costo_colore(G)
        k = self.calcolatore_k_mcpp()

        return G, k

    def genera_istanza_gruppo2(self, w: int, r: int, sorgente: str, destinazione: str):
        """Genera istanze del Gruppo 2 (Grafi a strati modificati con jump-arcs)."""

        G, k = self.genera_istanza_gruppo1(w, r, sorgente, destinazione)
        
        # Passaggi per trovare il costo massimo tra gli archi normali per generare i jump-arcs
        d_max = max(nx.get_edge_attributes(G, 'costo').values())

        # La numerosità dei colori deve essere un quarto del numero dei vertici
        num_colors = max(1, math.floor(G.number_of_edges() / 4))

        # Il numero dei jump-arcs è casuale e compreso nell'intervallo [10, 30]
        num_jumps = random.randint(10, 30) 
        
        for j in range(num_jumps):
            layer_i = random.randint(1, w - 2)
            layer_ip = random.randint(layer_i + 2, w)
            
            u = f'v_{layer_i}_{random.randint(1, r)}'
            v = f'v_{layer_ip}_{random.randint(1, r)}'

            # Costo fino a 30000 unità superiore rispetto al costo più elevato nell'arco
            cost = random.randint(d_max, d_max + 30000)  
            color = random.randint(1, num_colors)
            G.add_edge(u, v, costo=cost, colore=color)
            
        return G, k

    def genera_istanza_gruppo3(self, w: int, r: int, sorgente: str, destinazione: str):
        """Genera istanze del Gruppo 3 (Grafi a strati con cricche interne e archi ridotti).""" 
    
        G = self.creazione_base_nodes(w, r, sorgente, destinazione)
        
        # Connessioni sorgente -> strato 1
        for j in range(1, r + 1): G.add_edge('s', f'v_1_{j}')

        # Connessione strato w -> destinazione
        for j in range(1, r + 1): G.add_edge(f'v_{w}_{j}', 't')
        
        for i in range(1, w):
            layer_nodes = [f'v_{i}_{j}' for j in range(1, r + 1)]
            
            # Definizione di 3 vertici casuali per formare la cricca Qi
            Qi = random.sample(layer_nodes, 3)

            # Ricerca del vertice in Qi con l'etichetta minore
            Qi_sorted = sorted(Qi, key=lambda x: int(x.split('_')[2]))
            smallest_Qi = Qi_sorted[0]
            
            # Archi della cricca Qi (tutti connessi)
            for u in Qi:
                for v in Qi:
                    if u != v:
                        G.add_edge(u, v)
                        
            # Archi tra Qi e non-Qi con probabilità = 0.5
            non_Qi = [n for n in layer_nodes if n not in Qi]
            for u in Qi:
                for v in non_Qi:
                    if random.random() < 0.5: G.add_edge(u, v)
                    if random.random() < 0.5: G.add_edge(v, u)
                    
            # Connessioni verso il livello successivo (tranne il nodo smallest_Qi)
            if i < w:
                next_layer = [f'v_{i+1}_{j}' for j in range(1, r + 1)]
                for u in layer_nodes:
                    if u != smallest_Qi: 
                        for v in next_layer:
                            G.add_edge(u, v)
                            
        G = self.assegnazione_costo_colore(G)
        k = self.calcolatore_k_mcpp()
        
        return G, k

    def estrazione_dati_istanza(self, G):
        """Estrae dal grafo le liste e i dizionari richiesti dal modello_KCSPP."""

        V = list(G.nodes()) # Lista dei nodi del grafo
        A = list(G.edges()) # Lista degli archi del grafo
        costi = nx.get_edge_attributes(G, 'costo') # Dizionario chiave: arco - valore: costo
        colori = nx.get_edge_attributes(G, 'colore') # dizionario chiave: arco - valore: colore
        return V, A, costi, colori

    def pulisci_grafo(self, G):
        """Toglie gli attributi relativi agli archi del grafo."""

        for u, v in G.edges():
            G.edges[u, v].clear()

    def salva_istanza_csv(self, nome_file: str, nome_istanza: str, nodi: int, archi: int, k: int):
        """Salve le informazioni dell'istanza in formato csv su un file specificato"""

        # Controllo dell'esistenza del file 
        file_esiste = os.path.isfile(nome_file)
        
        with open(nome_file, mode='a', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            
            # Definizione dell'intestazione (caso con file non pre esistente)
            if not file_esiste:
                writer.writerow(["Istanza", "Nodi", "Archi", "K_Limite"])
                
            # Scrivi i dati dell'istanza risolta
            writer.writerow([nome_istanza, nodi, archi, k])

    


# --- TEST DEL MODULO TESTER ---
if __name__ == "__main__":

    import matplotlib.pyplot as plt

    #-----------------------------------------------------------
    print("=================================================================\n")
    print("Generazione istanza Gruppo 1")
    new_tester = Tester()
    G, k = new_tester.genera_istanza_gruppo1(5, 4, 's', 't')    
    print(f"Nodi totali: {G.number_of_nodes()}")
    print(f"Archi totali: {G.number_of_edges()}")

    # Estrazione dati per lo script di ottimizzazione    
    V, A, costi, colori = new_tester.estrazione_dati_istanza(G)
    print(f"\nEsempio arco {A[10]}:")
    print(f"  Costo:  {costi[A[10]]}")
    print(f"  Colore: {colori[A[10]]}")

    new_tester.salva_istanza_csv("info_istanze.csv", "stanza_1_gruppo_1", len(V), len(A), k)

    #-------------------------------------------------------------------
    print("=================================================================\n")
    print("Generazione istanza Gruppo 2")
    G, k = new_tester.genera_istanza_gruppo2(3, 3, 's', 't')    
    print(f"Nodi totali: {G.number_of_nodes()}")
    print(f"Archi totali: {G.number_of_edges()}")

    # Estrazione dati per lo script di ottimizzazione    
    V, A, colori, costi = new_tester.estrazione_dati_istanza(G)
    print(f"\nEsempio arco {A[10]}:")
    print(f"  Costo:  {costi[A[10]]}")
    print(f"  Colore: {colori[A[10]]}")

    #----------------------------------------------------------------------
    print("=================================================================\n")
    print("Generazione istanza Gruppo 3")
    G, k = new_tester.genera_istanza_gruppo3(4, 5, 's', 't')    
    print(f"Nodi totali: {G.number_of_nodes()}")
    print(f"Archi totali: {G.number_of_edges()}")
    
    # Estrazione dati per lo script di ottimizzazione    
    V, A, colori, costi = new_tester.estrazione_dati_istanza(G)
    print(f"\nEsempio arco {A[5]}:")
    print(f"  Costo:  {costi[A[5]]}")
    print(f"  Colore: {colori[A[5]]}")

    # Disegna il grafo
    nx.draw(G, with_labels=True, node_color='lightgreen', font_weight='bold', node_size=700)
        
    # Mostra il grafico in una finestra
    plt.show()