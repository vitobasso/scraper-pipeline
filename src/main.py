from src.flows import yahoo
import scheduler

if __name__ == '__main__':
    for i in range(100):
        scheduler.schedule_next(yahoo.flow())
    # proxy = random_proxy()
    # yahoo.compile_data()
    pass
