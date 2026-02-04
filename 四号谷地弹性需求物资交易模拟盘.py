import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import os
import sys  # 新增：用于判断exe运行环境
from PIL import Image, ImageTk

class GoodsTradingGUI:
    def __init__(self, root):
        # 初始化主窗口
        self.root = root
        self.root.title("四号谷地弹性货物需求交易市场模拟盘")
        self.root.geometry("1100x850")
        self.root.resizable(False, False)

        # ========== 核心配置 ==========
        self.BASE_INIT_PRICE = 2000
        self.PRICE_PRECISION = 2
        self.RATE_PRECISION = 1
        
        # 新增：适配exe和开发环境的路径逻辑（核心修复）
        if getattr(sys, 'frozen', False):
            # 若是exe运行环境：获取exe所在的实际目录
            self.CODE_DIR = os.path.dirname(sys.executable)
        else:
            # 若是开发环境：获取代码文件所在目录
            self.CODE_DIR = os.path.dirname(os.path.abspath(__file__))

        # ========== 货物基础信息 ==========
        self.shang_ping = [
            "锚点厨具货组","悬空骨雕货组","巫术矿钻货组","天使罐头货组",
            "谷地水培肉货组","团结牌口服液货组","源石树幼苗货组","塞什卡脾石货组",
            "星体晶块货组","警戒者矿镐货组","硬脑壳头盔货组","边角料积木货组"
        ]
        # 图片路径：始终指向「exe/代码」所在目录 + 图片名
        self.goods_image_paths = [
            os.path.join(self.CODE_DIR, "goods1.png"),
            os.path.join(self.CODE_DIR, "goods2.png"),
            os.path.join(self.CODE_DIR, "goods3.png"),
            os.path.join(self.CODE_DIR, "goods4.png"),
            os.path.join(self.CODE_DIR, "goods5.png"),
            os.path.join(self.CODE_DIR, "goods6.png"),
            os.path.join(self.CODE_DIR, "goods7.png"),
            os.path.join(self.CODE_DIR, "goods8.png"),
            os.path.join(self.CODE_DIR, "goods9.png"),
            os.path.join(self.CODE_DIR, "goods10.png"),
            os.path.join(self.CODE_DIR, "goods11.png"),
            os.path.join(self.CODE_DIR, "goods12.png")
        ]
        
        # ========== 业务数据初始化 ==========
        self.value_of_uppoint = []  # 价格波动系数（原始）
        self.value_bili = []        # 涨幅百分比（最终展示）
        self.value_shangping = []   # 当前货物价格（精确值，出售时用这个）
        self.basic_value_now = []   # 初始化时的基准价备份
        self.money = 100000         # 调度券
        self.day = 0                # 当前交易日
        self.sell_level = 1         # 交易等级
        self.sell_exp = 0           # 当前经验
        self.sell_level_list = [0,100000,300000,500000,700000,1000000,3000000,5000000,7000000,10000000,30000000,50000000,100000000]
        self.backup_number = [0]*12 # 货物库存
        self.value_of_buying = [50,100,150,200,250,300,350,400,450,500,550,600] # 各等级购买量
        self.backup_chengben = [0]*12 # 成本均价
        self.value_of_buying_now = 0  # 当日剩余购买量

        # 当前阶段标识（buy/sell）
        self.current_phase = "buy"

        # 网格组件引用
        self.buy_goods_widgets = []
        self.sell_goods_widgets = []

        # ========== 执行顺序：先初始化价格，再创建界面 ==========
        self.init_goods_price()  # 第一步：先生成价格数据
        self.create_widgets()    # 第二步：再创建界面

        # ========== 初始化数据并启动 ==========
        self.next_day()

    # 初始化货物价格（严格以2000为基准，精确计算）
    def init_goods_price(self):
        # 清空历史数据
        self.value_of_uppoint.clear()
        self.value_bili.clear()
        self.value_shangping.clear()
        self.basic_value_now.clear()

        # 为每个货物生成精准的波动系数（-50% ~ +50% 之间）
        for _ in range(12):
            is_rise = random.choice([True, False])
            fluctuate_rate = round(random.uniform(1, 50), self.PRICE_PRECISION) / 100
            if not is_rise:
                fluctuate_rate = -fluctuate_rate
            self.value_of_uppoint.append(fluctuate_rate)

        # 基于2000基准价计算最终价格和涨幅
        for idx in range(12):
            base_price = self.BASE_INIT_PRICE
            fluctuate_coeff = self.value_of_uppoint[idx]
            
            price_change = base_price * fluctuate_coeff
            final_price = base_price + price_change
            final_price = round(final_price, self.PRICE_PRECISION)
            
            rise_rate = round((price_change / base_price) * 100, self.RATE_PRECISION)
            
            self.value_shangping.append(final_price)
            self.value_bili.append(rise_rate)
            self.basic_value_now.append(base_price)

    # 刷新次日货物价格（基于前一日价格精准波动）
    def refresh_goods_price(self):
        self.value_of_uppoint.clear()
        prev_prices = [price for price in self.value_shangping]
        self.value_shangping.clear()
        self.value_bili.clear()

        # 生成新波动系数
        for _ in range(12):
            is_rise = random.choice([True, False])
            fluctuate_rate = round(random.uniform(1, 50), self.PRICE_PRECISION) / 100
            if not is_rise:
                fluctuate_rate = -fluctuate_rate
            self.value_of_uppoint.append(fluctuate_rate)

        # 计算新价格
        for idx in range(12):
            prev_price = prev_prices[idx]
            fluctuate_coeff = self.value_of_uppoint[idx]
            
            price_change = prev_price * fluctuate_coeff
            new_price = prev_price + price_change
            new_price = round(new_price, self.PRICE_PRECISION)
            
            rise_rate = round((price_change / prev_price) * 100, self.RATE_PRECISION)
            
            self.value_shangping.append(new_price)
            self.value_bili.append(rise_rate)

    # 通用方法：创建2×6货物网格（移除出售轮的当前售价显示）
    def create_goods_grid(self, parent, is_buy_phase):
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        widgets_list = []
        for row in range(2):
            for col in range(6):
                goods_idx = row * 6 + col
                # 创建带边框的小矩形
                goods_frame = ttk.LabelFrame(
                    grid_frame, 
                    text=f"[{goods_idx+1}]",
                    width=160, height=220
                )
                goods_frame.grid(row=row, column=col, padx=8, pady=8)
                goods_frame.pack_propagate(False)

                # 1. 货物图片
                img_label = tk.Label(goods_frame)
                img_label.pack(pady=5)
                self.load_goods_image(goods_idx, img_label)

                # 2. 货物名称
                name_label = ttk.Label(goods_frame, text=self.shang_ping[goods_idx], font=("SimHei", 10, "bold"))
                name_label.pack(pady=3)

                # 3. 购买轮/出售轮不同内容
                if is_buy_phase:
                    # 购买轮：价格（取整展示，计算用精确值）
                    price_label = ttk.Label(goods_frame, text=f"价格：{int(self.value_shangping[goods_idx])}", font=("SimHei", 10))
                    price_label.pack(pady=3)
                    # 购买轮：涨幅（初始占位）
                    rate_label = ttk.Label(goods_frame, text=f"涨幅：0.0%", font=("SimHei", 10))
                    rate_label.pack(pady=3)
                    widgets_list.append({
                        "img": img_label,
                        "name": name_label,
                        "price": price_label,
                        "rate": rate_label
                    })
                else:
                    # 出售轮：仅显示库存和成本均价（移除当前售价）
                    stock_label = ttk.Label(goods_frame, text=f"库存：{self.backup_number[goods_idx]}", font=("SimHei", 10))
                    stock_label.pack(pady=3)
                    cost_label = ttk.Label(goods_frame, text=f"成本均价：{self.backup_chengben[goods_idx]:.2f}", font=("SimHei", 10))
                    cost_label.pack(pady=3)
                    widgets_list.append({
                        "img": img_label,
                        "name": name_label,
                        "stock": stock_label,
                        "cost": cost_label
                    })
        
        return grid_frame, widgets_list

    # 加载货物图片（从代码目录读取）
    def load_goods_image(self, goods_idx, img_label):
        try:
            # 从代码所在目录加载图片
            image_path = self.goods_image_paths[goods_idx]
            image = Image.open(image_path)
            image = image.resize((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            img_label.config(image=photo)
            img_label.photo = photo  # 保留引用防止图片消失
        except FileNotFoundError:
            # 提示更精准：显示代码目录路径
            img_label.config(text=f"图片未找到\n代码目录：{self.CODE_DIR}\n请放入goods{goods_idx+1}.png", font=("SimHei", 7))
        except PermissionError:
            img_label.config(text="无图片访问权限", font=("SimHei", 8))
        except Exception as e:
            img_label.config(text=f"加载失败\n{str(e)[:8]}", font=("SimHei", 8))

    # 创建所有GUI组件
    def create_widgets(self):
        # 1. 顶部状态栏
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lbl_day = ttk.Label(self.status_frame, text="当前交易日：1")
        self.lbl_day.pack(side=tk.LEFT, padx=10)
        self.lbl_level = ttk.Label(self.status_frame, text="交易等级：1")
        self.lbl_level.pack(side=tk.LEFT, padx=10)
        self.lbl_money = ttk.Label(self.status_frame, text="当前调度券：100000")
        self.lbl_money.pack(side=tk.LEFT, padx=10)
        self.lbl_buy_remain = ttk.Label(self.status_frame, text="剩余购买量：50")
        self.lbl_buy_remain.pack(side=tk.LEFT, padx=10)
        self.lbl_exp_current = ttk.Label(self.status_frame, text="当前经验：0")
        self.lbl_exp_current.pack(side=tk.LEFT, padx=10)
        self.lbl_exp_next = ttk.Label(self.status_frame, text="下一级所需：100000")
        self.lbl_exp_next.pack(side=tk.LEFT, padx=10)
        self.lbl_exp_need = ttk.Label(self.status_frame, text="距离升级还差：100000")
        self.lbl_exp_need.pack(side=tk.LEFT, padx=10)

        # 2. 核心内容区
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 2.1 购买区域
        self.buy_area = ttk.Frame(self.content_frame)
        self.lbl_buy_title = ttk.Label(self.buy_area, text="【购买轮】今日货物价目表", font=("SimHei", 12, "bold"))
        self.lbl_buy_title.pack(anchor=tk.W, pady=5)
        self.buy_grid_frame, self.buy_goods_widgets = self.create_goods_grid(self.buy_area, is_buy_phase=True)
        
        # 购买操作区
        self.buy_op_frame = ttk.Frame(self.buy_area)
        self.buy_op_frame.pack(fill=tk.X, pady=10)
        ttk.Label(self.buy_op_frame, text="货物编号：").grid(row=0, column=0, padx=5)
        self.ent_buy_kind = ttk.Entry(self.buy_op_frame, width=10)
        self.ent_buy_kind.grid(row=0, column=1, padx=5)
        ttk.Label(self.buy_op_frame, text="购买数量：").grid(row=0, column=2, padx=5)
        self.ent_buy_num = ttk.Entry(self.buy_op_frame, width=10)
        self.ent_buy_num.grid(row=0, column=3, padx=5)
        self.btn_buy = ttk.Button(self.buy_op_frame, text="确认购买", command=self.buy_goods)
        self.btn_buy.grid(row=0, column=4, padx=10)
        self.btn_end_buy = ttk.Button(self.buy_op_frame, text="主动结束购买轮", command=self.end_buy_phase)
        self.btn_end_buy.grid(row=0, column=5, padx=10)

        # 2.2 出售区域（移除标题中的实时价格提示）
        self.sell_area = ttk.Frame(self.content_frame)
        self.lbl_sell_title = ttk.Label(self.sell_area, text="【出售轮】当前库存", font=("SimHei", 12, "bold"))
        self.lbl_sell_title.pack(anchor=tk.W, pady=5)
        self.sell_grid_frame, self.sell_goods_widgets = self.create_goods_grid(self.sell_area, is_buy_phase=False)
        
        # 出售操作区
        self.sell_op_frame = ttk.Frame(self.sell_area)
        self.sell_op_frame.pack(fill=tk.X, pady=10)
        ttk.Label(self.sell_op_frame, text="货物编号：").grid(row=0, column=0, padx=5)
        self.ent_sell_kind = ttk.Entry(self.sell_op_frame, width=10)
        self.ent_sell_kind.grid(row=0, column=1, padx=5)
        ttk.Label(self.sell_op_frame, text="出售数量：").grid(row=0, column=2, padx=5)
        self.ent_sell_num = ttk.Entry(self.sell_op_frame, width=10)
        self.ent_sell_num.grid(row=0, column=3, padx=5)
        self.btn_sell = ttk.Button(self.sell_op_frame, text="确认出售", command=self.sell_goods)
        self.btn_sell.grid(row=0, column=4, padx=10)
        self.btn_end_sell = ttk.Button(self.sell_op_frame, text="主动结束出售轮", command=self.next_day)
        self.btn_end_sell.grid(row=0, column=5, padx=10)

        # 3. 底部日志区
        self.log_frame = ttk.Frame(self.root)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.lbl_log = ttk.Label(self.log_frame, text="操作日志")
        self.lbl_log.pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=8, width=120)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    # 更新状态栏信息
    def update_status(self):
        self.lbl_day.config(text=f"当前交易日：{self.day}")
        self.lbl_level.config(text=f"交易等级：{self.sell_level}")
        self.lbl_money.config(text=f"当前调度券：{self.money}")
        self.lbl_buy_remain.config(text=f"剩余购买量：{self.value_of_buying_now}")

        current_exp = self.sell_exp
        next_level = self.sell_level
        if next_level >= len(self.sell_level_list):
            next_exp = "已满级"
            need_exp = 0
        else:
            next_exp = self.sell_level_list[next_level]
            need_exp = max(next_exp - current_exp, 0)
        
        self.lbl_exp_current.config(text=f"当前经验：{current_exp}")
        self.lbl_exp_next.config(text=f"下一级所需：{next_exp}")
        self.lbl_exp_need.config(text=f"距离升级还差：{need_exp}")

    # 更新购买轮网格（含彩色涨幅）
    def update_buy_goods_grid(self):
        for idx in range(12):
            self.buy_goods_widgets[idx]["price"].config(text=f"价格：{int(self.value_shangping[idx])}")
            rate = self.value_bili[idx]
            rate_text = f"涨幅：{rate:.1f}%"
            if rate > 0:
                self.buy_goods_widgets[idx]["rate"].config(text=rate_text, foreground="red")
            elif rate < 0:
                self.buy_goods_widgets[idx]["rate"].config(text=rate_text, foreground="green")
            else:
                self.buy_goods_widgets[idx]["rate"].config(text=rate_text, foreground="black")

    # 更新出售轮网格（仅更新库存和成本，移除当前售价）
    def update_sell_goods_grid(self):
        for idx in range(12):
            self.sell_goods_widgets[idx]["stock"].config(text=f"库存：{self.backup_number[idx]}")
            self.sell_goods_widgets[idx]["cost"].config(text=f"成本均价：{self.backup_chengben[idx]:.2f}")

    # 添加日志
    def add_log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # 切换到购买轮
    def show_buy_phase(self):
        self.current_phase = "buy"
        self.sell_area.pack_forget()
        self.buy_area.pack(fill=tk.BOTH, expand=True)
        self.update_buy_goods_grid()
        self.add_log("========== 进入购买轮 ==========")

    # 切换到出售轮
    def show_sell_phase(self):
        self.current_phase = "sell"
        self.buy_area.pack_forget()
        self.sell_area.pack(fill=tk.BOTH, expand=True)
        self.update_sell_goods_grid()
        self.add_log("========== 购买量已用尽/主动结束，进入出售轮 ==========")

    # 购买货物逻辑
    def buy_goods(self):
        try:
            buying_kind = int(self.ent_buy_kind.get())
            buying_number = int(self.ent_buy_num.get())
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
            return
        
        if buying_kind < 1 or buying_kind > 12:
            messagebox.showerror("编号错误", "货物编号必须是1-12之间的数字！")
            return
        
        if buying_number < 1:
            messagebox.showerror("数量错误", "购买数量必须大于0！")
            return
        
        if buying_number > self.value_of_buying_now:
            messagebox.showerror("数量错误", f"剩余购买量不足！当前剩余：{self.value_of_buying_now}")
            return
        
        kind_idx = buying_kind - 1
        unit_price = self.value_shangping[kind_idx]  # 当前购买价
        total_cost = round(unit_price * buying_number, self.PRICE_PRECISION)
        
        if total_cost > self.money:
            messagebox.showerror("调度券不足", f"需要{total_cost:.2f}调度券，当前仅有{self.money:.2f}！")
            return
        
        # 执行购买
        self.money -= total_cost
        self.value_of_buying_now -= buying_number
        self.backup_number[kind_idx] += buying_number
        
        # 加权平均计算成本
        current_price = unit_price
        if self.backup_chengben[kind_idx] == 0:
            self.backup_chengben[kind_idx] = current_price
        else:
            total_stock = self.backup_number[kind_idx]
            total_cost_prev = self.backup_chengben[kind_idx] * (total_stock - buying_number)
            new_avg_cost = (total_cost_prev + total_cost) / total_stock
            self.backup_chengben[kind_idx] = round(new_avg_cost, self.PRICE_PRECISION)
        
        self.add_log(f"购买成功！{self.shang_ping[kind_idx]} × {buying_number} | 单价：{int(unit_price)} | 消耗：{int(total_cost)} | 剩余调度券：{int(self.money)}")
        self.update_status()
        
        # 清空输入框
        self.ent_buy_kind.delete(0, tk.END)
        self.ent_buy_num.delete(0, tk.END)

        # 强制切换
        if self.value_of_buying_now == 0:
            self.add_log(f"剩余购买量为0，强制进入出售轮！")
            self.show_sell_phase()

    # 主动结束购买轮
    def end_buy_phase(self):
        self.show_sell_phase()
        self.add_log(f"你已主动结束购买轮（剩余购买量：{self.value_of_buying_now}）")

    # 出售货物按当前实时价格计算（仅日志保留单价，界面不显示）
    def sell_goods(self):
        try:
            sell_kind = int(self.ent_sell_kind.get())
            sell_number = int(self.ent_sell_num.get())
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
            return
        
        if sell_kind < 1 or sell_kind > 12:
            messagebox.showerror("编号错误", "货物编号必须是1-12之间的数字！")
            return
        
        kind_idx = sell_kind - 1
        
        if self.backup_number[kind_idx] == 0:
            messagebox.showerror("库存不足", "该货物库存为0，无法出售！")
            return
        
        if sell_number < 1 or sell_number > self.backup_number[kind_idx]:
            messagebox.showerror("数量错误", f"出售数量无效！当前库存：{self.backup_number[kind_idx]}")
            return
        
        # 核心：仍使用当前实时价格计算出售收入（界面不显示，仅计算用）
        current_sell_price = self.value_shangping[kind_idx]
        total_income = round(current_sell_price * sell_number, self.PRICE_PRECISION)
        
        # 执行出售
        self.money += total_income
        self.backup_number[kind_idx] -= sell_number
        
        # 精确计算成本和利润
        unit_cost = self.backup_chengben[kind_idx]
        total_cost = round(unit_cost * sell_number, self.PRICE_PRECISION)
        profit = total_income - total_cost
        get_sell_exp = max(round(profit, self.PRICE_PRECISION), 0)
        self.sell_exp += get_sell_exp
        
        # 等级提升
        level_up = False
        if self.sell_level < len(self.sell_level_list) and self.sell_exp >= self.sell_level_list[self.sell_level]:
            self.sell_level += 1
            level_up = True
        
        # 重置成本（库存为0时）
        if self.backup_number[kind_idx] == 0:
            self.backup_chengben[kind_idx] = 0
        
        # 日志保留实时单价（便于核对），界面不显示
        self.add_log(f"出售成功！{self.shang_ping[kind_idx]} × {sell_number} | 收入：{int(total_income)} | 剩余调度券：{int(self.money)}")
        self.add_log(f"本次成本：{int(total_cost)} | 利润：{int(profit)} | 获得经验：{int(get_sell_exp)}")
        if level_up:
            self.add_log(f"恭喜！交易等级提升至{self.sell_level}，每日可购买量+50")
        
        self.update_status()
        self.update_sell_goods_grid()  # 仅更新库存和成本
        
        # 清空输入框
        self.ent_sell_kind.delete(0, tk.END)
        self.ent_sell_num.delete(0, tk.END)

    # 进入下一天
    def next_day(self):
        self.day += 1
        self.value_of_buying_now = self.value_of_buying[self.sell_level-1]
        
        # 刷新价格（生成新的实时价格）
        self.refresh_goods_price()
        
        # 切换回购买轮
        self.show_buy_phase()
        self.update_status()
        self.add_log(f"========== 进入第{self.day}个交易日 ==========")
        self.add_log(f"货物价格已刷新，可开始购买")

# 程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = GoodsTradingGUI(root)
    app.show_buy_phase()
    root.mainloop()
