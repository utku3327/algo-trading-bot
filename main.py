import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. VERİ ÇEKME VE TEMİZLEME ---
def get_data(ticker):
    print(f"{ticker} verisi indiriliyor...")
    # Yeni yfinance formatını düzeltmek için auto_adjust=True kullanıyoruz
    data = yf.download(ticker, start="2023-01-01", end="2024-01-01", auto_adjust=False)
    
    # Eğer kolonlar "MultiIndex" (kutu içinde kutu) gelirse düzelt
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    return data

# --- 2. GÜVENLİ SAYI ÇEVİRİCİ ---
def safe_float(x):
    # Gelen veri bir Seri/Tablo ise içindeki tek sayıyı al
    if hasattr(x, "iloc"):
        return float(x.iloc[0])
    return float(x)

# --- 3. BACKTEST MOTORU ---
def backtest(df):
    balance = 1000
    position = 0
    df = df.dropna() # Boş verileri at

    print("\n--- İŞLEM GEÇMİŞİ ---")
    
    # Döngüyü kuruyoruz
    for i in range(1, len(df)):
        # Verileri güvenli şekilde sayıya çevir
        prev_sma20 = safe_float(df['SMA20'].iloc[i-1])
        prev_sma50 = safe_float(df['SMA50'].iloc[i-1])
        curr_sma20 = safe_float(df['SMA20'].iloc[i])
        curr_sma50 = safe_float(df['SMA50'].iloc[i])
        current_price = safe_float(df['Close'].iloc[i])
        
        date = df.index[i].date()

        # AL SİNYALİ (Golden Cross)
        if prev_sma20 < prev_sma50 and curr_sma20 > curr_sma50 and position == 0:
            position = balance / current_price
            balance = 0
            print(f"🟢 ALIM: {date} | Fiyat: ${current_price:.2f} (Ortalamalar: {curr_sma20:.1f} vs {curr_sma50:.1f})")

        # SAT SİNYALİ (Death Cross)
        elif prev_sma20 > prev_sma50 and curr_sma20 < curr_sma50 and position > 0:
            balance = position * current_price
            position = 0
            print(f"🔴 SATIŞ: {date} | Fiyat: ${current_price:.2f} | Bakiye: ${balance:.2f}")

    # Son gün elimizde hisse varsa satıp nakite geçelim
    if position > 0:
        last_price = safe_float(df['Close'].iloc[-1])
        balance = position * last_price
        
    return balance

if __name__ == "__main__":
    symbol = "BTC-USD"
    df = get_data(symbol)

    # İndikatörleri Hesapla
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()

    # Motoru Çalıştır
    try:
        final_money = backtest(df)
        print("\n---------------------------------")
        print(f"Başlangıç: $1000.00")
        print(f"Bitiş:     ${final_money:.2f}")
        print(f"Kâr/Zarar: %{((final_money - 1000) / 10):.2f}")
        print("---------------------------------")
    except Exception as e:
        print(f"Hata detayı: {e}")

    # Grafiği Çiz
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Fiyat (Mavi)', alpha=0.5)
    plt.plot(df['SMA20'], label='SMA 20 (Turuncu)', linestyle='--')
    plt.plot(df['SMA50'], label='SMA 50 (Yeşil)', linestyle='--')
    plt.title(f'{symbol} - Golden Cross Analizi')
    plt.legend()
    plt.grid(True)
    plt.show()