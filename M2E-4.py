#M2E系統-加密貨幣市場價格波動對M2E平台提供者及玩家的影響
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("/Users/renjie/Desktop/github/M2E/data_4.csv")
profile = pd.read_csv("/Users/renjie/Desktop/github/M2E/player_data/player_profile_4.csv")

#事件
class Event:
  def __init__(self,df,initial_price = 1,nft_amount=100, nft_price=2000, physical_shoe_price=2000, add_value_fee=1000, insurance_fee=500,compensation_amount=5000):
    self.initial_price = initial_price
    self.nft_amount = nft_amount
    self.nft_price = nft_price
    self.physical_shoe_price = physical_shoe_price
    self.add_value_fee = add_value_fee
    self.insurance_fee = insurance_fee
    self.compensation_amount = compensation_amount
    self.df = df
    #M2E角色初始值
    self.pool_cost = 0
    self.pool_crypto_cost = 0
    self.pool_income = 0
    self.pool_crypto_income = 0
    self.shoes_cost = 0
    self.shoes_crypto_cost = 0
    self.shoes_income = 0
    self.shoes_crypto_income = 0
    self.insurance_cost = 0
    self.insurance_crypto_cost = 0
    self.insurance_income = 0
    self.insurance_crypto_income = 0
    #代幣價格
    self.crypto = 0
    self.buy_crypto_price = 0
    self.sell_crypto_price = 0
    self.crypto_day = 0

    #M2E相關費用計算
    self.Transaction_fee = self.nft_price * 0.05  #交易手續費
    self.nft_price_commission = self.nft_price * 0.3 #鞋廠平台費
    self.physical_shoe_commission = self.physical_shoe_price * 0.3 #實體運動鞋銷售抽成(法幣)
    self.insurance_commission = self.insurance_fee * 0.3 #保險抽成(代幣)
    self.Creator_Earnings = self.nft_price * 0.05 #NFT運動鞋版稅(權利金代幣)

    #避免重複計算到玩家
    self.players_bought_NFT = set()
    self.players_add_NFT = set()
    #存玩家購買加密貨幣(法幣支出)
    self.players_USD_cost = {}
    #存玩家購買NFT(法幣收入)
    self.players_USD_income = {}
    #存玩家的累積獎勵(玩家代幣收入)
    self.players_crypto_income = {}
    #存玩家的累積加值金額(玩家代幣支出)
    self.players_crypto_cost = {}
    #存玩家的累積加值金額(玩家代幣淨值)
    self.players_crypto_net = {}
    #存玩家買NFT數量
    self.players_NFT_amount = {}
    #市場代幣買量
    self.market_crypto_buy = 0
    #市場代幣賣量
    self.market_crypto_sell = 0
    #存玩家磨損率
    self.players_distance = {}
    self.player_data = {}
    #計算玩家受傷
    self.player_hurt = {}
    #計算玩家進來買的次數
    self.player_NFT = {}
    
  def event1_crypto_price(self,player_amount,event_list,current_time): 
    self.buy_crypto_volume = 0
    self.sell_crypto_volume = 0  
    pool_buy_crypto=0
    pool_sell_crypto=0 
    #初始化市場價格與玩家向項目方購買的量
    if self.crypto_day == 0:
        self.crypto = self.initial_price
        self.crypto_day+=1
        for i in range(player_amount):
          player_id = profile['player'].iloc[i]
          keep = profile['keep_amount'].iloc[i]
          if player_id not in self.players_USD_income:
              self.players_USD_income[player_id] = 0  # 如果玩家不存在，則初始化玩家USD支出 
          if player_id not in self.players_USD_cost:
              self.players_USD_cost[player_id] = 0  # 如果玩家不存在，則初始化玩家USD支出
          if player_id not in self.players_crypto_cost:
              self.players_crypto_cost[player_id] = 0  # 如果玩家不存在，則初始化玩家代幣收入
          if player_id not in self.players_crypto_income:
              self.players_crypto_income[player_id] = 0  # 如果玩家不存在，則初始化玩家代幣收入
          if player_id not in self.players_crypto_net:
            self.players_crypto_net[player_id] = 0
        print(f"market sell crypto: {self.sell_crypto_volume}, market buy crypto: {self.buy_crypto_volume},crypto price:{self.crypto}")
        pool_net = (self.pool_income + self.pool_crypto_income * self.crypto) - (self.pool_cost+ self.pool_crypto_cost * self.crypto)
        return self.crypto,self.sell_crypto_volume,self.buy_crypto_volume,self.crypto_day,pool_net
    else:  
        self.crypto_day+=1
        self.sell_crypto_volume=3500*player_amount*3
        self.crypto = self.initial_price
        #檢查有沒有人在預期價格想賣出代幣
        for i in range(player_amount):
            player_id = profile['player'].iloc[i]
            sell_price_rate = profile['sell_price_rate'].iloc[i]
            # buy_price_rate = profile['buy_price_rate'].iloc[i]
            sell_amount_rate = profile['sell_amount_rate'].iloc[i]
            self.players_crypto_net[player_id] = self.players_crypto_income[player_id]-self.players_crypto_cost[player_id]               
            #價格大於購買價格玩家賣不同比例的數量
            if self.players_crypto_net[player_id]>0:
              if self.crypto >= self.initial_price * sell_price_rate:
                self.sell_crypto_volume += (self.players_crypto_net[player_id] * sell_amount_rate)
                self.players_USD_income[player_id]+=(self.players_crypto_net[player_id] * sell_amount_rate * self.crypto)
             
        #玩家進入每個事件中產生的需求供給量
        for i in range(len(event_list['EventTime'])):
            event_time = event_list['EventTime'][i]        
            if  event_time <= current_time+1 and event_time > current_time:
              next_event_id = event_list['EventId'][i]
              player_id = event_list['player'][i]               
              self.players_crypto_net[player_id] = self.players_crypto_income[player_id] - self.players_crypto_cost[player_id]
              keep = profile['keep_amount'].iloc[player_id+1]
              if next_event_id == 2 :
                  if player_id not in self.players_add_NFT:
                    self.players_add_NFT.add(player_id)
                  else:
                    buy_crypto = (self.nft_price + self.Transaction_fee + self.Creator_Earnings)
                    if self.players_crypto_net[player_id] < buy_crypto:
                      self.buy_crypto_volume+=(buy_crypto-self.players_crypto_net[player_id])
              elif next_event_id == 3:
                buy_crypto = (self.insurance_fee + self.add_value_fee + self.Transaction_fee)
                if self.players_crypto_net[player_id] < buy_crypto:
                  self.buy_crypto_volume+=(buy_crypto-self.players_crypto_net[player_id])
              #考慮玩家
              elif next_event_id == 4:
                self.players_add_NFT.add(player_id)
                keep = profile['keep_amount'].iloc[player_id+1]                               
                if self.players_crypto_net[player_id]>keep: 
                  self.sell_crypto_volume += (keep-self.players_crypto_net[player_id])                  
              elif next_event_id == 5:
                #鞋廠把實體鞋拿去賣
                sell_crypto = (self.nft_price + self.Transaction_fee + self.Creator_Earnings)
                self.sell_crypto_volume+=sell_crypto            
              elif next_event_id == 6:
                self.insurance_crypto_net = self.insurance_crypto_income-self.insurance_crypto_cost
                buy_crypto = self.compensation_amount
                if self.insurance_crypto_net < buy_crypto:
                  self.buy_crypto_volume+=(buy_crypto-self.insurance_crypto_net)
              else:
                return 
              
        #項目方       
        if self.sell_crypto_volume ==0:
          if self.buy_crypto_volume ==0:
            difference_ratio = 0 
          else:
            difference_ratio = -1              
        else:  
          difference_ratio = (self.sell_crypto_volume - self.buy_crypto_volume) / self.sell_crypto_volume

        ratio = 0.05
        self.crypto *= (1-difference_ratio*ratio)
        target_lower_bound = 0.9
        target_upper_bound = 1.1
        if self.crypto <= target_lower_bound:        
          required_difference_ratio = (1 - target_lower_bound / self.crypto) / ratio   
          pool_buy_crypto = self.sell_crypto_volume-required_difference_ratio *self.sell_crypto_volume - self.buy_crypto_volume  
          #計算資金池成本
          self.pool_cost += pool_buy_crypto 
          self.pool_crypto_income += pool_buy_crypto
          #增加資金池需求量
          self.buy_crypto_volume+=pool_buy_crypto
          #重新計算調整價格
          difference_ratio = (self.sell_crypto_volume - self.buy_crypto_volume) / self.sell_crypto_volume
          self.crypto *= (1 - required_difference_ratio * ratio)          
          print(f"pool will buy {pool_buy_crypto}")
          print(f"New crypto price: {self.crypto}")

        elif self.crypto >= target_upper_bound:            
            required_difference_ratio = (1 - target_upper_bound / self.crypto) / ratio
            pool_sell_crypto = (required_difference_ratio * self.sell_crypto_volume + self.buy_crypto_volume ) / (self.buy_crypto_volume + self.sell_crypto_volume)
            #計算資金池收益
            self.pool_income += pool_sell_crypto 
            self.pool_crypto_cost += pool_sell_crypto
            #增加資金池供給量
            self.sell_crypto_volume+=pool_sell_crypto
            #重新計算調整價格
            difference_ratio = (self.sell_crypto_volume - self.buy_crypto_volume) / self.sell_crypto_volume 
            self.crypto *= (1 - required_difference_ratio * ratio)  
            print(f"pool will provide {pool_sell_crypto}")
            print(f" New crypto price: {self.crypto}")
        pool_net = (self.pool_income + self.pool_crypto_income * self.crypto) - (self.pool_cost+ self.pool_crypto_cost * self.crypto)   
        print(f"market sell crypto: {self.sell_crypto_volume}, market buy crypto: {self.buy_crypto_volume},crypto price:{self.crypto}")        
        return round(self.crypto,2),self.sell_crypto_volume,self.buy_crypto_volume,self.crypto_day,pool_net

  def event2_player_buy_nft(self,player_id,event_id):
    print(f"player{player_id} in Event{event_id}: buy NFT")

    if player_id not in self.players_USD_cost:
        self.players_USD_cost[player_id] = 0  # 如果玩家不存在，則初始化玩家USD收入

    if player_id not in self.players_NFT_amount: # 初始化玩家的NFT數量
      self.players_NFT_amount[player_id]=0
    else:
      self.players_NFT_amount[player_id]+=1
    #玩家購買NFT
    self.players_crypto_cost[player_id] =(self.nft_price + self.Transaction_fee + self.Creator_Earnings)
    self.pool_crypto_income += (self.nft_price + self.Transaction_fee + self.Creator_Earnings+self.nft_price_commission)
    print("pool crypto income:", self.pool_crypto_income, "pool crypto cost:", self.pool_crypto_cost,
          "pool USD income:", self.pool_income, "pool USD cost:", self.pool_cost,
          f"player{player_id} crypto income:",self.players_crypto_income[player_id],
          f"player{player_id} crypto cost:",self.players_crypto_cost[player_id],
          f"player{player_id}'s nft amount:", self.players_NFT_amount[player_id],
          "shoes USD income:", self.shoes_income, "shoes USD cost:", self.shoes_cost)
    return self.pool_crypto_income,self.pool_crypto_cost,self.pool_income,self.pool_cost,self.players_crypto_income[player_id],self.players_crypto_cost[player_id],self.players_USD_cost[player_id],self.players_USD_income[player_id]


  def event3_player_add(self,player_id,event_id):
    #玩家加值
    self.players_crypto_cost[player_id] += (self.insurance_fee + self.add_value_fee + self.Transaction_fee) # 玩家代幣支出
    self.pool_crypto_income += (self.add_value_fee + self.Transaction_fee + self.insurance_commission)
    self.pool_crypto_cost += self.insurance_commission
    self.insurance_crypto_income += self.insurance_fee
    self.insurance_crypto_cost += self.insurance_commission
    print(f"player{player_id} add money ${self.add_value_fee + self.insurance_fee}")
    print("pool crypto income:", self.pool_crypto_income,"pool crypto cost:", self.pool_crypto_cost,
          "pool USD income:", self.pool_income, "pool USD cost:", self.pool_cost,
          f"player{player_id} crypto income:", self.players_crypto_income[player_id],
          f"player{player_id} crypto cost:", self.players_crypto_cost[player_id],
          "insurance crypto income:",self.insurance_crypto_income,
          "insurance crypto cost",self.insurance_crypto_cost)
    return self.pool_crypto_income,self.pool_crypto_cost,self.pool_income,self.pool_cost,self.players_crypto_income[player_id],self.players_crypto_cost[player_id],self.players_USD_cost[player_id],self.players_USD_income[player_id]

  def event4_player_reward(self,df,player_id,period,kmday,mileage,wear_tolerate,discount):
    print(f"player{player_id} in Event 4: move to earn")
    #計算獎勵
    player = player_id
    c_kmday = kmday
    loc = df[df['x'] == c_kmday]
    player_reward = loc['sum'].values
    reward= player_reward[0]*discount
    print(f"player{player} run {c_kmday}km , get reward {reward} ")
    self.players_crypto_income[player_id] += reward  # 更新玩家的累積獎勵
    self.pool_crypto_cost += reward
    print("pool crypto income:", self.pool_crypto_income,"pool crypto cost:", self.pool_crypto_cost,
      f"player{player_id} crypto income:", self.players_crypto_income[player_id],
      f"player{player_id} crypto cost:", self.players_crypto_cost[player_id])

    #計算磨損率
    if player_id not in self.players_distance: # 初始化玩家的磨損率
      self.players_distance[player_id] = c_kmday
      #這邊加上讀取玩家鞋子的磨損率
      wear_rate=1-(self.players_distance[player_id]/mileage)
      print(f"player {player_id} mileage:",mileage,"km")
      print(f"player {player_id} shoes Completion initialized with {wear_rate}")
      shoes = "no"
    else:
      self.players_distance[player_id] += c_kmday  # 更新玩家的磨損率
      wear_rate=1-(self.players_distance[player_id]/mileage)
      print(f"player {player_id} mileage:",mileage,"km")
      print(f"player {player_id} shoes Completion :{wear_rate}")
      shoes = "no"
      #加上玩家對運動鞋磨損的容忍度
      if(wear_rate <= wear_tolerate):
        print(f"player {player_id} needs to change shoes")
        self.players_distance[player_id]=0#重新計算玩家的磨損率
        shoes = "yes"
    return shoes,self.pool_crypto_income,self.pool_crypto_cost,self.pool_income,self.pool_cost,self.players_crypto_income[player_id],self.players_crypto_cost[player_id],self.players_USD_cost[player_id],self.players_USD_income[player_id]

  def event5_player_change_shoes(self,player_id,event_id):
    print(f"player{player_id} in Event{event_id}: change shoes")
    self.players_NFT_amount[player_id]=0#重新計算玩家的NFT數量
    self.players_crypto_cost[player_id]+=self.nft_price
    if player_id not in self.players_USD_income:
      self.players_USD_income[player_id] = 0  # 如果玩家不存在，則初始化玩家法幣收入
    self.players_USD_income[player_id] += self.physical_shoe_price 
    self.shoes_cost += self.physical_shoe_price
    self.shoes_crypto_income += self.nft_price
    print("pool crypto income:", self.pool_crypto_income, "pool crypto cost:", self.pool_crypto_cost,
          "pool USD income:", self.pool_income, "pool USD cost:", self.pool_cost,
          f"player{player_id} crypto income:",self.players_crypto_income[player_id],
          f"player{player_id} crypto cost:",self.players_crypto_cost[player_id],
          f"player{player_id}'s nft amount:", self.players_NFT_amount[player_id],
          "shoes crypto income:", self.shoes_crypto_income, "shoes crypto cost:", self.shoes_crypto_cost,
          "shoes USD income:", self.shoes_income, "shoes USD cost:", self.shoes_cost)
    return self.pool_crypto_income,self.pool_crypto_cost,self.pool_income,self.pool_cost,self.players_crypto_income[player_id],self.players_crypto_cost[player_id],self.players_USD_cost[player_id],self.players_USD_income[player_id]

  def event6_player_hurt(self,player_id,event_id,player_hurt):
    print(f"player{player_id} in Event{event_id}: player injury")
    self.players_crypto_income[player_id] += self.compensation_amount*(1/player_hurt) #player income
    self.insurance_crypto_cost += self.compensation_amount*(1/player_hurt) #假設先給玩家5000元代幣理賠
    print("pool crypto income:", self.pool_crypto_income, "pool crypto cost:", self.pool_crypto_cost,
          "pool USD income:", self.pool_income, "pool USD cost:", self.pool_cost,
          f"player{player_id} crypto income:",self.players_crypto_income[player_id],
          f"player{player_id} crypto cost:",self.players_crypto_cost[player_id],
          "insurance crypto income:", self.insurance_crypto_income,
          "insurance crypto cost:", self.insurance_crypto_cost)
    return self.pool_crypto_income,self.pool_crypto_cost,self.pool_income,self.pool_cost,self.players_crypto_income[player_id],self.players_crypto_cost[player_id],self.players_USD_cost[player_id],self.players_USD_income[player_id]


flag = 0
discount = 4.095581
# discount = 1
results = []
tested_discounts = set()
i=0
#事件排程
def main(discount):
  current_time = 0.0
  eventtime = 0.0
  event_id = 0
  player_amount = 100
  max_days = 120
  players_add_days = {}
  player_hurt = {}
  player_change_shoes ={}
  players_crypto_income ={}
  players_crypto_cost={}
  players_USD_cost={}
  players_USD_income={}
  net=0

  event = Event(df)
  event_list = {"player": [], "EventId": [], "EventTime": []}
  #紀錄每日價格與交易量
  price_list = {"day": [], "pool_net": [],"sell_crypto_volume": [], "buy_crypto_volume": [], "crypto": []}
  player_list ={"player": [], "net": []}
  player_profiles = {
      "player_id": [],
      "age": [],
      "days/week": [],
      "run_type": [],
      "km/day": [],
      "shoes_type": [],
      "place": [],
      "mileage": [],
      "wear_rate_tolerate": [],
      "hurt_rate": []
  }
  event_id = 1
  eventtime = 1
  event_list['player'].append(0)
  event_list['EventId'].append(event_id)
  event_list['EventTime'].append(eventtime)
  # 冷啟動
  for player in range(1, player_amount + 1):
    time_interval = np.random.exponential(1/max_days)
    eventtime += time_interval  # 知道下個事件的絕對時間
    player_id = player
    event_id = 2
    event_list['player'].append(player_id)
    event_list['EventId'].append(event_id)
    event_list['EventTime'].append(eventtime)
    # 將玩家資料存儲到 player_profiles 中
    player_profiles["player_id"].append(profile["player"].iloc[player-1])
    player_profiles["age"].append(profile["age"].iloc[player-1])
    player_profiles["days/week"].append(profile["days/week"].iloc[player-1])
    player_profiles["run_type"].append(profile["run_type"].iloc[player-1])
    player_profiles["km/day"].append(profile["km/day"].iloc[player-1])
    player_profiles["shoes_type"].append(profile["shoes_type"].iloc[player-1])
    player_profiles["place"].append(profile["place"].iloc[player-1])
    player_profiles["mileage"].append(profile["mileage"].iloc[player-1])
    player_profiles["wear_rate_tolerate"].append(profile["wear_rate_tolerate"].iloc[player-1])
    player_profiles["hurt_rate"].append(profile["hurt_rate"].iloc[player-1])
  player_profile_df = pd.DataFrame(player_profiles)

  # 使用 while 循環找到下一個發生的事件
  while current_time < max_days:
    smalltime = max_days
    next_event_id = -1
    next_event_time = -1
    # 遍歷 event_list 中的事件時間，找到比 current_time 大且最接近的時間
    for i in range(len(event_list['EventTime'])):
        event_time = event_list['EventTime'][i]
        if  event_time > current_time and event_time < smalltime:
            smalltime = event_time
            next_player = event_list['player'][i]
            next_event_id = event_list['EventId'][i]
            next_event_time =  event_time
            record_number = i

    if next_event_id == -1:
        print("No more events to simulate.")
        pool_net = (USD_income + crypto_income*crypto) - (USD_cost+ crypto_cost*crypto)
        Profit_Margin = pool_net /(USD_income+crypto_income*crypto)
        for player in range(1,player_amount+1):
           net = (players_USD_income[player]+players_crypto_income[player]*crypto)-(players_USD_cost[player]*crypto+players_crypto_cost[player])
           player_list['player'].append(player)
           player_list['net'].append(net)
        print("---------------------------Total----------------------------------")
        print(f"pool income is ${USD_income+crypto_income*crypto}, pool cost is ${USD_cost+crypto_cost*crypto}, pool net is ${pool_net}, Profit Margin is ${Profit_Margin}")
        break
    # print(event_list)
    del event_list['player'][record_number]
    del event_list['EventId'][record_number]
    del event_list['EventTime'][record_number]
    # print(event_list)
    print("--------------------------------------------------------------------")
    if next_player ==0:
       print(f"Update Crypto Price on day {int(next_event_time)}")
    else:
       print(f"Next event : player {next_player} in event{next_event_id} on time {next_event_time:.2f}")
    current_time = next_event_time  # 更新 current_times
    # 檢查是否跨天，並更新加密貨幣價格
    if next_event_id == 1:
      crypto,sell_crypto_volume,buy_crypto_volume,day,pool_net = event.event1_crypto_price(player_amount,event_list,current_time)
      event_id = 1
      eventtime = int(current_time)+1
      event_list['player'].append(0)
      event_list['EventId'].append(event_id)
      event_list['EventTime'].append(eventtime)
      price_list['day'].append(day)
      price_list['pool_net'].append(pool_net)
      price_list['sell_crypto_volume'].append(sell_crypto_volume)
      price_list['buy_crypto_volume'].append(buy_crypto_volume)
      price_list['crypto'].append(crypto)


    elif next_event_id == 2:
      if player_id not in players_USD_income:
         players_USD_income[next_player] = 0  # 如果玩家不存在，則初始化玩家USD支出
      if player_id not in players_USD_cost:
         players_USD_cost[next_player] = 0  # 如果玩家不存在，則初始化玩家USD支出
      if player_id not in players_crypto_cost:
         players_crypto_cost[next_player] = 0  # 如果玩家不存在，則初始化玩家代幣收入
      if player_id not in players_crypto_income:
          players_crypto_income[next_player] = 0  # 如果玩家不存在，則初始化玩家代幣收入

      runtype = player_profile_df['run_type'].iloc[next_player-1]
      crypto_income,crypto_cost,USD_income,USD_cost,players_crypto_income[next_player],players_crypto_cost[next_player],players_USD_cost[next_player],players_USD_income[next_player] = event.event2_player_buy_nft(next_player,next_event_id)
      nextevent = 3
      if nextevent == 3:
          next_event_id = 3
          time_interval = np.random.exponential(1/max_days)
          eventtime = current_time+time_interval  # 知道下個事件的絕對時間
          event_list['player'].append(next_player)
          event_list['EventId'].append(next_event_id)
          event_list['EventTime'].append(eventtime)

    elif next_event_id == 3:
      runtype = player_profile_df['run_type'].iloc[next_player-1]
      if runtype == 'A' :
        pass
      else:
        crypto_income,crypto_cost,USD_income,USD_cost,players_crypto_income[next_player],players_crypto_cost[next_player],players_USD_cost[next_player],players_USD_income[next_player] = event.event3_player_add(next_player,next_event_id)
        players_add_days[next_player]=1
        print(f"Cumulative {players_add_days[next_player]} days")
        # 設定下一個事件為事件4
        next_event_id = 4
        time_interval = np.random.exponential(1/max_days)
        eventtime = current_time+time_interval  # 知道下個事件的絕對時間
        event_list['player'].append(next_player)
        event_list['EventId'].append(next_event_id)
        event_list['EventTime'].append(eventtime)

    elif next_event_id == 4:
      period = player_profile_df['days/week'].iloc[next_player-1]
      runtype =player_profile_df['run_type'].iloc[next_player-1]
      kmday = player_profile_df['km/day'].iloc[next_player-1]
      period = player_profile_df['days/week'].iloc[next_player-1]
      mileage = player_profile_df['mileage'].iloc[next_player-1]
      wear_tolerate = player_profile_df['wear_rate_tolerate'].iloc[next_player-1]
      hurtrate = player_profile_df['hurt_rate'].iloc[next_player-1]

      #根據跑步週期分配時間間隔
      if players_add_days[next_player] >= 30:
        print(f"player {next_player} needs to add value in their NFT again")
        next_event_id = 3
        time_interval = np.random.exponential(1/max_days)
        eventtime = current_time + time_interval  # 知道下個事件的絕對時間
        event_list['player'].append(next_player)
        event_list['EventId'].append(next_event_id)
        event_list['EventTime'].append(eventtime)
      else:
        shoes,crypto_income,crypto_cost,USD_income,USD_cost,players_crypto_income[next_player],players_crypto_cost[next_player],players_USD_cost[next_player],players_USD_income[next_player] = event.event4_player_reward(df,next_player,period,kmday,mileage,wear_tolerate,discount)
        print(f"player{next_player} run {period} days per week")
        players_add_days[next_player]+=1
        print(f"Cumulative {players_add_days[next_player]} days")
        hurt = random.choices(["hurt", "nohurt"], weights=[80,20], k=1)[0]
        if hurt == "hurt":
          next_event_id = 6
        elif shoes == "yes":
          next_event_id = 5
        else:
          next_event_id = 4

        if next_event_id == 4:
          if period == 7:
              time_interval = 1
          elif period == 6:
              time_interval = 2
          elif period == 5:
              time_interval = 3
          elif period == 4:
              time_interval = 4
          elif period == 3:
              time_interval = 5
          elif period == 2:
              time_interval = 6
          else:
              time_interval = 7
        else:
          time_interval = np.random.exponential(1)
        eventtime = current_time + time_interval  # 知道下個事件的絕對時間
        event_list['player'].append(next_player)
        event_list['EventId'].append(next_event_id)
        event_list['EventTime'].append(eventtime)

    elif next_event_id == 5:
      if next_player not in player_change_shoes:
        player_change_shoes[next_player] = 1
      else:
        player_change_shoes[next_player] += 1
      crypto_income,crypto_cost,USD_income,USD_cost,players_crypto_income[next_player],players_crypto_cost[next_player],players_USD_cost[next_player],players_USD_income[next_player] = event.event5_player_change_shoes(next_player, next_event_id)
      print(f"player {next_player} has changed {player_change_shoes[next_player]} shoes")
      # 設定下一個事件為事件4
      next_event_id = 2
      time_interval = np.random.exponential(1/max_days)
      eventtime = current_time + time_interval  # 知道下個事件的絕對時間
      event_list['player'].append(next_player)
      event_list['EventId'].append(next_event_id)
      event_list['EventTime'].append(eventtime)

    elif next_event_id == 6:
      if next_player not in player_hurt:
        player_hurt[next_player] = 1
      else:
        player_hurt[next_player] += 1
      crypto_income,crypto_cost,USD_income,USD_cost,players_crypto_income[next_player],players_crypto_cost[next_player],players_USD_cost[next_player],players_USD_income[next_player] = event.event6_player_hurt(next_player,next_event_id,player_hurt[next_player])#保險理賠
      print(f"player{next_player} hurt {player_hurt[next_player]} times")
      next_event_id = 4
      player_current_age = player_profile_df['age'].iloc[next_player-1]
      if player_current_age > 60 :
        time_interval = 35
      elif 60>=player_current_age>50:
        time_interval = 28
      elif 50>=player_current_age>40 :
        time_interval = 21
      elif 40>=player_current_age>30 :
        time_interval = 14
      else :
        time_interval = 7
      print(f"player{next_player} needs to rest for {time_interval} days")
      eventtime = current_time+time_interval
      # 知道下個事件的絕對時間
      event_list['player'].append(next_player)
      event_list['EventId'].append(next_event_id)
      event_list['EventTime'].append(eventtime)

  price_list_df = pd.DataFrame(price_list)
  player_list_df =pd.DataFrame(player_list)
  return Profit_Margin,price_list_df,player_list_df
  # return Profit_Margin
Profit_Margin,price_list_df,player_list_df = main(discount)
print(player_list_df)
price_list_df.to_csv("/Users/renjie/Desktop/碩三/M2Ecode/price_list2_100_120(test).csv")
player_list_df.to_csv("/Users/renjie/Desktop/碩三/M2Ecode/player_list2_100_120(test).csv")
