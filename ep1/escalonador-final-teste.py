import os

class BCP():
  def __init__(self, nome, textoPrograma):
    self.estado = "Pronto"
    self.nome = nome
    self.regX = 0
    self.regY = 0
    
    #aponta para o programa na memória
    self.textoPrograma = textoPrograma
    
    #aponta para a próxima instrução a ser executada
    self.programCounter = textoPrograma
    
    #usado para calcular tempo de espera em comandos "E/S"
    self.tempoDeEspera = 0

  def getEstado(self):
    return self.estado
  
  def setEstadoBloq(self):
    self.estado = "Bloq"
    self.tempoDeEspera = 2

  def setEstadoPronto(self):
    self.estado = "Pronto"

  def setEstadoExec(self):
    self.estado = "Exec"

  def setEstadoTerminado(self):
    self.estado = "Terminado"

  def getNome(self):
    return self.nome

  def setRegX(self,n):
    self.regX = n
    
  def getRegX(self):
    return self.regX
  
  def setRegY(self, n):
    self.regY = n

  def getRegY(self):
    return self.regY

  def setProgramCounter(self, n):
    self.programCounter = n

  def getProgramCounter(self):
    return self.programCounter

  def incrementaProgramCounter(self):
    self.programCounter += 1
    
  def getTextoPrograma(self):
    return self.textoPrograma

  #rotina que decrementa o tempo de espera de um processo bloqueado,
  #e retorna True caso ele já tenha terminado seu tempo de espera
  def espera(self):
    self.tempoDeEspera -= 1
    return self.tempoDeEspera == 0
       
class Processador():
  def __init__(self):
    self.regX = 0
    self.regY = 0
    self.programCounter = 0

  def setRegX(self, n):
    self.regX = n

  def getRegX(self):
    return self.regX

  def setRegY(self, n):
    self.regY = n

  def getRegY(self):
    return self.regY

  def setProgramCounter(self, n):
    self.programCounter = n

  def getProgramCounter(self):
    return self.programCounter

  def incrementaProgramCounter(self):
    self.programCounter += 1

  def carregaContexto(self, BCP):
    self.setProgramCounter(BCP.getProgramCounter())
    self.setRegX(BCP.getRegX())
    self.setRegY(BCP.getRegY())

class Escalonador():
  def __init__(self, path):
    #Mantém todos os processos que estão carregados na memória
    self.tabelaDeProcessos = []
    
    #Lista de processos com estado = "Pronto"
    self.processosPronto = []
    
    #Lista de processos com estado = "Bloq"
    self.processosBloq = []
    
    #Processador da máquina
    self.processador = Processador()

    #Memória da máquina
    self.memoria = []
    for _ in range(1024):
      self.memoria.append(0)

    self.totalProcessos = 0
    self.trocas = 0
    self.instrucoes = 0

    #variável que acompanha a quantidade de instruções executadas por processo
    self.quanta = 0
    
    #Leitura do arquivo quantum.txt
    # with open(os.path.join(path, "quantum.txt"), 'r') as arquivo:
    #   quantum = arquivo.readlines().pop().replace('\n', '')
    #   self.quantumMax = int(quantum)

    self.path = path
          
  def incrementaTrocas(self):
    self.trocas += 1

  def incrementaInstrucoes(self):
    self.instrucoes += 1
    self.quanta += 1

  def processosBloqAppend(self, n):
    self.processosBloq.append(n)

  def processosProntoAppend(self, n):
    self.processosPronto.append(n)

  def tabelaDeProcessosAppend(self, n):
    self.tabelaDeProcessos.append(n)

  def processosBloqRemove(self, n):
    self.processosBloq.remove(n)

  def processosProntoRemove(self, n):
    self.processosPronto.remove(n)

  def tabelaDeProcessosRemove(self, n):
    self.tabelaDeProcessos.remove(n)

  def processosProntoPrimeiro(self):
    return self.processosPronto.pop(0)

  def getProgramCounter(self):
    return self.processador.getProgramCounter()

  def setRegX(self, valor):
    self.processador.setRegX(valor)

  def setRegY(self, valor):
    self.processador.setRegY(valor)  
    
  def printEstatisticas(self, arquivo):
    arquivo.write("Média de trocas: %.2f\n" % (self.trocas / self.totalProcessos))
    arquivo.write("Media de instruções (por troca): %.2f\n" % (self.instrucoes / self.trocas))
    arquivo.write(f"Quantum: {self.quantumMax}\n")

  def incrementaProgramCounter(self):
    self.processador.incrementaProgramCounter()
  
  def trataProcessosBloq(self):
    for p in self.processosBloq:
      if p.espera():
        self.processosBloqRemove(p)
        p.setEstadoPronto()
        self.processosProntoAppend(p)
                              
  def escreveLinhaMemoria(self, pos, valor):
    self.memoria[pos] = valor

  def lerLinhaMemoria(self, pos):
    return self.memoria[pos]

  def limpaLinhaMemoria(self, pos):
    self.memoria[pos] = 0

  def limpaTextoPrograma(self, processo, saida):
    #como range vai até var2-1, somamos 1 à saída
    for i in range(processo.getTextoPrograma(), saida + 1):
      self.limpaLinhaMemoria(i)

  def existeProcessos(self):
    return self.tabelaDeProcessos != []
    
  def carregaProgramas(self):
    #variável que acompanhará as linhas de self.memoria que já foram carregadas
    linhaMemoria = 0
    #contém todos os arquivos da pasta path em ordem alfabética
    arquivos = sorted(os.listdir(self.path))

    #lê os todos os arquivos da pasta path, exceto quantum.txt. Como sabemos
    #que os arquivos são númerados, sabemos que quantum.txt é o último arquivo
    i = 0      
    while(arquivos[i] != "quantum.txt"):
      with open(os.path.join(self.path, arquivos[i]), 'r') as arquivo:
        linhas = arquivo.readlines()
        nome = linhas.pop(0).replace('\n', '')
  
        textoPrograma = linhaMemoria
        comando = ""
        while (comando != "SAIDA" and linhas != []):
          comando = linhas.pop(0)
          self.escreveLinhaMemoria(linhaMemoria,comando)
          linhaMemoria += 1         

        self.tabelaDeProcessosAppend(BCP(nome, textoPrograma))
        self.totalProcessos += 1

      i += 1

  def interrupcao(self):
    return self.quanta < self.quantumMax

  def zeraQuanta(self):
    self.quanta = 0

  def getQuanta(self):
    return self.quanta

  def carregaContexto(self, BCP):
    self.processador.carregaContexto(BCP)
         
  def executar(self, quantumMax):
      self.quantumMax = quantumMax
      log_file_name = f"log{self.quantumMax:02d}.txt"
      with open(f"C:\sistemas-informacao\so-ACH2044\ep1\logs\{log_file_name}", 'w') as log_file:
        
        for p in self.tabelaDeProcessos:
          log_file.write("Carregando: %s\n" % p.getNome())
          self.processosProntoAppend(p)

        if self.processosPronto == []:
          return #verificando se há processos na fila

        #enquanto self.tabelaDeProcessos não estiver vazia
        while(self.existeProcessos()):
          #O processo é retirado da fila de processosPronto para sua execução
          processoAtual = self.processosProntoPrimeiro()
          
          #o estado do processo é alterado para "Exec"
          processoAtual.setEstadoExec()

          #o processador recebe e carrega o contexto do BCP
          self.carregaContexto(processoAtual)
          
          log_file.write(f"Executando {processoAtual.getNome()}\n")



          #Este while executa /quanta/ instruções de processoAtual
          #Quando self.quanta >= self.quantumMax, self.interrupcao() retorna false
          # print(processoAtual.getEstado())
          while(self.interrupcao() and processoAtual.getEstado() == "Exec"):
            
            comando = self.lerLinhaMemoria(self.getProgramCounter())
      
            if comando == "COM\n":        
              #O "COM" não foi representado com nada em especifíco,
              #apenas passa-se para a próxima instrução
              
              #Este método tanto contabiliza o número de instruções totais executadas,
              #quanto incrementa o quanta
              self.incrementaInstrucoes()
              
            elif comando == "SAIDA\n":            
              #Removemos o processo da tabelaDeProcessos
              self.tabelaDeProcessosRemove(processoAtual)
              
              #Note que o processo já não está na fila de prontos,
              #tampouco na de bloqueados, logo não precisamos excluir destas filas

              processoAtual.setEstadoTerminado()#evita que ele seja recolocado na fila de Prontos
      
              #Liberamos as posições de memória que continham o processo
              self.limpaTextoPrograma(processoAtual, self.getProgramCounter())        
              
              log_file.write(f"{processoAtual.getNome()} terminado. X = {processoAtual.getRegX()} Y = {processoAtual.getRegY()}\n")
              self.incrementaInstrucoes()
              break
              
            elif comando == "E/S\n":
              log_file.write(f"E/S iniciada em {processoAtual.getNome()}\n")
              
              processoAtual.setEstadoBloq()
              self.incrementaInstrucoes()
              
            else:
              valor = int(comando[2:].replace('\n',''))
              
              if comando[0] == 'X':
                self.setRegX(valor)#passando valor ao processador
                processoAtual.setRegX(valor)#atualizando o registrador do BCP
                
              else:#comando[0] = 'Y'
                self.setRegY(valor)
                processoAtual.setRegY(valor)

              self.incrementaInstrucoes()

            #O PC do processador avança para a próxima linha
            self.incrementaProgramCounter()

            #O pc do BCP acompanha a atualização do PC do processador
            processoAtual.incrementaProgramCounter()
            
          #fim do while que lê /quanta/ instruções
          log_file.write(f"Interrompendo {processoAtual.getNome()} após {self.quanta} instruções\n")
          self.zeraQuanta()
          
          #Uma interrupção acarreta em uma troca de contexto, computamos para as estatísticas
          self.incrementaTrocas()

          #Ao fim da instrução, tratamos a fila de bloqueados
          #O método já transfere um processo da fila de bloqueados
          #para a fila de prontos quando necessário
          self.trataProcessosBloq()
          #Note que neste momento, caso a instrução tenha sido uma E/S, o processo ainda não
          #está na fila de bloqueados, seu tempo de espera não é contabilizado
            
          if processoAtual.getEstado() == "Exec":
            #Processo é recolocado ao final da fila de Prontos
            processoAtual.setEstadoPronto()
            self.processosProntoAppend(processoAtual)
      
          elif processoAtual.getEstado() == "Bloq":
            self.processosBloqAppend(processoAtual)

          #Processos com estado "Terminado" não são salvos em qualquer fila,
          #ao sobrescrever processoAtual eles já não estão guardados em qualquer lugar

          #A rotina abaixo trata o caso de todos
          #os processos restantes estarem na fila de Bloq
          
          #Caso ainda haja processos em tabelaDeProcessos
          if self.existeProcessos():
            #Enquanto a lista de Prontos estiver vazia
            while self.processosPronto == []:
              self.trataProcessosBloq()

        #fim do while existeProcessos(), self.tabelaDeProcessos = []  
        self.printEstatisticas(log_file)
    
for i in range(1,21):
  escalonador = Escalonador("C:\sistemas-informacao\so-ACH2044\ep1\programas")
  escalonador.carregaProgramas()
  escalonador.executar(i)