import matplotlib.pyplot as plt
import io

def plot_progress_bar(words, correct, attempts):
    # Romanizatsiya label uchun
    def romanize(w):
        try:
            return w['romanized']
        except:
            from .utils import romanize_korean
            return romanize_korean(w['korean'])
    labels = [romanize(w) for w in words]
    values = [a if ok else 0 for a, ok in zip(attempts, correct)]
    colors = ['green' if ok else 'red' for ok in correct]
    fig, ax = plt.subplots(figsize=(max(6, len(labels)//2), 3))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel('Urinishlar')
    ax.set_title('Sozlar boyicha urinishlar')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf
