# Exemplo de Diagrama Mermaid

```mermaid
graph TD
A[Início] --> B[Chegada de Caminhões]
B --> C{Pátio Cheio?}
C --> |Sim| D[Caminhão Rejeitado]
C --> |Não| E[Caminhão Entra no Pátio]
E --> F[Descarregamento de Caminhões]
F --> G{Funcionários Disponíveis?}
G --> |Não| H[Aguardar]
G --> |Sim| I{Tempo Suficiente?}
I --> |Não| H
I --> |Sim| J[Descarregar Caminhão]
J --> K{Depósito Cheio?}
K --> |Sim| L[Parar Descarregamento]
K --> |Não| M[Continuar Descarregamento]
M --> N[Armazenamento no Depósito]
N --> O[Chegada de Vans]
O --> P{Todas as Vans Ocupadas?}
P --> |Sim| Q[Van Rejeitada]
P --> |Não| R[Van Entra na Fila]
R --> S[Carregamento das Vans]
S --> T{Funcionários Disponíveis?}
T --> |Não| H
T --> |Sim| U{Tempo Suficiente Dentro do Horário?}
U --> |Não| H
U --> |Sim| V[Carregar Van]
V --> W[Van Carregada]
W --> X[Saída das Vans para Entrega]
X --> Z[Fim]
