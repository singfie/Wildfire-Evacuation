#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 10:43:03 2019

@author: fietekrutein

This is a deterministic base case model formulation of the SIREN evacuation scenario
This base case scenario is going to be used for an implementation of a stochastic model in another iteration

"""
# Import of the pyomo module
from pyomo.environ import *
import random
import numpy as np

random.seed(123)
 
# Creation of a Concrete Model
model = ConcreteModel()

## Define sets ##
#  Sets
#       i   vessels              / Queen of Capilano, Queen of Cumberland, Island sky, etc. /
#       a   storage locations    / Horseshow Bay, Snug Cove, Swartz Bay, etc. / 
#       s   process steps        / arrival at location, docking, loading, undocking /
#       m   evacuation locations / Snug Cove, Bowen Bay, Tunstall Bay, etc. /
#       k   docks                / Ferry terminal, Marina, fishing wharf, beach, private dock /
#       xi  demand scenarios     / 1,2,3,4,5 /;  
model.i = Set(initialize=['Queen of Capilano','Queen of Cumberland', 'Island Sky', 'Queen of Alberni', 'Queen of Coquitlam', 
                          'Pilot 1', 'Pilot 2', 'Pilot 3'], ordered = False, doc='Vessels')
model.i.pprint() # cross check

model.a = Set(initialize=['Horseshoe Bay','Snug Cove', 'Swartz Bay', 'Tsawassen', 'Tsawassen - Duke Point', 
                          'Snug Cove - Horseshoe Bay', 'Langdale - Horseshoe Bay'], doc='Storage locations/routes')
model.a.pprint() # cross check

model.k = Set(initialize=['Ferry terminal Snug Cove', 'Marina Snug Cove', 'Beach 1 Snug Cove', 
                          'Private dock 1 Snug Cove', 'Beach 1 Bowen Bay', 'Beach 2 Bowen Bay', 'Beach 1 Tunstall Bay'], doc='Docks at evacuation location')
model.k.pprint()

## Define parameters ##

model.P = Param(initialize=10000, doc = 'Penalty for not evacuating persons')
model.P.pprint() # cross check

model.B = Param(initialize=200, doc = 'Upper bound for evacuation time')
model.B.pprint() # criss check

model.M = Param(initialize = 9999, doc = 'A very large number')
model.M.pprint()

model.Mtild = Param(initialize = 9999, doc = 'A very large number')
model.Mtild.pprint()

# Vessels
model.v = Param(model.i, initialize={'Queen of Capilano': 12.5 ,
                                         'Queen of Cumberland':12, 
                                         'Island Sky': 14.5, 
                                         'Queen of Alberni': 21, 
                                         'Queen of Coquitlam': 20.5,
                                         'Pilot 1': 25,
                                         'Pilot 2': 25,
                                         'Pilot 3': 25}, doc='Max speed of vessel i')
model.v.pprint() # cross check
    
model.cap = Param(model.i, initialize={'Queen of Capilano': 900, 
                                            'Queen of Cumberland':900, 
                                            'Island Sky': 800, 
                                            'Queen of Alberni': 1720, 
                                            'Queen of Coquitlam': 1720,
                                            'Pilot 1': 35,
                                            'Pilot 2': 35,
                                            'Pilot 3': 35}, doc='Max passenger capacity of vessel i')
model.cap.pprint() # cross check

model.c = Param(model.i, initialize={'Queen of Capilano': 0 ,
                                        'Queen of Cumberland':5000, 
                                        'Island Sky': 2000, 
                                        'Queen of Alberni': 10000, 
                                        'Queen of Coquitlam': 10000,
                                        'Pilot 1': 2000,
                                        'Pilot 2': 2000,
                                        'Pilot 3': 2000}, doc='Holding cost of vessel i')
model.c.pprint() # cross check
    
model.b = Param(model.i, initialize= 1, doc = 'variable cost per time unit')
model.b.pprint() # cross check

model.lr = Param(model.i, initialize={'Queen of Capilano': 6000 ,
                                                'Queen of Cumberland':6000,
                                                'Island Sky': 3000, 
                                                'Queen of Alberni': 10000, 
                                                'Queen of Coquitlam': 10000,
                                                'Pilot 1': 300,
                                                'Pilot 2': 300,
                                                'Pilot 3': 300}, doc='Max loading rate of vessel i per minute')
model.lr.pprint() # cross check

model.dock = Param(model.i, initialize={'Queen of Capilano': 0.05 ,
                                                'Queen of Cumberland': 0.05,
                                                'Island Sky': 0.05, 
                                                'Queen of Alberni': 0.07, 
                                                'Queen of Coquitlam': 0.07,
                                                'Pilot 1': 0.02,
                                                'Pilot 2': 0.02,
                                                'Pilot 3': 0.02}, doc='min docking time of vessel i')
model.dock.pprint() # cross check

model.undock = Param(model.i, initialize={'Queen of Capilano': 0.05 ,
                                                  'Queen of Cumberland': 0.05,
                                                  'Island Sky': 0.05, 
                                                  'Queen of Alberni': 0.07, 
                                                  'Queen of Coquitlam': 0.07,
                                                  'Pilot 1': 0.02,
                                                  'Pilot 2': 0.02,
                                                  'Pilot 3': 0.02}, doc='min undocking time of vessel i')
model.undock.pprint()

    
# compatibility between docks and vessels
dtab= {
       ('Ferry terminal Snug Cove', 'Queen of Capilano'): 1,
       ('Ferry terminal Snug Cove', 'Queen of Cumberland'): 1,
       ('Ferry terminal Snug Cove', 'Island Sky'): 1,
       ('Ferry terminal Snug Cove', 'Queen of Alberni'): 1,
       ('Ferry terminal Snug Cove', 'Queen of Coquitlam'): 1,
       ('Ferry terminal Snug Cove', 'Pilot 1'): 0,
       ('Ferry terminal Snug Cove', 'Pilot 2'): 0,
       ('Ferry terminal Snug Cove', 'Pilot 3'): 0,
       ('Marina Snug Cove', 'Queen of Capilano'): 0,
       ('Marina Snug Cove', 'Queen of Cumberland'): 0,
       ('Marina Snug Cove', 'Island Sky'): 0,
       ('Marina Snug Cove', 'Queen of Alberni'): 0,
       ('Marina Snug Cove', 'Queen of Coquitlam'): 0,
       ('Marina Snug Cove', 'Pilot 1'): 1,
       ('Marina Snug Cove', 'Pilot 2'): 1,
       ('Marina Snug Cove', 'Pilot 3'): 1,
       ('Beach 1 Snug Cove', 'Queen of Capilano'): 0,
       ('Beach 1 Snug Cove', 'Queen of Cumberland'): 0,
       ('Beach 1 Snug Cove', 'Island Sky'): 0,
       ('Beach 1 Snug Cove', 'Queen of Alberni'): 0,
       ('Beach 1 Snug Cove', 'Queen of Coquitlam'): 0,
       ('Beach 1 Snug Cove', 'Pilot 1'): 1,
       ('Beach 1 Snug Cove', 'Pilot 2'): 1,
       ('Beach 1 Snug Cove', 'Pilot 3'): 1,
       ('Private dock 1 Snug Cove', 'Queen of Capilano'): 0,
       ('Private dock 1 Snug Cove', 'Queen of Cumberland'): 0,
       ('Private dock 1 Snug Cove', 'Island Sky'): 0,
       ('Private dock 1 Snug Cove', 'Queen of Alberni'): 0,
       ('Private dock 1 Snug Cove', 'Queen of Coquitlam'): 0,
       ('Private dock 1 Snug Cove', 'Pilot 1'): 1,
       ('Private dock 1 Snug Cove', 'Pilot 2'): 1,
       ('Private dock 1 Snug Cove', 'Pilot 3'): 1,
       ('Beach 1 Bowen Bay', 'Queen of Capilano'): 0,
       ('Beach 1 Bowen Bay', 'Queen of Cumberland'): 0,
       ('Beach 1 Bowen Bay', 'Island Sky'): 0,
       ('Beach 1 Bowen Bay', 'Queen of Alberni'): 0,
       ('Beach 1 Bowen Bay', 'Queen of Coquitlam'): 0,
       ('Beach 1 Bowen Bay', 'Pilot 1'): 1,
       ('Beach 1 Bowen Bay', 'Pilot 2'): 1,
       ('Beach 1 Bowen Bay', 'Pilot 3'): 1,
       ('Beach 2 Bowen Bay', 'Queen of Capilano'): 0,
       ('Beach 2 Bowen Bay', 'Queen of Cumberland'): 0,
       ('Beach 2 Bowen Bay', 'Island Sky'): 0,
       ('Beach 2 Bowen Bay', 'Queen of Alberni'): 0,
       ('Beach 2 Bowen Bay', 'Queen of Coquitlam'): 0,
       ('Beach 2 Bowen Bay', 'Pilot 1'): 1,
       ('Beach 2 Bowen Bay', 'Pilot 2'): 1,
       ('Beach 2 Bowen Bay', 'Pilot 3'): 1,
       ('Beach 1 Tunstall Bay', 'Queen of Capilano'): 0,
       ('Beach 1 Tunstall Bay', 'Queen of Cumberland'): 0,
       ('Beach 1 Tunstall Bay', 'Island Sky'): 0,
       ('Beach 1 Tunstall Bay', 'Queen of Alberni'): 0,
       ('Beach 1 Tunstall Bay', 'Queen of Coquitlam'): 0,
       ('Beach 1 Tunstall Bay', 'Pilot 1'): 1,
       ('Beach 1 Tunstall Bay', 'Pilot 2'): 1,
       ('Beach 1 Tunstall Bay', 'Pilot 3'): 1    
     }
model.f = Param(model.k, model.i, initialize=dtab, doc='Compatibility between docks k and vessels i')    
model.f.pprint() # cross check

model.xl = Param(model.k, initialize={'Ferry terminal Snug Cove': 40,
                                       'Marina Snug Cove': 10,
                                       'Beach 1 Snug Cove': 5, 
                                       'Private dock 1 Snug Cove': 5, 
                                       'Beach 1 Bowen Bay': 10, 
                                       'Beach 2 Bowen Bay': 10, 
                                       'Beach 1 Tunstall Bay': 20},
                                       doc= 'Number of people evacuating with private vessels at location m')
model.xl.pprint() # cross check
    
    # arrival rate at location
model.lamb = Param(model.k, initialize={'Ferry terminal Snug Cove': 50,
                                       'Marina Snug Cove': 10,
                                       'Beach 1 Snug Cove': 10, 
                                       'Private dock 1 Snug Cove': 5, 
                                       'Beach 1 Bowen Bay': 15, 
                                       'Beach 2 Bowen Bay': 15, 
                                       'Beach 1 Tunstall Bay': 30}, doc='people arrival rate at location m per minute')

model.lamb.pprint()

ftab = {
       ('Ferry terminal Snug Cove', 'Queen of Capilano'): 2.8,
       ('Ferry terminal Snug Cove', 'Queen of Cumberland'): 29,
       ('Ferry terminal Snug Cove', 'Island Sky'): 29,
       ('Ferry terminal Snug Cove', 'Queen of Alberni'): 27,
       ('Ferry terminal Snug Cove', 'Queen of Coquitlam'): 9,
       ('Ferry terminal Snug Cove', 'Pilot 1'): 15,
       ('Ferry terminal Snug Cove', 'Pilot 2'): 2.8,
       ('Ferry terminal Snug Cove', 'Pilot 3'): 15,
       ('Marina Snug Cove', 'Queen of Capilano'): 2.8,
       ('Marina Snug Cove', 'Queen of Cumberland'): 29,
       ('Marina Snug Cove', 'Island Sky'): 29,
       ('Marina Snug Cove', 'Queen of Alberni'): 27,
       ('Marina Snug Cove', 'Queen of Coquitlam'): 9,
       ('Marina Snug Cove', 'Pilot 1'): 15,
       ('Marina Snug Cove', 'Pilot 2'): 2.8,
       ('Marina Snug Cove', 'Pilot 3'): 15,
       ('Beach 1 Snug Cove', 'Queen of Capilano'): 2.8,
       ('Beach 1 Snug Cove', 'Queen of Cumberland'): 29,
       ('Beach 1 Snug Cove', 'Island Sky'): 29,
       ('Beach 1 Snug Cove', 'Queen of Alberni'): 27,
       ('Beach 1 Snug Cove', 'Queen of Coquitlam'): 9,
       ('Beach 1 Snug Cove', 'Pilot 1'): 15,
       ('Beach 1 Snug Cove', 'Pilot 2'): 2.8,
       ('Beach 1 Snug Cove', 'Pilot 3'): 15,
       ('Private dock 1 Snug Cove', 'Queen of Capilano'): 2.8,
       ('Private dock 1 Snug Cove', 'Queen of Cumberland'): 29,
       ('Private dock 1 Snug Cove', 'Island Sky'): 29,
       ('Private dock 1 Snug Cove', 'Queen of Alberni'): 27,
       ('Private dock 1 Snug Cove', 'Queen of Coquitlam'): 9,
       ('Private dock 1 Snug Cove', 'Pilot 1'): 15,
       ('Private dock 1 Snug Cove', 'Pilot 2'): 2.8,
       ('Private dock 1 Snug Cove', 'Pilot 3'): 15,
       ('Beach 1 Bowen Bay', 'Queen of Capilano'): 7,
       ('Beach 1 Bowen Bay', 'Queen of Cumberland'): 26,
       ('Beach 1 Bowen Bay', 'Island Sky'): 26,
       ('Beach 1 Bowen Bay', 'Queen of Alberni'): 28,
       ('Beach 1 Bowen Bay', 'Queen of Coquitlam'): 10,
       ('Beach 1 Bowen Bay', 'Pilot 1'): 17,
       ('Beach 1 Bowen Bay', 'Pilot 2'): 7,
       ('Beach 1 Bowen Bay', 'Pilot 3'): 17,
       ('Beach 2 Bowen Bay', 'Queen of Capilano'): 7,
       ('Beach 2 Bowen Bay', 'Queen of Cumberland'): 26,
       ('Beach 2 Bowen Bay', 'Island Sky'):26,
       ('Beach 2 Bowen Bay', 'Queen of Alberni'): 28,
       ('Beach 2 Bowen Bay', 'Queen of Coquitlam'): 10,
       ('Beach 2 Bowen Bay', 'Pilot 1'): 17,
       ('Beach 2 Bowen Bay', 'Pilot 2'): 7,
       ('Beach 2 Bowen Bay', 'Pilot 3'): 17,
       ('Beach 1 Tunstall Bay', 'Queen of Capilano'): 7,
       ('Beach 1 Tunstall Bay', 'Queen of Cumberland'): 25,
       ('Beach 1 Tunstall Bay', 'Island Sky'): 25,
       ('Beach 1 Tunstall Bay', 'Queen of Alberni'): 28,
       ('Beach 1 Tunstall Bay', 'Queen of Coquitlam'): 12,
       ('Beach 1 Tunstall Bay', 'Pilot 1'): 17,
       ('Beach 1 Tunstall Bay', 'Pilot 2'): 6,
       ('Beach 1 Tunstall Bay', 'Pilot 3'): 17    
     }
model.dist = Param(model.k, model.i, initialize = ftab, doc = 'distances of vessels to evacuation docks')

# evacuation demand   
model.d = Param(model.k, initialize={'Ferry terminal Snug Cove': 2000,
                                       'Marina Snug Cove': 50,
                                       'Beach 1 Snug Cove': 30, 
                                       'Private dock 1 Snug Cove': 30, 
                                       'Beach 1 Bowen Bay': 25, 
                                       'Beach 2 Bowen Bay': 25, 
                                       'Beach 1 Tunstall Bay': 50}, doc = 'People to be evacuated at dock k')
model.d.pprint()



## Define variables ##


# deterministic decision variables

# people allocation
model.x = Var(model.k, model.i, within=NonNegativeIntegers, bounds=(0, None), initialize = 0, doc = 'Allocation of people to vessel i at dock k')
model.x.pprint()

# slack variable
model.sl = Var(model.k, within=NonNegativeIntegers, bounds=(0, None), initialize = 0, doc='slack of people not evacuated')
model.sl.pprint()

# vessel assignment variable
model.z = Var(model.k, model.i, within=Binary, initialize = 0, doc='Assignment of vessel i to dock k')
model.z.pprint()

# time variable for arrivals
model.t = Var(model.k, model.i, bounds=(0,None), initialize = 0, doc = 'arrival time of vessel i to dock k')
model.t.pprint()

# time variable for serving
model.p = Var(model.k, model.i, bounds=(0, None), initialize = 0, doc='time it takes to serve vessel i at dock k')
model.p.pprint()

# binary variable assigning the order of serving vessels
model.delta = Var(model.k, model.i, model.i, within=Binary, initialize = 0, doc = 'decide in which order to serve two vessels')
model.delta.pprint()

# an objective variable representing the total completion time
model.comp = Var(within = NonNegativeReals, bounds=(0,None), initialize = 100000, doc = 'time to complete entire evacuation')
model.comp.pprint()


## Define constraints

# constraint (2)
def vessel_assignment(model, i): # constraint to ensure that each vessel can only be assigned to one dock
    constr = (sum(model.z[k,i] for k in model.k) == 1)
    return(constr)
model.assign = Constraint(model.i, rule = vessel_assignment, doc = 'Ensure assignment of vessels to only one dock')
model.assign.pprint()

## constraint (3)
def dock_serve(model, k): # constraint to ensure that each location gets served if the evacuation demand is not zero
    if model.d[k] != 0:
        serve = (sum(model.z[k,i] for i in model.i) >= 1)
    else:
        serve = (sum(model.z[k,i] for i in model.i) == 0)
    return(serve)
model.serve = Constraint(model.k, rule = dock_serve, doc = 'Ensure that each location gets served that has demand')
model.serve.pprint()

# constraint (4) 
def max_cap_vessel(model, i): # constraint to ensure that the maximum vessel capacity at each location cannot be exceeded
    return (sum(model.x[k,i]for k in model.k) <= model.cap[i])
model.maxcap_vessel = Constraint(model.i, rule = max_cap_vessel, doc = 'Maximum capacity of vessels')
model.maxcap_vessel.pprint()

# constraint (5)
def evacuation_demand_satisfied_rule(model, k): # constraint to ensure that the evacuation demand is satisfied
    return (sum(model.x[k,i] for i in model.i) == model.d[k] - model.xl[k] - model.sl[k])
model.demand_satisf = Constraint(model.k, rule = evacuation_demand_satisfied_rule, doc = 'Check that evacuation demand is satisfied')
model.demand_satisf.pprint()

# constraint (6)
def order_one(model, k, i, j):
    if i != j:
        a = ((model.t[k,j]+model.p[k,j]-model.t[k,i]) <= model.M*(model.delta[k,i,j]))
    else:
        a = Constraint.Skip
    return(a)
    
# constraint (7)
def order_two(model,k,i,j):
    if i != j:
        a = ((model.t[k,i]+model.p[k,i]-model.t[k,j]) <= model.M*(1-model.delta[k,i,j]))
    else:
        a = Constraint.Skip
    return(a)

def order_secondary(k, i, j):
    model.ordered_one = Constraint(k, i, j, rule = order_one, doc = 'First order constraint')
    model.ordered_two = Constraint(k, i, j, rule = order_two, doc = 'Second order constraint')
    model.ordered_one.pprint()
    model.ordered_two.pprint()
    return(model.ordered_one, model.ordered_two)

model.ordered_one, model.ordered_two = order_secondary(model.k, model.i, model.i)

# constraint (8)
def maximum_completion(model, k, i):
    return(model.t[k,i] + model.p[k,i] <= model.comp)
model.max_comp = Constraint(model.k, model.i, rule = maximum_completion, doc = 'Constraint modeling the maximum completion time')
model.max_comp.pprint()

# constraint (9)
def lb_arrive(model, k, i):
    return(model.t[k,i] >= ((model.dist[k,i]/model.v[i])*model.z[k,i]))
model.lower_arrival = Constraint(model.k, model.i, rule = lb_arrive, doc = 'lower bound to arrival time of vessel')
model.lower_arrival.pprint()

# constraint (10)
def lb_serve(model, k, i):
    return(model.p[k,i] >= (model.dock[i] + (model.x[k,i]/model.lr[i]) + model.undock[i])*model.z[k,i])
model.serving = Constraint(model.k, model.i, rule = lb_serve, doc = 'lower bound to vessel serving')

# constraint (11)
def max_t(model, k, i):
    return(model.t[k,i] <= model.Mtild*(model.z[k,i]))
model.max_t = Constraint(model.k, model.i, rule = max_t, doc = 'maximum value of t if selected')

# constraint (12)
def max_p(model, k, i):
    return(model.p[k,i] <= model.Mtild*(model.z[k,i]))
model.max_p = Constraint(model.k, model.i, rule = max_p, doc = 'maximum value of p if selected')

# constraint (13)
def capa(model, k, i):
    return(model.x[k,i] <= model.Mtild * model.z[k,i] * model.f[k,i])
model.capa_max = Constraint(model.k, model.i, rule = capa, doc = 'Verify that capacity gets captured')



## Define objective

# objective (1)
def objective_rule(model):
  return (model.comp + model.P*(sum(model.sl[k] for k in model.k)))
model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')


## Solve problem


#instance = model.create_instance()
    
if __name__ == '__main__':
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    print("Solving model of index:")
    opt = SolverFactory('gurobi')
    opt.options['IntFeasTol']= 10e-10
    results = opt.solve(model, tee=True)

for v in model.component_objects(Var, active=True):
    print("Variable",v)  # doctest: +SKIP
    for index in v:
        print ("   ",index, value(v[index]))  # doctest: +SKIP
