#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 02:53:55 2019

@author: monika
"""

import operator
import copy
import random

def player_get_gem(envir, player_now, color, count):
    if_done=False
    if 'gems' in envir['players'][player_now].keys():
        for gem in envir['players'][player_now]['gems']:
            if gem['color']==color:
                gem['count']+=count
                if_done=True
                break
        if not if_done:
            envir['players'][player_now]['gems'].append({'color': color, 'count':count})
    else:
        envir['players'][player_now]['gems']=[{'color': color, 'count':count}]

def player_remove_gem(envir, player_now, color, count, gold_ind):
    for gem in envir['players'][player_now]['gems']:
        if gem['color']==color:
            gem['count']-=count
            if gem['count']>=0:
                table_get_gem(envir,color,count)
            else:
                envir['players'][player_now]['gems'][gold_ind]['count']+= gem['count']
                table_get_gem(envir,'gold', -gem['count'])
                table_get_gem(envir,color, count+gem['count'])
            break

def table_get_gem(envir,color, count):
    if_done=False
    if 'gems' in envir['table'].keys():
        for gem in envir['table']['gems']:
            if gem['color']==color:
                gem['count']+=count
                if_done=True
                break
        if not if_done:
            envir['table']['gems'].append({'color': color, 'count':count})
    else:
        envir['table']['gems']=[{'color': color, 'count':count}]

def table_remove_gem(envir, color, count):
    for gem in envir['table']['gems']:
        if gem['color']==color:
            gem['count']-=count

def table_remove_card(envir, card):
    for i in range(len(envir['table']['cards'])):
        if operator.eq(card,envir['table']['cards'][i]):
            envir['table']['cards'].pop(i)
            break
        
def dividend_of_player(envir,player_now,color):
    ans=0
    for card in envir['players'][player_now]["purchased_cards"]:
        if card['color']==color:
            ans+=1
    return ans

'''
def randcard(level):
    if level==1:
        card={"level": 1,
             "score": 0,
             "color": ['red','green','blue','white','black'][random.randint(0,4)]
             "costs": [{
               "color": ['red','green','blue'][random.randint(0,4)],
               "count": random.randint(1,2)
             }, {
               "color": ['white','black'][random.randint(0,4)],
               "count": random.randint(1,2)
             }, {
               "color": "green",
            "count": 2 }]
            }
'''    
def change_envir(ope,player_now,envir):
    envir_new=copy.deepcopy(envir)
    if 'get_two_same_color_gems' in ope.keys():
        color=ope['get_two_same_color_gems']
        table_remove_gem(envir_new,color,2)
        player_get_gem(envir_new, player_now, color,2)

    if "get_different_color_gems" in ope.keys():
        for color in ope["get_different_color_gems"]:
            table_remove_gem(envir_new,color,1)
            player_get_gem(envir_new, player_now, color,1)
            
    if "reserve_card" in ope.keys():
        if 'card' in ope["reserve_card"].keys():
            card=ope["reserve_card"]['card']
            table_remove_card(envir_new,card)
            if "reserved_cards" in envir_new['players'][player_now].keys():
                envir_new['players'][player_now]["reserved_cards"].append(card)
            else:
                envir_new['players'][player_now]["reserved_cards"]=[card]
            if 'gems' in envir_new['table'].keys():
                for gem in envir_new['table']['gems']:
                    if gem['color']=='gold' and gem['count']>0:
                        gem['count']-=1
                        player_get_gem(envir_new,player_now,'gold',1)
                        break
        
    if "purchase_card" in ope.keys():
        card=ope["purchase_card"]
        table_remove_card(envir_new,card)
        gold_ind=-1
        for i in range(len(envir_new['players'][player_now]['gems'])):
            if envir_new['players'][player_now]['gems'][i]['color']=='gold':
                gold_ind=i
        if gold_ind==-1:
            envir_new['players'][player_now]['gems'].append({'color':'gold','count':0})
            gold_ind=len(envir_new['players'][player_now]['gems'])-1
        for gem in card["costs"]:
            
            player_remove_gem(envir_new,player_now, gem['color'],gem['count']-dividend_of_player(envir_new,player_now,gem['color']),gold_ind)
        if "purchased_cards" in envir_new['players'][player_now].keys():
            envir_new['players'][player_now]["purchased_cards"].append(card)
        else:
            envir_new['players'][player_now]["purchased_cards"]=[card]
        if 'score' in card.keys():
            if 'score' in envir_new['players'][player_now]:
                envir_new['players'][player_now]['score']+=card['score']
            else:
                envir_new['players'][player_now]['score']=card['score']
        
    if "purchase_reserved_card" in ope.keys():
        card=ope["purchase_reserved_card"]
        for i in range(len(envir_new['players'][player_now]['reserved_cards'])):
            if operator.eq(card,envir_new['players'][player_now]['reserved_cards'][i]):
                envir_new['players'][player_now]['reserved_cards'].pop(i)
                break
        gold_ind=-1
        for i in range(len(envir_new['players'][player_now]['gems'])):
            if envir_new['players'][player_now]['gems'][i]['color']=='gold':
                gold_ind=i
        if gold_ind==-1:
            envir_new['players'][player_now]['gems'].append({'color':'gold','count':0})
            gold_ind=len(envir_new['players'][player_now]['gems'])-1
        for gem in card["costs"]:
            player_remove_gem(envir_new,player_now, gem['color'],gem['count']-dividend_of_player(envir_new,player_now,gem['color']),gold_ind)
        if "purchased_cards" in envir_new['players'][player_now].keys():
            envir_new['players'][player_now]["purchased_cards"].append(card)
        else:
            envir_new['players'][player_now]["purchased_cards"]=[card]
        if 'score' in card.keys():
            if 'score' in envir_new['players'][player_now].keys():
                envir_new['players'][player_now]['score']+=card['score']
            else:
                envir_new['players'][player_now]['score']=card['score']
                
    if 'a_new_card' in ope.keys():
        card=ope['a_new_card']
        envir_new['table']['cards'].append(card)

    if 'noble' in ope.keys():
        for i in range(len(envir_new['table']['nobles'])):
            if operator.eq(ope['noble'],envir_new['table']['nobles'][i]):
                envir_new['table']['nobles'].pop(i)
        if 'nobles' in envir_new['players'][player_now].keys():
            envir_new['players'][player_now]['nobles'].append(ope['noble'])
        else:
            envir_new['players'][player_now]['nobles']=[ope['noble']]
        if 'score' in envir_new['players'][player_now]:
            envir_new['players'][player_now]['score']+=3
        else:
            envir_new['players'][player_now]['score']=3
        
    return envir_new