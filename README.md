# QUANVAS a CRUD approach to do PORTFOLIO MANAGEMENT
*** 10 markets targeted, but BINANCE is deployed.

### This project is FOSS && I share my philosophy 
### There is no warrants, you have a program as is

4 STAGES for a portfolio in its lifecycle

(1) Generate portfolio based on the clients inputs
Risk-Profiles From conservative to Agressive Sharpe Ratio to Min VaR

(2) Notify daily performance 

(3) Change based on update-weights/change-amount-invested/reset-risk

(4) GoBacktoBasics and inform daily performance of portfolio to client

# COMMANDS.

## pip install -r requirements.txt
## see fakeClients.py that simulates data for clients


## 1-Step Create portfolio individually or macro 
```bash
python micro.py # enter input of each portfolio by hand

python fakeClients.py &&macro.py # reads  new_clients.xlsx as inputs
```
## 2-Notify Portolio Creation & its daily performance 
```bash
python welcome.py # Reads NewOnes Folder, sent email and moves'em to DATABASE
python bienvenido.py # same in spanish

python resume.py # via scanner.py that creates scanner.xlsx notify DATABASE performance
```
## 3-Change base on Update|Change-Amount|Reset-Risk
```bash
python ATM.py # as an ATM machine, if a change is done it moves the excel to Update/ folder
maintainer* script reads excel and maintainer_perform do it all in a loop

update.py # notify the change to the client and moves new the excel to DATABASE,
keep the old in OldPortfolio to track history
```
## Bonus - market report 
```bash
python marketReport.py # Give your clients a market watch
```

&& Criteria in order to develop

As soon as you achieve a functionality you will have to ask yourself before adding
it to your program the following questions:

What is the goal of the program? What problem you try to solve?

Describe it plain and simple.

what is the vision/approach you are following doing this?

is it readable/simple? 

what value it adds this version compared to the previous one?

how can i debug it? where does it crash?

what updates demands in the rest of the code in order to implement it?

Once you end a program, it will be the sum the whole process and not only
the last version.
