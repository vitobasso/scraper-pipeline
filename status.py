from src.active_pipes import pipes
from src.scheduler import report

csv_acoes_br = 'input/ticker-list/acoes-br.csv'

if __name__ == '__main__':
    report(pipes)

