import customtkinter as ctk
from tkinter import filedialog, ttk
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def parse_dump(path):
    resultado = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        setor = None
        bloco = 0
        for linha in f:
            linha = linha.strip()
            if linha.startswith("+Sector"):
                setor = int(linha.replace("+Sector: ", ""))
                bloco = 0
                continue
            if not linha:
                continue
            resultado[(setor, bloco)] = linha.upper()
            bloco += 1
    return resultado


# PROXMARK JSON
def parse_json_dump(path):
    resultado = {}

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)

    if "blocks" not in data:
        return resultado

    for block_str, hexdata in data["blocks"].items():

        try:
            bloco_global = int(block_str)

            setor = bloco_global // 4
            bloco = bloco_global % 4

            hexdata = hexdata.replace(" ", "").upper()

            if len(hexdata) == 32:
                resultado[(setor, bloco)] = hexdata
        except:
            pass

    return resultado


# FLIPPER ZERO NFC
def parse_flipper_nfc(path):
    resultado = {}

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:

            linha = linha.strip()

            if not linha.startswith("Block"):
                continue

            try:
                parte = linha.split(":")

                bloco_global = int(parte[0].replace("Block", "").strip())

                hexdata = parte[1].replace(" ", "").strip().upper()

                if "?" in hexdata:
                    continue

                if len(hexdata) != 32:
                    continue

                setor = bloco_global // 4
                bloco = bloco_global % 4

                resultado[(setor, bloco)] = hexdata

            except:
                pass

    return resultado


# LOADER UNIVERSAL
def load_any_dump(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".json":
        return parse_json_dump(path)

    elif ext == ".nfc":
        return parse_flipper_nfc(path)

    elif ext in [".mct", ".txt"]:
        return parse_dump(path)

    else:
        raise ValueError("Formato não suportado")


def is_value_block(data_bytes):
    if len(data_bytes) != 16:
        return False

    v1 = data_bytes[0:4]
    v2 = data_bytes[4:8]
    v3 = data_bytes[8:12]
    addr = data_bytes[12:16]

    if v1 == v3 and v2 == bytes([~b & 0xFF for b in v1]):
        if addr[0] == addr[2] and addr[1] == addr[3]:
            if addr[1] == (~addr[0] & 0xFF):
                return True
    return False


def format_block_columns(hexdata):
    dados = bytes.fromhex(hexdata)
    colunas = []

    for i in range(0, 16, 4):
        parte = dados[i : i + 4]
        invertido = parte[::-1]

        decimal = int.from_bytes(invertido, byteorder="big", signed=False)

        colunas.append(f"{invertido.hex().upper()} ({decimal})")

    return colunas


class MifareAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MIFARE Dump Analyzer - HexToDecimal")
        self.geometry("1820x920")

        self.dump1 = None
        self.dump2 = None

        # Top frame para botões
        top = ctk.CTkFrame(self)
        top.pack(fill="x", pady=5)

        ctk.CTkButton(top, text="Carregar Dump 1", command=self.load_dump1).pack(
            side="left", padx=10
        )

        ctk.CTkButton(top, text="Carregar Dump 2", command=self.load_dump2).pack(
            side="left"
        )

        # Barra de pesquisa
        self.search_var = ctk.StringVar()

        search_frame = ctk.CTkFrame(top)
        search_frame.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(search_frame, text="Pesquisar:").pack(side="left", padx=5)

        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var)

        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            search_frame,
            text="Pesquisar",
            command=lambda: self.highlight_search(self.search_var.get()),
        ).pack(side="left", padx=5)

        # Frame principal
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True)

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        self.tree1 = self.create_table(main)
        self.tree1.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)

        self.tree2 = self.create_table(main)
        self.tree2.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)

        scrollbar = ttk.Scrollbar(main, orient="vertical", command=self.on_scrollbar)

        scrollbar.grid(row=0, column=2, sticky="ns")

        self.tree1.configure(yscrollcommand=scrollbar.set)

        self.tree2.configure(yscrollcommand=scrollbar.set)

        self.bind_mouse_scroll(self.tree1)
        self.bind_mouse_scroll(self.tree2)

    def create_table(self, parent):

        columns = ("Setor", "Bloco", "HEX (16 bytes)", "D1", "D2", "D3", "D4")

        tree = ttk.Treeview(parent, columns=columns, show="headings", height=30)

        for col in columns:
            tree.heading(col, text=col)

        tree.column("Setor", width=30)
        tree.column("Bloco", width=30)
        tree.column("HEX (16 bytes)", width=250)
        tree.column("D1", width=130)
        tree.column("D2", width=130)
        tree.column("D3", width=130)
        tree.column("D4", width=130)

        tree.tag_configure("changed", background="#FF4949")

        tree.tag_configure("valueblock", background="#3DFF3D")

        tree.tag_configure("highlight", background="#FFDD00")

        return tree

    def on_scrollbar(self, *args):
        self.tree1.yview(*args)
        self.tree2.yview(*args)

    def bind_mouse_scroll(self, tree):
        tree.bind("<MouseWheel>", self._on_mousewheel)
        tree.bind("<Button-4>", self._on_mousewheel)
        tree.bind("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):

        delta = (
            -1 * (event.delta // 120)
            if hasattr(event, "delta")
            else (1 if event.num == 5 else -1)
        )

        self.tree1.yview_scroll(delta, "units")
        self.tree2.yview_scroll(delta, "units")

        return "break"

    def load_dump1(self):
        path = filedialog.askopenfilename(
            filetypes=[("Dump", "*.mct *.txt *.json *.nfc")]
        )

        if path:
            self.dump1 = load_any_dump(path)
            self.refresh()

    def load_dump2(self):
        path = filedialog.askopenfilename(
            filetypes=[("Dump", "*.mct *.txt *.json *.nfc")]
        )

        if path:
            self.dump2 = load_any_dump(path)
            self.refresh()

    def refresh(self):

        for tree in (self.tree1, self.tree2):
            for item in tree.get_children():
                tree.delete(item)

        if not self.dump1:
            return

        keys = sorted(
            set(self.dump1.keys()) | (set(self.dump2.keys()) if self.dump2 else set())
        )

        for key in keys:

            setor, bloco = key

            hex1 = self.dump1.get(key, "")
            hex2 = self.dump2.get(key, "") if self.dump2 else ""

            tag1 = ""
            tag2 = ""

            if self.dump2 and hex1 != hex2:
                tag1 = tag2 = "changed"

            if hex1 and is_value_block(bytes.fromhex(hex1)):
                tag1 = "valueblock"

            if hex2 and is_value_block(bytes.fromhex(hex2)):
                tag2 = "valueblock"

            if hex1:
                s = format_block_columns(hex1)
                self.tree1.insert(
                    "", "end", values=(setor, bloco, hex1, *s), tags=(tag1,)
                )

            if hex2:
                s = format_block_columns(hex2)
                self.tree2.insert(
                    "", "end", values=(setor, bloco, hex2, *s), tags=(tag2,)
                )

    def highlight_search(self, termo):
        termo = termo.upper()
        for tree, dump in ((self.tree1, self.dump1), (self.tree2, self.dump2)):
            if not dump or not termo:
                continue
            for item in tree.get_children():
                tree_values = tree.item(item, "values")
                new_tags = list(tree.item(item, "tags"))

                # Limpa highlight antigo
                if "highlight" in new_tags:
                    new_tags.remove("highlight")

                # Verifica colunas D1-D4
                s_columns = [3, 4, 5, 6]
                for i in s_columns:
                    if termo in str(tree_values[i]):
                        if "highlight" not in new_tags:
                            new_tags.append("highlight")
                        break  # só precisa de 1 célula para marcar

                tree.item(item, tags=new_tags)


if __name__ == "__main__":
    app = MifareAnalyzer()
    app.mainloop()
