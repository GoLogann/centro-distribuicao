import simpy
import random

# Definição das variáveis e parâmetros do sistema
CAMINHOES_CAPACIDADE = 20  # Capacidade máxima do caminhão em m³
VANS_CAPACIDADE = 8  # Capacidade máxima da van em m³
DEPOSITO_CAPACIDADE = 300  # Capacidade do depósito em m³
FUNCIONARIOS = 6  # Número total de funcionários
HORAS_POR_DIA = 8  # Horas de operação por dia

class CentroDistribuicao:
    def __init__(self, env):
        self.env = env
        self.fila_caminhoes = []  # Fila de caminhões esperando para descarregar
        self.fila_vans = []  # Fila de vans esperando para carregar
        self.deposito = 0  # Volume atual no depósito
        self.funcionarios_disponiveis = FUNCIONARIOS  # Funcionários disponíveis

    def receber_caminhao(self):
        if len(self.fila_caminhoes) < 5:  # Capacidade do pátio
            # Gerar caminhão com volume aleatório
            volume_carga = random.triangular(0.03, 0.12, 1.0) * CAMINHOES_CAPACIDADE
            caixas = int(volume_carga / random.triangular(0.03, 0.12, 1.0))
            caminhao = {'volume': volume_carga, 'caixas': caixas}
            self.fila_caminhoes.append(caminhao)
            print(f'{self.env.now:.2f}: Caminhão chegou com {volume_carga:.2f}m³')
        else:
            print(f'{self.env.now:.2f}: Caminhão foi rejeitado (pátio cheio)')

    def receber_van(self):
        if len(self.fila_vans) < 4:  # Número máximo de vans
            # Criar uma van
            van = {'volume': 0, 'caixas': 0}
            self.fila_vans.append(van)
            print(f'{self.env.now:.2f}: Van chegou')
        else:
            print(f'{self.env.now:.2f}: Van foi rejeitada (todas as vans ocupadas)')

def chegada_caminhoes(env, centro_distribuicao):
    while True:
        # Intervalo de chegada dos caminhões
        yield env.timeout(random.expovariate(1/15.0))
        # Criar caminhão
        centro_distribuicao.receber_caminhao()

def processo_descarregamento(env, centro_distribuicao):
    while True:
        # Verificar se está dentro do horário de operação
        if env.now % 24 < HORAS_POR_DIA:
            # Verificar se há caminhões na fila e funcionários disponíveis
            if len(centro_distribuicao.fila_caminhoes) > 0 and centro_distribuicao.funcionarios_disponiveis >= 4:
                caminhao = centro_distribuicao.fila_caminhoes.pop(0)
                centro_distribuicao.funcionarios_disponiveis -= 4
                # Calcular o tempo necessário para descarregar, considerando as caixas
                tempo_descarregamento = caminhao['caixas'] / 12.0
                # Verificar se o descarregamento pode ser concluído antes do final do expediente
                if env.now % 24 + tempo_descarregamento <= HORAS_POR_DIA:
                    yield env.timeout(tempo_descarregamento)
                    centro_distribuicao.funcionarios_disponiveis += 4
                    centro_distribuicao.deposito += caminhao['volume']
                    print(f'{env.now:.2f}: Caminhão descarregado ({caminhao["volume"]:.2f}m³)')
                else:
                    # Se não puder ser concluído, re-coloca o caminhão na fila e espera o próximo dia útil
                    centro_distribuicao.fila_caminhoes.insert(0, caminhao)
                    yield env.timeout(24 - (env.now % 24))  # Espera até o próximo dia útil
            else:
                yield env.timeout(1)  # Esperar 1 hora antes de tentar novamente
        else:
            # Fora do horário de operação, espera até o próximo dia útil
            yield env.timeout(24 - (env.now % 24))

def processo_carregamento_vans(env, centro_distribuicao):
    while True:
        # Verificar se está dentro do horário de operação
        if env.now % 24 < HORAS_POR_DIA:
            # Verificar se há vans na fila e se há volume disponível no depósito
            if len(centro_distribuicao.fila_vans) > 0 and centro_distribuicao.deposito > 0 and centro_distribuicao.funcionarios_disponiveis >= 2:
                van = centro_distribuicao.fila_vans.pop(0)
                centro_distribuicao.funcionarios_disponiveis -= 2

                # Calcular o volume que pode ser carregado na van
                volume_carregar = min(VANS_CAPACIDADE, centro_distribuicao.deposito)
                if volume_carregar > 0:
                    # Calcular o número de caixas baseado no volume
                    caixas = int(volume_carregar / random.triangular(0.03, 0.12, 1.0))
                    tempo_carregamento = caixas / 20.0
                    # Verificar se o carregamento pode ser concluído antes do final do expediente
                    if env.now % 24 + tempo_carregamento <= HORAS_POR_DIA:
                        yield env.timeout(tempo_carregamento)
                        centro_distribuicao.deposito -= volume_carregar
                        print(f'{env.now:.2f}: Van carregada ({volume_carregar:.2f}m³)')
                    else:
                        # Se não puder ser concluído, re-coloca a van na fila e espera o próximo dia útil
                        centro_distribuicao.fila_vans.insert(0, van)
                        yield env.timeout(24 - (env.now % 24))  # Espera até o próximo dia útil

                centro_distribuicao.funcionarios_disponiveis += 2
            else:
                yield env.timeout(1)  # Esperar 1 hora antes de tentar novamente
        else:
            # Fora do horário de operação, espera até o próximo dia útil
            yield env.timeout(24 - (env.now % 24))

def saida_vans(env, centro_distribuicao):
    while True:
        # Intervalo de saída das vans para entrega, usando uma distribuição normal truncada para evitar tempos negativos
        tempo_saida = max(0, random.gauss(4, 1))
        yield env.timeout(tempo_saida)
        centro_distribuicao.receber_van()

# Criação do ambiente e processos
env = simpy.Environment()
centro_distribuicao = CentroDistribuicao(env)

# Processos
env.process(chegada_caminhoes(env, centro_distribuicao))
env.process(processo_descarregamento(env, centro_distribuicao))
env.process(processo_carregamento_vans(env, centro_distribuicao))
env.process(saida_vans(env, centro_distribuicao))

# Execução da simulação
env.run(until=30*24)  # Simular 30 dias
