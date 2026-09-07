import pandas as pd


# ============================================================
# SOLAR INTELLIGENCE CORE
# Dataset Inspection
# ============================================================

# 1. Load the dataset
df = pd.read_csv("intelligence_core/data/synthetic.csv")


# ============================================================
# 2. FIRST 5 ROWS
# ============================================================

print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print("=" * 60)

print(df.head())


# ============================================================
# 3. DATASET SHAPE
# ============================================================

print("\n" + "=" * 60)
print("DATASET SHAPE")
print("=" * 60)

rows, columns = df.shape

print(f"Rows    : {rows}")
print(f"Columns : {columns}")


# ============================================================
# 4. COLUMN NAMES
# ============================================================

print("\n" + "=" * 60)
print("COLUMN NAMES")
print("=" * 60)

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")


# ============================================================
# 5. DATA TYPES
# ============================================================

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)

print(df.dtypes)


# ============================================================
# 6. BASIC STATISTICS
# ============================================================

print("\n" + "=" * 60)
print("BASIC STATISTICS")
print("=" * 60)

print(df.describe())


# ============================================================
# 7. MISSING VALUES
# ============================================================

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

missing_values = df.isnull().sum()

print(missing_values)


# ============================================================
# 8. DUPLICATE ROWS
# ============================================================

print("\n" + "=" * 60)
print("DUPLICATE ROWS")
print("=" * 60)

duplicates = df.duplicated().sum()

print(f"Duplicate rows: {duplicates}")


# ============================================================
# 9. UNIQUE VALUES
# ============================================================

print("\n" + "=" * 60)
print("UNIQUE VALUES")
print("=" * 60)

for column in df.columns:
    print(f"{column}: {df[column].nunique()} unique values")


# ============================================================
# 10. DATASET MEMORY USAGE
# ============================================================

print("\n" + "=" * 60)
print("DATASET MEMORY USAGE")
print("=" * 60)

memory_usage = df.memory_usage(deep=True).sum()

print(f"Memory used: {memory_usage / 1024:.2f} KB")


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DATASET INSPECTION COMPLETE")
print("=" * 60)

print(f"Total rows       : {rows}")
print(f"Total columns    : {columns}")
print(f"Duplicate rows   : {duplicates}")
print(f"Missing values   : {missing_values.sum()}")

print("\nDataset is ready for detailed analysis.")