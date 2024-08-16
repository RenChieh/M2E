#M2E系統-探討不同專業跑者比例對獎勵權重值的影響
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("/Users/renjie/Desktop/github/M2E/data_4.csv")
profile = pd.read_csv("/Users/renjie/Desktop/github/M2E/player_data/player_profile3_50.csv")
#事件
class Event:
  def __init__(self,df,nft_amount=100, nft_price=2000, physical_shoe_price=2000, add_value_fee=1000, insurance_fee=2000,compensation_amount=5000):
    self.nft_amount = nft_amount
    self.nft_price = nft_price
    self.physical_shoe_price = physical_shoe_price
    self.add_value_fee = add_value_fee
    self.insurance_fee = insurance_fee
    self.compensation_amount = compensation_amount
    self.df = df
    #M2E角色初始值
    self.player_cost = 0
    self.player_income = 0
    self.pool_cost = 0
    self.pool_income = 0
    self.shoes_cost = 0
    self.shoes_income = 0
    self.insurance_cost = 0
    self.insurance_income = 0
    self.add_day = 0
    #M2E相關費用計算
    self.Transaction_fee = nft_price * 0.05  #交易手續費
    self.physical_shoe_commission = physical_shoe_price * 0.3 #實體運動鞋銷售抽成
    self.insurance_commission = insurance_fee * 0.3 #保險抽成
    self.Creator_Earnings = nft_price * 0.05 #NFT運動鞋版稅(權利金)
    #避免重複計算到玩家
    self.players_bought_NFT = set()
    self.players_add_NFT = set()
    #存玩家的累積加值金額
    self.players_topup = {}
    #存玩家的累積天數
    self.players_buy_NFT = {}
    self.players_income_NFT = {}
    #存玩家的累積獎勵
    self.players_rewards = {}
    #存玩家磨損率
    self.players_distance = {}
    self.player_data = {}
    #計算玩家受傷
    self.player_hurt = {}
# def event1_player_log_in(self,player_id):

#     return player_profile

  def event2_player_buy_nft(self,player_id,event_id,eventtime):
    print(f"player{player_id} in Event{event_id}: buy NFT")
    if player_id not in self.players_rewards:
        self.players_rewards[player_id] = 0  # 如果玩家不存在，則初始化玩家獎勵
    self.nft_amount -= 1
    self.players_topup[player_id] = self.nft_price + self.Transaction_fee + self.Creator_Earnings  # 玩家支出
    self.pool_income += (self.nft_price + self.Transaction_fee + self.Creator_Earnings)
    print("pool income:", self.pool_income, "pool cost:", self.pool_cost,
          f"player{player_id} income:",self.players_rewards[player_id],f"player{player_id} cost:",
    self.players_topup[player_id],"nft amount:", self.nft_amount)

  def event3_player_add(self,player_id,event_id,eventtime):
    if player_id not in self.players_rewards:
        self.players_rewards[player_id] = 0  # 如果玩家不存在，則初始化玩家獎勵
    if player_id not in self.players_topup:
        self.players_topup[player_id] = self.add_value_fee + self.nft_price + self.Transaction_fee + self.Creator_Earnings
        self.pool_income += (self.add_value_fee + self.Transaction_fee)
        print(f"player{player_id} add money ${self.add_value_fee + self.insurance_fee}")
        print("pool income:", self.pool_income,"pool cost:", self.pool_cost,
          f"player{player_id} income:", self.players_rewards[player_id],f"player{player_id} cost:", self.players_topup[player_id])
        return
    else:
        print(f"player{player_id} in Event {event_id}: top-up NFT")
        # self.player_cost += (self.add_value_fee + self.insurance_fee)
        self.players_topup[player_id] += (self.add_value_fee + self.Transaction_fee)
        self.pool_income += (self.add_value_fee + self.Transaction_fee)
        print("pool income:", self.pool_income,"pool cost:", self.pool_cost,
                  f"player{player_id} income:", self.players_rewards[player_id],f"player{player_id} cost:", self.players_topup[player_id])
    return self.pool_income,self.pool_cost
  def event4_player_reward(self,df,player_id,period,kmday,mileage,wear_tolerate,discount):
    print(f"player{player_id} in Event 4: move to earn")
    #計算獎勵
    player = player_id
    c_kmday = kmday
    loc = df[df['x'] == c_kmday]
    player_reward = loc['sum'].values
    reward= player_reward[0]*discount
    print(f"player{player} run {c_kmday}km , get reward {reward} ")
    if player_id not in self.players_rewards:
      self.players_rewards[player_id] = reward  # 如果玩家不存在，則初始化玩家獎勵
      self.pool_cost += reward
      # self.player_cost =
      print(f"player{player_id} initialized with {reward} reward")
      print("pool income:",self.pool_income,"pool cost:",self.pool_cost,
            f"player{player_id} income:",self.players_rewards[player_id],f"player{player_id} cost:",self.players_topup[player_id])
    else:
      self.players_rewards[player_id] += reward  # 更新玩家的累積獎勵
      self.pool_cost += reward
      print("pool income:",self.pool_income,"pool cost:",self.pool_cost,
            f"player{player_id} income:",self.players_rewards[player_id],f"player{player_id} cost:",self.players_topup[player_id])
    #計算磨損率
    if player_id not in self.players_distance: # 初始化玩家的磨損率
      self.players_distance[player_id] = c_kmday
      #這邊加上讀取玩家鞋子的磨損率
      wear_rate=self.players_distance[player_id]/mileage
      print(f"player {player_id} mileage:",mileage,"km")
      print(f"player {player_id} shoes wear rate initialized with {wear_rate}")
      shoes = "no"
    else:
      self.players_distance[player_id] += c_kmday  # 更新玩家的磨損率
      wear_rate=self.players_distance[player_id]/mileage
      print(f"player {player_id} mileage:",mileage,"km")
      print(f"player {player_id} shoes wear rate :{wear_rate}")
      shoes = "no"
      #加上玩家對運動鞋磨損的容忍度
      if(wear_rate >= wear_tolerate):
        print(f"player {player_id} needs to change shoes")
        self.players_distance[player_id]=0#重新計算玩家的磨損率
        shoes = "yes"
    return shoes,self.pool_income,self.pool_cost

  def event5_player_change_shoes(self,player_id,event_id,eventtime):
    print(f"player{player_id} in Event{event_id}: change shoes")
    self.players_topup[player_id] += self.physical_shoe_price #player cost
    self.shoes_income += self.physical_shoe_price
    self.shoes_cost += self.physical_shoe_commission
    self.pool_income += self.physical_shoe_commission
    print("pool income:",self.pool_income,"pool cost:",self.pool_cost,f"player{player_id} income:",self.players_rewards[player_id],f"player{player_id} cost:",self.players_topup[player_id],
          "insurance income:", self.insurance_income, "insurance cost:", self.insurance_cost)
    return self.pool_income,self.pool_cost

  def event6_player_hurt(self,player_id,event_id,eventtime):
    print(f"player{player_id} in Event{event_id}: player injury")
    self.players_rewards[player_id] += self.compensation_amount #player income
    self.insurance_cost += self.compensation_amount #假設先給玩家5000保險理賠
    print("pool income:",self.pool_income,"pool cost:",self.pool_cost,f"player{player_id} income:",self.players_rewards[player_id],f"player{player_id} cost:",self.players_topup[player_id],
          "insurance income:", self.insurance_income, "insurance cost:", self.insurance_cost)
    return self.pool_income,self.pool_cost

flag = 0
discount = 1

results = []
tested_discounts = set()
i=0
#事件排程
def main(discount):
  current_time = 0.0
  eventtime = 0.0
  event_id = 0
  player_amount = 300
  max_days = 480
  players_add_days = {}
  player_change_shoes = {}
  player_hurt = {}

  event = Event(df)
  event_list = {"player": [], "EventId": [], "EventTime": []}
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


  # 冷啟動
  for player in range(1, player_amount + 1):
    time_interval = np.random.exponential(1/max_days)
    eventtime += time_interval  # 知道下個事件的絕對時間
    player_id = player
    event_id = 1
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
        pool_net = pool_income - pool_cost
        Profit_Margin = (pool_income - pool_cost)/pool_cost
        print("---------------------------Total----------------------------------")
        print(f"pool income is {pool_income}, pool cost is {pool_cost}, pool net is {pool_net}, Profit Margin is {Profit_Margin}")
        break
    # print(event_list)
    del event_list['player'][record_number]
    del event_list['EventId'][record_number]
    del event_list['EventTime'][record_number]
    # print(event_list)
    print("--------------------------------------------------------------------")
    print(f"Next event : player{next_player} in event{next_event_id} at time {next_event_time:.2f}")
    current_time = next_event_time  # 更新 current_time
    if next_event_id == 1:
      next_event_id = 2
      time_interval = np.random.exponential(1/max_days)
      eventtime = current_time+time_interval  # 知道下個事件的絕對時間
      event_list['player'].append(next_player)
      event_list['EventId'].append(next_event_id)
      event_list['EventTime'].append(eventtime)

    elif next_event_id == 2:
      event.event2_player_buy_nft(next_player,next_event_id,next_event_time)
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
        pool_income,pool_cost = event.event3_player_add(next_player,next_event_id,next_event_time)
        players_add_days[next_player]=1
        print(f"Cumulative {players_add_days[next_player]} days")
        nextevent = 4
        if nextevent == 4:
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
        shoes,pool_income,pool_cost = event.event4_player_reward(df,next_player,period,kmday,mileage,wear_tolerate,discount)
        print(f"player{next_player} run {period} days per week")
        players_add_days[next_player]+=1
        print(f"Cumulative {players_add_days[next_player]} days")
        hurt = random.choices(["hurt", "nohurt"], weights=[hurtrate,1-hurtrate], k=1)[0]
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
      pool_income,pool_cost = event.event5_player_change_shoes(next_player, next_event_id, next_event_time)
      print(f"player {next_player} has changed {player_change_shoes[next_player]} shoes")
      # 設定下一個事件為事件4
      next_event_id = 4
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
      pool_income,pool_cost =  event.event6_player_hurt(next_player,next_event_id,next_event_time)#保險理賠
      print(f"player{next_player} hurt {player_hurt[next_player]} times")
      next_event_id = 4
      player_current_age = player_profile_df['age'].iloc[next_player-1]
      # time_interval = np.random.exponential(1/player_amount)
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
  return Profit_Margin


while(flag==0):
    Profit_Margin = main(discount)
    i += 1

    results.append({"Test_Num": i, "Profit_Margin": Profit_Margin ,"weight": discount})
    if 0.1 <= Profit_Margin <= 0.12:
        print(f"Profit Margin is {Profit_Margin}, weight is {discount}")
        break
    if Profit_Margin > 0.12:
        discount = discount * 1.05  # 增加折扣，减少Profit Margin
        print(f"Profit Margin too high, is {Profit_Margin}, increasing weight to {discount}")
    if Profit_Margin < 0.1:
        discount = discount * 0.95  # 减少折扣，增加Profit Margin
        print(f"Profit Margin too low, is {Profit_Margin}, decreasing weight to {discount}")
  
results_df = pd.DataFrame(results)
print(results_df)