import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
from PIL import Image, ImageDraw, ImageTk, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import random, os
import platform
import sys

preview_window = None
preview_canvas = None

# Stałe
CM_TO_PT = 28.35  # 1 cm = 28.35 punktów PDF
CM_TO_PX = 37.8  # 1 cm ≈ 37.8 px (96 DPI)


def resource_path(*relative_parts: str) -> str:
    """Resolve a resource path for both source runs and PyInstaller bundles."""
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, *relative_parts)


# Funkcja do znajdowania dostępnych czcionek
def get_available_fonts():
    system = platform.system()
    font_list = []

    # Ścieżki do czcionek w różnych systemach
    font_dirs = []
    if system == "Windows":
        font_dirs = [
            "C:\\Windows\\Fonts\\",
            "C:\\Windows\\System32\\Fonts\\"
        ]
    elif system == "Darwin":  # macOS
        font_dirs = [
            "/System/Library/Fonts/",
            "/Library/Fonts/",
            os.path.expanduser("~/Library/Fonts/")
        ]
    else:  # Linux
        font_dirs = [
            "/usr/share/fonts/",
            "/usr/local/share/fonts/",
            os.path.expanduser("~/.fonts/"),
            "/usr/share/fonts/truetype/",
            "/usr/share/fonts/opentype/"
        ]

    # Przeszukaj katalogi czcionek
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            try:
                for root, dirs, files in os.walk(font_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            full_path = os.path.join(root, file)
                            font_list.append((file, full_path))
            except PermissionError:
                continue

    # Dodaj popularne nazwy czcionek
    common_fonts = [
        ("Arial", "arial.ttf"),
        ("Times New Roman", "times.ttf"),
        ("Courier New", "cour.ttf"),
        ("Calibri", "calibri.ttf"),
        ("Verdana", "verdana.ttf"),
        ("Tahoma", "tahoma.ttf"),
        ("Comic Sans MS", "comic.ttf"),
        ("Impact", "impact.ttf"),
        ("Georgia", "georgia.ttf"),
        ("Trebuchet MS", "trebuc.ttf")
    ]

    # Usuń duplikaty i posortuj
    all_fonts = list(set(font_list + common_fonts))
    all_fonts.sort(key=lambda x: x[0].lower())

    return all_fonts


def generate_bingo_numbers(cols, rows, use_standard=True):
    """
    PK BINGO PK EDITION FORMAT XD
    """
    numbers = []

    if use_standard and cols == 5:
        # Standardowe zakresy dla Bingo
        ranges = [
            (1, 18),  # B
            (19, 36),  # I
            (37, 54),  # N
            (55, 72),  # G
            (73, 90)  # O
        ]

        for col in range(cols):
            start, end = ranges[col]
            col_numbers = random.sample(range(start, end + 1), rows)
            numbers.append(col_numbers)
    else:
        # Jeśli nie używamy standardu lub liczba kolumn != 5
        # Użyj ogólnych zakresów z pól from/to
        num_from = int(from_entry.get())
        num_to = int(to_entry.get())
        available_numbers = list(range(num_from, num_to + 1))

        # Podziel zakres równo na kolumny
        range_size = (num_to - num_from + 1) // cols

        for col in range(cols):
            if col == cols - 1:
                # Ostatnia kolumna bierze wszystkie pozostałe liczby
                start = num_from + col * range_size
                end = num_to
            else:
                start = num_from + col * range_size
                end = start + range_size - 1

            col_range = list(range(start, end + 1))
            if len(col_range) >= rows:
                col_numbers = random.sample(col_range, rows)
            else:
                col_numbers = random.choices(col_range, k=rows)

            numbers.append(col_numbers)

    return numbers


def generate_card(cols, rows, num_from, num_to, width_cm, height_cm, top_margin_cm,
                  bg_path=None, square_bg_color="white", font_path="arial.ttf", font_size=20,
                  padding_cm=0.2, left_margin_cm=0.5, square_w_cm=None, square_h_cm=None,
                  center_img_path=None, use_standard_bingo=True):
    width_px = int(width_cm * CM_TO_PX)
    height_px = int(height_cm * CM_TO_PX)
    margin = int(padding_cm * CM_TO_PX)
    left_margin_px = int(left_margin_cm * CM_TO_PX)

    # Jeśli brak indywidualnych wymiarów kwadratu, dopasuj automatycznie
    cell_w_px = int(square_w_cm * CM_TO_PX) if square_w_cm else int(
        (width_px - 2 * left_margin_px - (cols - 1) * margin) / cols)
    cell_h_px = int(square_h_cm * CM_TO_PX) if square_h_cm else int(
        (height_px - int(top_margin_cm * CM_TO_PX) - (rows - 1) * margin) / rows)

    img = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(img)

    # Czcionka
    font = None
    font_px = int(font_size * CM_TO_PX / CM_TO_PT)

    if font_path and font_path.strip():
        try:
            font = ImageFont.truetype(font_path, font_px)
        except Exception as e:
            print(f"Błąd ładowania czcionki {font_path}: {e}")

    if font is None:
        for fallback in ["arial.ttf", "DejaVuSans.ttf", "calibri.ttf", "tahoma.ttf"]:
            try:
                font = ImageFont.truetype(fallback, font_px)
                break
            except:
                continue
    if font is None:
        font = ImageFont.load_default()

    # Tło
    if bg_path and os.path.exists(bg_path):
        try:
            bg_img = Image.open(bg_path).resize((width_px, height_px))
            img.paste(bg_img, (0, 0))
        except Exception as e:
            print(f"Błąd ładowania tła: {e}")

    # Generuj liczby według standardu Bingo
    numbers_by_column = generate_bingo_numbers(cols, rows, use_standard_bingo)

    middle_r = rows // 2 if rows % 2 == 1 else None
    middle_c = cols // 2 if cols % 2 == 1 else None

    # Rysowanie kwadratów
    for r in range(rows):
        for c in range(cols):
            x0 = left_margin_px + c * (cell_w_px + margin)
            y0 = int(top_margin_cm * CM_TO_PX) + r * (cell_h_px + margin)
            x1 = x0 + cell_w_px
            y1 = y0 + cell_h_px

            draw.rectangle([x0, y0, x1, y1], fill=square_bg_color, outline="black", width=2)

            if center_img_path and middle_r is not None and middle_c is not None and r == middle_r and c == middle_c:
                try:
                    center_img = Image.open(center_img_path)

                    # Konwertuj do RGBA jeśli obrazek ma przezroczystość
                    if center_img.mode in ('RGBA', 'LA') or (
                            center_img.mode == 'P' and 'transparency' in center_img.info):
                        center_img = center_img.convert('RGBA')
                    else:
                        center_img = center_img.convert('RGB')

                    # Rozciągnij obrazek na cały kwadrat (bez zachowania proporcji)
                    center_img = center_img.resize((cell_w_px, cell_h_px), Image.Resampling.LANCZOS)

                    # Wklej z zachowaniem przezroczystości
                    if center_img.mode == 'RGBA':
                        img.paste(center_img, (x0, y0), center_img)
                    else:
                        img.paste(center_img, (x0, y0))

                    continue
                except Exception as e:
                    print(f"Błąd wstawiania obrazka do środka: {e}")

            # Normalna liczba - pobierz z odpowiedniej kolumny
            num = str(numbers_by_column[c][r])
            try:
                bbox = draw.textbbox((0, 0), num, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except:
                text_w, text_h = draw.textsize(num, font=font)

            text_x = x0 + (cell_w_px - text_w) / 2
            text_y = y0 + (cell_h_px - text_h) / 2
            draw.text((text_x, text_y), num, fill="black", font=font)

    return img


def update_font_preview(*args):
    selection = font_listbox.curselection()
    if selection:
        index = selection[0]
        value = font_listbox.get(index)
        if " | " in value:
            font_name_or_path = value.split(" | ")[1]
            font_entry.delete(0, tk.END)
            font_entry.insert(0, font_name_or_path)


# Podgląd
def show_preview():
    global preview_window, preview_canvas
    try:
        cols = int(cols_entry.get())
        rows = int(rows_entry.get())
        num_from = int(from_entry.get())
        num_to = int(to_entry.get())
        width_cm = float(width_entry.get())
        height_cm = float(height_entry.get())
        top_margin_cm = float(top_margin_entry.get())
        bg_path = background_entry.get() if background_entry.get().strip() else None
        square_color = square_color_var.get()
        font_path = font_entry.get() if font_entry.get().strip() else None
        font_size = int(font_size_entry.get())
        padding_cm = float(padding_entry.get())
        square_w_cm = float(square_width_entry.get()) if square_width_entry.get() else None
        square_h_cm = float(square_height_entry.get()) if square_height_entry.get() else None
        left_margin_cm = float(left_margin_entry.get())
        center_img_path = center_img_entry.get() if center_img_entry.get().strip() else None
        use_standard = standard_bingo_var.get()

        img = generate_card(
            cols, rows, num_from, num_to,
            width_cm, height_cm, top_margin_cm,
            bg_path, square_color, font_path, font_size,
            padding_cm, left_margin_cm, square_w_cm, square_h_cm,
            center_img_path, use_standard
        )

        max_preview_size = 800
        if img.width > max_preview_size or img.height > max_preview_size:
            ratio = min(max_preview_size / img.width, max_preview_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            preview_img = img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            preview_img = img

        if preview_window is None or not preview_window.winfo_exists():
            preview_window = tk.Toplevel(root)
            preview_window.title("Podgląd karty")
            preview_canvas = tk.Canvas(preview_window, width=preview_img.width, height=preview_img.height, bg="gray")
            preview_canvas.pack()
        else:
            preview_canvas.config(width=preview_img.width, height=preview_img.height)

        preview_tk = ImageTk.PhotoImage(preview_img)
        preview_canvas.image = preview_tk
        preview_canvas.delete("all")
        preview_canvas.create_image(0, 0, anchor="nw", image=preview_tk)

    except Exception as e:
        messagebox.showerror("Błąd podglądu", f"Błąd: {str(e)}")


# Funkcje wyboru plików i kolorów
def choose_background():
    path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if path:
        background_entry.delete(0, tk.END)
        background_entry.insert(0, path)


def choose_font():
    path = filedialog.askopenfilename(filetypes=[("Czcionki", "*.ttf *.otf")])
    if path:
        font_entry.delete(0, tk.END)
        font_entry.insert(0, path)


def choose_square_color():
    color_code = colorchooser.askcolor(title="Wybierz kolor kwadratów")
    if color_code[1]:
        square_color_var.set(color_code[1])


def choose_file(entry_widget):
    path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, path)


def find_center():
    try:
        cols = int(cols_entry.get())
        padding_cm_val = float(padding_entry.get())

        if square_width_entry.get():
            square_w_cm_val = float(square_width_entry.get())
        else:
            width_cm_card = float(width_entry.get())
            square_w_cm_val = width_cm_card / cols

        total_content_width = cols * square_w_cm_val + (cols - 1) * padding_cm_val
        width_cm_card = float(width_entry.get())
        margin_cm = max((width_cm_card - total_content_width) / 2, 0)

        left_margin_entry.delete(0, tk.END)
        left_margin_entry.insert(0, f"{margin_cm:.2f}")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można wyliczyć centrum: {e}")


def generate_pdf():
    try:
        cols = int(cols_entry.get())
        rows = int(rows_entry.get())
        num_from = int(from_entry.get())
        num_to = int(to_entry.get())
        width_cm = float(width_entry.get())
        height_cm = float(height_entry.get())
        top_margin_cm = float(top_margin_entry.get())
        count = int(count_entry.get())
        bg_path = background_entry.get() if background_entry.get().strip() else None
        square_color = square_color_var.get()
        font_path = font_entry.get() if font_entry.get().strip() else None
        font_size = int(font_size_entry.get())
        padding_cm = float(padding_entry.get())
        left_margin_cm = float(left_margin_entry.get())
        square_w_cm = float(square_width_entry.get()) if square_width_entry.get() else None
        square_h_cm = float(square_height_entry.get()) if square_height_entry.get() else None
        center_img_path = center_img_entry.get() if center_img_entry.get().strip() else None
        use_standard = standard_bingo_var.get()

        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not pdf_path:
            return

        c = canvas.Canvas(pdf_path, pagesize=A4)
        page_w, page_h = A4
        card_w_pt = width_cm * CM_TO_PT
        card_h_pt = height_cm * CM_TO_PT

        x_cursor = 0
        y_cursor = page_h - card_h_pt

        for i in range(count):
            img = generate_card(cols, rows, num_from, num_to, width_cm, height_cm, top_margin_cm,
                                bg_path, square_color, font_path, font_size, padding_cm,
                                left_margin_cm, square_w_cm, square_h_cm, center_img_path, use_standard)

            tmp_path = f"_tmp_card_{i}.png"
            img.save(tmp_path, "PNG")

            if x_cursor + card_w_pt > page_w:
                x_cursor = 0
                y_cursor -= card_h_pt

            if y_cursor < 0:
                c.showPage()
                x_cursor = 0
                y_cursor = page_h - card_h_pt

            c.drawImage(tmp_path, x_cursor, y_cursor, card_w_pt, card_h_pt)

            try:
                os.remove(tmp_path)
            except:
                pass

            x_cursor += card_w_pt

        c.save()
        messagebox.showinfo("Sukces", f"Karty zapisane do {pdf_path}")

    except Exception as e:
        messagebox.showerror("Błąd PDF", f"Błąd generowania PDF: {str(e)}")


# --- GUI ---
root = tk.Tk()
root.title("Generator Kart Bingo - Standard Edition")
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Checkbox dla standardowego Bingo
standard_bingo_var = tk.BooleanVar(value=False)
standard_check = tk.Checkbutton(frame,
                                text="Użyj formatu PK BINGO",
                                variable=standard_bingo_var, fg="blue", font=("Arial", 9, "bold"))
standard_check.grid(row=0, column=0, columnspan=3, sticky="w", pady=5)

# Pola wejściowe
tk.Label(frame, text="Od liczby:").grid(row=1, column=0, sticky="w")
from_entry = tk.Entry(frame)
from_entry.insert(0, "1")
from_entry.grid(row=1, column=1, padx=5, pady=2)

tk.Label(frame, text="Do liczby:").grid(row=2, column=0, sticky="w")
to_entry = tk.Entry(frame)
to_entry.insert(0, "75")
to_entry.grid(row=2, column=1, padx=5, pady=2)

tk.Label(frame, text="Kolumny:").grid(row=3, column=0, sticky="w")
cols_entry = tk.Entry(frame)
cols_entry.insert(0, "5")
cols_entry.grid(row=3, column=1, padx=5, pady=2)

tk.Label(frame, text="Wiersze:").grid(row=4, column=0, sticky="w")
rows_entry = tk.Entry(frame)
rows_entry.insert(0, "5")
rows_entry.grid(row=4, column=1, padx=5, pady=2)

tk.Label(frame, text="Szerokość [cm]:").grid(row=5, column=0, sticky="w")
width_entry = tk.Entry(frame)
width_entry.insert(0, "10.4")
width_entry.grid(row=5, column=1, padx=5, pady=2)

tk.Label(frame, text="Wysokość [cm]:").grid(row=6, column=0, sticky="w")
height_entry = tk.Entry(frame)
height_entry.insert(0, "14.8")
height_entry.grid(row=6, column=1, padx=5, pady=2)

tk.Label(frame, text="Miejsce na górze [cm]:").grid(row=7, column=0, sticky="w")
top_margin_entry = tk.Entry(frame)
top_margin_entry.insert(0, "4.25")
top_margin_entry.grid(row=7, column=1, padx=5, pady=2)

tk.Label(frame, text="Ilość kart:").grid(row=8, column=0, sticky="w")
count_entry = tk.Entry(frame)
count_entry.insert(0, "30")
count_entry.grid(row=8, column=1, padx=5, pady=2)

# Tło
tk.Label(frame, text="Tło (ścieżka):").grid(row=9, column=0, sticky="w")
background_entry = tk.Entry(frame, width=30)
background_entry.insert(0, resource_path("assets", "karta.png"))
background_entry.grid(row=9, column=1, padx=5, pady=2)
choose_bg_btn = tk.Button(frame, text="Wybierz...", command=choose_background)
choose_bg_btn.grid(row=9, column=2, padx=5)

# Obrazek w środku
tk.Label(frame, text="Obrazek w środku:").grid(row=10, column=0, sticky="w")
center_img_entry = tk.Entry(frame, width=30)
center_img_entry.insert(0, resource_path("assets", "kwadrat_kolor_cut_no_border.png"))
center_img_entry.grid(row=10, column=1, padx=5, pady=2)
choose_center_img_btn = tk.Button(frame, text="Wybierz...", command=lambda: choose_file(center_img_entry))
choose_center_img_btn.grid(row=10, column=2, padx=5)

# Kolor kwadratów
square_color_var = tk.StringVar(value="white")
choose_color_btn = tk.Button(frame, text="Wybierz kolor kwadratów", command=choose_square_color)
choose_color_btn.grid(row=11, column=0, columnspan=3, pady=5)

# Przyciski główne
preview_btn = tk.Button(frame, text="Podgląd", command=show_preview, bg="lightblue")
preview_btn.grid(row=12, column=0, pady=5)
generate_btn = tk.Button(frame, text="Generuj PDF", command=generate_pdf, bg="lightgreen")
generate_btn.grid(row=12, column=1, pady=5)

# Czcionka
tk.Label(frame, text="Ścieżka czcionki:").grid(row=13, column=0, sticky="w")
font_entry = tk.Entry(frame, width=30)
font_entry.insert(0, resource_path("assets", "Luckiest_Guy", "LuckiestGuy-Regular.ttf"))
font_entry.grid(row=13, column=1, padx=5, pady=2)
choose_font_btn = tk.Button(frame, text="Wybierz czcionkę", command=choose_font)
choose_font_btn.grid(row=13, column=2, padx=5)

tk.Label(frame, text="Lista czcionek:").grid(row=14, column=0, sticky="w")
font_listbox = tk.Listbox(frame, width=40, height=10)
font_listbox.grid(row=14, column=1, padx=5, pady=5)
font_listbox.bind("<<ListboxSelect>>", update_font_preview)

available_fonts = get_available_fonts()
for name, path in available_fonts:
    font_listbox.insert(tk.END, f"{name} | {path}")

tk.Label(frame, text="Rozmiar czcionki:").grid(row=15, column=0, sticky="w")
font_size_entry = tk.Entry(frame)
font_size_entry.insert(0, "24")
font_size_entry.grid(row=15, column=1, padx=5, pady=2)

# Marginesy i rozmiary
tk.Label(frame, text="Odstęp [cm]:").grid(row=16, column=0, sticky="w")
padding_entry = tk.Entry(frame)
padding_entry.insert(0, "0.2")
padding_entry.grid(row=16, column=1, padx=5, pady=2)

tk.Label(frame, text="Margines z lewej [cm]:").grid(row=17, column=0, sticky="w")
left_margin_entry = tk.Entry(frame)
left_margin_entry.insert(0, "1.15   ")
left_margin_entry.grid(row=17, column=1, padx=5, pady=2)

tk.Label(frame, text="Szerokość kwadratu [cm]:").grid(row=18, column=0, sticky="w")
square_width_entry = tk.Entry(frame)
square_width_entry.insert(0, "1.5")
square_width_entry.grid(row=18, column=1, padx=5, pady=2)

tk.Label(frame, text="Wysokość kwadratu [cm]:").grid(row=19, column=0, sticky="w")
square_height_entry = tk.Entry(frame)
square_height_entry.insert(0,"1.5")
square_height_entry.grid(row=19, column=1, padx=5, pady=2)

center_btn = tk.Button(frame, text="Znajdź centrum", command=find_center, bg="orange")
center_btn.grid(row=20, column=0, columnspan=2, pady=5)

root.mainloop()