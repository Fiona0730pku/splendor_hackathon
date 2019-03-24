#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 00:22:26 2019

@author: mac
"""
import json

colours = ['white', 'blue', 'green', 'red', 'black', 'glod']
num_bit_size = 6
color_bit_size = num_bit_size*len(colours)
maxgem_num_bit = 11
players = 3
cards_num = 8
score_bit_size=21
color_dict={'white':0, 'blue':1, 'green':2, 'red':3, 'black':4, 'glod':5}

#[1]当前场面各个颜色的bit位表示
def envirgemsColorNums(envir_table_gems):
    out = [0]*color_bit_size
    
    for gem in envir_table_gems:
        for i, color in enumerate(colours):
            if gem['color'] == color:
                out[i*num_bit_size + gem['count']] = 1
            else:
                out[i*num_bit_size] = 1
                  
    return out

#[2.1]当前玩家手中gems总和的bit位表示 
def playergemsColorSums(envir_table_gems):
    out = [0]*maxgem_num_bit
    
    count = 0
    for gem in envir_table_gems:
        count += gem['count']
    
    out[count] = 1                 
    return out

#[2]当前玩家手中各个颜色的bit位表示           
def playersgemsColorNums(players_table_gems):
    player_size = color_bit_size+maxgem_num_bit
    out = [0]*player_size*players
    
    for i in range(players):
        if 'gems' in players_table_gems[i].keys():
            out[i*player_size:i*player_size+maxgem_num_bit-1] = envirgemsColorNums(players_table_gems[i]['gems'])+playergemsColorSums(players_table_gems[i]['gems'])
        else:
            out[i*player_size]=1
    return out

#[3]玩家手中每种颜色牌总数的bit位表示
def playersPurchasedCardsSums(players_table_cards):
    cards_total = cards_num*5;
    out = [0]*cards_total*players
    count = {'white':0, 'blue':0, 'green':0, 'red':0, 'black':0, 'glod':0}   
    
    for i in range(players):
        if 'purchased_cards' in players_table_cards[i].keys():
            for card in players_table_cards[i]['purchased_cards']:
                count[card['color']] += 1
            
        for j in range(5):
            for key,value in count.items():
                for k in range(i*cards_total + cards_num*j+value, i*cards_total + cards_num*(j+1)):
                    out[k] =1

    return out

#[4]玩家当前得分
def PlayerScores(envir):
    out = [0]*score_bit_size*players
    
    for i in range(3):
        out[i*21]=1
        if 'score' in envir['players'][i].keys():
            score=envir['players'][i]['score']
            for j in range(score+1):
                out[j+i*21]=1
    return out

#[5]当前玩家
def CurrentPlayer(envir):
    out=[0]*players
    
    for i in range(3):
        if envir['playerName']==envir['players'][i]['name']:
            out[i]=1
    return out

#[6]四张贵族牌需要的颜色位
def AvailNoble(envir):
    tmp=[0]*100
    for i in range(len(envir['table']['nobles'])):
        for gem in envir['table']['nobles'][i]["requirements"]:
            tmp[i*25+color_dict[gem['color']]*5+gem['count']]=1
    out=tmp*3
    return out

#[7]四张贵族牌是否还在
def CurrentNoble(envir):
    out=[0]*4
    
    if 'nobles' in envir['table'].keys():
        for i in range(len(envir['table']['nobles'])):
            out[i]=1
    return out

#[8]面上的卡需要的所有宝石数
def CardCost(envir):
    out=[0]*4*5*(5+7+8)
    cnt1=0
    cnt2=0
    cnt3=0
    for card in envir['table']['cards']:
        if card['level']==1:
            for gem in card["costs"]:
                out[cnt1*25+color_dict[gem['color']]*5+gem['count']]=1
            cnt1+=1
        if card['level']==2:
            for gem in card["costs"]:
                out[100+cnt2*35+color_dict[gem['color']]*7+gem['count']]=1
            cnt2+=1
        if card['level']==3:
            for gem in card["costs"]:
                out[240+cnt3*40+color_dict[gem['color']]*8+gem['count']]=1
            cnt3+=1
    return out

#[9]保留卡需要的宝石数
def ResevedCardCost(envir):
    out=[0]*3*3*5*8
    for i in range(3):
        if "reserved_cards" in envir['players'][i].keys():
            for j in range(len(envir['players'][i]["reserved_cards"])):
                for gem in envir['players'][i]["reserved_cards"][i]['costs']:
                    out[i*120+j*40+color_dict[gem['color']]*8+gem['count']]=1
    return out

#[10]每个用户离每张面上的卡相差的宝石数
def CardRemainCost(envir):
    out=[]
    for i in range(3):
        tmp=[0]*4*5*(5+7+8)
        dividend_of_player={'white':0, 'blue':0, 'green':0, 'red':0, 'black':0}
        if "purchased_cards" in envir['players'][i].keys():
            for card in envir['players'][i]["purchased_cards"]:
                dividend_of_player[card['color']]+=1
        gem_of_player={'white':0, 'blue':0, 'green':0, 'red':0, 'black':0}
        if "gems" in envir['players'][i].keys():
            for gem in envir['players'][i]["gems"]:
                gem_of_player[gem['color']]=gem['count']
        cnt1=0
        cnt2=0
        cnt3=0
        for card in envir['table']['cards']:
            if card['level']==1:
                for gem in card["costs"]:
                    count=gem['count']-dividend_of_player[gem['color']]-gem_of_player[gem['color']]
                    if count<0:
                        count=0
                    for j in range(count+1):
                        tmp[cnt1*25+color_dict[gem['color']]*5+j]=1
                cnt1+=1
            if card['level']==2:
                for gem in card["costs"]:
                    count=gem['count']-dividend_of_player[gem['color']]-gem_of_player[gem['color']]
                    if count<0:
                        count=0
                    for j in range(count+1):
                        tmp[100+cnt2*35+color_dict[gem['color']]*7+j]=1
                cnt2+=1
            if card['level']==3:
                for gem in card["costs"]:
                    count=gem['count']-dividend_of_player[gem['color']]-gem_of_player[gem['color']]
                    if count<0:
                        count=0
                    for j in range(count+1):
                        tmp[240+cnt3*40+color_dict[gem['color']]*8+j]=1
                cnt3+=1
        out=out+tmp
    return out

    
#[11]每个用户离自己的保留卡相差的宝石数
def ReservedCardRemainCost(envir):
    out=[]
    for player in envir['players']:
        tmp=[0]*3*5*8
        dividend_of_player={'white':0, 'blue':0, 'green':0, 'red':0, 'black':0}
        if "purchased_cards" in player.keys():
            for card in player["purchased_cards"]:
                dividend_of_player[card['color']]+=1
        gem_of_player={'white':0, 'blue':0, 'green':0, 'red':0, 'black':0}
        if "gems" in player.keys():
            for gem in player["gems"]:
                gem_of_player[gem['color']]=gem['count']
        if "reserved_cards" in player.keys():
            cnt=0
            for card in player["reserved_cards"]:
                for gem in card["costs"]:
                    count=gem['count']-dividend_of_player[gem['color']]-gem_of_player[gem['color']]
                    if count<0:
                        count=0
                    for j in range(count+1):
                        tmp[cnt*40+color_dict[gem['color']]*8+j]=1
                cnt+=1
        out=out+tmp
    return out
    
#[12]面上的卡的分数
def CardScore(envir):
    out=[0]*4*(2+3+3)
    cnt1=0
    cnt2=0
    cnt3=0
    for card in envir['table']['cards']:
        if card['level']==1:
            if 'score' in card.keys():
                out[cnt1*2+card['score']]=1
            else:
                out[cnt1*2]=1
            cnt1+=1
        if card['level']==2:
            out[8+cnt2*3+card['score']-1]=1
            cnt2+=1
        if card['level']==3:
            out[20+cnt3*3+card['score']-3]=1
            cnt3+=1
    return out

#[13]保留卡的分数
def ResevedCardScore(envir):
    out=[0]*3*3*6
    for i in range(3):
        if "reserved_cards" in envir['players'][i].keys():
            for j in range(len(envir['players'][i]["reserved_cards"])):
                if 'score' in envir['players'][i]["reserved_cards"][j].keys():
                    out[i*18+j*6+envir['players'][i]["reserved_cards"][j]['score']]=1
                else:
                    out[i*18+j*6]=1
    return out

#[14]面上的卡的颜色，即红利
def CardDividend(envir):
    out=[0]*3*4*6
    cnt1=0
    cnt2=0
    cnt3=0
    for card in envir['table']['cards']:
        if card['level']==1:
            out[cnt1*6+color_dict[card['color']]]=1
            cnt1+=1
        if card['level']==2:
            out[24+cnt2*6+color_dict[card['color']]]=1
            cnt2+=1
        if card['level']==3:
            out[48+cnt3*6+color_dict[card['color']]]=1
            cnt3+=1
    return out

#[15]保留卡的颜色，即红利
def ResevedCardDividend(envir):
    out=[0]*3*3*6
    for i in range(3):
        if "reserved_cards" in envir['players'][i].keys():
            for j in range(len(envir['players'][i]["reserved_cards"])):
                color=envir['players'][i]["reserved_cards"][j]['color']
                out[i*18+j*6+color_dict[color]]=1            
    return out

#[16]拥有的没有分数的卡
def NoScore(envir):
    out=[0]*3*16    
    for i in range(3):
        cnt=0
        out[i*16+cnt]=1
        if "purchased_cards" in envir['players'][i].keys():
            for card in envir['players'][i]["purchased_cards"]:
                if card['score']==0:
                    cnt+=1
                    out[i*16+cnt]=1
    return out
    
#[17]拥有的有分数的卡
def HasScore(envir):
    out=[0]*3*10   
    for i in range(3):
        cnt=0
        out[i*10+cnt]=1
        if "purchased_cards" in envir['players'][i].keys():
            for card in envir['players'][i]["purchased_cards"]:
                if card['score']!=0:
                    cnt+=1
                    out[i*10+cnt]=1
    return out

#将环境变量转化为可以input的向量
def envir2vec(envir):
    inputlist = [0]*3277
    
    #[1]当前场面各个gems颜色的bit位表示
    cur_index = 0
    env_gem_colornums = envirgemsColorNums(envir['table']['gems'])
    bit_size = 36
    assert(bit_size == len(env_gem_colornums))
    inputlist[cur_index : cur_index+len(env_gem_colornums)] = env_gem_colornums
    
    #[2]当前玩家手中各个颜色的bit位表示
    cur_index +=  bit_size
    players_gem_colornums = playersgemsColorNums(envir['players'])
    bit_size = 141
    #print(len(players_gem_colornums))
    #assert(bit_size == len(players_gem_colornums))
    inputlist[cur_index : cur_index+len(players_gem_colornums)] = players_gem_colornums
    
    #[3]每位玩家手中每种颜色牌总数的bit位表示
    cur_index +=  bit_size
    players_colours_indices = playersPurchasedCardsSums(envir['players'])
    bit_size = 120
    assert(bit_size == len(players_colours_indices))
    inputlist[cur_index : cur_index+len(players_colours_indices)] = players_colours_indices
    
    #[4]玩家当前得分
    cur_index +=  bit_size
    players_Scores = PlayerScores(envir)
    bit_size = 63
    assert(bit_size == len(players_Scores))
    inputlist[cur_index : cur_index+len(players_Scores)] = players_Scores
    
    #[5]当前玩家
    cur_index +=  bit_size
    Current_Player = CurrentPlayer(envir)
    bit_size = 3
    assert(bit_size == len(Current_Player))
    inputlist[cur_index : cur_index+len(Current_Player)] = Current_Player
    
    #[6]四张贵族牌需要的颜色位
    cur_index +=  bit_size
    Avail_Noble = AvailNoble(envir)
    bit_size = 300
    assert(bit_size == len(Avail_Noble))
    inputlist[cur_index : cur_index+len(Avail_Noble)] = Avail_Noble
    
    #[7]四张贵族牌是否还在
    cur_index +=  bit_size
    Current_Noble = CurrentNoble(envir)
    bit_size = 4
    assert(bit_size == len(Current_Noble))
    inputlist[cur_index : cur_index+len(Current_Noble)] = Current_Noble
    
    #[8]桌面上的卡需要的所有宝石数
    cur_index +=  bit_size
    Card_Cost = CardCost(envir)
    bit_size = 400
    assert(bit_size == len(Card_Cost))
    inputlist[cur_index : cur_index+len(Card_Cost)] = Card_Cost
    
    #[9]每个用户保留的卡需要的宝石数
    cur_index += bit_size
    Reseved_Card_Cost = ResevedCardCost(envir)
    bit_size = 360
    assert(bit_size == len(Reseved_Card_Cost))
    inputlist[cur_index : cur_index+len(Reseved_Card_Cost)] = Reseved_Card_Cost
    
    #[10]每个用户离每张面上的卡相差的宝石数
    cur_index += bit_size
    Card_Remain_Cost = CardRemainCost(envir)
    bit_size = 1200
    assert(bit_size == len(Card_Remain_Cost))
    inputlist[cur_index : cur_index+len(Card_Remain_Cost)] = Card_Remain_Cost
    
    #[11]每个用户离自己的保留卡相差的宝石数
    ReservedCardRemainCost
    cur_index += bit_size
    Reserved_Card_Remain_Cost = ReservedCardRemainCost(envir)
    bit_size = 360
    assert(bit_size == len(Reserved_Card_Remain_Cost))
    inputlist[cur_index : cur_index+len(Reserved_Card_Remain_Cost)] = Reserved_Card_Remain_Cost
    
    #[12]面上的卡的分数
    cur_index += bit_size
    Card_Score = CardScore(envir)
    bit_size = 32
    assert(bit_size == len(Card_Score))
    inputlist[cur_index : cur_index+len(Card_Score)] = Card_Score
    
    #[13]保留卡的分数
    cur_index += bit_size
    Reseved_Card_Score = ResevedCardScore(envir)
    bit_size = 54
    assert(bit_size == len(Reseved_Card_Score))
    inputlist[cur_index : cur_index+len(Reseved_Card_Score)] = Reseved_Card_Score
    
    #[14]面上的卡的颜色，即红利
    cur_index += bit_size
    Card_Dividend = CardDividend(envir)
    bit_size = 72
    assert(bit_size == len(Card_Dividend))
    inputlist[cur_index : cur_index+len(Card_Dividend)] = Card_Dividend
    
    #[15]保留卡的颜色，即红利
    cur_index += bit_size
    Reseved_Card_Dividend = ResevedCardDividend(envir)
    bit_size = 54
    assert(bit_size == len(Reseved_Card_Dividend))
    inputlist[cur_index : cur_index+len(Reseved_Card_Dividend)] = Reseved_Card_Dividend
    
    #[16]拥有的没有分数的卡
    cur_index += bit_size
    No_Score = NoScore(envir)
    bit_size = 48
    assert(bit_size == len(No_Score))
    inputlist[cur_index : cur_index+len(No_Score)] = No_Score
    
    
    #[17]拥有的有分数的卡
    cur_index += bit_size
    Has_Score = HasScore(envir)
    bit_size = 30
    assert(bit_size == len(Has_Score))
    inputlist[cur_index : cur_index+len(Has_Score)] = Has_Score
    return inputlist
    
    

def main():
    with open('input.json') as envir_input:
        envir=json.load(envir_input)
        inputlist = envir2vec(envir)  
        print(inputlist)
        envir_input.close()


if __name__ == "__main__":
    main()