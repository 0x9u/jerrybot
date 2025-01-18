def adjust_price(base_price, current_demand, baseline_demand, sensitivity=0.01):
  demand_ratio = current_demand / baseline_demand if baseline_demand > 0 else 1
  
  if demand_ratio > 1:
    price_adjustment = (demand_ratio - 1) * sensitivity
    new_price = base_price * (1 + price_adjustment)
  elif demand_ratio < 1:
    price_adjustment = (1 - demand_ratio) * sensitivity
    new_price = base_price * (1 - price_adjustment)
  else:
    new_price = base_price
  
  return round(new_price)