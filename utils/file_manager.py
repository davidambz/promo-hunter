import pandas as pd
from os.path import exists


def load_sent_products(csv_path: str) -> tuple[set, pd.DataFrame]:
    if exists(csv_path):
        df = pd.read_csv(csv_path)
        sent = set(df['Nome']) if 'Nome' in df.columns else set()
    else:
        df = pd.DataFrame(columns=['Nome', 'Preço', 'Preço Antigo', 'Desconto', 'Link do Produto', 'Data'])
        sent = set()
    return sent, df


def save_product(csv_path: str, df: pd.DataFrame, new_entry: dict):
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(csv_path, index=False)
    return df
