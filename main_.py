#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json
from itertools import combinations
import pandas as pd
import sys
import copy
from envir2Vec import envir2vec
from inference import inference
from change_envir2 import change_envir

def trans_envir_now(envir):

    pot_oper=[]
    
    gem_num={'red':0, 'green':0,'blue':0,'black':0,'white':0} #场上各个颜色的宝石的数量
    
    gold_num=0; #场上黄金的数量
    
    for i in range(3):
        if envir['players'][i]['name']==envir["playerName"]:
            player_now=i
            break
    
    gem_of_player=pd.DataFrame(0, columns=[0,1,2], index=['red', 'green','blue','black','white','gold'])
        
    #score_of_player=[0,0,0]
    #cardnum_of_player=[0,0,0]
    for i in range(3):
        #if 'score' in envir['players'][i].keys():
        #    score_of_player[i]=envir['players'][i]['score']
        #if "reserved_cards" in envir['players'][i].keys():
        #    cardnum_of_player[i]=len(envir['players'][i]["reserved_cards"])
        if 'gems' in envir['players'][i].keys():
            for gem in envir['players'][i]['gems']:
                gem_of_player[i][gem['color']]=gem['count']
        #gem_of_player=gem_of_player.rename(columns={i:envir['players'][i]['name']})
    gem_sum=gem_of_player.iloc[player_now,:].sum()
    
    if 'gems' in envir["table"].keys():
        gem_ava=[]
        for gem in envir['table']['gems']:
            if 'count' in gem.keys():
                if gem['color']!='gold':
                    gem_num[gem['color']]=gem['count']
                    if gem['count']>=4 and gem_sum<=8:
                        pot_oper.append({"get_two_same_color_gems":gem['color']})
                    if gem['count']>=1:
                        gem_ava.append(gem['color'])
                else:
                    gold_num=gem['count']
        if gem_sum<=7:
            for color_comb in list(combinations(gem_ava, 3)):
                pot_oper.append({"get_different_color_gems":list(color_comb)})
        else:
            for color_comb in list(combinations(gem_ava, 10-gem_sum)):
                pot_oper.append({"get_different_color_gems":list(color_comb)})
        
    if gold_num==0 or gem_sum<=9:
        for card in envir['table']['cards']:
            pot_oper.append({"reserve_card":{"card":card}})
        for i in range(1,4):
            pot_oper.append({"reserve_card":{'level':i}})
    
    card_of_player=pd.DataFrame(0, columns=[0,1,2], index=['red', 'green','blue','black','white'])
    for i in range(3):
        if "purchased_cards" in envir['players'][i].keys():
            for card in envir['players'][i]["purchased_cards"]:
                card_of_player[i][card['color']]+=1
        #card_of_player=card_of_player.rename(columns={i:envir['players'][i]['name']})
    
    for card in envir['table']['cards']:
        gem_gap=0;
        for gem in card['costs']:
            gem_gap+=max(0, gem['count']-gem_of_player[player_now][gem['color']]-card_of_player[player_now][gem['color']])
        if gem_gap<=gem_of_player[player_now]['gold']:
            pot_oper.append({"purchase_card":card})
        
    if "reserved_cards" in envir['players'][player_now].keys():
        for card in envir['players'][player_now]["reserved_cards"]:
            gem_gap=0;
            for gem in card['costs']:
                gem_gap+=max(0, gem['count']-gem_of_player[player_now][gem['color']]-card_of_player[player_now][gem['color']])
            if gem_gap<=gem_of_player[player_now]['gold']:
                pot_oper.append({"purchase_reserved_card":card})
    '''
    card_request=pd.DataFrame(0, columns=range(len(envir['table']['cards'])), index=['red', 'green','blue','black','white'])
    score_of_card=[]
    dividend_num={'red':0, 'green':0,'blue':0,'black':0,'white':0}
    for i in range(len(envir['table']['cards'])):
        if 'score' in envir['table']['cards'][i].keys():
            score_of_card.append(envir['table']['cards'][i]['score'])
        else:
            score_of_card.append(0)
        dividend_num[envir['table']['cards'][i]['color']]+=1
        for gem in envir['table']['cards'][i]['costs']:
            card_request[i][gem['color']]=gem['count']
    '''
    return player_now, pot_oper, gem_num, gold_num, gem_of_player, card_of_player#, card_request, dividend_num,score_of_card, score_of_player,cardnum_of_player

def oper_value(player_now,y,x): 
    #print(y,x)
    v = 0
    # v = (y[player_now]-x[player_now])*0.8
    for i in range(3):
        if i==player_now:
            v += (y[player_now]-x[0][player_now])*0.8
        else:
            v -= (y[i]-x[0][i])*0.2
    return v


def main():
    
    envir=json.loads(sys.argv[1])
    #with open('input.json') as envir_input:
        #envir=json.load(envir_input)
        #envir_input.close()

    player_now, pot_oper,gem_num, gold_num, gem_of_player, card_of_player= trans_envir_now(envir)  
    
    input_vec = envir2vec(envir)
    
    win_est_now=inference(input_vec)

    ope_value=[]
    input_vec=[]
    for i in range(len(pot_oper)):
        envir_new=change_envir(pot_oper[i],player_now,envir)
        input_vec.append(envir2vec(envir_new))
    win_est_new=inference(input_vec)
    for i in range(len(pot_oper)):
        ope_value.append(oper_value(player_now,win_est_new[i],win_est_now))

    opt_ope=0
    max_value=ope_value[0]
    for i in range(len(ope_value)):
        if max_value<ope_value[i]:
            max_value=ope_value[i]
            opt_ope=i
    opt_oper=pot_oper[opt_ope]
    
    envir_new=change_envir(opt_oper,player_now,envir)
    dividend_of_player={'red':0, 'green':0,'blue':0,'black':0,'white':0}
    if "purchased_cards" in envir_new['players'][player_now].keys():
        for card in envir_new['players'][player_now]["purchased_cards"]:
            dividend_of_player[card['color']]+=1
    
    if 'nobles' in envir_new.keys():
        for noble in envir_new['nobles']:
            if_ava=True
            for gem in noble["requirements"]:
                if dividend_of_player[gem['color']]<gem['count']:
                    if_ava=False
            if if_ava:
                opt_oper['noble']=noble
                break
    print(json.dumps(opt_oper))

if __name__ == "__main__":
    main()