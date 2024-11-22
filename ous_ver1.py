#%%
from pyqubo import Array
import openjij as oj
import itertools
import pandas as pd

# 学年の定義
grade = ['1年生', '2年生']
num_grade = len(grade)

# 各学年の講義
grade1 = [0, 2, 5, 6, 8, 9, 12, 13]
grade2 = [1, 3, 4, 7, 10, 11, 14]
sub_G = [grade1, grade2]

#色の数・時間枠(コマ数)
day = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日']
time = ['1限', '2限', '3限', '4限']
day_of_week = len(day)
time_per_day = len(time)


# 辺集合の定義

# edge2 : プロ基とWebプロは連続開講したい
edge2 = [(1,7), (5,8)]

# edge_P(p)：p番目の先生が担当する科目の全ての組合せ
edge_P = {}
for i, subject in enumerate(sub_P):
  list_pair = []
  for pair in itertools.combinations(subject, 2):
    list_pair.append(pair)
  edge_P[i] = list_pair

# edge_G(g)：g年生の科目の全ての組合せ
edge_G = {}
for i, subject in enumerate(sub_G):
  list_pair = []
  for pair in itertools.combinations(subject, 2):
    list_pair.append(pair)
  edge_G[i] = list_pair

# edge4 : プロ基とWebプロは同時に開講しない
edge4 = [(1,5), (1,8), (5,7), (7,8)]

# edge5：情報リテラシーとプログラミング基礎は同じ曜日にしない
edge5 = [(2,5), (2,8), (5,6), (6,8)]

# edge6：基礎数学lと情報リテラシーと人間工学は週２開講(月木or火金)
edge6 = [(3,10), (0,13), (2,6)]

# 決定変数
x = Array.create('x', shape=(n, day_of_week, time_per_day), vartype='BINARY')
# スラック変数
z = Array.create('z', shape=(num_grade, day_of_week, 2), vartype='BINARY')

# チューニング済みのハイパーパラメータ
lam1 = 3
lam2 = 3
lam3 = 5
lam4 = 4
lam5 = 2
lam6 = 4
lam7 = 3
lam8 = 4
lam9 = 2
lam10_ = 2
lamA = 3
lamB = 5
lam = 3

# H1(制約条件1)を定式化
H1 = 0
for i in range(n):
  if i != 12:
    for d in range(day_of_week):
      for t in range(time_per_day):
        H1 += x[12][d][t] * x[i][d][t]


# H2(制約条件2)を定式化
H2 = 0
for (i2, j2) in edge2:
  sum = 0
  for d in range(day_of_week):
    for t in range(time_per_day - 1):
      if (t+1) % 2 == 1:
        sum += x[i2][d][t] * x[j2][d][t+1]
  H2 += 1 - sum


# H3(制約条件3)を定式化
H3 = 0
for p in range(num_person):
  for (i3, j3) in edge_P[p]:
    if (i3, j3) not in edge2:
      for d in range(day_of_week):
        for t in range(time_per_day-1):
          H3 += x[i3][d][t] * x[j3][d][t+1] + x[j3][d][t] * x[i3][d][t+1]


# H4(制約条件4)を定式化
H4 = 0
for (i4, j4) in edge4:
  for d in range(day_of_week):
    for t in range(time_per_day):
      H4 += x[i4][d][t] * x[j4][d][t]


# H5(制約条件5)を定式化
H5 = 0
for (i5, j5) in edge5:
  for d in range(day_of_week):
    for t in range(time_per_day):
      for t_ in range(time_per_day):
        H5 += x[i5][d][t] * x[j5][d][t_]


# H6(制約条件6)を定式化
H6 = 0
for (i6, j6) in edge6:
  sum = 0
  for d in range(2):
    for t in range(time_per_day):
      sum += x[i6][d][t] * x[j6][d+3][t]

  sum_wednesday = 0
  for t in range(time_per_day):
    sum_wednesday += x[i6][2][t] + x[j6][2][t]

  H6 += (1 - sum) + sum_wednesday


# H7(制約条件7)を定式化
H7 = 0
for i in sub_P[0]:
  for d in range(day_of_week):
    H7 += x[i][d][0]


# H8(制約条件8)を定式化
H8 = 0
for i in sub_P[7]:
  for d in range(day_of_week):
    H8 += x[i][d][3]


# H9(制約条件9)を定式化
H9 = 0
for i in range(n):
  for t in range(2,time_per_day):
    H9 += x[i][2][t]

# H10'(制約条件10')を定式化
H10_ = 0
for g in range(num_grade):
  for d in range(day_of_week):
    sum = 0
    for i in sub_G[g]:
      for t in range(time_per_day):
        sum += x[i][d][t]
    for k in range(2):
      sum += 2 ** k * z[g][d][k]
    H10_ += (sum - 3) ** 2

# HA(制約A)を定式化
HA = 0
for p in range(num_person):
  for (iA, jA) in edge_P[p]:
    for d in range(day_of_week):
      for t in range(time_per_day):
        HA += x[iA][d][t] * x[jA][d][t]


# HB(制約B)を定式化
HB = 0
for g in range(num_grade):
  for (iB, jB) in edge_G[g]:
    for d in range(day_of_week):
      for t in range(time_per_day):
        HB += x[iB][d][t] * x[jB][d][t]

# H_onehot(One-hot制約)を定式化
H_onehot = 0
for i in range(n):
  sum = 0
  for d in range(day_of_week):
    for t in range(time_per_day):
        sum += x[i][d][t]
  H_onehot += (1 - sum) ** 2

# ハミルトニアン全体を定義
H = lam1 * H1 + lam2 * H2 + lam3 * H3 + lam4 * H4 + lam5 * H5 + lam6 * H6 + lam7 * H7 + lam8 * H8 + lam9 * H9 + lam10_ * H10_ + lamA * HA + lamB * HB + lam * H_onehot

model = H.compile()
qubo, offset = model.to_qubo()

sampler = oj.SQASampler()
response = sampler.sample_qubo(Q=qubo, num_reads = 10)

# エネルギーが一番低い状態を取りだす
dict_solution = response.first.sample

# 得られた結果をデコード
decoded_sample = model.decode_sample(dict_solution, vartype="BINARY")

# さらに解を見やすくする処理を追加
# .array(変数名, 要素番号)で希望する要素の値を抽出することができる
x_solution = {}
for i in range(n):
    sum = 0
    for d in range(day_of_week):
        for t in range(time_per_day):
            x = decoded_sample.array('x', (i, d, t))
            sum += x
            if x == 1:
                x_solution[node_label[i]] = time_per_day * d + t + 1
    if sum != 1:
      print(f'sum = {sum}より、{node_label[i]}はone-hot制約を満たしていない。')

# ハミルトニアン・エネルギーの値
energy = response.first.energy + offset
print("エネルギー：", energy)
print("制約違反：", decoded_sample.constraints(only_broken = True))


dic = sorted(x_solution.items(), key=lambda x:x[1])
list_subject = []
for d in range(day_of_week):
  list_day = []
  for t in range(time_per_day):
    list_time = []
    for subject in dic:
      if subject[1] == time_per_day * d + t + 1:
        list_time.append(subject[0])
      else:
        continue
    list_day.append(list_time)
  list_subject.append(list_day)

df = pd.DataFrame(
    data = list_subject,
    index=day,
    columns=time
    ).T

df
#%%
