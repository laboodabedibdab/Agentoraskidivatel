import multiprocessing
import psutil
import os
import time
import random

def get_cpu_load():
    loads = psutil.cpu_percent(interval=0.1, percpu=True)
    return loads[:16]

def _worker_wrapper(func, core_index, args):
    p = psutil.Process(os.getpid())
    try:
        p.cpu_affinity([core_index])
    except AttributeError:
        pass
    func(*args)

def run_on_core(core_index, func, args=()):
    p = multiprocessing.Process(target=_worker_wrapper, args=(func, core_index, args))
    p.start()
    return p

# 3) Убивает функцию по объекту
def stop_worker(proc_obj):
    if proc_obj.is_alive():
        proc_obj.terminate()
        proc_obj.join()
        return True
    return False

def move_worker(proc_obj, new_core_index):
    """
    Меняет привязку (affinity) уже запущенного процесса к новому ядру.
    """
    if proc_obj.is_alive():
        try:
            p = psutil.Process(proc_obj.pid)
            p.cpu_affinity([new_core_index])
            return True
        except (psutil.NoSuchProcess, AttributeError):
            return False
    return False

_proc_cache = {}

def get_worker_load(proc_obj,a=False):
    """
    Узнает нагрузку воркера (multiprocessing.Process) мгновенно.
    Возвращает процент (0.0 - 100.0).
    """
    
    pid = proc_obj.pid
    
    if pid not in _proc_cache:
        try:
            p = psutil.Process(pid)
            p.cpu_percent(interval=0.1 if a else None)
            _proc_cache[pid] = p
            if a:
                return -1.0
            else:
                return get_worker_load(proc_obj,True)
        except psutil.NoSuchProcess:
            return -2.0
            
    try:
        return _proc_cache[pid].cpu_percent(interval=None)
    except psutil.NoSuchProcess:
        _proc_cache.pop(pid, None)
        return -3.0

def get_worker_core(proc_obj):
    """Возвращает список ядер, к которым привязан воркер"""
    if proc_obj and proc_obj.is_alive():
        try:
            p = psutil.Process(proc_obj.pid)
            return p.cpu_affinity()  # Вернет список, например [2]
        except (psutil.NoSuchProcess, AttributeError):
            return []
    return []

def heavy_work(name, hard):
    print(f"Агент {name} запущен на ядре...")
    #hard = random.randint(1,9)
    while True:
        _ = hard ** hard
        time.sleep(0.001)
# --- Пример использования (для теста) ---
workers=[]
if __name__ == "__main__":
    for thread_i in range(16):
        for worker_i in range(3):
            workers.append(run_on_core(thread_i, heavy_work, args=(f"Agent{str(worker_i)}", thread_i**(thread_i//2),)))
    print(f"Воркеры запущены Загрузка: {get_cpu_load()}")
    last_moved=0
    while True:
        time.sleep(0.2)
        thread_i,_=list(dict(sorted(enumerate(get_cpu_load()), key=lambda x: x[1])).items())[-1]
        max_worker=(0,0)
        print(thread_i)
        for worker in workers:
            if thread_i == psutil.Process(worker.pid).cpu_affinity()[0]:
                print("SUCCES")
                load = psutil.Process(worker.pid).cpu_percent(interval=0.1)
                print(load)
                if max_worker[0] < load:
                    max_worker = (load, worker)
            else:
                print(psutil.Process(worker.pid).cpu_affinity()[0])
        if max_worker[1].pid != last_moved:
            print(list(dict(sorted(enumerate(get_cpu_load()), key=lambda x: x[1])).items())[0][0])
            move_worker(max_worker[1],list(dict(sorted(enumerate(get_cpu_load()), key=lambda x: x[1])).items())[0][0])
            last_moved=max_worker[1].pid

    time.sleep(20)
    
    # # Перемещаем на ядро 1
    # if move_worker(worker, 1):
    #     print("Воркер успешно перемещен на ядро 1")
    
    # time.sleep(2)
    # print(f"Загрузка после перемещения: {get_cpu_load()}")
    
    # stop_worker(worker)