import requests
from bs4 import BeautifulSoup
import webbrowser
import threading
from tkinter import *
from tkinter import ttk
from datetime import datetime


def fetch_news():
    """Fetches the latest 30 news from Hacker News."""
    url = 'https://news.ycombinator.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    news_list = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title_rows = soup.find_all('span', class_='titleline')

        for row in title_rows[:30]:
            link_tag = row.find('a')

            if link_tag:
                title = link_tag.text
                link = link_tag['href']

                if link.startswith('item?id='):
                    link = 'https://news.ycombinator.com/' + link

                news_list.append({"title": title, "link": link})

        return news_list

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


def open_link(event, tree):
    """Opens the clicked news link in browser."""
    selected_items = tree.selection()
    if not selected_items:
        return

    selected_item = tree.item(selected_items[0])
    values = selected_item.get('values', [])

    if len(values) >= 3:
        link = values[2]
        if link and isinstance(link, str) and link.startswith('http'):
            webbrowser.open_new_tab(link)


def create_ui():
    window = Tk()
    window.title("Hacker News Reader")
    window.geometry("1000x650")
    window.configure(bg='#ffffff')

    # Style settings
    style = ttk.Style()
    style.theme_use('clam')

    style.configure("Treeview",
                    background="#ffffff",
                    foreground="#2c3e50",
                    rowheight=40,
                    fieldbackground="#ffffff",
                    font=('Segoe UI', 10))

    style.configure("Treeview.Heading",
                    background="#34495e",
                    foreground="#ffffff",
                    font=('Segoe UI', 11, 'bold'))

    style.map('Treeview',
              background=[('selected', '#3498db')],
              foreground=[('selected', '#ffffff')])

    # Header
    header_frame = Frame(window, bg='#34495e', height=70)
    header_frame.pack(fill=X, side=TOP)
    header_frame.pack_propagate(False)

    title_label = Label(header_frame,
                        text="📰 Hacker News Reader",
                        font=("Segoe UI", 18, "bold"),
                        bg='#34495e',
                        fg='#ffffff')
    title_label.pack(side=LEFT, padx=20, pady=15)

    subtitle_label = Label(header_frame,
                           text="Latest 30 News",
                           font=("Segoe UI", 10),
                           bg='#34495e',
                           fg='#ecf0f1')
    subtitle_label.pack(side=LEFT, padx=5, pady=15)

    # Status bar
    status_frame = Frame(window, bg='#ecf0f1', height=45)
    status_frame.pack(fill=X, side=TOP)
    status_frame.pack_propagate(False)

    def refresh_news():
        refresh_btn.config(state='disabled', text='Loading...')
        status_label.config(text='⏳ Updating news...')

        for item in tree.get_children():
            tree.delete(item)

        def load():
            news = fetch_news()

            def update():
                if news:
                    for i, item in enumerate(news):
                        tree.insert('', END, values=(i + 1, item['title'], item['link']))
                    time = datetime.now().strftime("%H:%M:%S")
                    status_label.config(text=f'✓ {len(news)} news loaded - Last update: {time}')
                else:
                    tree.insert('', END, values=('', "❌ Failed to load news. Please check your connection.", ""))
                    status_label.config(text='❌ Loading failed')

                refresh_btn.config(state='normal', text='🔄 Refresh')

            window.after(0, update)

        threading.Thread(target=load, daemon=True).start()

    refresh_btn = Button(status_frame,
                         text='🔄 Refresh',
                         command=refresh_news,
                         bg='#3498db',
                         fg='#ffffff',
                         font=('Segoe UI', 9, 'bold'),
                         relief='flat',
                         padx=20,
                         pady=8,
                         cursor='hand2',
                         activebackground='#2980b9',
                         activeforeground='#ffffff',
                         borderwidth=0)
    refresh_btn.pack(side=LEFT, padx=15, pady=7)

    status_label = Label(status_frame,
                         text='⏳ Loading news...',
                         font=('Segoe UI', 9),
                         bg='#ecf0f1',
                         fg='#7f8c8d',
                         anchor='w')
    status_label.pack(side=LEFT, padx=10, pady=5, fill=X, expand=True)

    # Main content
    content_frame = Frame(window, bg='#ffffff')
    content_frame.pack(pady=15, padx=15, fill=BOTH, expand=True)

    frame = Frame(content_frame, bg='#bdc3c7', relief='solid', bd=1)
    frame.pack(fill=BOTH, expand=True)

    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill='y')

    tree = ttk.Treeview(frame,
                        columns=("No", "Title", "Link"),
                        show='headings',
                        displaycolumns=("No", "Title"),
                        yscrollcommand=scrollbar.set,
                        style="Treeview")
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar.config(command=tree.yview)

    tree.heading("No", text="#")
    tree.heading("Title", text="📰 News Title")

    tree.column("No", width=50, anchor='center', minwidth=50)
    tree.column("Title", width=900, anchor='w', minwidth=200)

    # Footer
    footer_frame = Frame(window, bg='#ecf0f1', height=35)
    footer_frame.pack(fill=X, side=TOP)
    footer_frame.pack_propagate(False)

    info_label = Label(footer_frame,
                       text='💡 Tip: Click to open the news',
                       font=('Segoe UI', 9),
                       bg='#ecf0f1',
                       fg='#7f8c8d')
    info_label.pack(pady=8)

    # Initial loading
    def initial_load():
        news = fetch_news()

        def update():
            if news:
                for i, item in enumerate(news):
                    tree.insert('', END, values=(i + 1, item['title'], item['link']))
                time = datetime.now().strftime("%H:%M:%S")
                status_label.config(text=f'✓ {len(news)} news loaded - Last update: {time}')
            else:
                tree.insert('', END, values=('', "❌ Failed to load news. Please check your connection.", ""))
                status_label.config(text='❌ Loading failed')

        window.after(0, update)

    threading.Thread(target=initial_load, daemon=True).start()

    # Event handler - Single click
    def handle_click(event):
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                open_link(event, tree)

    tree.bind("<Button-1>", handle_click)

    def on_motion(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            tree.configure(cursor="hand2")
        else:
            tree.configure(cursor="")

    tree.bind("<Motion>", on_motion)

    # Zebra effect
    tree.tag_configure('oddrow', background='#ffffff')
    tree.tag_configure('evenrow', background='#f8f9fa')

    def update_row_colors():
        for i, item in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(item, tags=('evenrow',))
            else:
                tree.item(item, tags=('oddrow',))

    original_insert = tree.insert

    def custom_insert(*args, **kwargs):
        result = original_insert(*args, **kwargs)
        update_row_colors()
        return result

    tree.insert = custom_insert

    window.mainloop()


if __name__ == "__main__":
    create_ui()
