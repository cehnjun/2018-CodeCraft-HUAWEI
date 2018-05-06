# coding=utf-8
import datetime
import random
import copy
import math


def first_fit(server, flavor_to_put, server_cpu, server_mem, resource_to_op):
    server_min = len(flavor_to_put) + 1
    Temperature = 100.0
    Temperature_min = 1.0
    rate = 0.999
    flavor_sequence = range(len(flavor_to_put))
    #list_flavor = sorted(flavor_to_put, key=lambda item: item[resource_to_op], reverse=True)

    while Temperature > Temperature_min:
        server_use = copy.deepcopy(server)
        random.shuffle(flavor_sequence)
        new_flavor_to_put = copy.deepcopy(flavor_to_put)
        new_flavor_to_put[flavor_sequence[0]],new_flavor_to_put[flavor_sequence[1]] = new_flavor_to_put[flavor_sequence[1]],new_flavor_to_put[flavor_sequence[0]]
        for flavor in new_flavor_to_put:
            j = 1
            while (server_use[j]['CPU'] - flavor['CPU'] < 0) or (server_use[j]['MEM'] - flavor['MEM'] < 0):
                j += 1
                if j not in server_use:
                    server_use[j] = dict(CPU=server_cpu, MEM=server_mem, VM=[])
            server_use[j]['CPU'] -= flavor['CPU']
            server_use[j]['MEM'] -= flavor['MEM']
            server_use[j]['VM'].extend([flavor['NAME']])

        if resource_to_op == 'CPU':
            server_num = len(server_use) - 1 + (1-float(server_use[j]['CPU'])/float(server_cpu))
        else:
            server_num = len(server_use) - 1 + (1-float(server_use[j]['MEM'])/float(server_mem))

        if server_num < server_min:
            server_min = copy.deepcopy(server_num)
            server_new = copy.deepcopy(server_use)
            flavor_to_put = copy.deepcopy(new_flavor_to_put)
        else:
            k = random.random()
            if math.exp(float(server_min - server_num)/Temperature) > k:
                server_min = copy.deepcopy(server_num)
                server_new = copy.deepcopy(server_use)
                flavor_to_put = copy.deepcopy(new_flavor_to_put)

        Temperature *= rate

    return server_new


def predict_vm(ecs_line, input_line):
    # Do your work from here#
    result = []
    if ecs_line is None:
        print 'ecs information is none'
        return result
    if input_line is None:
        print 'input file information is none'
        return result

    ecs_lines = []
    for line in ecs_line:
        line = line.strip()
        if line != '':
            ecs_lines.append(line)

    input_lines = []
    for lines in input_line:
        lines = lines.strip()
        if lines != '':
            input_lines.append(lines)
    

    train_beginTime = datetime.datetime.strptime(ecs_lines[0].split()[2], '%Y-%m-%d')
    train_endTime = datetime.datetime.strptime(ecs_lines[-1].split()[2], '%Y-%m-%d')

    date_span = (train_endTime - train_beginTime).days + 1
    ecs_data = dict()
    for ecs in set([line.split()[1] for line in ecs_lines]):
        ecs_data[ecs] = [0]*date_span

    for ecs in [line.split() for line in ecs_lines]:
        ecs_time = datetime.datetime.strptime(ecs[2], '%Y-%m-%d')
        ecs_data[ecs[1]][(ecs_time - train_beginTime).days] = ecs_data[ecs[1]][(ecs_time - train_beginTime).days] + 1


    predict_beginTime = datetime.datetime.strptime(input_lines[-2].split()[0], '%Y-%m-%d')
    predict_endTime = datetime.datetime.strptime(input_lines[-1].split()[0], '%Y-%m-%d')

    date_delta = (predict_endTime - predict_beginTime).days + 1

    predict_result = dict()
    for vm in input_lines[2:-3]:
        predict_result[vm.split()[0]] = int(math.ceil(sum(ecs_data[vm.split()[0]][-(date_delta*2):])/2.0)) + 1

    flavor_list = []
    for vm in input_lines[2:-3]:
        flavor_list.extend([{'NAME': vm.split()[0], 'CPU': int(vm.split()[1]), 'MEM': int(vm.split()[2])}] * predict_result[vm.split()[0]])

    SERVER_CPU = int(input_lines[0].split()[0])
    SERVER_MEM = int(input_lines[0].split()[1]) * 1024

    server_dict = {1: {'CPU': SERVER_CPU, 'MEM': SERVER_MEM, 'VM': []}}
    server_result = first_fit(server_dict, flavor_list, SERVER_CPU, SERVER_MEM, input_lines[-3].strip())
    result = [len(flavor_list)]
    for vm in input_lines[2:-3]:
        result.append(vm.split()[0] + ' ' + str(predict_result[vm.split()[0]]))

    result.append('\n'+str(len(server_result)))
    for key in server_result:
        line = str(key) + ' ' + ' '.join(
            vm + ' ' + str(server_result[key]['VM'].count(vm)) for vm in set(server_result[key]['VM']))
        result.append(line)

    return result