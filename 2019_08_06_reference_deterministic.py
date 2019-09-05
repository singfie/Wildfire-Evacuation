#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 10:43:03 2019

@author: fietekrutein

This is a deterministic base case model formulation of the SIREN evacuation scenario
This base case scenario is going to be used for an implementation of a stochastic model

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
                          'Pilot 1', 'Pilot 2', 'Pilot 3', 'Pilot 4', 'Pilot 5', 'Pilot 6'], doc='Vessels')
model.i.pprint() # cross check

model.a = Set(initialize=['Horseshoe Bay','Snug Cove', 'Swartz Bay', 'Tsawassen', 'Tsawassen - Duke Point', 
                          'Snug Cove - Horseshoe Bay', 'Langdale - Horseshoe Bay'], doc='Storage locations/routes')
model.a.pprint() # cross check

model.s = Set(initialize=['arrival at location', 'docking', 'loading', 'undocking'], doc='Process steps')
model.s.pprint() # cross check

model.m = Set(initialize=['Snug Cove', 'Bowen Bay', 'Tunstall Bay'], doc='Evacuation locations')
model.m.pprint() # cross check

model.k = Set(initialize=['Ferry terminal Snug Cove', 'Marina Snug Cove', 'Beach 1 Snug Cove', 
                          'Private dock 1 Snug Cove', 'Beach 1 Bowen Bay', 'Beach 2 Bowen Bay', 'Beach 1 Tunstall Bay'], doc='Docks at evacuation location')
model.k.pprint()

model.xi = Set(initialize=['1', '2', '3', '4', '5'], doc='Scenarios')
model.xi.pprint()

## Define parameters ##

# high level
def latest(t0, maximum):
    return(t0 + maximum*60) # allow a maximum evacuation time of 12 hours

model.p = Param(initialize=10000, doc = 'Penalty for not evacuating persons')
model.p.pprint() # cross check

model.B = Param(initialize=2000, doc = 'Upper bound for evacuation time')
model.B.pprint() # criss check

# Vessels
model.v = Param(model.i, initialize={'Queen of Capilano': 12.5 ,
                                         'Queen of Cumberland':12, 
                                         'Island Sky': 14.5, 
                                         'Queen of Alberni': 21, 
                                         'Queen of Coquitlam': 20.5,
                                         'Pilot 1': 25,
                                         'Pilot 2': 25,
                                         'Pilot 3': 25,
                                         'Pilot 4': 25,
                                         'Pilot 5': 25,
                                         'Pilot 6': 25}, doc='Max speed of vessel i')
model.v.pprint() # cross check
    
model.cap = Param(model.i, initialize={'Queen of Capilano': 900, 
                                            'Queen of Cumberland':900, 
                                            'Island Sky': 800, 
                                            'Queen of Alberni': 1720, 
                                            'Queen of Coquitlam': 1720,
                                            'Pilot 1': 35,
                                            'Pilot 2': 35,
                                            'Pilot 3': 35,
                                            'Pilot 4': 35,
                                            'Pilot 5': 35,
                                            'Pilot 6': 35}, doc='Max passenger capacity of vessel i')
model.cap.pprint() # cross check

model.a_loc = Param(model.i, initialize={'Queen of Capilano': 'Snug Cove - Horsehoe Bay', 
                                            'Queen of Cumberland': 'Swartz Bay',
                                            'Island Sky': 'Swartz Bay', 
                                            'Queen of Alberni': 'Tsawassen - Duke Point', 
                                            'Queen of Coquitlam': 'Langdale - Horseshoe Bay',
                                            'Pilot 1': 'Horseshoe Bay',
                                            'Pilot 2': 'Tsawassen',
                                            'Pilot 3': 'Swartz Bay',
                                            'Pilot 4': 'Horseshoe Bay',
                                            'Pilot 5': 'Tsawassen',
                                            'Pilot 6': 'Swartz Bay'}, doc='Storage location or route assigned to vessel i')
model.a_loc.pprint() # cross check

model.c = Param(model.i, initialize={'Queen of Capilano': 0 ,
                                        'Queen of Cumberland':5000, 
                                        'Island Sky': 2000, 
                                        'Queen of Alberni': 10000, 
                                        'Queen of Coquitlam': 10000,
                                        'Pilot 1': 2000,
                                        'Pilot 2': 2000,
                                        'Pilot 3': 2000,
                                        'Pilot 4': 2000,
                                        'Pilot 5': 2000,
                                        'Pilot 6': 2000}, doc='Holding cost of vessel i')
model.c.pprint() # cross check
    
model.var_c = Param(model.i, initialize= 10, doc = 'variable cost per time unit')
model.var_c.pprint() # cross check

model.lr = Param(model.i, initialize={'Queen of Capilano': 40 ,
                                                'Queen of Cumberland': 40,
                                                'Island Sky': 30, 
                                                'Queen of Alberni': 100, 
                                                'Queen of Coquitlam': 100,
                                                'Pilot 1': 15,
                                                'Pilot 2': 15,
                                                'Pilot 3': 15,
                                                'Pilot 4': 15,
                                                'Pilot 5': 15,
                                                'Pilot 6': 15}, doc='Max loading rate of vessel i per minute')
model.lr.pprint() # cross check

model.dt = Param(model.i, initialize={'Queen of Capilano': 5 ,
                                                'Queen of Cumberland': 5,
                                                'Island Sky': 5, 
                                                'Queen of Alberni': 7, 
                                                'Queen of Coquitlam': 7,
                                                'Pilot 1': 2,
                                                'Pilot 2': 2,
                                                'Pilot 3': 2,
                                                'Pilot 4': 2,
                                                'Pilot 5': 2,
                                                'Pilot 6': 2}, doc='min docking time of vessel i')
model.dt.pprint() # cross check

model.lt = Param(model.i, initialize={'Queen of Capilano': 15 ,
                                                'Queen of Cumberland': 15,
                                                'Island Sky': 10, 
                                                'Queen of Alberni': 20, 
                                                'Queen of Coquitlam': 20,
                                                'Pilot 1': 5,
                                                'Pilot 2': 5,
                                                'Pilot 3': 5,
                                                'Pilot 4': 5,
                                                'Pilot 5': 5,
                                                'Pilot 6': 5}, doc='min loading time of vessel i') # this is not lower bounded yet
model.lt.pprint() # cross check

model.udt = Param(model.i, initialize={'Queen of Capilano': 5 ,
                                                  'Queen of Cumberland': 5,
                                                  'Island Sky': 5, 
                                                  'Queen of Alberni': 7, 
                                                  'Queen of Coquitlam': 7,
                                                  'Pilot 1': 2,
                                                  'Pilot 2': 2,
                                                  'Pilot 3': 2,
                                                  'Pilot 4': 2,
                                                  'Pilot 5': 2,
                                                  'Pilot 6': 2}, doc='min undocking time of vessel i')
model.udt.pprint()


# Evacuation docks
    # locations of docks 
atab = {
        ('Ferry terminal Snug Cove', 'Snug Cove'): 1,
        ('Ferry terminal Snug Cove', 'Bowen Bay'): 0,
        ('Ferry terminal Snug Cove', 'Tunstall Bay'): 0,
        ('Marina Snug Cove', 'Snug Cove'): 1, 
        ('Marina Snug Cove', 'Bowen Bay'): 0, 
        ('Marina Snug Cove', 'Tunstall Bay'): 0,
        ('Beach 1 Snug Cove', 'Snug Cove'): 1, 
        ('Beach 1 Snug Cove', 'Bowen Bay'): 0, 
        ('Beach 1 Snug Cove', 'Tunstall Bay'): 0,
        ('Private dock 1 Snug Cove', 'Snug Cove'): 1, 
        ('Private dock 1 Snug Cove', 'Bowen Bay'): 0, 
        ('Private dock 1 Snug Cove', 'Tunstall Bay'): 0, 
        ('Beach 1 Bowen Bay', 'Snug Cove'): 0, 
        ('Beach 1 Bowen Bay', 'Bowen Bay'): 1,
        ('Beach 1 Bowen Bay', 'Tunstall Bay'): 0,
        ('Beach 2 Bowen Bay', 'Snug Cove'): 0, 
        ('Beach 2 Bowen Bay', 'Bowen Bay'): 1, 
        ('Beach 2 Bowen Bay', 'Tunstall Bay'): 0, 
        ('Beach 1 Tunstall Bay', 'Snug Cove'): 0, 
        ('Beach 1 Tunstall Bay', 'Bowen Bay'): 0, 
        ('Beach 1 Tunstall Bay', 'Tunstall Bay'): 1
        }
model.e = Param(model.k, model.m, initialize=atab, doc='Dock to location allocation')
model.e.pprint()
    
    # compatibility between docks and vessels
dtab= {
       ('Ferry terminal Snug Cove', 'Queen of Capilano'): 1,
       ('Ferry terminal Snug Cove', 'Queen of Cumberland'): 1,
       ('Ferry terminal Snug Cove', 'Island Sky'): 1,
       ('Ferry terminal Snug Cove', 'Queen of Alberni'): 1,
       ('Ferry terminal Snug Cove', 'Queen of Coquitlam'): 1,
       ('Ferry terminal Snug Cove', 'Queen of Capilano'): 1,
       ('Ferry terminal Snug Cove', 'Pilot 1'): 0,
       ('Ferry terminal Snug Cove', 'Pilot 2'): 0,
       ('Ferry terminal Snug Cove', 'Pilot 3'): 0,
       ('Ferry terminal Snug Cove', 'Pilot 4'): 0,
       ('Ferry terminal Snug Cove', 'Pilot 5'): 0,
       ('Ferry terminal Snug Cove', 'Pilot 6'): 0,
       ('Marina Snug Cove', 'Queen of Capilano'): 0,
       ('Marina Snug Cove', 'Queen of Cumberland'): 0,
       ('Marina Snug Cove', 'Island Sky'): 0,
       ('Marina Snug Cove', 'Queen of Alberni'): 0,
       ('Marina Snug Cove', 'Queen of Coquitlam'): 0,
       ('Marina Snug Cove', 'Queen of Capilano'): 0,
       ('Marina Snug Cove', 'Pilot 1'): 1,
       ('Marina Snug Cove', 'Pilot 2'): 1,
       ('Marina Snug Cove', 'Pilot 3'): 1,
       ('Marina Snug Cove', 'Pilot 4'): 1,
       ('Marina Snug Cove', 'Pilot 5'): 1,
       ('Marina Snug Cove', 'Pilot 6'): 1,
       ('Beach 1 Snug Cove', 'Queen of Capilano'): 0,
       ('Beach 1 Snug Cove', 'Queen of Cumberland'): 0,
       ('Beach 1 Snug Cove', 'Island Sky'): 0,
       ('Beach 1 Snug Cove', 'Queen of Alberni'): 0,
       ('Beach 1 Snug Cove', 'Queen of Coquitlam'): 0,
       ('Beach 1 Snug Cove', 'Queen of Capilano'): 0,
       ('Beach 1 Snug Cove', 'Pilot 1'): 1,
       ('Beach 1 Snug Cove', 'Pilot 2'): 1,
       ('Beach 1 Snug Cove', 'Pilot 3'): 1,
       ('Beach 1 Snug Cove', 'Pilot 4'): 1,
       ('Beach 1 Snug Cove', 'Pilot 5'): 1,
       ('Beach 1 Snug Cove', 'Pilot 6'): 1,
       ('Private dock 1 Snug Cove', 'Queen of Capilano'): 0,
       ('Private dock 1 Snug Cove', 'Queen of Cumberland'): 0,
       ('Private dock 1 Snug Cove', 'Island Sky'): 0,
       ('Private dock 1 Snug Cove', 'Queen of Alberni'): 0,
       ('Private dock 1 Snug Cove', 'Queen of Coquitlam'): 0,
       ('Private dock 1 Snug Cove', 'Queen of Capilano'): 0,
       ('Private dock 1 Snug Cove', 'Pilot 1'): 1,
       ('Private dock 1 Snug Cove', 'Pilot 2'): 1,
       ('Private dock 1 Snug Cove', 'Pilot 3'): 1,
       ('Private dock 1 Snug Cove', 'Pilot 4'): 1,
       ('Private dock 1 Snug Cove', 'Pilot 5'): 1,
       ('Private dock 1 Snug Cove', 'Pilot 6'): 1,
       ('Beach 1 Bowen Bay', 'Queen of Capilano'): 0,
       ('Beach 1 Bowen Bay', 'Queen of Cumberland'): 0,
       ('Beach 1 Bowen Bay', 'Island Sky'): 0,
       ('Beach 1 Bowen Bay', 'Queen of Alberni'): 0,
       ('Beach 1 Bowen Bay', 'Queen of Coquitlam'): 0,
       ('Beach 1 Bowen Bay', 'Queen of Capilano'): 0,
       ('Beach 1 Bowen Bay', 'Pilot 1'): 1,
       ('Beach 1 Bowen Bay', 'Pilot 2'): 1,
       ('Beach 1 Bowen Bay', 'Pilot 3'): 1,
       ('Beach 1 Bowen Bay', 'Pilot 4'): 1,
       ('Beach 1 Bowen Bay', 'Pilot 5'): 1,
       ('Beach 1 Bowen Bay', 'Pilot 6'): 1,
       ('Beach 2 Bowen Bay', 'Queen of Capilano'): 0,
       ('Beach 2 Bowen Bay', 'Queen of Cumberland'): 0,
       ('Beach 2 Bowen Bay', 'Island Sky'): 0,
       ('Beach 2 Bowen Bay', 'Queen of Alberni'): 0,
       ('Beach 2 Bowen Bay', 'Queen of Coquitlam'): 0,
       ('Beach 2 Bowen Bay', 'Queen of Capilano'): 0,
       ('Beach 2 Bowen Bay', 'Pilot 1'): 1,
       ('Beach 2 Bowen Bay', 'Pilot 2'): 1,
       ('Beach 2 Bowen Bay', 'Pilot 3'): 1,
       ('Beach 2 Bowen Bay', 'Pilot 4'): 1,
       ('Beach 2 Bowen Bay', 'Pilot 5'): 1,
       ('Beach 2 Bowen Bay', 'Pilot 6'): 1,
       ('Beach 1 Tunstall Bay', 'Queen of Capilano'): 0,
       ('Beach 1 Tunstall Bay', 'Queen of Cumberland'): 0,
       ('Beach 1 Tunstall Bay', 'Island Sky'): 0,
       ('Beach 1 Tunstall Bay', 'Queen of Alberni'): 0,
       ('Beach 1 Tunstall Bay', 'Queen of Coquitlam'): 0,
       ('Beach 1 Tunstall Bay', 'Queen of Capilano'): 0,
       ('Beach 1 Tunstall Bay', 'Pilot 1'): 1,
       ('Beach 1 Tunstall Bay', 'Pilot 2'): 1,
       ('Beach 1 Tunstall Bay', 'Pilot 3'): 1,
       ('Beach 1 Tunstall Bay', 'Pilot 4'): 1,
       ('Beach 1 Tunstall Bay', 'Pilot 5'): 1,
       ('Beach 1 Tunstall Bay', 'Pilot 6'): 1      
     }
model.f = Param(model.k, model.i, initialize=dtab, doc='Compatibility between docks k and vessels i')    
model.f.pprint() # cross check
# Evacuation locations

    # number of people evacuating with their private vessels
# xml is a random variable
# mean_xl = 20
# sd_xl = 5

model.xl = Param(model.m, initialize={'Snug Cove': 60, 
                                       'Bowen Bay': 20, 
                                       'Tunstall Bay': 20},
                                       doc= 'Number of people evacuating with private vessels at location m')
model.xl.pprint() # cross check
    
    # arrival rate at location
model.lamb = Param(model.m, initialize={'Snug Cove': 90, 
                                       'Bowen Bay': 30, 
                                       'Tunstall Bay': 30}, doc='people arrival rate at location m per minute')

model.lamb.pprint()

    # distances between storage locations and evacuation locations
ctab = {
        ('Horseshoe Bay', 'Snug Cove'): 2.8 ,
        ('Horseshoe Bay', 'Bowen Bay'): 7,
        ('Horseshoe Bay', 'Tunstall Bay'): 6,
        ('Snug Cove', 'Snug Cove'): 0,
        ('Snug Cove', 'Bowen Bay'): 5,
        ('Snug Cove', 'Tunstall Bay'): 3,
        ('Swartz Bay', 'Snug Cove'): 29,
        ('Swartz Bay', 'Bowen Bay'): 26,
        ('Swartz Bay', 'Tunstall Bay'): 25,
        ('Tsawassen', 'Snug Cove'): 15,
        ('Tsawassen', 'Bowen Bay'): 17,
        ('Tsawassen', 'Tunstall Bay'): 17,
        ('Tsawassen - Duke Point', 'Snug Cove'): 27,
        ('Tsawassen - Duke Point', 'Bowen Bay'):28,
        ('Tsawassen - Duke Point', 'Tunstall Bay'): 28,
        ('Snug Cove - Horseshoe Bay', 'Snug Cove'): 2.8,
        ('Snug Cove - Horseshoe Bay', 'Bowen Bay'): 7,
        ('Snug Cove - Horseshoe Bay', 'Tunstall Bay'): 7,
        ('Langdale - Horseshoe Bay', 'Snug Cove'): 9,
        ('Langdale - Horseshoe Bay', 'Bowen Bay'): 10,
        ('Langdale - Horseshoe Bay', 'Tunstall Bay'): 12
        }

model.dist = Param(model.a, model.m, initialize = ctab, doc='Distances between storage locations/routes a and evacuation locations m')
model.dist.pprint()
    # evacuation demand
    
model.d = Param(model.m, initialize={'Snug Cove': 180,
                                          'Bowen Bay': 20,
                                          'Tunstall Bay': 20}, doc = 'People to be evacuated at location m')
model.d.pprint()
# Process steps
    # step length for each process step
def lb_s(model, s, a, m, i):
    if s == 'arrival at location':
        if model.dist[(a,m)] != 0:
            ps = model.v[i]/model.dist[(a,m)]
        else:
            ps = 0
    if s == 'docking':
        ps = model.dt[i]
    if s == 'loading':
        ps = model.lt[i]
    if s == 'undocking':
        ps = model.udt[i]
    return (ps)
model.step_length = Param(model.s, model.a, model.m, model.i, initialize=lb_s, doc='Minimum length of step s')
model.step_length.pprint() # cross check


## Define variables ##

# first stage decision variable
model.y = Var(model.i, within=Binary, doc='Decide to contract vessel i')
model.y.pprint()

# second stage decision variables

# people allocation
model.x = Var(model.m, model.k, model.i, within=Integers, bounds=(0, None), doc = 'Allocation of people from location m to vessel i at dock k')
model.x.pprint()

# slack variable
model.sl = Var(model.m, domain=IntegerSet, bounds=(0, None), doc='slack of people not evacuated')
model.sl.pprint()

# vessel assignment variable
model.z = Var(model.m, model.k, model.i, within=Binary, doc='Assignment of vessel i to dock k of location m')
model.z.pprint()

# delay variable
model.delay = Var(model.s, model.i, bounds=(0, None), doc='Delay of process step s at dock k of location m with vessel i')
model.delay.pprint()

# time variable
model.t = Var(model.s, model.k, model.i, bounds=(0,None), doc = 'Process step completion times')
model.t.pprint()




## Define constraints
def evacuation_demand_satisfied_rule(model, m, k, i): # constraint to ensure that the evacuation demand is satisfied
    return (sum(model.z[m,k,i]*model.y[i]*model.x[m,k,i] for i in model.i) + model.sl[m] == model.d[m] - model.xl[m])
model.demand_satisf = Constraint(model.m, model.k, model.i, rule = evacuation_demand_satisfied_rule, doc = 'Check that evacuation demand is satisfied')
model.demand_satisf.pprint()

def max_cap_vessel(model, m, k, i): # constraint to ensure that the maximum vessel capacity at each location cannot be exceeded
    return (sum(model.z[m,k,i]*model.f[k,i]*model.x[m,k,i] for m in model.m for k in model.k) <= model.cap[i])
model.maxcap_vessel = Constraint(model.m, model.k, model.i, rule = max_cap_vessel, doc = 'Maximum capacity of vessels')
model.maxcap_vessel.pprint()

def recursive_time(model, s, k, a, m, i): # constraint implementing the recursive time steps
    if s == 'arrival at location':
        ret = (model.t[(s,k,i)] == 0)
    elif s == 'docking':
        sm = 'arrival at location'
        ret = (model.t[(s,k,i)] == model.t[(sm,k,i)] + model.step_length[(s,a,m,i)] + model.delay[(s,i)])
    elif s == 'loading':
        sm = 'docking'
        ret = (model.t[(s,k,i)] == model.t[(sm,k,i)] + model.step_length[(s,a,m,i)] + model.delay[(s,i)])
    elif s == 'undocking':
        sm = 'loading'
        ret = (model.t[(s,k,i)] == model.t[(sm,k,i)] + model.step_length[(s,a,m,i)] + model.delay[(s,i)])
    return (ret)
model.t_rec = Constraint(model.s, model.k, model.a, model.m, model.i, rule = recursive_time, doc = 'start counting time at 0')
model.t_rec.pprint()

def ub_time(model, s, k, i): # constraint to define the maximum evacuation time length
    if s == 'undocking':
        end = (model.t[s,k,i] <= model.B)
    else:
        end = Constraint.Skip
    return(end)
model.latest_evac = Constraint(model.s, model.k, model.i, rule = ub_time, doc = 'latest time to evacuate')
model.latest_evac.pprint()

def lower_bound_loading(model, s, a, m, k, i): # constraint to implement that the loading rate is lower bounded by the vessel loading rate
    if s == 'loading':
        lb = (model.step_length[s,a,m,i] >= (model.x[m,k,i]/model.lr[i])) 
    else: 
        lb = Constraint.Skip
    return(lb)
model.lb_load = Constraint(model.s, model.a, model.m, model.k, model.i, rule = lower_bound_loading, doc = 'Lower bound for loading time from loading rate')
model.lb_load.pprint()

def lower_bound_loading_arrivals(model, s, a, m, k, i): # constraint to implement taht the loading rate is lower bounded by the location arrival rate
    if s == 'loading':
        lb = (model.step_length[s,a,m,i] >= (model.x[m,k,i]/model.lamb[m]))
    else:
        lb = Constraint.Skip
    return(lb)
model.lb_load_arrivals = Constraint(model.s, model.a, model.m, model.k, model.i, rule = lower_bound_loading_arrivals, doc = 'Lower bound for loading time from arrival rate')
model.lb_load_arrivals.pprint()


#def upper_bound_longest_time(model, step_length, s, m, k, i, t0, maximum): # constraint that upper bounds the total completion time
#    return(model.step_length[3,m,k,i] for m in M for k in K for i in I <= latest(t0, maximum))
#model.ub_complete = Constraint(model.step_length, model.m, model.k, model.i, rule = upper_bound_longest_time, doc = 'longest time to evacuate')

def vessel_assignment(model, m, k, i): # constraint to ensure that each vessel can only be assigned to one dock
    return(sum(model.z[m,k,i] for k in model.k) == 1)
model.assign = Constraint(model.m, model.k, model.i, rule = vessel_assignment, doc = 'Ensure assignment of vessels to only one dock')
model.assign.pprint()


def location_serve(model, m, k, i): # constraint to ensure that each location gets served if the evacuation demand is not zero
    if model.d[m] != 0:
        serve = (sum(model.z[m,k,i] for i in model.i) >= 1)
    else:
        serve = Constraint.Skip
    return(serve)
model.serve = Constraint(model.m, model.k, model.i, rule = location_serve, doc = 'Ensure that each location gets served that has demand')
model.serve.pprint()


#def avoid_overlap(model, s, i): # ensure that assigned times cannot overlap. This is difficult to implement
#    return(range(model.t['arrival at location',i], model.t['undocking', i])) 
    
    
def time_consecutive1(model, s, k, i): # constraint to ensure that process steps are consecutively
    return(model.t['arrival at location', k, i] <= model.t['docking', k, i])
model.consec1 = Constraint(model.s, model.k, model.i, rule = time_consecutive1, doc = 'Ensure that time step 1 and 2 are consecutive')
model.consec1.pprint()


def time_consecutive2(model, s, k, i): # constraint to ensure that process steps are consecutively
    return(model.t['docking', k, i] <= model.t['loading', k, i])
model.consec2 = Constraint(model.s, model.k, model.i, rule = time_consecutive2, doc = 'Ensure that time step 2 and 3 are consecutive')
model.consec2.pprint()

def time_consecutive3(model, s, k, i): # constraint to ensure that process steps are consecutively
    return(model.t['loading', k, i] <= model.t['undocking', k, i])
model.consec3 = Constraint(model.s, model.k, model.i, rule = time_consecutive3, doc = 'Ensure that time step 3 and 4 are consecutive')
model.consec3.pprint()
    


## Define objective and solve

# This is not working yet

## Define Objective and solve ##
#  cost        define objective function
#  cost ..        z  =e=  sum((i,j), c(i,j)*x(i,j)) ;
#  Model transport /all/ ;
#  Solve transport using lp minimizing z ;
def objective_rule(model, y, k, i, m):
  return (sum(model.c[i]*model.y[i] for i in model.i) + 
          max(model.var_c[i] * model.y[i] * model.t['undocking',k, i] for i in model.i) + 
          model.p*sum(model.sl[m] for m in model.m))
model.objective = Objective(model.y, model.k, model.i, model.m, rule=objective_rule, sense=minimize, doc='Define objective function')


if __name__ == '__main__':
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    opt = SolverFactory("glpk")
    results = opt.solve(model)
    #sends results to stdout
    results.write()
    print("\nDisplaying Solution\n" + '-'*60)
    pyomo_postprocess(None, model, results)










