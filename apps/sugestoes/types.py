from enum import Enum

class Status_Sugestao(str, Enum):
    ativa     = 'ativa'     # padrao
    cancelada = 'cancelada' # cancelada por autor da sugestao

    # acoes por proprietario do problema
    rejeitada = 'rejeitada'
    aceita    = 'aceita'    # aceita mas ainda nao implementada
    aplicada  = 'aplicada'  # aceita e implementada
