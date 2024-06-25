import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import asyncio
import os
from bs4 import BeautifulSoup
from pyppeteer import launch
import time


class FilmFreewayScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("FilmFreeway SCRAPER")
        self.resizable(False, False)

        self.queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Set up the main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(padx=10, pady=10)

        # Create the header label
        self.header_label = tk.Label(self.main_frame, text="FilmFreeway SCRAPER", font=("Helveltica", 20))
        self.header_label.grid(row=0, column=0, columnspan=3)

        # Create the author label
        self.author_label = tk.Label(self.main_frame, text="By Jonathan Caputo (v1.0)", font=("Helveltica", 10), pady=20)
        self.author_label.grid(row=1, column=0, columnspan=3)

        # Create the link entry field and insert button
        self.link_entry = tk.Entry(self.main_frame, width=80)
        self.link_entry.insert(0, "https://filmfreeway.com/")
        self.link_entry.grid(row=2, column=0, padx=(0, 10), pady=(0,10), sticky='ew')

        self.insert_button = tk.Button(self.main_frame, text="Inserisci Link", command=self.insert_link)
        self.insert_button.grid(row=2, column=1, padx=(10, 0), pady=(0,10), sticky='ew')

        self.link_entry.bind('<Return>', lambda event: self.insert_link())

        # Create the table
        self.create_table()

        # Create progress bar and status label
        self.progress_label = tk.Label(self.main_frame, text="Stato corrente: Inattivo")
        self.progress_label.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(self.main_frame, length=800, mode='determinate')
        self.progress_bar.grid(row=8, column=0, columnspan=3, pady=(5, 10))

        # Create buttons
        self.start_button = tk.Button(self.main_frame, text="Avvia Analisi", height=2, command=self.start_analysis, state='disabled')
        self.start_button.grid(row=9, column=0, sticky='ew', pady=(5, 10), padx=(50, 5))

        self.export_button = tk.Button(self.main_frame, text="Esporta in CSV", height=2, command=self.export_csv, state='disabled')
        self.export_button.grid(row=9, column=1, sticky='ew', pady=(5, 10), padx=(5, 50))

        self.main_frame.grid_columnconfigure(0, weight=9)
        self.main_frame.grid_columnconfigure(1, weight=1) 

    def insert_link(self):
        # Get the link from the entry field
        link = self.link_entry.get()
        # Check if the link is valid
        if not link.startswith('https://filmfreeway.com/') or link == 'https://filmfreeway.com/' or link == 'https://filmfreeway.com':
            messagebox.showerror('Link non valido', 'Il link inserito non è valido')
            return
        # Check if the link already exists in the table
        if self.tree.get_children():
            for link_id in self.tree.get_children():
                if self.tree.item(link_id)['values'][0] == link:
                    messagebox.showerror('Link duplicato', 'Il link inserito è già presente nella tabella')
                    return
        # Insert the link into the table
        self.tree.insert('', 'end', values=(link, 'Da analizzare', '', 'Rimuovi'))
        # Enable the start button
        self.start_button['state'] = 'normal'
        # Clear the entry field
        self.link_entry.delete(0, 'end')
        self.link_entry.insert(0, 'https://filmfreeway.com/')

    def remove_link(self, event):
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)

        # Check if the 'Azioni' column was clicked
        if column == '#4':
            self.tree.delete(item)
            if not self.tree.get_children():
                self.start_button['state'] = 'disabled'
        if column == '#3':
            print("TODO")

    def create_table(self):
        columns = ('link', 'stato', 'contatti', 'azioni')
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')
        self.tree.heading('link', text='Link Festival')
        self.tree.heading('stato', text='Stato')
        self.tree.heading('contatti', text='Contatti')
        self.tree.heading('azioni', text='Azioni')
        self.tree.column('link', width=600)
        self.tree.column('stato', width=100)
        self.tree.column('contatti', width=100)
        self.tree.column('azioni', width=100)

        self.tree.tag_configure('center', anchor='center')

        self.tree.bind('<Double-1>', self.remove_link)
        self.tree.grid(row=3, column=0, columnspan=3)

    def check_queue(self):
        while not self.queue.empty():
            message = self.queue.get()
            print(message)

        self.after(100, self.check_queue)     

    def start_analysis(self):
        self.start_button['state'] = 'disabled'
        self.check_queue()

        self.executor.submit(self.run_asyncio_loop)

    async def run_asyncio_loop(self):
        browser = await launch(headless=False)
        page = browser.newPage()
        self.queue.put("asdadas")

    async def test(self):
        browser = await launch(headless=False)
        page = await browser.newPage()
        self.queue.put("asdadas")
        await page.goto("https://google.com")
        await page.waitForSelector('body')
        return await page.content()

    def tttt(self):
        try:
            self.start_button['state'] = 'disabled'
            asyncio.create_task(self.scrape_and_render())
        except Exception as e:
            for item_id in self.tree.get_children():
                riga = self.tree.item(item_id)
                self.tree.item(item_id, values=(riga['values'][0], f'Impossibile analizzare', '', 'Elimina link'))

            self.progress_label.config(text=f"Impossibile analizzare i festival")
            self.start_button['state'] = 'disabled'
            messagebox.showerror("Errore", f"Si è verificato un errore durante l'analisi:\n{str(e)}")

    def updateProgressLabels(self, item_id, label, item_label):
        riga = self.tree.item(item_id)
        self.progress_label.config(text=label)
        self.tree.item(item_id, values=(riga['values'][0], item_label, '', 'Elimina link'))

    async def analyze_festivals(self):
        try:
            browser = await launch(headless=False)  # Avvia il browser Chromium in modalità headless
            
            for item_id in self.tree.get_children():
                riga = self.tree.item(item_id)

                # Get ID festival from link
                page = await browser.newPage()
                await page.goto(riga['values'][0])
                await page.waitForSelector('body')
                page_content = await page.content()
                print(page_content)
                
                # if response_festivalpage.status_code != 200:
                #     self.tree.item(item_id, values=(riga['values'][0], f'Errore ({response_festivalpage.status_code})', '', 'Elimina link'))
                #     self.progress_label.config(text=f"Errore {response_festivalpage.status_code} nell'analisi preliminare del festival {riga['values'][0]}")

                await asyncio.sleep(1)
            await browser.close()
        except Exception as e:
            for item_id in self.tree.get_children():
                riga = self.tree.item(item_id)
                self.tree.item(item_id, values=(riga['values'][0], f'Impossibile analizzare', '', 'Elimina link'))

            self.progress_label.config(text=f"Impossibile analizzare i festival")
            self.start_button['state'] = 'disabled'
            messagebox.showerror("Errore", f"Si è verificato un errore durante l'analisi:\n{str(e)}")


        # Dummy analysis function
        # for i in range(6):
        #     self.progress_bar['value'] = (i + 1) * 16.67  # update progress bar
        #     self.progress_label.config(text=f"Analizzando festival {i + 1} di 6...")
        #     self.root.update_idletasks()
        #     # Simulate analysis time
        #     self.tree.set(self.tree.get_children()[i], column='stato', value='In analisi')
        #     self.root.after(1000)  # Simulate delay
        #     self.tree.set(self.tree.get_children()[i], column='stato', value='Success')
        #     self.tree.set(self.tree.get_children()[i], column='contatti', value='10')  # Example number of contacts

        # self.progress_label.config(text="Analisi completata!")

    def export_csv(self):
        # Export the results to a CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        # Gather data
        data = []
        for row_id in self.tree.get_children():
            row = self.tree.item(row_id)['values']
            data.append(row)

        # Create a DataFrame and export to CSV
        df = pd.DataFrame(data, columns=['Link Festival', 'Contatti', 'Stato', 'Azioni'])
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Esportazione completata", f"Risultati esportati in {file_path}")

    def open_contacts_window(self, contacts):
        contacts_window = tk.Toplevel(self.root)
        contacts_window.title("Contatti trovati")
        
        columns = ('nome', 'cognome', 'email', 'ruolo', 'città', 'compleanno')
        contacts_tree = ttk.Treeview(contacts_window, columns=columns, show='headings')
        contacts_tree.heading('nome', text='Nome')
        contacts_tree.heading('cognome', text='Cognome')
        contacts_tree.heading('email', text='Email')
        contacts_tree.heading('ruolo', text='Ruolo')
        contacts_tree.heading('città', text='Città')
        contacts_tree.heading('compleanno', text='Compleanno')

        contacts_tree.pack(fill='both', expand=True)

        for contact in contacts:
            contacts_tree.insert('', 'end', values=contact)

        export_button = tk.Button(contacts_window, text="Esporta in CSV", command=lambda: self.export_contacts_csv(contacts))
        export_button.pack(pady=(5, 10))

    def export_contacts_csv(self, contacts):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        df = pd.DataFrame(contacts, columns=['Nome', 'Cognome', 'Email', 'Ruolo', 'Città', 'Compleanno'])
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Esportazione completata", f"Contatti esportati in {file_path}")
        
if __name__ == "__main__":
    os.environ['PYPPETEER_CHROMIUM_REVISION'] = "1263111"

    app = FilmFreewayScraperApp()
    app.mainloop()

 