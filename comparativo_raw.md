# Comparativo bruto — Groq vs Gemini

## Síndico / Condomínio — "Como dividir o custo de energia entre os moradores de abril?"

### groq
- Latência: 2.41s
- Tokens: in=1187 out=632 total=1819
- Resposta:

```
**Divisão do custo de energia elétrica dos carregadores EV – Abril**

| Apartamento | Consumo (kWh) | Valor (R$) |
|-------------|--------------|-----------|
| 42          | 45 kWh       | 32,49 |
| 87          | 38 kWh       | 27,44 |
| 15          | 52 kWh       | 37,55 |

### Como calcular a participação de cada morador

1. **Somar o consumo total**  
   \[
   45 + 38 + 52 = 135\ \text{kWh}
   \]

2. **Somar o custo total**  
   \[
   32,49 + 27,44 + 37,55 = 97,48\ \text{R\$}
   \]

3. **Obter o custo por kWh** (valor médio da tarifa aplicada)  
   \[
   \frac{97,48\ \text{R\$}}{135\ \text{kWh}} \approx 0,722\ \text{R\$ / kWh}
   \]

4. **Calcular o valor de cada apartamento**  
   - **Apto 42**: 45 kWh × 0,722 R$/kWh ≈ **R$ 32,49** (já informado)  
   - **Apto 87**: 38 kWh × 0,722 R$/kWh ≈ **R$ 27,44** (já informado)  
   - **Apto 15**: 52 kWh × 0,722 R$/kWh ≈ **R$ 37,55** (já informado)

> **Resultado:** Cada morador paga exatamente o valor já apresentado, pois o cálculo já está baseado no consumo real de cada unidade.

### Próximos passos recomendados

- **Gerar relatório mensal**: Acesse o **SEMS+ Portal** (ou o app PV Master) → “Relatórios de Consumo” → selecione o período “Abril 2026” → exporte em PDF/Excel para enviar ao conselho e aos condôminos.
- **Comunicar os valores**: Envie o relatório por e‑mail ou inclua no boletim do condomínio, indicando a fórmula utilizada (custo total ÷ consumo total) para transparência.
- **Planejar a próxima cobrança**: Caso deseje automatizar a divisão, configure no SEMS+ a geração automática de faturas mensais por unidade.

Se precisar de ajuda para exportar o relatório ou configurar a cobrança automática, estou à disposição!
```

### gemini
- Latência: 165.94s
- Tokens: in=1178 out=1011 total=2189
- Resposta:

```
Olá! Para facilitar a gestão e o rateio das despesas do condomínio, os dados de consumo e os valores individuais referentes ao mês de **abril** calculados pela plataforma SEMS+ são:

### **Demonstrativo de Consumo — Abril**
* **Apartamento 42:** 45 kWh — **R$ 32,49**
* **Apartamento 87:** 38 kWh — **R$ 27,44**
* **Apartamento 15:** 52 kWh — **R$ 37,55**
---
* **Total Geral do Mês:** 135 kWh — **R$ 97,48**

---

### **Como emitir o relatório no SEMS+ para cobrança:**
1. Acesse o **SEMS Portal** (navegador) ou o aplicativo com sua conta de administrador.
2. Vá até a aba **Gestão de EV Charger / Relatórios de Consumo**.
3. Selecione o período desejado (ex: 01/04 a 30/04) e exporte o arquivo em **Excel/CSV** ou **PDF**.
4. Envie o relatório diretamente para a administradora do condomínio incluir os valores na taxa condominial de cada morador.

Gostaria que eu te oriente sobre como exportar esse relatório detalhado na plataforma ou como cadastrar novos cartões RFID para outros moradores?
```

## Técnico / Instalador — "O carregador está mostrando o erro E-04. O que significa? Como resolver?"

### groq
- Latência: 2.90s
- Tokens: in=1119 out=433 total=1552
- Resposta:

```
**AR​IA – GoodWe Brasil**  

Olá, técnico!  

O código de erro **E‑04** não está contemplado na documentação que tenho disponível aqui (manuais de comissionamento, indicadores de status e procedimentos de manutenção).  

**Próximos passos recomendados**

1. **Verifique a tela de diagnóstico** – alguns carregadores exibem detalhes adicionais ao pressionar o botão **“Info”** ou ao acessar o menu de diagnóstico via aplicativo **SolarGo**. Anote se aparece alguma mensagem complementar.  
2. **Reinicie o carregador**  
   - Desligue o carregador na alimentação principal (certifique‑se de que o RCBO esteja aberto).  
   - Aguarde ≈ 30 segundos e religue.  
   - Observe se o erro persiste.  
3. **Cheque as conexões elétricas**  
   - Confirme que todos os cabos de alimentação e de comunicação estejam bem crimpados e sem danos.  
   - Verifique se o interruptor upstream está aberto antes de iniciar a manutenção.  
4. **Consulte o suporte técnico da GoodWe**  
   - Como o código não está documentado nos manuais que possuo, a melhor solução é abrir um chamado técnico.  
   - Envie as seguintes informações: modelo do carregador, firmware instalado, descrição completa do erro (incluindo tempo de ocorrência e condições de operação) e fotos da tela de erro.  

**Contato do suporte humano**  
- **E‑mail:** suporte@goodwe.com.br  
- **Telefone:** 0800 123 4567 (horário comercial)  

Caso precise de auxílio para abrir o chamado ou para coletar os dados acima, estou à disposição!
```

### gemini
- Latência: 63.84s
- Tokens: in=1092 out=1000 total=2092
- Resposta:

```
No contexto dos manuais disponíveis no momento, o código de erro específico **E-04** não possui detalhamento direto no resumo técnico. 

Para um diagnóstico preciso como instalador/técnico, siga o procedimento recomendado:

1. **Acesse o App SolarGo:** Conecte-se ao carregador via aplicativo SolarGo no perfil de instalador. O aplicativo exibirá a descrição completa do erro, causas prováveis e leituras de parâmetros em tempo real (como sobretensão, subtensão, falha de aterramento ou sobrecorrente).
2. **Verifique os LEDs do Carregador:** Confirme o comportamento da luz indicadora (por exemplo, LED **Vermelho LIGADO** indica falha do sistema).
3. **Reset do Equipamento:** Para tentar limpar a falha temporária, desative o disjuntor de proteção (*RCBO*) a montante (*upstream*), aguarde cerca de 1 minuto e religue o sistema.

Se o erro **E-04** persistir no aplicativo SolarGo após o restart, recomendo acionar diretamente o **Suporte Técnico da GoodWe Brasil** munido do número de série (SN) do carregador para abertura de chamado.

Deseja orientações sobre como realizar o diagnóstico de parâmetros de rede ou leitura de status no SolarGo?
```

## Morador — "Como agendar uma recarga?"

### groq
- Latência: 1.61s
- Tokens: in=1127 out=472 total=1599
- Resposta:

```
**Como agendar a recarga do seu EV Charger (GoodWe)**  

1. **Abra o aplicativo**  
   - **SEMS Portal** (Android/iOS) ou **PV Master**.  
   - Faça login com seu usuário e senha cadastrados.

2. **Selecione a estação**  
   - Na lista de carregadores, escolha a vaga que deseja usar (ex.: *Vaga 12 – 7 kW livres*).

3. **Acesse a opção “Agendar Recarga”**  
   - Geralmente está no menu → “Carregamento” → “Agendar”.  

4. **Defina os parâmetros do agendamento**  
   - **Data** e **horário de início** da recarga.  
   - **Duração** ou **energia desejada** (kWh) – se o seu carregador permitir.  
   - **Modo de carregamento** (rápido = 7 kW ou outro, conforme a potência disponível).  

5. **Confirme o agendamento**  
   - Revise as informações e toque em **“Confirmar”**.  
   - O aplicativo mostrará um resumo e enviará uma notificação de confirmação.

6. **Acompanhe o status**  
   - Na tela da vaga, você verá o horário programado e, quando chegar a hora, o carregador iniciará automaticamente.  
   - Caso queira alterar ou cancelar, basta retornar ao mesmo menu e escolher “Editar” ou “Cancelar”.

---

**Próximo passo:**  
Abra agora o **SEMS Portal** ou **PV Master**, siga os passos acima e agende sua primeira recarga. Se encontrar alguma dificuldade (por exemplo, a opção “Agendar” não aparece), avise-me que eu ajudo a resolver!
```

### gemini
- Latência: 12.26s
- Tokens: in=1127 out=855 total=1982
- Resposta:

```
Olá! Agendar a recarga do seu veículo elétrico é muito simples e você pode fazer tudo pelo celular através do aplicativo **SEMS Portal** (ou SEMS+).

Siga este passo a passo para programar seu agendamento:

1. **Abra o aplicativo SEMS Portal** no seu smartphone e faça o login.
2. **Selecione o seu carregador** na tela principal de dispositivos.
3. Acesse as **Configurações de Carregamento** e escolha a opção de **Agendamento** (ou *Horário Programado*).
4. **Defina o horário** desejado para o início e término da recarga (uma ótima opção para carregar em horários com tarifas de energia mais baixas).
5. **Conecte o cabo do carregador ao seu veículo**. O processo começará automaticamente no horário configurado.

📌 *Nota:* A **Vaga 12** está disponível no momento com **7 kW** liberados.

Precisa de ajuda para baixar o aplicativo ou tem alguma dúvida sobre a conexão do cabo? Estou à disposição!
```
