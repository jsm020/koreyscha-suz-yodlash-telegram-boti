import matplotlib.pyplot as plt
import io

def plot_progress_bar(words, correct, attempts):
    # Romanizatsiya qilish (fallback uchun)
    def romanize(w):
        return w.get('romanized') or w.get('korean')

    # Faqat birinchi 20 ta so‘zni olaylik (agar ko‘p bo‘lsa)
    N = 20
    labels = [romanize(w) for w in words[:N]]
    values = [a if ok else 0 for a, ok in zip(attempts, correct)][:N]
    colors = ['green' if ok else 'red' for ok in correct][:N]

    fig, ax = plt.subplots(figsize=(max(6, len(labels) // 2), 3))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel('Urinishlar soni')
    ax.set_title('So‘zlar bo‘yicha mashq statistikasi')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf
