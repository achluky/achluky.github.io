"""
Demo Pertemuan 11 — Itemset Mining dengan mlxtend (Apriori & FP-Growth).
Dataset: 9 transaksi contoh Han, Kamber & Pei (2012), Tabel 6.1.

    pip install mlxtend pandas
    python p11_itemset_mining_demo.py
"""
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder

transaksi = [
    ["I1", "I2", "I5"], ["I2", "I4"], ["I2", "I3"], ["I1", "I2", "I4"], ["I1", "I3"],
    ["I2", "I3"], ["I1", "I3"], ["I1", "I2", "I3", "I5"], ["I1", "I2", "I3"],
]

# 1. One-hot encoding: baris = transaksi, kolom = item (True/False)
te = TransactionEncoder()
df = pd.DataFrame(te.fit(transaksi).transform(transaksi), columns=te.columns_)
print(df.astype(int), "\n")

# 2. Frequent itemset (min_support = 2/9 ≈ 0.222)
min_sup = 2 / 9
fi_apriori = apriori(df, min_support=min_sup, use_colnames=True)
fi_fpgrowth = fpgrowth(df, min_support=min_sup, use_colnames=True)
fi_apriori["count"] = (fi_apriori["support"] * len(df)).round().astype(int)
print(fi_apriori.sort_values(["count", "itemsets"], ascending=[False, True]).to_string(index=False), "\n")
print("Apriori dan FP-Growth menghasilkan himpunan yang sama:",
      set(fi_apriori["itemsets"]) == set(fi_fpgrowth["itemsets"]), "\n")

# 3. Aturan asosiasi (min_confidence = 70%)
rules = association_rules(fi_apriori, num_itemsets=len(df), metric="confidence", min_threshold=0.7)
cols = ["antecedents", "consequents", "support", "confidence", "lift", "leverage", "conviction"]
print(rules[cols].sort_values("lift", ascending=False).round(3).to_string(index=False))
