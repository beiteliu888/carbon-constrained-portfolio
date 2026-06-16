# Portfolio Optimization 简明学习笔记

> 项目：Carbon-Constrained Portfolio Optimization Prototype  
> 主题：mean-variance optimization、objective function、constraints、carbon constraint  
> 定位：learning-oriented prototype，不是成熟交易策略，也不是 alpha research。

---

## 1. Portfolio Optimization 要解决什么问题？

Portfolio optimization 的核心问题是：

$$
\text{在给定股票池、收益估计、风险估计和约束条件下，每只股票应该配置多少权重？}
$$

Equal-weight portfolio 的做法是每只股票一样多：

$$
w_i = \frac{1}{N}
$$

其中：

- $w_i$：第 $i$ 只股票的权重；
- $N$：股票数量。

这种方法简单、透明，但它不考虑：

- 哪些股票 expected return 更高；
- 哪些股票 volatility 更大；
- 哪些股票经常一起涨跌；
- 哪些股票 carbon intensity 更高；
- 组合是否满足 carbon budget。

所以本项目需要 optimization 来研究：

$$
\text{收益、风险和碳约束之间如何权衡？}
$$

---

## 2. 最基础概念

### 2.1 Portfolio Weights

Portfolio weights 是每只资产在组合中的比例。

Fully invested portfolio 满足：

$$
\sum_{i=1}^{N} w_i = 1
$$

这表示 100% 资金都被投资。

---

### 2.2 Expected Return

Expected return 是对未来收益的估计，通常记作：

$$
\mu_i
$$

在本项目中，$\mu_i$ 来自历史窗口内的平均收益率。

重要限制：

$$
\text{历史平均收益不等于可靠的未来收益预测。}
$$

---

### 2.3 Volatility 和 Variance

Volatility 衡量收益率波动程度，通常记作：

$$
\sigma_i
$$

Variance 是 volatility 的平方：

$$
\operatorname{Var}(r_i) = \sigma_i^2
$$

Mean-variance optimization 中的 “variance” 指的是组合收益率的方差，也就是组合风险。

---

### 2.4 Covariance

Covariance 衡量两只资产是否经常一起涨跌：

$$
\operatorname{Cov}(r_i,r_j)
$$

直觉：

- covariance > 0：两只资产倾向于一起涨跌；
- covariance < 0：一只涨时另一只更可能跌；
- covariance 接近 0：两只资产共同波动关系较弱。

---

### 2.5 Covariance Matrix

Covariance matrix 记作：

$$
\Sigma
$$

它是一个矩阵，里面包含：

- 每只资产自己的 variance；
- 每两只资产之间的 covariance。

三只资产时可以理解为：

$$
\Sigma =
\begin{bmatrix}
\operatorname{Var}(A) & \operatorname{Cov}(A,B) & \operatorname{Cov}(A,C) \\
\operatorname{Cov}(B,A) & \operatorname{Var}(B) & \operatorname{Cov}(B,C) \\
\operatorname{Cov}(C,A) & \operatorname{Cov}(C,B) & \operatorname{Var}(C)
\end{bmatrix}
$$

---

## 3. 关于 $\Sigma$、$w$、$\Sigma w$ 和 $w^{\mathsf{T}}\Sigma w$

这是一个很重要的符号区别。

### 3.1 $w$ 是什么？

$w$ 是 portfolio weights，也就是权重向量。

如果有两只股票 A 和 B：

$$
w =
\begin{bmatrix}
w_A \\
w_B
\end{bmatrix}
$$

例如 $w_A = 60\%$，$w_B = 40\%$。

---

### 3.2 $\Sigma$ 是什么？

$\Sigma$ 才是 covariance matrix。

两只股票时：

$$
\Sigma =
\begin{bmatrix}
\operatorname{Var}(A) & \operatorname{Cov}(A,B) \\
\operatorname{Cov}(B,A) & \operatorname{Var}(B)
\end{bmatrix}
$$

注意：

$$
\Sigma \neq \Sigma w
$$

$\Sigma$ 是矩阵，$\Sigma w$ 是矩阵乘以向量后的结果。

---

### 3.3 $\Sigma w$ 是什么？

$\Sigma w$ 是：

$$
\text{covariance matrix} \times \text{weight vector}
$$

结果是一个向量，不是 covariance matrix。

你可以把它理解成一个中间计算步骤。

---

### 3.4 $w^{\mathsf{T}}\Sigma w$ 是什么？

这个表达式最后得到一个数字：

$$
w^{\mathsf{T}}\Sigma w = \text{portfolio variance}
$$

计算逻辑是：

$$
\Sigma w \rightarrow \text{先得到一个向量}
$$

$$
w^{\mathsf{T}}(\Sigma w) \rightarrow \text{再得到一个数字}
$$

所以最简单的记法是：

```text
w        = portfolio weights
Σ        = covariance matrix
Σw       = 中间向量
wᵀΣw     = portfolio variance
```

---

## 4. 为什么 Portfolio Risk 不是风险的简单平均？

Portfolio expected return 是权重加权平均：

$$
E[R_p] = w^{\mathsf{T}}\mu
$$

但 portfolio variance 不是每只股票 variance 的简单平均。

原因是组合风险还取决于资产之间是否一起波动。

两只股票时：

$$
\operatorname{Var}(R_p) = w_A^2\operatorname{Var}(R_A) + w_B^2\operatorname{Var}(R_B) + 2w_Aw_B\operatorname{Cov}(R_A,R_B)
$$

其中：

- 前两项是股票 A 和 B 各自的风险；
- 最后一项是 cross term；
- cross term 代表 A 和 B 的共同波动。

如果两只股票高度正相关，cross term 会增加组合风险。  
如果两只股票相关性较低，组合风险可能下降。  
这就是 diversification 的数学来源。

---

## 5. Mean-Variance Optimization 是什么？

Mean 指 expected return：

$$
w^{\mathsf{T}}\mu
$$

Variance 指 portfolio variance：

$$
w^{\mathsf{T}}\Sigma w
$$

Mean-variance optimization 想做的事情是：

$$
\text{在 expected return 和 portfolio risk 之间做权衡。}
$$

不能只追求 expected return 最大，因为那可能导致组合过度集中在少数历史收益高的股票上。

也不能只追求 variance 最小，因为那可能牺牲过多收益。

Efficient frontier 指的是：

$$
\text{在每个风险水平下，可以达到的最高 expected return。}
$$

本项目没有完整画 efficient frontier，而是给定一个 risk aversion 参数，求一个具体组合。

---

## 6. Objective Function

本项目的目标函数可以理解为：

$$
\min \left(\text{risk penalty} - \text{expected return}\right)
$$

更具体地：

$$
\min_{w}\left(\frac{1}{2}\lambda w^{\mathsf{T}}\Sigma w - w^{\mathsf{T}}\mu\right)
$$

其中：

- $w$：portfolio weights；
- $\lambda$：risk aversion 参数；
- $\Sigma$：covariance matrix；
- $\mu$：expected return vector；
- $w^{\mathsf{T}}\Sigma w$：portfolio variance；
- $w^{\mathsf{T}}\mu$：portfolio expected return。

---

### 6.1 为什么是 “risk penalty - expected return”？

因为优化器需要一个评分标准。

如果组合风险更高，我们希望分数更高：

$$
\text{risk penalty 越大，组合越不吸引人。}
$$

如果组合 expected return 更高，我们希望分数更低：

$$
\left(-w^{\mathsf{T}}\mu\right) \text{ 会变得更小。}
$$

所以最小化：

$$
\text{risk penalty} - \text{expected return}
$$

等价于寻找：

$$
\text{风险惩罚较低，同时预期收益较高的组合。}
$$

---

### 6.2 Risk Penalty 是什么？

Risk penalty 是：

$$
\frac{1}{2}\lambda w^{\mathsf{T}}\Sigma w
$$

其中：

- $w^{\mathsf{T}}\Sigma w$ 是组合 variance；
- $\lambda$ 决定你有多讨厌风险；
- $\frac{1}{2}$ 主要是数学上方便求导，不改变经济直觉。

可以简单理解为：

$$
\text{组合风险越高，惩罚越大。}
$$

---

## 7. Risk Aversion

Risk aversion 通常记作：

$$
\lambda
$$

它决定风险惩罚的强度。

如果 $\lambda$ 较大：

- 优化器更讨厌波动；
- 组合可能更分散；
- 组合可能更偏向低风险资产。

如果 $\lambda$ 较小：

- 优化器更愿意追求 expected return；
- 组合可能更集中；
- 结果更依赖 expected return 估计。

本项目中：

$$
\lambda = 5
$$

这只是教学默认值，不是客观真理，也不是严格校准出的真实投资者偏好。

---

## 8. Constraints

Constraints 定义哪些组合是允许的。

它们不是附加说明，而是优化问题的一部分。

### 8.1 Weights Sum to 1

$$
\sum_{i=1}^{N} w_i = 1
$$

含义：

$$
\text{所有资金都被投资。}
$$

本项目不考虑现金或杠杆。

---

### 8.2 Long-Only Constraint

$$
w_i \geq 0
$$

含义：

$$
\text{只能买入，不能做空。}
$$

---

### 8.3 Maximum Single-Name Weight

$$
w_i \leq 25\%
$$

含义：

$$
\text{单只股票最多占组合 25%。}
$$

这是集中度控制。

---

### 8.4 Carbon Budget Constraint

$$
w^{\mathsf{T}}c \leq 0.70 \times \text{Carbon Exposure}_{\text{equal-weight}}
$$

其中：

- $c$：每只股票的 carbon intensity vector；
- $w^{\mathsf{T}}c$：portfolio carbon exposure。

这个约束会限制高碳股票在组合中的权重，但不一定把它们完全剔除。

---

## 9. Carbon Constraint 的直觉

Portfolio carbon exposure 是：

$$
\text{Portfolio Carbon Exposure} = \sum_{i=1}^{N} w_i c_i
$$

也就是每只股票 carbon intensity 的加权平均。

如果某只股票 carbon intensity 很高，那么它的权重越高，组合 carbon exposure 越高。

因此 carbon constraint 可能导致：

- 高碳股票权重下降；
- 其他股票权重上升；
- 组合 expected return 改变；
- 组合 risk profile 改变；
- turnover 改变。

但是：

- 高碳股票不一定被完全剔除；
- 低碳股票不一定获得最高权重；
- carbon constraint 不是 alpha signal；
- 降低 portfolio carbon exposure 不等于真实世界减排。

---

## 10. Unconstrained MV 和 Carbon-Constrained MV 的区别

Unconstrained MV 主要关心：

$$
\text{expected return 和 portfolio variance}
$$

Carbon-constrained MV 还必须满足：

$$
w^{\mathsf{T}}c \leq \text{carbon budget}
$$

如果无约束组合本来已经满足碳预算，carbon constraint 可能不会改变权重。

如果无约束组合依赖高碳股票，carbon constraint 会迫使优化器重新分配权重。

---

## 11. 为什么 Equal-Weight 是 Benchmark？

Equal-weight portfolio：

$$
w_i = \frac{1}{N}
$$

它不需要：

- expected return；
- covariance matrix；
- optimizer；
- risk aversion。

它是一个简单、透明的 baseline。

但 equal-weight 也有局限：

- 不考虑风险差异；
- 不考虑股票之间相关性；
- 不考虑 carbon intensity；
- 不考虑公司规模；
- 不控制 sector exposure。

所以不能只看 optimized portfolio 有没有跑赢 equal-weight 就下结论。

---

## 12. Backtest 中为什么要滚动估计？

不能用全样本收益率一次性估计参数，因为那会使用未来数据。

Look-ahead bias 指：

$$
\text{在历史回测中使用当时尚不可获得的信息。}
$$

所以每次 rebalance 只能使用过去数据估计：

- expected return；
- covariance matrix；
- 当时已经公开的 carbon intensity。

Rolling window 是简化但合理的做法，因为市场风险和资产相关性会随时间变化。

---

## 13. 最容易被质疑的地方

这个优化问题最容易被质疑的地方包括：

- expected return 很难估计；
- covariance matrix 可能不稳定；
- 股票池很小；
- constraints 可能产生边界解；
- 结果对参数敏感；
- carbon intensity 数据口径可能不一致；
- 没有完整交易成本和滑点；
- backtest 不能证明未来表现；
- 这不是 alpha research；
- carbon constraint 不代表真实减排。

---

## 14. 最后用一个数字例子串起来

假设只有股票 A 和 B。

权重是：

$$
w =
\begin{bmatrix}
0.6 \\
0.4
\end{bmatrix}
$$

Expected return vector 是：

$$
\mu =
\begin{bmatrix}
8\% \\
4\%
\end{bmatrix}
$$

那么组合 expected return 是：

$$
w^{\mathsf{T}}\mu = 0.6 \times 8\% + 0.4 \times 4\% = 6.4\%
$$

假设 covariance matrix 是：

$$
\Sigma =
\begin{bmatrix}
0.04 & 0.006 \\
0.006 & 0.01
\end{bmatrix}
$$

先计算中间向量：

$$
\Sigma w =
\begin{bmatrix}
0.04 \times 0.6 + 0.006 \times 0.4 \\
0.006 \times 0.6 + 0.01 \times 0.4
\end{bmatrix}
=
\begin{bmatrix}
0.0264 \\
0.0076
\end{bmatrix}
$$

再计算 portfolio variance：

$$
w^{\mathsf{T}}\Sigma w =
\begin{bmatrix}
0.6 & 0.4
\end{bmatrix}
\begin{bmatrix}
0.0264 \\
0.0076
\end{bmatrix}
= 0.01888
$$

Portfolio volatility 是：

$$
\sqrt{0.01888} \approx 13.74\%
$$

如果 risk aversion 是：

$$
\lambda = 5
$$

那么 objective function 的核心评分是：

$$
\frac{1}{2}\lambda w^{\mathsf{T}}\Sigma w - w^{\mathsf{T}}\mu
$$

这个分数同时考虑：

- 组合收益 $w^{\mathsf{T}}\mu$；
- 组合风险 $w^{\mathsf{T}}\Sigma w$；
- 投资者对风险的厌恶程度 $\lambda$；
- 以及外部约束，例如 long-only、weight cap 和 carbon budget。

---

## 15. 一句话总结

Mean-variance optimization 是在给定约束下，用 covariance matrix 衡量组合风险，用 expected return 衡量组合收益，并通过 objective function 在二者之间做权衡。
